import logging
from uuid import UUID

from app.models.entities import Hazard

logger = logging.getLogger(__name__)


def trigger_emergency_hooks(rw_id: UUID, hazard: Hazard) -> list[str]:
    hooks = ["digital_twin_engine", "routing_engine", "push_notification_fcm_apns"]
    logger.info(
        "Emergency hooks triggered",
        extra={
            "rw_id": str(rw_id),
            "hazard_id": str(hazard.id),
            "hooks": hooks,
        },
    )
    return hooks
