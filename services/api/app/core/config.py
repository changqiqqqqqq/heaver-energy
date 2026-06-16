from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


API_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "heaver-energy-api"
    auth_secret_key: SecretStr = SecretStr("dev-only-change-me")
    app_access_token_ttl_seconds: int = 7 * 24 * 60 * 60
    admin_access_token_ttl_seconds: int = 12 * 60 * 60

    database_url: str | None = Field(default=None, description="Full SQLAlchemy database URL override.")
    database_driver: str = "mysql+pymysql"
    database_host: str = "127.0.0.1"
    database_port: int = 3306
    database_name: str = "heaver_energy"
    database_user: str = "root"
    database_password: SecretStr = SecretStr("")
    database_echo: bool = False
    database_pool_size: int = 5
    database_max_overflow: int = 10
    database_pool_recycle_seconds: int = 1800

    redis_url: str = "redis://localhost:6379/0"

    wechat_miniapp_appid: str | None = None
    wechat_miniapp_secret: SecretStr | None = None
    wechat_dev_mock_enabled: bool = True

    model_config = SettingsConfigDict(
        env_file=API_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.database_url:
            return self.database_url

        return URL.create(
            drivername=self.database_driver,
            username=self.database_user,
            password=self.database_password.get_secret_value(),
            host=self.database_host,
            port=self.database_port,
            database=self.database_name,
        ).render_as_string(hide_password=False)


settings = Settings()
