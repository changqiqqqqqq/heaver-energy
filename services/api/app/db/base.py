from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Alembic 自动发现元数据时需要导入已登记模型。
from app.modules.auth import model as auth_model  # noqa: E402,F401
from app.modules.questionnaire import model as questionnaire_model  # noqa: E402,F401
from app.modules.user import model as user_model  # noqa: E402,F401
