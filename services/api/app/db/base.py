from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Alembic 自动发现元数据时需要导入已登记模型。
from app.modules.auth import model as auth_model  # noqa: E402,F401
from app.modules.bill import model as bill_model  # noqa: E402,F401
from app.modules.crm import model as crm_model  # noqa: E402,F401
from app.modules.enterprise import model as enterprise_model  # noqa: E402,F401
from app.modules.file import model as file_model  # noqa: E402,F401
from app.modules.lead import model as lead_model  # noqa: E402,F401
from app.modules.questionnaire import model as questionnaire_model  # noqa: E402,F401
from app.modules.screening import model as screening_model  # noqa: E402,F401
from app.modules.security_audit import model as security_audit_model  # noqa: E402,F401
from app.modules.service_request import model as service_request_model  # noqa: E402,F401
from app.modules.supplier import model as supplier_model  # noqa: E402,F401
from app.modules.user import model as user_model  # noqa: E402,F401
