"""认证、安全散列与敏感信息处理工具。"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

from app.core.config import settings

TokenSubjectType = Literal["app_user", "admin"]

_PHONE_PATTERN = re.compile(r"^1[3-9]\d{9}$")
_PASSWORD_ALGORITHM = "pbkdf2_sha256"
_PASSWORD_ITERATIONS = 260_000


class TokenError(ValueError):
    """Token 无效、过期或类型不匹配。"""


def _secret_bytes() -> bytes:
    return settings.auth_secret_key.get_secret_value().encode("utf-8")


def _b64_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))


def create_access_token(
    *,
    subject_type: TokenSubjectType,
    subject_id: int,
    ttl_seconds: int,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """创建 HMAC 签名的轻量访问令牌。"""

    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "typ": subject_type,
        "sub": str(subject_id),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=ttl_seconds)).timestamp()),
        "jti": secrets.token_urlsafe(12),
    }
    if extra_claims:
        payload.update(extra_claims)

    payload_bytes = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    encoded_payload = _b64_encode(payload_bytes)
    signature = hmac.new(_secret_bytes(), encoded_payload.encode("ascii"), hashlib.sha256).digest()
    return f"{encoded_payload}.{_b64_encode(signature)}"


def decode_access_token(token: str, *, expected_type: TokenSubjectType | None = None) -> dict[str, Any]:
    """校验并解析访问令牌。"""

    try:
        encoded_payload, encoded_signature = token.split(".", maxsplit=1)
    except ValueError as exc:
        raise TokenError("token format invalid") from exc

    expected_signature = hmac.new(_secret_bytes(), encoded_payload.encode("ascii"), hashlib.sha256).digest()
    try:
        actual_signature = _b64_decode(encoded_signature)
    except (ValueError, TypeError) as exc:
        raise TokenError("token signature invalid") from exc

    if not hmac.compare_digest(expected_signature, actual_signature):
        raise TokenError("token signature invalid")

    try:
        payload = json.loads(_b64_decode(encoded_payload))
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        raise TokenError("token payload invalid") from exc

    if expected_type and payload.get("typ") != expected_type:
        raise TokenError("token subject type mismatch")

    exp = payload.get("exp")
    if not isinstance(exp, int) or exp < int(datetime.now(UTC).timestamp()):
        raise TokenError("token expired")

    return payload


def hash_password(password: str) -> str:
    """使用 PBKDF2 保存后台管理员密码。"""

    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PASSWORD_ITERATIONS)
    return "$".join(
        [
            _PASSWORD_ALGORITHM,
            str(_PASSWORD_ITERATIONS),
            _b64_encode(salt),
            _b64_encode(digest),
        ]
    )


def verify_password(password: str, password_hash: str) -> bool:
    """校验后台管理员密码。"""

    try:
        algorithm, iterations_text, salt_text, digest_text = password_hash.split("$", maxsplit=3)
        iterations = int(iterations_text)
    except ValueError:
        return False

    if algorithm != _PASSWORD_ALGORITHM:
        return False

    try:
        salt = _b64_decode(salt_text)
        expected_digest = _b64_decode(digest_text)
    except (ValueError, TypeError):
        return False

    actual_digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(expected_digest, actual_digest)


def normalize_phone(phone_number: str) -> str:
    """规范化中国大陆手机号，当前 MVP 只接受 11 位手机号。"""

    normalized = re.sub(r"\D", "", phone_number)
    if not _PHONE_PATTERN.match(normalized):
        raise ValueError("invalid phone number")
    return normalized


def mask_phone(phone_number: str) -> str:
    normalized = normalize_phone(phone_number)
    return f"{normalized[:3]}****{normalized[-4:]}"


def hash_phone(phone_number: str) -> str:
    normalized = normalize_phone(phone_number)
    return hmac.new(_secret_bytes(), normalized.encode("utf-8"), hashlib.sha256).hexdigest()


def extract_bearer_token(authorization: str | None) -> str:
    """从 Authorization 头中提取 Bearer token。"""

    if not authorization:
        raise TokenError("missing authorization header")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise TokenError("authorization scheme invalid")

    return token
