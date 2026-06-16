"""认证模块数据访问。"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.common.datetime import utc_now
from app.modules.auth.model import AdminUser
from app.modules.user.model import AppUser, UserConsent, WechatIdentity


def get_app_user_by_id(db: Session, user_id: int) -> AppUser | None:
    return db.get(AppUser, user_id)


def get_wechat_identity(db: Session, *, openid: str, appid: str) -> WechatIdentity | None:
    statement = select(WechatIdentity).where(
        WechatIdentity.openid == openid,
        WechatIdentity.appid == appid,
    )
    return db.scalar(statement)


def create_app_user_with_wechat_identity(
    db: Session,
    *,
    appid: str,
    openid: str,
    unionid: str | None,
    nickname: str | None,
    avatar_url: str | None,
) -> AppUser:
    user = AppUser(
        nickname=nickname,
        avatar_url=avatar_url,
        status="active",
        last_login_at=utc_now(),
    )
    db.add(user)
    db.flush()

    identity = WechatIdentity(
        user_id=user.id,
        appid=appid,
        openid=openid,
        unionid=unionid,
        session_key_cipher=None,
    )
    db.add(identity)
    db.flush()
    return user


def touch_app_user_login(
    db: Session,
    user: AppUser,
    *,
    nickname: str | None,
    avatar_url: str | None,
) -> AppUser:
    if nickname:
        user.nickname = nickname
    if avatar_url:
        user.avatar_url = avatar_url
    user.last_login_at = utc_now()
    db.add(user)
    db.flush()
    return user


def update_app_user_phone(db: Session, user: AppUser, *, phone_masked: str, phone_hash: str) -> AppUser:
    user.phone_masked = phone_masked
    user.phone_hash = phone_hash
    db.add(user)
    db.flush()
    return user


def create_user_consent(
    db: Session,
    *,
    user_id: int,
    consent_type: str,
    version: str,
    granted: bool,
    ip_address: str | None,
    user_agent: str | None,
) -> UserConsent:
    consent = UserConsent(
        user_id=user_id,
        consent_type=consent_type,
        version=version,
        granted=granted,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(consent)
    db.flush()
    return consent


def get_admin_by_username(db: Session, username: str) -> AdminUser | None:
    statement = select(AdminUser).where(AdminUser.username == username, AdminUser.deleted_at.is_(None))
    return db.scalar(statement)


def get_admin_by_id(db: Session, admin_id: int) -> AdminUser | None:
    return db.get(AdminUser, admin_id)


def touch_admin_login(db: Session, admin: AdminUser) -> AdminUser:
    admin.last_login_at = utc_now()
    db.add(admin)
    db.flush()
    return admin
