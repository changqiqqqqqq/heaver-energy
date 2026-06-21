"""补齐经营体质测试线索运营闭环

Revision ID: 20260621_0002
Revises: 20260614_0001
Create Date: 2026-06-21
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

revision: str = "20260621_0002"
down_revision: str | None = "20260614_0001"
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
    # 1. 企业与线索底座
    op.create_table(
        "enterprises",
        sa.Column("id", ID_TYPE, primary_key=True, autoincrement=True),
        sa.Column("owner_user_id", ID_TYPE, nullable=True),
        sa.Column("name", sa.String(length=128), nullable=True),
        sa.Column("region_province", sa.String(length=32), nullable=True),
        sa.Column("region_city", sa.String(length=32), nullable=True),
        sa.Column("region_district", sa.String(length=32), nullable=True),
        sa.Column("region_tag", sa.String(length=32), nullable=True),
        sa.Column("industry_type", sa.String(length=64), nullable=True),
        sa.Column("monthly_kwh_range", sa.String(length=32), nullable=True),
        sa.Column("monthly_cost_range", sa.String(length=32), nullable=True),
        sa.Column("scale_remark", sa.String(length=128), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        *_timestamp_columns(),
    )
    op.create_index("idx_enterprises_owner_user", "enterprises", ["owner_user_id"])
    op.create_index("idx_enterprises_region", "enterprises", ["region_province", "region_city"])
    op.create_index("idx_enterprises_region_tag", "enterprises", ["region_tag"])
    op.create_index("idx_enterprises_industry", "enterprises", ["industry_type"])

    op.create_table(
        "enterprise_contacts",
        sa.Column("id", ID_TYPE, primary_key=True, autoincrement=True),
        sa.Column("enterprise_id", ID_TYPE, sa.ForeignKey("enterprises.id"), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=True),
        sa.Column("role_title", sa.String(length=64), nullable=True),
        sa.Column("phone_masked", sa.String(length=32), nullable=True),
        sa.Column("phone_cipher", sa.String(length=512), nullable=True),
        sa.Column("phone_hash", sa.String(length=64), nullable=True),
        sa.Column("wechat_no", sa.String(length=128), nullable=True),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        *_timestamp_columns(),
    )
    op.create_index("idx_contacts_enterprise", "enterprise_contacts", ["enterprise_id"])
    op.create_index("idx_contacts_phone_hash", "enterprise_contacts", ["phone_hash"])

    op.create_table(
        "leads",
        sa.Column("id", ID_TYPE, primary_key=True, autoincrement=True),
        sa.Column("lead_no", sa.String(length=32), nullable=False),
        sa.Column("enterprise_id", ID_TYPE, sa.ForeignKey("enterprises.id"), nullable=True),
        sa.Column("user_id", ID_TYPE, nullable=True),
        sa.Column("source_channel", sa.String(length=64), nullable=False, server_default="miniapp"),
        sa.Column("source_entry", sa.String(length=64), nullable=True),
        sa.Column("lead_grade", sa.String(length=16), nullable=True),
        sa.Column("lead_status", sa.String(length=32), nullable=False, server_default="pending_followup"),
        sa.Column("primary_need_type", sa.String(length=32), nullable=True),
        sa.Column("profile_code", sa.String(length=64), nullable=True),
        sa.Column("score_snapshot_json", mysql.JSON(), nullable=True),
        sa.Column("need_tags_json", mysql.JSON(), nullable=True),
        sa.Column("result_summary", sa.String(length=512), nullable=True),
        sa.Column("has_bill_uploaded", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("has_phone_authorized", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("assigned_admin_id", ID_TYPE, nullable=True),
        sa.Column("first_submitted_at", DATETIME_TYPE, nullable=True),
        sa.Column("last_activity_at", DATETIME_TYPE, nullable=True),
        *_timestamp_columns(),
    )
    op.create_index("uk_leads_lead_no", "leads", ["lead_no"], unique=True)
    op.create_index("idx_leads_user", "leads", ["user_id", "created_at"])
    op.create_index("idx_leads_enterprise", "leads", ["enterprise_id"])
    op.create_index("idx_leads_grade_status", "leads", ["lead_grade", "lead_status"])
    op.create_index("idx_leads_profile_grade", "leads", ["profile_code", "lead_grade"])
    op.create_index("idx_leads_need_type", "leads", ["primary_need_type"])
    op.create_index("idx_leads_last_activity", "leads", ["last_activity_at"])
    op.create_index("idx_leads_assigned_admin", "leads", ["assigned_admin_id"])

    op.create_table(
        "lead_status_logs",
        sa.Column("id", ID_TYPE, primary_key=True, autoincrement=True),
        sa.Column("lead_id", ID_TYPE, sa.ForeignKey("leads.id"), nullable=False),
        sa.Column("from_status", sa.String(length=32), nullable=True),
        sa.Column("to_status", sa.String(length=32), nullable=False),
        sa.Column("operator_admin_id", ID_TYPE, nullable=True),
        sa.Column("operator_type", sa.String(length=32), nullable=False, server_default="admin"),
        sa.Column("remark", sa.String(length=512), nullable=True),
        sa.Column("created_at", DATETIME_TYPE, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP(3)")),
    )
    op.create_index("idx_lead_status_logs_lead", "lead_status_logs", ["lead_id", "created_at"])

    # 2. 问卷增强
    op.add_column("questionnaire_sets", sa.Column("result_config_json", mysql.JSON(), nullable=True))
    op.add_column("questionnaire_questions", sa.Column("question_code", sa.String(length=32), nullable=True))
    op.add_column(
        "questionnaire_questions",
        sa.Column("score_mode", sa.String(length=32), nullable=False, server_default="score"),
    )
    op.create_index(
        "uk_questions_questionnaire_code",
        "questionnaire_questions",
        ["questionnaire_id", "question_code"],
        unique=True,
    )
    op.add_column("questionnaire_options", sa.Column("tags_json", mysql.JSON(), nullable=True))
    op.add_column(
        "questionnaire_result_profiles",
        sa.Column("priority", sa.Integer(), nullable=False, server_default="100"),
    )
    op.add_column("questionnaire_result_profiles", sa.Column("result_page_json", mysql.JSON(), nullable=True))
    op.create_index(
        "idx_profile_questionnaire_priority",
        "questionnaire_result_profiles",
        ["questionnaire_id", "priority"],
    )
    op.add_column("questionnaire_submissions", sa.Column("lead_grade", sa.String(length=16), nullable=True))
    op.add_column("questionnaire_submissions", sa.Column("dimension_stars_json", mysql.JSON(), nullable=True))
    op.add_column("questionnaire_submissions", sa.Column("answer_tags_json", mysql.JSON(), nullable=True))
    op.create_index("idx_submissions_grade", "questionnaire_submissions", ["lead_grade", "created_at"])
    op.add_column("questionnaire_answers", sa.Column("question_snapshot_json", mysql.JSON(), nullable=True))
    op.add_column("questionnaire_answers", sa.Column("option_snapshot_json", mysql.JSON(), nullable=True))
    op.add_column("questionnaire_answers", sa.Column("tags_json", mysql.JSON(), nullable=True))

    # 3. 结果页承接能力
    op.create_table(
        "screening_requests",
        sa.Column("id", ID_TYPE, primary_key=True, autoincrement=True),
        sa.Column("user_id", ID_TYPE, nullable=False),
        sa.Column("enterprise_id", ID_TYPE, sa.ForeignKey("enterprises.id"), nullable=True),
        sa.Column("lead_id", ID_TYPE, sa.ForeignKey("leads.id"), nullable=True),
        sa.Column("submission_id", ID_TYPE, sa.ForeignKey("questionnaire_submissions.id"), nullable=True),
        sa.Column("region_text", sa.String(length=128), nullable=True),
        sa.Column("enterprise_name", sa.String(length=128), nullable=True),
        sa.Column("enterprise_type", sa.String(length=64), nullable=True),
        sa.Column("monthly_kwh_range", sa.String(length=32), nullable=True),
        sa.Column("contact_name", sa.String(length=64), nullable=True),
        sa.Column("contact_phone_masked", sa.String(length=32), nullable=True),
        sa.Column("contact_phone_cipher", sa.String(length=512), nullable=True),
        sa.Column("contact_phone_hash", sa.String(length=64), nullable=True),
        sa.Column("bill_upload_status", sa.String(length=32), nullable=False, server_default="not_uploaded"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="submitted"),
        sa.Column("extra_json", mysql.JSON(), nullable=True),
        sa.Column("submitted_at", DATETIME_TYPE, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP(3)")),
        sa.Column("created_at", DATETIME_TYPE, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP(3)")),
        sa.Column("updated_at", DATETIME_TYPE, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP(3)")),
    )
    op.create_index("idx_screening_lead", "screening_requests", ["lead_id"])
    op.create_index("idx_screening_enterprise", "screening_requests", ["enterprise_id"])
    op.create_index("idx_screening_status", "screening_requests", ["status"])
    op.create_index("idx_screening_phone_hash", "screening_requests", ["contact_phone_hash"])

    op.create_table(
        "service_requests",
        sa.Column("id", ID_TYPE, primary_key=True, autoincrement=True),
        sa.Column("request_no", sa.String(length=32), nullable=False),
        sa.Column("user_id", ID_TYPE, nullable=False),
        sa.Column("enterprise_id", ID_TYPE, sa.ForeignKey("enterprises.id"), nullable=True),
        sa.Column("lead_id", ID_TYPE, sa.ForeignKey("leads.id"), nullable=True),
        sa.Column("submission_id", ID_TYPE, sa.ForeignKey("questionnaire_submissions.id"), nullable=True),
        sa.Column("primary_need_type", sa.String(length=32), nullable=True),
        sa.Column("description", sa.String(length=512), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="submitted"),
        sa.Column("submitted_at", DATETIME_TYPE, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP(3)")),
        *_timestamp_columns(),
    )
    op.create_index("uk_service_requests_no", "service_requests", ["request_no"], unique=True)
    op.create_index("idx_service_requests_lead", "service_requests", ["lead_id"])
    op.create_index("idx_service_requests_need_status", "service_requests", ["primary_need_type", "status"])

    op.create_table(
        "service_request_items",
        sa.Column("id", ID_TYPE, primary_key=True, autoincrement=True),
        sa.Column("service_request_id", ID_TYPE, sa.ForeignKey("service_requests.id"), nullable=False),
        sa.Column("need_type", sa.String(length=32), nullable=False),
        sa.Column("need_name", sa.String(length=64), nullable=False),
        sa.Column("extra_json", mysql.JSON(), nullable=True),
        sa.Column("created_at", DATETIME_TYPE, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP(3)")),
    )
    op.create_index("idx_service_items_request", "service_request_items", ["service_request_id"])
    op.create_index("idx_service_items_need_type", "service_request_items", ["need_type"])

    op.create_table(
        "files",
        sa.Column("id", ID_TYPE, primary_key=True, autoincrement=True),
        sa.Column("uploader_user_id", ID_TYPE, nullable=True),
        sa.Column("uploader_admin_id", ID_TYPE, nullable=True),
        sa.Column("biz_type", sa.String(length=32), nullable=False),
        sa.Column("biz_id", ID_TYPE, nullable=True),
        sa.Column("storage_provider", sa.String(length=32), nullable=False, server_default="local"),
        sa.Column("bucket", sa.String(length=128), nullable=True),
        sa.Column("object_key", sa.String(length=512), nullable=False),
        sa.Column("original_filename", sa.String(length=256), nullable=True),
        sa.Column("mime_type", sa.String(length=128), nullable=True),
        sa.Column("file_size", mysql.BIGINT(unsigned=True), nullable=True),
        sa.Column("sha256", sa.String(length=64), nullable=True),
        sa.Column("sensitivity_level", sa.String(length=32), nullable=False, server_default="normal"),
        sa.Column("access_policy", sa.String(length=32), nullable=False, server_default="private"),
        sa.Column("created_at", DATETIME_TYPE, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP(3)")),
        sa.Column("deleted_at", DATETIME_TYPE, nullable=True),
    )
    op.create_index("idx_files_biz_type", "files", ["biz_type", "biz_id"])
    op.create_index("idx_files_sha256", "files", ["sha256"])

    op.create_table(
        "bill_uploads",
        sa.Column("id", ID_TYPE, primary_key=True, autoincrement=True),
        sa.Column("enterprise_id", ID_TYPE, sa.ForeignKey("enterprises.id"), nullable=True),
        sa.Column("lead_id", ID_TYPE, sa.ForeignKey("leads.id"), nullable=True),
        sa.Column("file_id", ID_TYPE, sa.ForeignKey("files.id"), nullable=False),
        sa.Column("bill_month", sa.String(length=16), nullable=True),
        sa.Column("upload_source", sa.String(length=32), nullable=False, server_default="miniapp"),
        sa.Column("parse_status", sa.String(length=32), nullable=False, server_default="not_parsed"),
        sa.Column("parsed_result_json", mysql.JSON(), nullable=True),
        sa.Column("manual_remark", sa.String(length=512), nullable=True),
        *_timestamp_columns(),
    )
    op.create_index("idx_bill_uploads_enterprise", "bill_uploads", ["enterprise_id", "created_at"])
    op.create_index("idx_bill_uploads_lead", "bill_uploads", ["lead_id"])
    op.create_index("idx_bill_uploads_parse_status", "bill_uploads", ["parse_status"])

    op.create_table(
        "electricity_bills",
        sa.Column("id", ID_TYPE, primary_key=True, autoincrement=True),
        sa.Column("enterprise_id", ID_TYPE, sa.ForeignKey("enterprises.id"), nullable=False),
        sa.Column("bill_upload_id", ID_TYPE, sa.ForeignKey("bill_uploads.id"), nullable=True),
        sa.Column("bill_month", sa.String(length=16), nullable=False),
        sa.Column("total_kwh", sa.Numeric(14, 2), nullable=True),
        sa.Column("total_amount", sa.Numeric(14, 2), nullable=True),
        sa.Column("peak_kwh", sa.Numeric(14, 2), nullable=True),
        sa.Column("flat_kwh", sa.Numeric(14, 2), nullable=True),
        sa.Column("valley_kwh", sa.Numeric(14, 2), nullable=True),
        sa.Column("capacity_fee", sa.Numeric(14, 2), nullable=True),
        sa.Column("demand_fee", sa.Numeric(14, 2), nullable=True),
        sa.Column("raw_data_json", mysql.JSON(), nullable=True),
        *_timestamp_columns(),
    )
    op.create_index("uk_electricity_bill_month", "electricity_bills", ["enterprise_id", "bill_month"], unique=True)
    op.create_index("idx_electricity_bills_month", "electricity_bills", ["bill_month"])

    # 4. 运营、供应商和审计权限
    op.create_table(
        "lead_followups",
        sa.Column("id", ID_TYPE, primary_key=True, autoincrement=True),
        sa.Column("lead_id", ID_TYPE, sa.ForeignKey("leads.id"), nullable=False),
        sa.Column("admin_id", ID_TYPE, nullable=False),
        sa.Column("followup_type", sa.String(length=32), nullable=False, server_default="phone"),
        sa.Column("followup_result", sa.String(length=32), nullable=False, server_default="contacted"),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("next_followup_at", DATETIME_TYPE, nullable=True),
        *_timestamp_columns(include_deleted_at=False),
    )
    op.create_index("idx_followups_lead", "lead_followups", ["lead_id", "created_at"])
    op.create_index("idx_followups_admin_next", "lead_followups", ["admin_id", "next_followup_at"])

    op.create_table(
        "lead_notes",
        sa.Column("id", ID_TYPE, primary_key=True, autoincrement=True),
        sa.Column("lead_id", ID_TYPE, sa.ForeignKey("leads.id"), nullable=False),
        sa.Column("admin_id", ID_TYPE, nullable=False),
        sa.Column("note_type", sa.String(length=32), nullable=False, server_default="general"),
        sa.Column("content", sa.Text(), nullable=False),
        *_timestamp_columns(),
    )
    op.create_index("idx_lead_notes_lead", "lead_notes", ["lead_id", "created_at"])

    op.create_table(
        "suppliers",
        sa.Column("id", ID_TYPE, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("supplier_type", sa.String(length=32), nullable=False),
        sa.Column("region_scope_json", mysql.JSON(), nullable=True),
        sa.Column("service_tags_json", mysql.JSON(), nullable=True),
        sa.Column("contact_name", sa.String(length=64), nullable=True),
        sa.Column("contact_phone_masked", sa.String(length=32), nullable=True),
        sa.Column("contact_phone_cipher", sa.String(length=512), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("remark", sa.String(length=512), nullable=True),
        *_timestamp_columns(),
    )
    op.create_index("idx_suppliers_type_status", "suppliers", ["supplier_type", "status"])

    op.create_table(
        "supplier_transfers",
        sa.Column("id", ID_TYPE, primary_key=True, autoincrement=True),
        sa.Column("lead_id", ID_TYPE, sa.ForeignKey("leads.id"), nullable=False),
        sa.Column("supplier_id", ID_TYPE, sa.ForeignKey("suppliers.id"), nullable=False),
        sa.Column("service_request_id", ID_TYPE, sa.ForeignKey("service_requests.id"), nullable=True),
        sa.Column("transfer_status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("transfer_reason", sa.String(length=512), nullable=True),
        sa.Column("operator_admin_id", ID_TYPE, nullable=False),
        *_timestamp_columns(include_deleted_at=False),
    )
    op.create_index("idx_supplier_transfers_lead", "supplier_transfers", ["lead_id", "created_at"])
    op.create_index("idx_supplier_transfers_supplier", "supplier_transfers", ["supplier_id", "transfer_status"])

    op.create_table(
        "admin_roles",
        sa.Column("id", ID_TYPE, primary_key=True, autoincrement=True),
        sa.Column("role_code", sa.String(length=64), nullable=False),
        sa.Column("role_name", sa.String(length=64), nullable=False),
        sa.Column("description", sa.String(length=256), nullable=True),
        *_timestamp_columns(include_deleted_at=False),
    )
    op.create_index("uk_admin_roles_code", "admin_roles", ["role_code"], unique=True)

    op.create_table(
        "admin_permissions",
        sa.Column("id", ID_TYPE, primary_key=True, autoincrement=True),
        sa.Column("permission_code", sa.String(length=128), nullable=False),
        sa.Column("permission_name", sa.String(length=128), nullable=False),
        sa.Column("module_code", sa.String(length=64), nullable=False),
        *_timestamp_columns(include_deleted_at=False),
    )
    op.create_index("uk_permissions_code", "admin_permissions", ["permission_code"], unique=True)

    op.create_table(
        "admin_user_roles",
        sa.Column("id", ID_TYPE, primary_key=True, autoincrement=True),
        sa.Column("admin_user_id", ID_TYPE, sa.ForeignKey("admin_users.id"), nullable=False),
        sa.Column("role_id", ID_TYPE, sa.ForeignKey("admin_roles.id"), nullable=False),
        sa.Column("created_at", DATETIME_TYPE, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP(3)")),
    )
    op.create_index("uk_admin_user_role", "admin_user_roles", ["admin_user_id", "role_id"], unique=True)

    op.create_table(
        "admin_role_permissions",
        sa.Column("id", ID_TYPE, primary_key=True, autoincrement=True),
        sa.Column("role_id", ID_TYPE, sa.ForeignKey("admin_roles.id"), nullable=False),
        sa.Column("permission_id", ID_TYPE, sa.ForeignKey("admin_permissions.id"), nullable=False),
        sa.Column("created_at", DATETIME_TYPE, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP(3)")),
    )
    op.create_index("uk_role_permission", "admin_role_permissions", ["role_id", "permission_id"], unique=True)

    op.create_table(
        "audit_logs",
        sa.Column("id", ID_TYPE, primary_key=True, autoincrement=True),
        sa.Column("actor_type", sa.String(length=32), nullable=False, server_default="admin"),
        sa.Column("actor_id", ID_TYPE, nullable=True),
        sa.Column("action", sa.String(length=128), nullable=False),
        sa.Column("target_type", sa.String(length=64), nullable=True),
        sa.Column("target_id", ID_TYPE, nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        sa.Column("request_id", sa.String(length=64), nullable=True),
        sa.Column("detail_json", mysql.JSON(), nullable=True),
        sa.Column("created_at", DATETIME_TYPE, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP(3)")),
    )
    op.create_index("idx_audit_actor", "audit_logs", ["actor_type", "actor_id", "created_at"])
    op.create_index("idx_audit_target", "audit_logs", ["target_type", "target_id", "created_at"])
    op.create_index("idx_audit_action", "audit_logs", ["action", "created_at"])


def downgrade() -> None:
    op.drop_index("idx_audit_action", table_name="audit_logs")
    op.drop_index("idx_audit_target", table_name="audit_logs")
    op.drop_index("idx_audit_actor", table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_index("uk_role_permission", table_name="admin_role_permissions")
    op.drop_table("admin_role_permissions")
    op.drop_index("uk_admin_user_role", table_name="admin_user_roles")
    op.drop_table("admin_user_roles")
    op.drop_index("uk_permissions_code", table_name="admin_permissions")
    op.drop_table("admin_permissions")
    op.drop_index("uk_admin_roles_code", table_name="admin_roles")
    op.drop_table("admin_roles")
    op.drop_index("idx_supplier_transfers_supplier", table_name="supplier_transfers")
    op.drop_index("idx_supplier_transfers_lead", table_name="supplier_transfers")
    op.drop_table("supplier_transfers")
    op.drop_index("idx_suppliers_type_status", table_name="suppliers")
    op.drop_table("suppliers")
    op.drop_index("idx_lead_notes_lead", table_name="lead_notes")
    op.drop_table("lead_notes")
    op.drop_index("idx_followups_admin_next", table_name="lead_followups")
    op.drop_index("idx_followups_lead", table_name="lead_followups")
    op.drop_table("lead_followups")
    op.drop_index("idx_electricity_bills_month", table_name="electricity_bills")
    op.drop_index("uk_electricity_bill_month", table_name="electricity_bills")
    op.drop_table("electricity_bills")
    op.drop_index("idx_bill_uploads_parse_status", table_name="bill_uploads")
    op.drop_index("idx_bill_uploads_lead", table_name="bill_uploads")
    op.drop_index("idx_bill_uploads_enterprise", table_name="bill_uploads")
    op.drop_table("bill_uploads")
    op.drop_index("idx_files_sha256", table_name="files")
    op.drop_index("idx_files_biz_type", table_name="files")
    op.drop_table("files")
    op.drop_index("idx_service_items_need_type", table_name="service_request_items")
    op.drop_index("idx_service_items_request", table_name="service_request_items")
    op.drop_table("service_request_items")
    op.drop_index("idx_service_requests_need_status", table_name="service_requests")
    op.drop_index("idx_service_requests_lead", table_name="service_requests")
    op.drop_index("uk_service_requests_no", table_name="service_requests")
    op.drop_table("service_requests")
    op.drop_index("idx_screening_phone_hash", table_name="screening_requests")
    op.drop_index("idx_screening_status", table_name="screening_requests")
    op.drop_index("idx_screening_enterprise", table_name="screening_requests")
    op.drop_index("idx_screening_lead", table_name="screening_requests")
    op.drop_table("screening_requests")
    op.drop_column("questionnaire_answers", "tags_json")
    op.drop_column("questionnaire_answers", "option_snapshot_json")
    op.drop_column("questionnaire_answers", "question_snapshot_json")
    op.drop_index("idx_submissions_grade", table_name="questionnaire_submissions")
    op.drop_column("questionnaire_submissions", "answer_tags_json")
    op.drop_column("questionnaire_submissions", "dimension_stars_json")
    op.drop_column("questionnaire_submissions", "lead_grade")
    op.drop_index("idx_profile_questionnaire_priority", table_name="questionnaire_result_profiles")
    op.drop_column("questionnaire_result_profiles", "result_page_json")
    op.drop_column("questionnaire_result_profiles", "priority")
    op.drop_column("questionnaire_options", "tags_json")
    op.drop_index("uk_questions_questionnaire_code", table_name="questionnaire_questions")
    op.drop_column("questionnaire_questions", "score_mode")
    op.drop_column("questionnaire_questions", "question_code")
    op.drop_column("questionnaire_sets", "result_config_json")
    op.drop_index("idx_lead_status_logs_lead", table_name="lead_status_logs")
    op.drop_table("lead_status_logs")
    op.drop_index("idx_leads_assigned_admin", table_name="leads")
    op.drop_index("idx_leads_last_activity", table_name="leads")
    op.drop_index("idx_leads_need_type", table_name="leads")
    op.drop_index("idx_leads_profile_grade", table_name="leads")
    op.drop_index("idx_leads_grade_status", table_name="leads")
    op.drop_index("idx_leads_enterprise", table_name="leads")
    op.drop_index("idx_leads_user", table_name="leads")
    op.drop_index("uk_leads_lead_no", table_name="leads")
    op.drop_table("leads")
    op.drop_index("idx_contacts_phone_hash", table_name="enterprise_contacts")
    op.drop_index("idx_contacts_enterprise", table_name="enterprise_contacts")
    op.drop_table("enterprise_contacts")
    op.drop_index("idx_enterprises_industry", table_name="enterprises")
    op.drop_index("idx_enterprises_region_tag", table_name="enterprises")
    op.drop_index("idx_enterprises_region", table_name="enterprises")
    op.drop_index("idx_enterprises_owner_user", table_name="enterprises")
    op.drop_table("enterprises")
