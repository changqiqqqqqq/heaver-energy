"""创建认证与测评核心表

Revision ID: 20260614_0001
Revises:
Create Date: 2026-06-14
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

revision: str = "20260614_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ID_TYPE = mysql.BIGINT(unsigned=True)
DATETIME_TYPE = mysql.DATETIME(fsp=3)


def _timestamp_columns(include_deleted_at: bool = True) -> list[sa.Column]:
    columns = [
        sa.Column("created_at", DATETIME_TYPE, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP(3)")),
        sa.Column("updated_at", DATETIME_TYPE, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP(3)")),
    ]
    if include_deleted_at:
        columns.append(sa.Column("deleted_at", DATETIME_TYPE, nullable=True))
    return columns


def upgrade() -> None:
    op.create_table(
        "app_users",
        sa.Column("id", ID_TYPE, primary_key=True, autoincrement=True),
        sa.Column("nickname", sa.String(length=64), nullable=True),
        sa.Column("avatar_url", sa.String(length=512), nullable=True),
        sa.Column("phone_masked", sa.String(length=32), nullable=True),
        sa.Column("phone_cipher", sa.String(length=512), nullable=True),
        sa.Column("phone_hash", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("last_login_at", DATETIME_TYPE, nullable=True),
        *_timestamp_columns(),
    )
    op.create_index("idx_app_users_phone_hash", "app_users", ["phone_hash"])
    op.create_index("idx_app_users_status", "app_users", ["status"])

    op.create_table(
        "wechat_identities",
        sa.Column("id", ID_TYPE, primary_key=True, autoincrement=True),
        sa.Column("user_id", ID_TYPE, sa.ForeignKey("app_users.id"), nullable=False),
        sa.Column("openid", sa.String(length=128), nullable=False),
        sa.Column("unionid", sa.String(length=128), nullable=True),
        sa.Column("session_key_cipher", sa.String(length=512), nullable=True),
        sa.Column("appid", sa.String(length=64), nullable=False),
        *_timestamp_columns(include_deleted_at=False),
    )
    op.create_index("uk_wechat_openid_appid", "wechat_identities", ["openid", "appid"], unique=True)
    op.create_index("idx_wechat_user_id", "wechat_identities", ["user_id"])

    op.create_table(
        "user_consents",
        sa.Column("id", ID_TYPE, primary_key=True, autoincrement=True),
        sa.Column("user_id", ID_TYPE, sa.ForeignKey("app_users.id"), nullable=False),
        sa.Column("consent_type", sa.String(length=32), nullable=False),
        sa.Column("version", sa.String(length=32), nullable=False),
        sa.Column("granted", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        sa.Column("created_at", DATETIME_TYPE, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP(3)")),
    )
    op.create_index("idx_user_consents_user_type", "user_consents", ["user_id", "consent_type"])

    op.create_table(
        "admin_users",
        sa.Column("id", ID_TYPE, primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("display_name", sa.String(length=64), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("phone_masked", sa.String(length=32), nullable=True),
        sa.Column("phone_cipher", sa.String(length=512), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("last_login_at", DATETIME_TYPE, nullable=True),
        *_timestamp_columns(),
    )
    op.create_index("uk_admin_users_username", "admin_users", ["username"], unique=True)
    op.create_index("idx_admin_users_status", "admin_users", ["status"])

    op.create_table(
        "questionnaire_sets",
        sa.Column("id", ID_TYPE, primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("version", sa.String(length=32), nullable=False, server_default="v1"),
        sa.Column("description", sa.String(length=512), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("published_at", DATETIME_TYPE, nullable=True),
        *_timestamp_columns(),
    )
    op.create_index("uk_questionnaire_code_version", "questionnaire_sets", ["code", "version"], unique=True)

    op.create_table(
        "questionnaire_questions",
        sa.Column("id", ID_TYPE, primary_key=True, autoincrement=True),
        sa.Column("questionnaire_id", ID_TYPE, sa.ForeignKey("questionnaire_sets.id"), nullable=False),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("subtitle", sa.String(length=256), nullable=True),
        sa.Column("dimension_code", sa.String(length=64), nullable=True),
        sa.Column("question_type", sa.String(length=32), nullable=False, server_default="single_choice"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_required", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        *_timestamp_columns(include_deleted_at=False),
    )
    op.create_index("idx_questions_questionnaire_sort", "questionnaire_questions", ["questionnaire_id", "sort_order"])

    op.create_table(
        "questionnaire_options",
        sa.Column("id", ID_TYPE, primary_key=True, autoincrement=True),
        sa.Column("question_id", ID_TYPE, sa.ForeignKey("questionnaire_questions.id"), nullable=False),
        sa.Column("option_label", sa.String(length=8), nullable=True),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("subtitle", sa.String(length=256), nullable=True),
        sa.Column("score_json", mysql.JSON(), nullable=True),
        sa.Column("profile_bias", sa.String(length=64), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        *_timestamp_columns(include_deleted_at=False),
    )
    op.create_index("idx_options_question_sort", "questionnaire_options", ["question_id", "sort_order"])

    op.create_table(
        "questionnaire_result_profiles",
        sa.Column("id", ID_TYPE, primary_key=True, autoincrement=True),
        sa.Column("questionnaire_id", ID_TYPE, sa.ForeignKey("questionnaire_sets.id"), nullable=False),
        sa.Column("profile_code", sa.String(length=64), nullable=False),
        sa.Column("profile_name", sa.String(length=64), nullable=False),
        sa.Column("lead_grade_suggestion", sa.String(length=16), nullable=True),
        sa.Column("theme_color", sa.String(length=32), nullable=True),
        sa.Column("tags_json", mysql.JSON(), nullable=True),
        sa.Column("summary", sa.String(length=512), nullable=True),
        sa.Column("recommendations_json", mysql.JSON(), nullable=True),
        sa.Column("rule_json", mysql.JSON(), nullable=True),
        *_timestamp_columns(include_deleted_at=False),
    )
    op.create_index(
        "uk_profile_questionnaire_code",
        "questionnaire_result_profiles",
        ["questionnaire_id", "profile_code"],
        unique=True,
    )

    op.create_table(
        "questionnaire_submissions",
        sa.Column("id", ID_TYPE, primary_key=True, autoincrement=True),
        sa.Column("user_id", ID_TYPE, sa.ForeignKey("app_users.id"), nullable=False),
        sa.Column("enterprise_id", ID_TYPE, nullable=True),
        sa.Column("lead_id", ID_TYPE, nullable=True),
        sa.Column("questionnaire_id", ID_TYPE, sa.ForeignKey("questionnaire_sets.id"), nullable=False),
        sa.Column("result_profile_id", ID_TYPE, sa.ForeignKey("questionnaire_result_profiles.id"), nullable=True),
        sa.Column("profile_code", sa.String(length=64), nullable=True),
        sa.Column("total_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("dimension_scores_json", mysql.JSON(), nullable=True),
        sa.Column("answers_snapshot_json", mysql.JSON(), nullable=True),
        sa.Column("result_snapshot_json", mysql.JSON(), nullable=True),
        sa.Column("created_at", DATETIME_TYPE, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP(3)")),
    )
    op.create_index("idx_submissions_user", "questionnaire_submissions", ["user_id", "created_at"])
    op.create_index("idx_submissions_lead", "questionnaire_submissions", ["lead_id"])
    op.create_index("idx_submissions_profile", "questionnaire_submissions", ["profile_code"])

    op.create_table(
        "questionnaire_answers",
        sa.Column("id", ID_TYPE, primary_key=True, autoincrement=True),
        sa.Column("submission_id", ID_TYPE, sa.ForeignKey("questionnaire_submissions.id"), nullable=False),
        sa.Column("question_id", ID_TYPE, sa.ForeignKey("questionnaire_questions.id"), nullable=False),
        sa.Column("option_id", ID_TYPE, sa.ForeignKey("questionnaire_options.id"), nullable=False),
        sa.Column("score_json", mysql.JSON(), nullable=True),
        sa.Column("created_at", DATETIME_TYPE, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP(3)")),
    )
    op.create_index("idx_answers_submission", "questionnaire_answers", ["submission_id"])


def downgrade() -> None:
    op.drop_index("idx_answers_submission", table_name="questionnaire_answers")
    op.drop_table("questionnaire_answers")
    op.drop_index("idx_submissions_profile", table_name="questionnaire_submissions")
    op.drop_index("idx_submissions_lead", table_name="questionnaire_submissions")
    op.drop_index("idx_submissions_user", table_name="questionnaire_submissions")
    op.drop_table("questionnaire_submissions")
    op.drop_index("uk_profile_questionnaire_code", table_name="questionnaire_result_profiles")
    op.drop_table("questionnaire_result_profiles")
    op.drop_index("idx_options_question_sort", table_name="questionnaire_options")
    op.drop_table("questionnaire_options")
    op.drop_index("idx_questions_questionnaire_sort", table_name="questionnaire_questions")
    op.drop_table("questionnaire_questions")
    op.drop_index("uk_questionnaire_code_version", table_name="questionnaire_sets")
    op.drop_table("questionnaire_sets")
    op.drop_index("idx_admin_users_status", table_name="admin_users")
    op.drop_index("uk_admin_users_username", table_name="admin_users")
    op.drop_table("admin_users")
    op.drop_index("idx_user_consents_user_type", table_name="user_consents")
    op.drop_table("user_consents")
    op.drop_index("idx_wechat_user_id", table_name="wechat_identities")
    op.drop_index("uk_wechat_openid_appid", table_name="wechat_identities")
    op.drop_table("wechat_identities")
    op.drop_index("idx_app_users_status", table_name="app_users")
    op.drop_index("idx_app_users_phone_hash", table_name="app_users")
    op.drop_table("app_users")
