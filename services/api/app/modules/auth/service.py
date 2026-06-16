"""认证业务服务。"""

from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    TokenError,
    create_access_token,
    decode_access_token,
    hash_phone,
    mask_phone,
    normalize_phone,
    verify_password,
)
from app.modules.auth import repository
from app.modules.auth.model import AdminUser
from app.modules.auth.schema import (
    AdminLoginRequest,
    AdminTokenResponse,
    AdminUserResponse,
    AppPhoneAuthorizeRequest,
    AppWechatLoginRequest,
    AuthTokenResponse,
    AuthUserResponse,
    PhoneAuthorizeResponse,
)
from app.modules.user.model import AppUser


class AuthServiceError(ValueError):
    """认证业务错误，router 层会转成 HTTP 响应。"""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


@dataclass(frozen=True)
class WechatSession:
    appid: str
    openid: str
    unionid: str | None


def _auth_user_response(user: AppUser) -> AuthUserResponse:
    return AuthUserResponse(
        id=user.id,
        nickname=user.nickname,
        avatar_url=user.avatar_url,
        phone_masked=user.phone_masked,
        status=user.status,
        has_phone_authorized=bool(user.phone_hash),
    )


def _admin_response(admin: AdminUser) -> AdminUserResponse:
    return AdminUserResponse(
        id=admin.id,
        username=admin.username,
        display_name=admin.display_name,
        phone_masked=admin.phone_masked,
        status=admin.status,
    )


def _wechat_secret_value() -> str | None:
    if settings.wechat_miniapp_secret is None:
        return None
    return settings.wechat_miniapp_secret.get_secret_value()


def _wechat_credentials_available() -> bool:
    return bool(settings.wechat_miniapp_appid and _wechat_secret_value())


def _request_json(url: str, *, method: str = "GET", payload: dict[str, Any] | None = None) -> dict[str, Any]:
    data = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            body = response.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise AuthServiceError("微信服务请求失败", status_code=502) from exc

    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise AuthServiceError("微信服务响应解析失败", status_code=502) from exc


def _exchange_code_for_wechat_session(code: str) -> WechatSession:
    if _wechat_credentials_available():
        query = urllib.parse.urlencode(
            {
                "appid": settings.wechat_miniapp_appid,
                "secret": _wechat_secret_value(),
                "js_code": code,
                "grant_type": "authorization_code",
            }
        )
        payload = _request_json(f"https://api.weixin.qq.com/sns/jscode2session?{query}")
        if payload.get("errcode"):
            raise AuthServiceError(f"微信登录失败：{payload.get('errmsg', 'unknown error')}", status_code=400)

        openid = payload.get("openid")
        if not openid:
            raise AuthServiceError("微信登录失败：缺少 openid", status_code=502)

        return WechatSession(
            appid=settings.wechat_miniapp_appid or "unknown",
            openid=openid,
            unionid=payload.get("unionid"),
        )

    if settings.wechat_dev_mock_enabled:
        digest = hashlib.sha256(code.encode("utf-8")).hexdigest()
        return WechatSession(
            appid=settings.wechat_miniapp_appid or "dev-miniapp",
            openid=f"mock_{digest[:32]}",
            unionid=None,
        )

    raise AuthServiceError("未配置微信小程序 AppID/Secret", status_code=503)


def _get_wechat_access_token() -> str:
    if not _wechat_credentials_available():
        raise AuthServiceError("未配置微信小程序 AppID/Secret", status_code=503)

    query = urllib.parse.urlencode(
        {
            "grant_type": "client_credential",
            "appid": settings.wechat_miniapp_appid,
            "secret": _wechat_secret_value(),
        }
    )
    payload = _request_json(f"https://api.weixin.qq.com/cgi-bin/token?{query}")
    if payload.get("errcode"):
        raise AuthServiceError(f"微信 access_token 获取失败：{payload.get('errmsg', 'unknown error')}", status_code=502)

    access_token = payload.get("access_token")
    if not access_token:
        raise AuthServiceError("微信 access_token 响应缺少 access_token", status_code=502)
    return access_token


def _exchange_phone_code(phone_code: str) -> str:
    access_token = _get_wechat_access_token()
    query = urllib.parse.urlencode({"access_token": access_token})
    payload = _request_json(
        f"https://api.weixin.qq.com/wxa/business/getuserphonenumber?{query}",
        method="POST",
        payload={"code": phone_code},
    )
    if payload.get("errcode"):
        raise AuthServiceError(f"微信手机号授权失败：{payload.get('errmsg', 'unknown error')}", status_code=400)

    phone_info = payload.get("phone_info") or {}
    phone_number = phone_info.get("phoneNumber") or phone_info.get("purePhoneNumber")
    if not phone_number:
        raise AuthServiceError("微信手机号授权失败：缺少手机号", status_code=502)
    return normalize_phone(phone_number)


def _resolve_phone_number(request: AppPhoneAuthorizeRequest) -> str:
    if request.dev_phone_number:
        if not settings.wechat_dev_mock_enabled:
            raise AuthServiceError("开发手机号仅允许在 mock 模式使用", status_code=400)
        return normalize_phone(request.dev_phone_number)

    if request.phone_code:
        return _exchange_phone_code(request.phone_code)

    if request.encrypted_data or request.iv:
        raise AuthServiceError("当前 MVP 后端仅支持微信 getPhoneNumber 返回的 code 授权", status_code=400)

    raise AuthServiceError("缺少手机号授权凭证", status_code=400)


def login_with_wechat(db: Session, request: AppWechatLoginRequest) -> AuthTokenResponse:
    wechat_session = _exchange_code_for_wechat_session(request.code)
    identity = repository.get_wechat_identity(
        db,
        openid=wechat_session.openid,
        appid=wechat_session.appid,
    )

    if identity is None:
        user = repository.create_app_user_with_wechat_identity(
            db,
            appid=wechat_session.appid,
            openid=wechat_session.openid,
            unionid=wechat_session.unionid,
            nickname=request.nickname,
            avatar_url=request.avatar_url,
        )
    else:
        user = identity.user
        if user.deleted_at is not None or user.status != "active":
            raise AuthServiceError("用户已被禁用", status_code=403)
        repository.touch_app_user_login(
            db,
            user,
            nickname=request.nickname,
            avatar_url=request.avatar_url,
        )

    db.commit()
    db.refresh(user)

    expires_in = settings.app_access_token_ttl_seconds
    token = create_access_token(subject_type="app_user", subject_id=user.id, ttl_seconds=expires_in)
    return AuthTokenResponse(access_token=token, expires_in=expires_in, user=_auth_user_response(user))


def authorize_phone(
    db: Session,
    *,
    user: AppUser,
    request: AppPhoneAuthorizeRequest,
    ip_address: str | None,
    user_agent: str | None,
) -> PhoneAuthorizeResponse:
    if not request.granted:
        repository.create_user_consent(
            db,
            user_id=user.id,
            consent_type="phone_auth",
            version=request.consent_version,
            granted=False,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.commit()
        db.refresh(user)
        return PhoneAuthorizeResponse(user=_auth_user_response(user), phone_authorized=False)

    phone_number = _resolve_phone_number(request)
    repository.update_app_user_phone(
        db,
        user,
        phone_masked=mask_phone(phone_number),
        phone_hash=hash_phone(phone_number),
    )
    repository.create_user_consent(
        db,
        user_id=user.id,
        consent_type="phone_auth",
        version=request.consent_version,
        granted=True,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.commit()
    db.refresh(user)
    return PhoneAuthorizeResponse(user=_auth_user_response(user), phone_authorized=True)


def login_admin(db: Session, request: AdminLoginRequest) -> AdminTokenResponse:
    admin = repository.get_admin_by_username(db, request.username)
    if admin is None or admin.status != "active" or not verify_password(request.password, admin.password_hash):
        raise AuthServiceError("用户名或密码错误", status_code=401)

    repository.touch_admin_login(db, admin)
    db.commit()
    db.refresh(admin)

    expires_in = settings.admin_access_token_ttl_seconds
    token = create_access_token(subject_type="admin", subject_id=admin.id, ttl_seconds=expires_in)
    return AdminTokenResponse(access_token=token, expires_in=expires_in, admin=_admin_response(admin))


def get_app_user_by_token(db: Session, token: str) -> AppUser:
    try:
        payload = decode_access_token(token, expected_type="app_user")
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError, TokenError) as exc:
        raise AuthServiceError("登录已失效，请重新登录", status_code=401) from exc

    user = repository.get_app_user_by_id(db, user_id)
    if user is None or user.deleted_at is not None or user.status != "active":
        raise AuthServiceError("登录已失效，请重新登录", status_code=401)
    return user


def get_admin_by_token(db: Session, token: str) -> AdminUser:
    try:
        payload = decode_access_token(token, expected_type="admin")
        admin_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError, TokenError) as exc:
        raise AuthServiceError("登录已失效，请重新登录", status_code=401) from exc

    admin = repository.get_admin_by_id(db, admin_id)
    if admin is None or admin.deleted_at is not None or admin.status != "active":
        raise AuthServiceError("登录已失效，请重新登录", status_code=401)
    return admin


def build_app_user_response(user: AppUser) -> AuthUserResponse:
    return _auth_user_response(user)


def build_admin_user_response(admin: AdminUser) -> AdminUserResponse:
    return _admin_response(admin)
