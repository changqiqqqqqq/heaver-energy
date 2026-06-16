from fastapi import APIRouter

from app.modules.auth.router_admin import router as auth_router
from app.modules.crm.router_admin import router as crm_router
from app.modules.lead.router_admin import router as lead_router
from app.modules.questionnaire.router_admin import router as questionnaire_router
from app.modules.security_audit.router_admin import router as security_audit_router
from app.modules.statistics.router_admin import router as statistics_router
from app.modules.supplier.router_admin import router as supplier_router

router = APIRouter(prefix="/admin")
router.include_router(auth_router, prefix="/auth", tags=["admin-auth"])
router.include_router(statistics_router, prefix="/dashboard", tags=["admin-dashboard"])
router.include_router(lead_router, prefix="/leads", tags=["admin-leads"])
router.include_router(supplier_router, prefix="/suppliers", tags=["admin-suppliers"])
router.include_router(questionnaire_router, prefix="/questionnaires", tags=["admin-questionnaires"])
router.include_router(crm_router, prefix="/crm", tags=["admin-crm"])
router.include_router(security_audit_router, prefix="/audit-logs", tags=["admin-audit"])

