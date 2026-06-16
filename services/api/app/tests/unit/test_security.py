from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    hash_phone,
    mask_phone,
    verify_password,
)


def test_access_token_round_trip() -> None:
    token = create_access_token(subject_type="app_user", subject_id=123, ttl_seconds=60)

    payload = decode_access_token(token, expected_type="app_user")

    assert payload["typ"] == "app_user"
    assert payload["sub"] == "123"


def test_password_hash_and_verify() -> None:
    password_hash = hash_password("secret-password")

    assert verify_password("secret-password", password_hash)
    assert not verify_password("wrong-password", password_hash)


def test_phone_mask_and_hash() -> None:
    assert mask_phone("13812345678") == "138****5678"
    assert hash_phone("13812345678") == hash_phone("138 1234 5678")
