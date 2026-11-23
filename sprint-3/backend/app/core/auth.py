import base64
import hashlib
import hmac
import json
import math
import time
from typing import Literal
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.core.config import get_settings

_bearer_scheme = HTTPBearer(auto_error=False)


class OperatorPrincipal(BaseModel):
    id: UUID
    role: Literal["operator", "admin"]


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=401,
        detail={"code": "UNAUTHORIZED", "message": "Token operator tidak valid"},
        headers={"WWW-Authenticate": "Bearer"},
    )


def _decode_segment(segment: str) -> dict:
    padding = "=" * (-len(segment) % 4)
    decoded = base64.urlsafe_b64decode(segment + padding)
    value = json.loads(decoded)
    if not isinstance(value, dict):
        raise ValueError("JWT segment must contain an object")
    return value


def _decode_jwt(token: str, secret: str) -> dict | None:
    if not secret:
        return None
    parts = token.split(".")
    if len(parts) != 3:
        return None
    try:
        header = _decode_segment(parts[0])
        claims = _decode_segment(parts[1])
        if header.get("alg") != "HS256":
            return None
        expected = hmac.new(
            secret.encode("utf-8"),
            f"{parts[0]}.{parts[1]}".encode("ascii"),
            hashlib.sha256,
        ).digest()
        actual = base64.urlsafe_b64decode(parts[2] + "=" * (-len(parts[2]) % 4))
        if not hmac.compare_digest(expected, actual):
            return None
        now = time.time()
        for claim in ("exp", "nbf"):
            if claim in claims:
                value = claims[claim]
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    return None
                if not math.isfinite(value):
                    return None
        if "exp" in claims and claims["exp"] <= now:
            return None
        if "nbf" in claims and claims["nbf"] > now:
            return None
        return claims
    except (ValueError, TypeError, KeyError, OverflowError, json.JSONDecodeError):
        return None


def require_operator(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> OperatorPrincipal:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _unauthorized()

    token = credentials.credentials
    settings = get_settings()
    if settings.operator_api_token and hmac.compare_digest(token, settings.operator_api_token):
        if settings.operator_user_id is None:
            raise _unauthorized()
        return OperatorPrincipal(id=settings.operator_user_id, role="operator")

    claims = _decode_jwt(token, settings.auth_jwt_secret)
    if claims is None:
        raise _unauthorized()

    try:
        subject = UUID(str(claims["sub"]))
    except (KeyError, TypeError, ValueError):
        raise _unauthorized() from None
    role = claims.get("role")
    if not isinstance(role, str) or role not in {"operator", "admin"}:
        raise HTTPException(
            status_code=403,
            detail={"code": "FORBIDDEN", "message": "Role tidak memiliki akses operator"},
        )
    return OperatorPrincipal(id=subject, role=role)
