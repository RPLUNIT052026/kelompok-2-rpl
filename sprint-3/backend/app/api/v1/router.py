from fastapi import APIRouter

from app.api.v1.admin_reports import router as admin_reports_router
from app.api.v1.admin_routes import router as admin_routes_router
from app.api.v1.devices import router as devices_router
from app.api.v1.hazards import router as hazards_router
from app.api.v1.health import router as health_router
from app.api.v1.reports import router as reports_router
from app.api.v1.routes import router as routes_router
from app.api.v1.twin import router as twin_router

router = APIRouter(prefix="/v1")
router.include_router(devices_router)
router.include_router(hazards_router)
router.include_router(routes_router)
router.include_router(health_router)
router.include_router(reports_router)
router.include_router(admin_reports_router)
router.include_router(admin_routes_router)
router.include_router(twin_router)
