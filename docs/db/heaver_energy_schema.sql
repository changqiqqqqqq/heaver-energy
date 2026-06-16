-- Heaver Energy MVP database schema
-- Generated from: docs/db/河狸数字能源MVP数据库设计与字典.md
-- Generated on: 2026-06-12
-- Target: MySQL 8.x
-- Notes: Foreign keys are intentionally omitted for MVP soft-delete flexibility.

SET NAMES utf8mb4;
SET time_zone = '+08:00';

CREATE DATABASE IF NOT EXISTS `heaver_energy`
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;

USE `heaver_energy`;

-- ------------------------------------------------------------
-- Table structure for app_users
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `app_users` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户 ID',
  `nickname` VARCHAR(64) NULL DEFAULT NULL COMMENT '微信昵称或系统昵称',
  `avatar_url` VARCHAR(512) NULL DEFAULT NULL COMMENT '头像 URL',
  `phone_masked` VARCHAR(32) NULL DEFAULT NULL COMMENT '脱敏手机号，如 138****8888',
  `phone_cipher` VARCHAR(512) NULL DEFAULT NULL COMMENT '加密手机号',
  `phone_hash` CHAR(64) NULL DEFAULT NULL COMMENT '手机号哈希，用于去重',
  `status` VARCHAR(32) NOT NULL DEFAULT 'active' COMMENT 'active、disabled',
  `last_login_at` DATETIME(3) NULL DEFAULT NULL COMMENT '最近登录时间',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间',
  `deleted_at` DATETIME(3) NULL DEFAULT NULL COMMENT '软删除时间',
  PRIMARY KEY (`id`),
  KEY `idx_app_users_phone_hash` (`phone_hash`),
  KEY `idx_app_users_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='小程序端用户主体';

-- ------------------------------------------------------------
-- Table structure for wechat_identities
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `wechat_identities` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `user_id` BIGINT UNSIGNED NOT NULL COMMENT '关联 app_users.id',
  `openid` VARCHAR(128) NOT NULL COMMENT '小程序 OpenID',
  `unionid` VARCHAR(128) NULL DEFAULT NULL COMMENT '微信 UnionID',
  `session_key_cipher` VARCHAR(512) NULL DEFAULT NULL COMMENT '加密后的 session_key，谨慎保存',
  `appid` VARCHAR(64) NOT NULL COMMENT '小程序 AppID',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_wechat_openid_appid` (`openid`, `appid`),
  KEY `idx_wechat_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='微信身份绑定信息';

-- ------------------------------------------------------------
-- Table structure for user_consents
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `user_consents` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `user_id` BIGINT UNSIGNED NOT NULL COMMENT '关联用户',
  `consent_type` VARCHAR(32) NOT NULL COMMENT 'privacy、bill_sensitive、phone_auth',
  `version` VARCHAR(32) NOT NULL COMMENT '协议版本',
  `granted` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否同意',
  `ip_address` VARCHAR(64) NULL DEFAULT NULL COMMENT 'IP',
  `user_agent` VARCHAR(512) NULL DEFAULT NULL COMMENT '客户端信息',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '授权时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_consents_user_type` (`user_id`, `consent_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户协议、隐私政策、账单敏感信息授权记录';

-- ------------------------------------------------------------
-- Table structure for enterprises
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `enterprises` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '企业 ID',
  `owner_user_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT '来源小程序用户',
  `name` VARCHAR(128) NOT NULL COMMENT '企业简称或名称',
  `region_province` VARCHAR(32) NULL DEFAULT NULL COMMENT '省份',
  `region_city` VARCHAR(32) NULL DEFAULT NULL COMMENT '城市',
  `region_district` VARCHAR(32) NULL DEFAULT NULL COMMENT '区县',
  `industry_type` VARCHAR(64) NULL DEFAULT NULL COMMENT '企业类型，如制造业 / 工厂',
  `monthly_cost_range` VARCHAR(32) NULL DEFAULT NULL COMMENT '月电费规模，如 10-20 万/月',
  `scale_remark` VARCHAR(128) NULL DEFAULT NULL COMMENT '规模补充',
  `status` VARCHAR(32) NOT NULL DEFAULT 'active' COMMENT 'active、merged、disabled',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间',
  `deleted_at` DATETIME(3) NULL DEFAULT NULL COMMENT '软删除时间',
  PRIMARY KEY (`id`),
  KEY `idx_enterprises_owner_user` (`owner_user_id`),
  KEY `idx_enterprises_region` (`region_province`, `region_city`),
  KEY `idx_enterprises_industry` (`industry_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='企业客户主体';

-- ------------------------------------------------------------
-- Table structure for enterprise_contacts
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `enterprise_contacts` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '联系人 ID',
  `enterprise_id` BIGINT UNSIGNED NOT NULL COMMENT '企业 ID',
  `name` VARCHAR(64) NULL DEFAULT NULL COMMENT '联系人姓名',
  `role_title` VARCHAR(64) NULL DEFAULT NULL COMMENT '职务，如老板、负责人',
  `phone_masked` VARCHAR(32) NULL DEFAULT NULL COMMENT '脱敏手机号',
  `phone_cipher` VARCHAR(512) NULL DEFAULT NULL COMMENT '加密手机号',
  `phone_hash` CHAR(64) NULL DEFAULT NULL COMMENT '手机号哈希',
  `wechat_no` VARCHAR(128) NULL DEFAULT NULL COMMENT '微信号，可选',
  `is_primary` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否主联系人',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间',
  `deleted_at` DATETIME(3) NULL DEFAULT NULL COMMENT '软删除时间',
  PRIMARY KEY (`id`),
  KEY `idx_contacts_enterprise` (`enterprise_id`),
  KEY `idx_contacts_phone_hash` (`phone_hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='企业联系人。手机号建议加密保存，列表页展示脱敏值';

-- ------------------------------------------------------------
-- Table structure for leads
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `leads` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '线索 ID',
  `lead_no` VARCHAR(32) NOT NULL COMMENT '线索编号',
  `enterprise_id` BIGINT UNSIGNED NOT NULL COMMENT '企业 ID',
  `user_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT '来源用户',
  `source_channel` VARCHAR(64) NOT NULL DEFAULT 'miniapp' COMMENT '来源渠道',
  `source_entry` VARCHAR(64) NULL DEFAULT NULL COMMENT '来源入口，如 体质测试、免费初筛',
  `lead_grade` VARCHAR(16) NULL DEFAULT NULL COMMENT 'A、B、C',
  `lead_status` VARCHAR(32) NOT NULL DEFAULT 'pending_followup' COMMENT 'pending_followup、following、transferred_supplier、content_saved、closed',
  `primary_need_type` VARCHAR(32) NULL DEFAULT NULL COMMENT 'use_energy、green_power、green_certificate、solar_storage',
  `profile_code` VARCHAR(64) NULL DEFAULT NULL COMMENT '测评画像，如 cost_sensitive',
  `has_bill_uploaded` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否上传账单',
  `has_phone_authorized` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否授权手机号',
  `assigned_admin_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT '当前负责人',
  `first_submitted_at` DATETIME(3) NULL DEFAULT NULL COMMENT '首次提交时间',
  `last_activity_at` DATETIME(3) NULL DEFAULT NULL COMMENT '最近动作时间',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间',
  `deleted_at` DATETIME(3) NULL DEFAULT NULL COMMENT '软删除时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_leads_lead_no` (`lead_no`),
  KEY `idx_leads_grade_status` (`lead_grade`, `lead_status`),
  KEY `idx_leads_need_type` (`primary_need_type`),
  KEY `idx_leads_created_at` (`created_at`),
  KEY `idx_leads_assigned_admin` (`assigned_admin_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='后台线索主表，承载列表、筛选、状态和等级';

-- ------------------------------------------------------------
-- Table structure for lead_status_logs
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `lead_status_logs` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `lead_id` BIGINT UNSIGNED NOT NULL COMMENT '线索 ID',
  `from_status` VARCHAR(32) NULL DEFAULT NULL COMMENT '原状态',
  `to_status` VARCHAR(32) NOT NULL COMMENT '新状态',
  `operator_admin_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT '操作人',
  `remark` VARCHAR(512) NULL DEFAULT NULL COMMENT '状态变化备注',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_lead_status_logs_lead` (`lead_id`, `created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='线索状态流转记录';

-- ------------------------------------------------------------
-- Table structure for questionnaire_sets
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `questionnaire_sets` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '问卷 ID',
  `code` VARCHAR(64) NOT NULL COMMENT '问卷编码',
  `name` VARCHAR(128) NOT NULL COMMENT '问卷名称，如经营体质测试',
  `version` VARCHAR(32) NOT NULL DEFAULT 'v1' COMMENT '版本',
  `description` VARCHAR(512) NULL DEFAULT NULL COMMENT '描述',
  `status` VARCHAR(32) NOT NULL DEFAULT 'draft' COMMENT 'draft、published、archived',
  `published_at` DATETIME(3) NULL DEFAULT NULL COMMENT '发布时间',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间',
  `deleted_at` DATETIME(3) NULL DEFAULT NULL COMMENT '软删除时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_questionnaire_code_version` (`code`, `version`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='测试问卷版本';

-- ------------------------------------------------------------
-- Table structure for questionnaire_questions
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `questionnaire_questions` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '题目 ID',
  `questionnaire_id` BIGINT UNSIGNED NOT NULL COMMENT '问卷 ID',
  `title` VARCHAR(256) NOT NULL COMMENT '题目标题',
  `subtitle` VARCHAR(256) NULL DEFAULT NULL COMMENT '题目副标题',
  `dimension_code` VARCHAR(64) NULL DEFAULT NULL COMMENT '评分维度，如 cost、growth、risk',
  `question_type` VARCHAR(32) NOT NULL DEFAULT 'single_choice' COMMENT 'single_choice、multiple_choice',
  `sort_order` INT NOT NULL DEFAULT 0 COMMENT '排序',
  `is_required` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否必答',
  `status` VARCHAR(32) NOT NULL DEFAULT 'active' COMMENT 'active、disabled',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_questions_questionnaire_sort` (`questionnaire_id`, `sort_order`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='问卷题目';

-- ------------------------------------------------------------
-- Table structure for questionnaire_options
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `questionnaire_options` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '选项 ID',
  `question_id` BIGINT UNSIGNED NOT NULL COMMENT '题目 ID',
  `option_label` VARCHAR(8) NULL DEFAULT NULL COMMENT 'A、B、C、D',
  `title` VARCHAR(256) NOT NULL COMMENT '选项文案',
  `subtitle` VARCHAR(256) NULL DEFAULT NULL COMMENT '选项副文案',
  `score_json` JSON NULL COMMENT '各维度加分，如 {"cost": 3}',
  `profile_bias` VARCHAR(64) NULL DEFAULT NULL COMMENT '倾向画像',
  `sort_order` INT NOT NULL DEFAULT 0 COMMENT '排序',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_options_question_sort` (`question_id`, `sort_order`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='题目选项和评分配置';

-- ------------------------------------------------------------
-- Table structure for questionnaire_result_profiles
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `questionnaire_result_profiles` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '画像 ID',
  `questionnaire_id` BIGINT UNSIGNED NOT NULL COMMENT '问卷 ID',
  `profile_code` VARCHAR(64) NOT NULL COMMENT '画像编码',
  `profile_name` VARCHAR(64) NOT NULL COMMENT '画像名称',
  `lead_grade_suggestion` VARCHAR(16) NULL DEFAULT NULL COMMENT '默认建议线索等级',
  `theme_color` VARCHAR(32) NULL DEFAULT NULL COMMENT '分享卡片颜色',
  `tags_json` JSON NULL COMMENT '标签列表',
  `summary` VARCHAR(512) NULL DEFAULT NULL COMMENT '结果说明',
  `recommendations_json` JSON NULL COMMENT '建议列表',
  `rule_json` JSON NULL COMMENT '命中规则',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_profile_questionnaire_code` (`questionnaire_id`, `profile_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='测试结果画像配置，如稳健经营型、成本敏感型、增长扩张型、隐性浪费型';

-- ------------------------------------------------------------
-- Table structure for questionnaire_submissions
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `questionnaire_submissions` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '提交 ID',
  `user_id` BIGINT UNSIGNED NOT NULL COMMENT '用户 ID',
  `enterprise_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT '企业 ID',
  `lead_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT '线索 ID',
  `questionnaire_id` BIGINT UNSIGNED NOT NULL COMMENT '问卷 ID',
  `result_profile_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT '命中的画像 ID',
  `profile_code` VARCHAR(64) NULL DEFAULT NULL COMMENT '画像编码快照',
  `total_score` INT NOT NULL DEFAULT 0 COMMENT '总分',
  `dimension_scores_json` JSON NULL COMMENT '维度得分快照',
  `answers_snapshot_json` JSON NULL COMMENT '答案快照',
  `result_snapshot_json` JSON NULL COMMENT '结果页快照',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '提交时间',
  PRIMARY KEY (`id`),
  KEY `idx_submissions_user` (`user_id`, `created_at`),
  KEY `idx_submissions_lead` (`lead_id`),
  KEY `idx_submissions_profile` (`profile_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='用户答题提交记录';

-- ------------------------------------------------------------
-- Table structure for questionnaire_answers
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `questionnaire_answers` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '明细 ID',
  `submission_id` BIGINT UNSIGNED NOT NULL COMMENT '提交 ID',
  `question_id` BIGINT UNSIGNED NOT NULL COMMENT '题目 ID',
  `option_id` BIGINT UNSIGNED NOT NULL COMMENT '选项 ID',
  `score_json` JSON NULL COMMENT '本题得分快照',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_answers_submission` (`submission_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='答题明细';

-- ------------------------------------------------------------
-- Table structure for screening_requests
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `screening_requests` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '初筛 ID',
  `user_id` BIGINT UNSIGNED NOT NULL COMMENT '用户 ID',
  `enterprise_id` BIGINT UNSIGNED NOT NULL COMMENT '企业 ID',
  `lead_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT '线索 ID',
  `region_text` VARCHAR(128) NULL DEFAULT NULL COMMENT '用户选择的地区文本',
  `enterprise_type` VARCHAR(64) NULL DEFAULT NULL COMMENT '企业类型',
  `contact_phone_masked` VARCHAR(32) NULL DEFAULT NULL COMMENT '脱敏联系方式',
  `bill_upload_status` VARCHAR(32) NOT NULL DEFAULT 'not_uploaded' COMMENT 'not_uploaded、uploaded',
  `status` VARCHAR(32) NOT NULL DEFAULT 'submitted' COMMENT 'submitted、reviewed、invalid',
  `submitted_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '提交时间',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_screening_lead` (`lead_id`),
  KEY `idx_screening_enterprise` (`enterprise_id`),
  KEY `idx_screening_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='免费用能初筛提交记录';

-- ------------------------------------------------------------
-- Table structure for service_requests
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `service_requests` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '需求 ID',
  `request_no` VARCHAR(32) NOT NULL COMMENT '需求编号',
  `user_id` BIGINT UNSIGNED NOT NULL COMMENT '用户 ID',
  `enterprise_id` BIGINT UNSIGNED NOT NULL COMMENT '企业 ID',
  `lead_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT '线索 ID',
  `primary_need_type` VARCHAR(32) NULL DEFAULT NULL COMMENT '主需求类型',
  `description` VARCHAR(512) NULL DEFAULT NULL COMMENT '用户补充描述',
  `status` VARCHAR(32) NOT NULL DEFAULT 'submitted' COMMENT 'submitted、reviewed、matched、closed',
  `submitted_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '提交时间',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间',
  `deleted_at` DATETIME(3) NULL DEFAULT NULL COMMENT '软删除时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_service_requests_no` (`request_no`),
  KEY `idx_service_requests_lead` (`lead_id`),
  KEY `idx_service_requests_need_status` (`primary_need_type`, `status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='服务需求主表。一次提交可包含多个需求类型';

-- ------------------------------------------------------------
-- Table structure for service_request_items
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `service_request_items` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '明细 ID',
  `service_request_id` BIGINT UNSIGNED NOT NULL COMMENT '需求 ID',
  `need_type` VARCHAR(32) NOT NULL COMMENT 'use_energy、green_power、green_certificate、solar_storage',
  `need_name` VARCHAR(64) NOT NULL COMMENT '展示名称',
  `extra_json` JSON NULL COMMENT '扩展信息',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_service_items_request` (`service_request_id`),
  KEY `idx_service_items_need_type` (`need_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='服务需求类型明细';

-- ------------------------------------------------------------
-- Table structure for files
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `files` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '文件 ID',
  `uploader_user_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT '小程序上传用户',
  `uploader_admin_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT '后台上传管理员',
  `biz_type` VARCHAR(32) NOT NULL COMMENT 'bill、share_card、other',
  `storage_provider` VARCHAR(32) NOT NULL DEFAULT 'local' COMMENT 'local、cos、oss',
  `bucket` VARCHAR(128) NULL DEFAULT NULL COMMENT '存储桶',
  `object_key` VARCHAR(512) NOT NULL COMMENT '对象存储 Key',
  `original_filename` VARCHAR(256) NULL DEFAULT NULL COMMENT '原始文件名',
  `mime_type` VARCHAR(128) NULL DEFAULT NULL COMMENT 'MIME 类型',
  `file_size` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT '文件大小',
  `sha256` CHAR(64) NULL DEFAULT NULL COMMENT '文件哈希',
  `sensitivity_level` VARCHAR(32) NOT NULL DEFAULT 'normal' COMMENT 'normal、sensitive',
  `access_policy` VARCHAR(32) NOT NULL DEFAULT 'private' COMMENT 'private、public_read',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `deleted_at` DATETIME(3) NULL DEFAULT NULL COMMENT '删除时间',
  PRIMARY KEY (`id`),
  KEY `idx_files_biz_type` (`biz_type`),
  KEY `idx_files_sha256` (`sha256`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='文件元数据。真实文件存在对象存储或本地文件系统';

-- ------------------------------------------------------------
-- Table structure for bill_uploads
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `bill_uploads` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '上传记录 ID',
  `enterprise_id` BIGINT UNSIGNED NOT NULL COMMENT '企业 ID',
  `lead_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT '线索 ID',
  `file_id` BIGINT UNSIGNED NOT NULL COMMENT '文件 ID',
  `bill_month` VARCHAR(16) NULL DEFAULT NULL COMMENT '账单月份，如 2026-06',
  `upload_source` VARCHAR(32) NOT NULL DEFAULT 'miniapp' COMMENT 'miniapp、admin',
  `parse_status` VARCHAR(32) NOT NULL DEFAULT 'not_parsed' COMMENT 'not_parsed、parsed、failed',
  `parsed_result_json` JSON NULL COMMENT '结构化结果预留',
  `manual_remark` VARCHAR(512) NULL DEFAULT NULL COMMENT '人工备注',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间',
  `deleted_at` DATETIME(3) NULL DEFAULT NULL COMMENT '软删除时间',
  PRIMARY KEY (`id`),
  KEY `idx_bill_uploads_enterprise` (`enterprise_id`, `created_at`),
  KEY `idx_bill_uploads_lead` (`lead_id`),
  KEY `idx_bill_uploads_parse_status` (`parse_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='电费账单上传记录';

-- ------------------------------------------------------------
-- Table structure for electricity_bills
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `electricity_bills` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '账单 ID',
  `enterprise_id` BIGINT UNSIGNED NOT NULL COMMENT '企业 ID',
  `bill_upload_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT '来源上传记录',
  `bill_month` VARCHAR(16) NOT NULL COMMENT '账单月份',
  `total_kwh` DECIMAL(14,2) NULL DEFAULT NULL COMMENT '总用电量',
  `total_amount` DECIMAL(14,2) NULL DEFAULT NULL COMMENT '总电费',
  `peak_kwh` DECIMAL(14,2) NULL DEFAULT NULL COMMENT '峰电量',
  `flat_kwh` DECIMAL(14,2) NULL DEFAULT NULL COMMENT '平电量',
  `valley_kwh` DECIMAL(14,2) NULL DEFAULT NULL COMMENT '谷电量',
  `capacity_fee` DECIMAL(14,2) NULL DEFAULT NULL COMMENT '容量费',
  `demand_fee` DECIMAL(14,2) NULL DEFAULT NULL COMMENT '需量费',
  `raw_data_json` JSON NULL COMMENT '原始结构化信息',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间',
  `deleted_at` DATETIME(3) NULL DEFAULT NULL COMMENT '软删除时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_electricity_bill_month` (`enterprise_id`, `bill_month`),
  KEY `idx_electricity_bills_month` (`bill_month`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='结构化电费账单。MVP 可先不完全录入，预留后续诊断和报表';

-- ------------------------------------------------------------
-- Table structure for share_cards
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `share_cards` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '分享卡 ID',
  `user_id` BIGINT UNSIGNED NOT NULL COMMENT '用户 ID',
  `submission_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT '答题提交 ID',
  `profile_code` VARCHAR(64) NULL DEFAULT NULL COMMENT '画像编码',
  `file_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT '卡片图片文件',
  `scene` VARCHAR(128) NULL DEFAULT NULL COMMENT '小程序码 scene',
  `status` VARCHAR(32) NOT NULL DEFAULT 'generated' COMMENT 'generated、failed',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_share_cards_user` (`user_id`, `created_at`),
  KEY `idx_share_cards_submission` (`submission_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='测试结果分享卡片记录';

-- ------------------------------------------------------------
-- Table structure for share_events
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `share_events` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '事件 ID',
  `share_card_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT '分享卡 ID',
  `from_user_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT '分享人',
  `visitor_user_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT '访问人',
  `event_type` VARCHAR(32) NOT NULL COMMENT 'share、scan、visit、submit',
  `channel_code` VARCHAR(64) NULL DEFAULT NULL COMMENT '渠道编码',
  `extra_json` JSON NULL COMMENT '扩展参数',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_share_events_card` (`share_card_id`, `created_at`),
  KEY `idx_share_events_type` (`event_type`, `created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='分享、扫码、访问等事件';

-- ------------------------------------------------------------
-- Table structure for suppliers
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `suppliers` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '供应商 ID',
  `name` VARCHAR(128) NOT NULL COMMENT '供应商名称',
  `supplier_type` VARCHAR(32) NOT NULL COMMENT 'retail_power、green_power、certificate、solar_storage、consulting',
  `region_scope_json` JSON NULL COMMENT '服务地区',
  `contact_name` VARCHAR(64) NULL DEFAULT NULL COMMENT '联系人',
  `contact_phone_masked` VARCHAR(32) NULL DEFAULT NULL COMMENT '脱敏电话',
  `contact_phone_cipher` VARCHAR(512) NULL DEFAULT NULL COMMENT '加密电话',
  `status` VARCHAR(32) NOT NULL DEFAULT 'active' COMMENT 'active、disabled',
  `remark` VARCHAR(512) NULL DEFAULT NULL COMMENT '备注',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间',
  `deleted_at` DATETIME(3) NULL DEFAULT NULL COMMENT '软删除时间',
  PRIMARY KEY (`id`),
  KEY `idx_suppliers_type_status` (`supplier_type`, `status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='供应商 / 服务商资料';

-- ------------------------------------------------------------
-- Table structure for supplier_transfers
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `supplier_transfers` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '转接 ID',
  `lead_id` BIGINT UNSIGNED NOT NULL COMMENT '线索 ID',
  `supplier_id` BIGINT UNSIGNED NOT NULL COMMENT '供应商 ID',
  `service_request_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT '关联需求',
  `transfer_status` VARCHAR(32) NOT NULL DEFAULT 'pending' COMMENT 'pending、accepted、rejected、completed',
  `transfer_reason` VARCHAR(512) NULL DEFAULT NULL COMMENT '转接原因',
  `operator_admin_id` BIGINT UNSIGNED NOT NULL COMMENT '操作管理员',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '转接时间',
  `updated_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_supplier_transfers_lead` (`lead_id`, `created_at`),
  KEY `idx_supplier_transfers_supplier` (`supplier_id`, `transfer_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='后台“转供应商”操作记录';

-- ------------------------------------------------------------
-- Table structure for lead_followups
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `lead_followups` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '跟进 ID',
  `lead_id` BIGINT UNSIGNED NOT NULL COMMENT '线索 ID',
  `admin_id` BIGINT UNSIGNED NOT NULL COMMENT '跟进人',
  `followup_type` VARCHAR(32) NOT NULL DEFAULT 'phone' COMMENT 'phone、wechat、offline、system',
  `followup_result` VARCHAR(32) NOT NULL DEFAULT 'contacted' COMMENT 'contacted、no_answer、interested、not_interested、invalid',
  `content` TEXT NULL COMMENT '跟进内容',
  `next_followup_at` DATETIME(3) NULL DEFAULT NULL COMMENT '下次跟进时间',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_followups_lead` (`lead_id`, `created_at`),
  KEY `idx_followups_admin_next` (`admin_id`, `next_followup_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='后台“发起跟进”与跟进记录';

-- ------------------------------------------------------------
-- Table structure for lead_notes
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `lead_notes` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '备注 ID',
  `lead_id` BIGINT UNSIGNED NOT NULL COMMENT '线索 ID',
  `admin_id` BIGINT UNSIGNED NOT NULL COMMENT '备注人',
  `note_type` VARCHAR(32) NOT NULL DEFAULT 'general' COMMENT 'general、risk、supplier、internal',
  `content` TEXT NOT NULL COMMENT '备注内容',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间',
  `deleted_at` DATETIME(3) NULL DEFAULT NULL COMMENT '软删除时间',
  PRIMARY KEY (`id`),
  KEY `idx_lead_notes_lead` (`lead_id`, `created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='后台“备注”记录。备注和跟进分开，便于权限和统计';

-- ------------------------------------------------------------
-- Table structure for admin_users
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `admin_users` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '管理员 ID',
  `username` VARCHAR(64) NOT NULL COMMENT '登录名',
  `display_name` VARCHAR(64) NOT NULL COMMENT '展示名',
  `password_hash` VARCHAR(255) NOT NULL COMMENT '密码哈希',
  `phone_masked` VARCHAR(32) NULL DEFAULT NULL COMMENT '脱敏手机号',
  `phone_cipher` VARCHAR(512) NULL DEFAULT NULL COMMENT '加密手机号',
  `status` VARCHAR(32) NOT NULL DEFAULT 'active' COMMENT 'active、disabled',
  `last_login_at` DATETIME(3) NULL DEFAULT NULL COMMENT '最近登录',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间',
  `deleted_at` DATETIME(3) NULL DEFAULT NULL COMMENT '软删除时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_admin_users_username` (`username`),
  KEY `idx_admin_users_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='后台管理员账号';

-- ------------------------------------------------------------
-- Table structure for admin_roles
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `admin_roles` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '角色 ID',
  `role_code` VARCHAR(64) NOT NULL COMMENT '角色编码，如 super_admin、operator',
  `role_name` VARCHAR(64) NOT NULL COMMENT '角色名称',
  `description` VARCHAR(256) NULL DEFAULT NULL COMMENT '描述',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_admin_roles_code` (`role_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='后台角色';

-- ------------------------------------------------------------
-- Table structure for admin_permissions
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `admin_permissions` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '权限 ID',
  `permission_code` VARCHAR(128) NOT NULL COMMENT '权限编码，如 lead:view、lead:transfer',
  `permission_name` VARCHAR(128) NOT NULL COMMENT '权限名称',
  `module_code` VARCHAR(64) NOT NULL COMMENT '模块编码',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_permissions_code` (`permission_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='后台权限点';

-- ------------------------------------------------------------
-- Table structure for admin_user_roles
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `admin_user_roles` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `admin_user_id` BIGINT UNSIGNED NOT NULL COMMENT '管理员 ID',
  `role_id` BIGINT UNSIGNED NOT NULL COMMENT '角色 ID',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_admin_user_role` (`admin_user_id`, `role_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='管理员与角色关系';

-- ------------------------------------------------------------
-- Table structure for admin_role_permissions
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `admin_role_permissions` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `role_id` BIGINT UNSIGNED NOT NULL COMMENT '角色 ID',
  `permission_id` BIGINT UNSIGNED NOT NULL COMMENT '权限 ID',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_role_permission` (`role_id`, `permission_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='角色与权限关系';

-- ------------------------------------------------------------
-- Table structure for audit_logs
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `audit_logs` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '日志 ID',
  `actor_type` VARCHAR(32) NOT NULL DEFAULT 'admin' COMMENT 'admin、user、system',
  `actor_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT '操作人 ID',
  `action` VARCHAR(128) NOT NULL COMMENT '操作编码，如 lead.view_sensitive',
  `target_type` VARCHAR(64) NULL DEFAULT NULL COMMENT '操作对象类型',
  `target_id` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT '操作对象 ID',
  `ip_address` VARCHAR(64) NULL DEFAULT NULL COMMENT 'IP',
  `user_agent` VARCHAR(512) NULL DEFAULT NULL COMMENT '客户端信息',
  `request_id` VARCHAR(64) NULL DEFAULT NULL COMMENT '请求 ID',
  `detail_json` JSON NULL COMMENT '操作详情',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_audit_actor` (`actor_type`, `actor_id`, `created_at`),
  KEY `idx_audit_target` (`target_type`, `target_id`, `created_at`),
  KEY `idx_audit_action` (`action`, `created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='操作日志。重点记录后台查看敏感信息、下载账单、转供应商、修改线索状态等动作';
