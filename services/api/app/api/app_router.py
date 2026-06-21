from fastapi import APIRouter

from app.modules.auth.router_app import router as auth_router
from app.modules.bill.router_app import router as bill_router
from app.modules.enterprise.router_app import router as enterprise_router
from app.modules.file.router_app import router as file_router
from app.modules.questionnaire.router_app import router as questionnaire_router
from app.modules.screening.router_app import router as screening_router
from app.modules.service_request.router_app import router as service_request_router
from app.modules.user.router_app import router as user_router

router = APIRouter(prefix="/app")
router.include_router(auth_router, prefix="/auth", tags=["app-auth"])
router.include_router(user_router, prefix="/users", tags=["app-users"])
router.include_router(enterprise_router, prefix="/enterprises", tags=["app-enterprises"])
router.include_router(questionnaire_router, prefix="/questionnaires", tags=["app-questionnaires"])
router.include_router(screening_router, prefix="/screening-requests", tags=["app-screening"])
router.include_router(service_request_router, prefix="/service-requests", tags=["app-service-requests"])
router.include_router(bill_router, prefix="/bills", tags=["app-bills"])
router.include_router(file_router, prefix="/files", tags=["app-files"])

