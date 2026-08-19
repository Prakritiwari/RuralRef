from fastapi import APIRouter
from .auth import router as auth_router
from .phcs import router as phcs_router
from .hospitals import router as hospitals_router
from .resources import router as resources_router
from .referrals import router as referrals_router
from .ambulances import router as ambulances_router
from .tracking import router as tracking_router
from .dashboard import router as dashboard_router

api_router = APIRouter(prefix="/api")

api_router.include_router(auth_router)
api_router.include_router(phcs_router)
api_router.include_router(hospitals_router)
api_router.include_router(resources_router)
api_router.include_router(referrals_router)
api_router.include_router(ambulances_router)
api_router.include_router(tracking_router)
api_router.include_router(dashboard_router)
