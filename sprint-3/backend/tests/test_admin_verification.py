import base64
import hashlib
import hmac
import json
from datetime import datetime, timezone
from types import SimpleNamespace

from app.models.entities import RoadSegment
from sprint3b_fakes import DEVICE_ID, REPORT_ID, SEGMENT_ID, Sprint3BSession


def _jwt(role):
    encode = lambda value: base64.urlsafe_b64encode(
        json.dumps(value, separators=(",", ":")).encode()
    ).decode().rstrip("=")
    header = encode({"alg": "HS256", "typ": "JWT"})
    claims = encode(
        {
            "sub": "00000000-0000-0000-0000-000000000002",
            "role": role,
            "exp": int(datetime.now(timezone.utc).timestamp()) + 600,
        }
    )
    signature = hmac.new(
        b"test-jwt-secret", f"{header}.{claims}".encode(), hashlib.sha256
    ).digest()
    return f"{header}.{claims}.{base64.urlsafe_b64encode(signature).decode().rstrip('=')}"


def _pending_report(db, segment_status="AMAN", report_type="tertutup"):
    segment = db.get(RoadSegment, SEGMENT_ID)
    segment.status = segment_status
    report = SimpleNamespace(
        id=REPORT_ID,
        segment_id=SEGMENT_ID,
        device_id=DEVICE_ID,
        tipe=report_type,
        lat=4.4683,
        lng=97.9683,
        catatan="test report",
        skor_kepercayaan=0.8,
        status="menunggu_tinjauan",
        diverifikasi_oleh=None,
        dibuat_pada=datetime.now(timezone.utc),
    )
    db.reports.append(report)
    return report, segment


def test_admin_routes_require_authentication_and_operator_role(api_client, api_state, operator_headers):
    api_state.db = Sprint3BSession()

    missing_token = api_client.get("/v1/admin/reports")
    assert missing_token.status_code == 401
    assert missing_token.json()["error"]["code"] == "UNAUTHORIZED"

    invalid_token = api_client.get(
        "/v1/admin/reports",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert invalid_token.status_code == 401
    assert invalid_token.headers["www-authenticate"] == "Bearer"

    warga_headers = {"Authorization": f"Bearer {_jwt('warga')}"}
    forbidden = api_client.get("/v1/admin/reports", headers=warga_headers)
    assert forbidden.status_code == 403
    assert forbidden.json()["error"]["code"] == "FORBIDDEN"


def test_operator_lists_reports_and_accepts_closed_report(api_client, api_state, operator_headers):
    db = Sprint3BSession()
    report, segment = _pending_report(db)
    api_state.db = db

    queue = api_client.get("/v1/admin/reports", headers=operator_headers)
    assert queue.status_code == 200
    assert queue.json()["data"][0]["id"] == str(REPORT_ID)

    response = api_client.patch(
        f"/v1/admin/reports/{REPORT_ID}",
        headers=operator_headers,
        json={"keputusan": "diterima"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "diterima"
    assert response.json()["road_segment_status"] == "TERTUTUP"
    assert response.json()["reputasi_diperbarui"] is True
    assert response.json()["rute_dihitung_ulang"] is True
    assert db.devices[DEVICE_ID].reputasi == 0.6
    assert segment.status == "TERTUTUP"


def test_rejected_temporary_closure_reopens_and_lowers_reputation(api_client, api_state, operator_headers):
    db = Sprint3BSession()
    report, segment = _pending_report(db, "TERTUTUP_SEMENTARA")
    api_state.db = db

    response = api_client.patch(
        f"/v1/admin/reports/{REPORT_ID}",
        headers=operator_headers,
        json={"keputusan": "ditolak"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ditolak"
    assert response.json()["road_segment_status"] == "AMAN"
    assert response.json()["rute_dihitung_ulang"] is True
    assert db.devices[DEVICE_ID].reputasi == 0.35
    assert segment.status == "AMAN"


def test_signed_admin_jwt_is_authorized(api_client, api_state, operator_headers):
    api_state.db = Sprint3BSession()
    headers = {"Authorization": f"Bearer {_jwt('admin')}"}

    response = api_client.get("/v1/admin/reports", headers=headers)

    assert response.status_code == 200
    assert response.json() == {"data": []}


def test_cors_preflight_allows_dashboard_origin(api_client):
    response = api_client.options(
        "/v1/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
