# 河狸数字能源 MVP 数据库设计与字典

版本：v0.1  
来源：由产品项目结构文档拆分。  
适用范围：MySQL 8.x、FastAPI 模块化单体、MVP 阶段线索管理闭环。

---

## 1. 数据库设计原则

### 1.1 命名规范

1. 表名使用小写下划线，复数或业务名词均可，但全库保持一致。
2. 主键统一使用 `BIGINT UNSIGNED AUTO_INCREMENT`。
3. 状态字段优先使用 `VARCHAR(32)`，避免 MySQL `ENUM` 后续修改困难。
4. 金额使用 `DECIMAL(12,2)`。
5. 时间使用 `DATETIME(3)`。
6. 配置、快照、扩展字段使用 `JSON`。
7. 所有业务表建议包含：

```text
id
created_at
updated_at
deleted_at
```

### 1.2 通用字段说明

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | BIGINT UNSIGNED | 主键 |
| `created_at` | DATETIME(3) | 创建时间 |
| `updated_at` | DATETIME(3) | 更新时间 |
| `deleted_at` | DATETIME(3) NULL | 软删除时间 |

### 1.3 核心业务关系

```text
user
  -> enterprise
    -> lead
    -> questionnaire_submission
    -> screening_request
    -> service_request
    -> bill_upload

lead
  -> lead_followup
  -> supplier_transfer
  -> audit_log
```

---

## 2. 数据库字典

## 2.1 用户与微信登录

### 表：app_users

说明：小程序端用户主体。

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `id` | BIGINT UNSIGNED | 是 | 自增 | 用户 ID |
| `nickname` | VARCHAR(64) | 否 | NULL | 微信昵称或系统昵称 |
| `avatar_url` | VARCHAR(512) | 否 | NULL | 头像 URL |
| `phone_masked` | VARCHAR(32) | 否 | NULL | 脱敏手机号，如 138****8888 |
| `phone_cipher` | VARCHAR(512) | 否 | NULL | 加密手机号 |
| `phone_hash` | CHAR(64) | 否 | NULL | 手机号哈希，用于去重 |
| `status` | VARCHAR(32) | 是 | active | active、disabled |
| `last_login_at` | DATETIME(3) | 否 | NULL | 最近登录时间 |
| `created_at` | DATETIME(3) | 是 | 当前时间 | 创建时间 |
| `updated_at` | DATETIME(3) | 是 | 当前时间 | 更新时间 |
| `deleted_at` | DATETIME(3) | 否 | NULL | 软删除时间 |

索引：

| 索引名 | 字段 | 说明 |
|---|---|---|
| `idx_app_users_phone_hash` | `phone_hash` | 手机号去重和检索 |
| `idx_app_users_status` | `status` | 状态筛选 |

### 表：wechat_identities

说明：微信身份绑定信息。

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `id` | BIGINT UNSIGNED | 是 | 自增 | 主键 |
| `user_id` | BIGINT UNSIGNED | 是 | 无 | 关联 `app_users.id` |
| `openid` | VARCHAR(128) | 是 | 无 | 小程序 OpenID |
| `unionid` | VARCHAR(128) | 否 | NULL | 微信 UnionID |
| `session_key_cipher` | VARCHAR(512) | 否 | NULL | 加密后的 session_key，谨慎保存 |
| `appid` | VARCHAR(64) | 是 | 无 | 小程序 AppID |
| `created_at` | DATETIME(3) | 是 | 当前时间 | 创建时间 |
| `updated_at` | DATETIME(3) | 是 | 当前时间 | 更新时间 |

索引：

| 索引名 | 字段 | 说明 |
|---|---|---|
| `uk_wechat_openid_appid` | `openid`, `appid` | 同一小程序下 OpenID 唯一 |
| `idx_wechat_user_id` | `user_id` | 查询用户微信身份 |

### 表：user_consents

说明：用户协议、隐私政策、账单敏感信息授权记录。

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `id` | BIGINT UNSIGNED | 是 | 自增 | 主键 |
| `user_id` | BIGINT UNSIGNED | 是 | 无 | 关联用户 |
| `consent_type` | VARCHAR(32) | 是 | 无 | privacy、bill_sensitive、phone_auth |
| `version` | VARCHAR(32) | 是 | 无 | 协议版本 |
| `granted` | TINYINT(1) | 是 | 1 | 是否同意 |
| `ip_address` | VARCHAR(64) | 否 | NULL | IP |
| `user_agent` | VARCHAR(512) | 否 | NULL | 客户端信息 |
| `created_at` | DATETIME(3) | 是 | 当前时间 | 授权时间 |

索引：

| 索引名 | 字段 | 说明 |
|---|---|---|
| `idx_user_consents_user_type` | `user_id`, `consent_type` | 查询用户授权 |

---

## 2.2 企业与线索

### 表：enterprises

说明：企业客户主体。

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `id` | BIGINT UNSIGNED | 是 | 自增 | 企业 ID |
| `owner_user_id` | BIGINT UNSIGNED | 否 | NULL | 来源小程序用户 |
| `name` | VARCHAR(128) | 是 | 无 | 企业简称或名称 |
| `region_province` | VARCHAR(32) | 否 | NULL | 省份 |
| `region_city` | VARCHAR(32) | 否 | NULL | 城市 |
| `region_district` | VARCHAR(32) | 否 | NULL | 区县 |
| `industry_type` | VARCHAR(64) | 否 | NULL | 企业类型，如制造业 / 工厂 |
| `monthly_cost_range` | VARCHAR(32) | 否 | NULL | 月电费规模，如 10-20 万/月 |
| `scale_remark` | VARCHAR(128) | 否 | NULL | 规模补充 |
| `status` | VARCHAR(32) | 是 | active | active、merged、disabled |
| `created_at` | DATETIME(3) | 是 | 当前时间 | 创建时间 |
| `updated_at` | DATETIME(3) | 是 | 当前时间 | 更新时间 |
| `deleted_at` | DATETIME(3) | 否 | NULL | 软删除时间 |

索引：

| 索引名 | 字段 | 说明 |
|---|---|---|
| `idx_enterprises_owner_user` | `owner_user_id` | 用户企业查询 |
| `idx_enterprises_region` | `region_province`, `region_city` | 地区筛选 |
| `idx_enterprises_industry` | `industry_type` | 行业筛选 |

### 表：enterprise_contacts

说明：企业联系人。手机号建议加密保存，列表页展示脱敏值。

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `id` | BIGINT UNSIGNED | 是 | 自增 | 联系人 ID |
| `enterprise_id` | BIGINT UNSIGNED | 是 | 无 | 企业 ID |
| `name` | VARCHAR(64) | 否 | NULL | 联系人姓名 |
| `role_title` | VARCHAR(64) | 否 | NULL | 职务，如老板、负责人 |
| `phone_masked` | VARCHAR(32) | 否 | NULL | 脱敏手机号 |
| `phone_cipher` | VARCHAR(512) | 否 | NULL | 加密手机号 |
| `phone_hash` | CHAR(64) | 否 | NULL | 手机号哈希 |
| `wechat_no` | VARCHAR(128) | 否 | NULL | 微信号，可选 |
| `is_primary` | TINYINT(1) | 是 | 1 | 是否主联系人 |
| `created_at` | DATETIME(3) | 是 | 当前时间 | 创建时间 |
| `updated_at` | DATETIME(3) | 是 | 当前时间 | 更新时间 |
| `deleted_at` | DATETIME(3) | 否 | NULL | 软删除时间 |

索引：

| 索引名 | 字段 | 说明 |
|---|---|---|
| `idx_contacts_enterprise` | `enterprise_id` | 查询企业联系人 |
| `idx_contacts_phone_hash` | `phone_hash` | 联系方式去重 |

### 表：leads

说明：后台线索主表，承载列表、筛选、状态和等级。

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `id` | BIGINT UNSIGNED | 是 | 自增 | 线索 ID |
| `lead_no` | VARCHAR(32) | 是 | 无 | 线索编号 |
| `enterprise_id` | BIGINT UNSIGNED | 是 | 无 | 企业 ID |
| `user_id` | BIGINT UNSIGNED | 否 | NULL | 来源用户 |
| `source_channel` | VARCHAR(64) | 是 | miniapp | 来源渠道 |
| `source_entry` | VARCHAR(64) | 否 | NULL | 来源入口，如 体质测试、免费初筛 |
| `lead_grade` | VARCHAR(16) | 否 | NULL | A、B、C |
| `lead_status` | VARCHAR(32) | 是 | pending_followup | pending_followup、following、transferred_supplier、content_saved、closed |
| `primary_need_type` | VARCHAR(32) | 否 | NULL | use_energy、green_power、green_certificate、solar_storage |
| `profile_code` | VARCHAR(64) | 否 | NULL | 测评画像，如 cost_sensitive |
| `has_bill_uploaded` | TINYINT(1) | 是 | 0 | 是否上传账单 |
| `has_phone_authorized` | TINYINT(1) | 是 | 0 | 是否授权手机号 |
| `assigned_admin_id` | BIGINT UNSIGNED | 否 | NULL | 当前负责人 |
| `first_submitted_at` | DATETIME(3) | 否 | NULL | 首次提交时间 |
| `last_activity_at` | DATETIME(3) | 否 | NULL | 最近动作时间 |
| `created_at` | DATETIME(3) | 是 | 当前时间 | 创建时间 |
| `updated_at` | DATETIME(3) | 是 | 当前时间 | 更新时间 |
| `deleted_at` | DATETIME(3) | 否 | NULL | 软删除时间 |

索引：

| 索引名 | 字段 | 说明 |
|---|---|---|
| `uk_leads_lead_no` | `lead_no` | 线索编号唯一 |
| `idx_leads_grade_status` | `lead_grade`, `lead_status` | 后台筛选 |
| `idx_leads_need_type` | `primary_need_type` | 需求方向筛选 |
| `idx_leads_created_at` | `created_at` | 统计与排序 |
| `idx_leads_assigned_admin` | `assigned_admin_id` | 负责人筛选 |

### 表：lead_status_logs

说明：线索状态流转记录。

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `id` | BIGINT UNSIGNED | 是 | 自增 | 主键 |
| `lead_id` | BIGINT UNSIGNED | 是 | 无 | 线索 ID |
| `from_status` | VARCHAR(32) | 否 | NULL | 原状态 |
| `to_status` | VARCHAR(32) | 是 | 无 | 新状态 |
| `operator_admin_id` | BIGINT UNSIGNED | 否 | NULL | 操作人 |
| `remark` | VARCHAR(512) | 否 | NULL | 状态变化备注 |
| `created_at` | DATETIME(3) | 是 | 当前时间 | 创建时间 |

索引：

| 索引名 | 字段 | 说明 |
|---|---|---|
| `idx_lead_status_logs_lead` | `lead_id`, `created_at` | 线索状态时间线 |

---

## 2.3 经营体质测试

### 表：questionnaire_sets

说明：测试问卷版本。

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `id` | BIGINT UNSIGNED | 是 | 自增 | 问卷 ID |
| `code` | VARCHAR(64) | 是 | 无 | 问卷编码 |
| `name` | VARCHAR(128) | 是 | 无 | 问卷名称，如经营体质测试 |
| `version` | VARCHAR(32) | 是 | v1 | 版本 |
| `description` | VARCHAR(512) | 否 | NULL | 描述 |
| `status` | VARCHAR(32) | 是 | draft | draft、published、archived |
| `published_at` | DATETIME(3) | 否 | NULL | 发布时间 |
| `created_at` | DATETIME(3) | 是 | 当前时间 | 创建时间 |
| `updated_at` | DATETIME(3) | 是 | 当前时间 | 更新时间 |
| `deleted_at` | DATETIME(3) | 否 | NULL | 软删除时间 |

索引：

| 索引名 | 字段 | 说明 |
|---|---|---|
| `uk_questionnaire_code_version` | `code`, `version` | 同一问卷版本唯一 |

### 表：questionnaire_questions

说明：问卷题目。

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `id` | BIGINT UNSIGNED | 是 | 自增 | 题目 ID |
| `questionnaire_id` | BIGINT UNSIGNED | 是 | 无 | 问卷 ID |
| `title` | VARCHAR(256) | 是 | 无 | 题目标题 |
| `subtitle` | VARCHAR(256) | 否 | NULL | 题目副标题 |
| `dimension_code` | VARCHAR(64) | 否 | NULL | 评分维度，如 cost、growth、risk |
| `question_type` | VARCHAR(32) | 是 | single_choice | single_choice、multiple_choice |
| `sort_order` | INT | 是 | 0 | 排序 |
| `is_required` | TINYINT(1) | 是 | 1 | 是否必答 |
| `status` | VARCHAR(32) | 是 | active | active、disabled |
| `created_at` | DATETIME(3) | 是 | 当前时间 | 创建时间 |
| `updated_at` | DATETIME(3) | 是 | 当前时间 | 更新时间 |

索引：

| 索引名 | 字段 | 说明 |
|---|---|---|
| `idx_questions_questionnaire_sort` | `questionnaire_id`, `sort_order` | 题目排序 |

### 表：questionnaire_options

说明：题目选项和评分配置。

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `id` | BIGINT UNSIGNED | 是 | 自增 | 选项 ID |
| `question_id` | BIGINT UNSIGNED | 是 | 无 | 题目 ID |
| `option_label` | VARCHAR(8) | 否 | NULL | A、B、C、D |
| `title` | VARCHAR(256) | 是 | 无 | 选项文案 |
| `subtitle` | VARCHAR(256) | 否 | NULL | 选项副文案 |
| `score_json` | JSON | 否 | NULL | 各维度加分，如 `{"cost": 3}` |
| `profile_bias` | VARCHAR(64) | 否 | NULL | 倾向画像 |
| `sort_order` | INT | 是 | 0 | 排序 |
| `created_at` | DATETIME(3) | 是 | 当前时间 | 创建时间 |
| `updated_at` | DATETIME(3) | 是 | 当前时间 | 更新时间 |

索引：

| 索引名 | 字段 | 说明 |
|---|---|---|
| `idx_options_question_sort` | `question_id`, `sort_order` | 选项排序 |

### 表：questionnaire_result_profiles

说明：测试结果画像配置，如稳健经营型、成本敏感型、增长扩张型、隐性浪费型。

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `id` | BIGINT UNSIGNED | 是 | 自增 | 画像 ID |
| `questionnaire_id` | BIGINT UNSIGNED | 是 | 无 | 问卷 ID |
| `profile_code` | VARCHAR(64) | 是 | 无 | 画像编码 |
| `profile_name` | VARCHAR(64) | 是 | 无 | 画像名称 |
| `lead_grade_suggestion` | VARCHAR(16) | 否 | NULL | 默认建议线索等级 |
| `theme_color` | VARCHAR(32) | 否 | NULL | 分享卡片颜色 |
| `tags_json` | JSON | 否 | NULL | 标签列表 |
| `summary` | VARCHAR(512) | 否 | NULL | 结果说明 |
| `recommendations_json` | JSON | 否 | NULL | 建议列表 |
| `rule_json` | JSON | 否 | NULL | 命中规则 |
| `created_at` | DATETIME(3) | 是 | 当前时间 | 创建时间 |
| `updated_at` | DATETIME(3) | 是 | 当前时间 | 更新时间 |

索引：

| 索引名 | 字段 | 说明 |
|---|---|---|
| `uk_profile_questionnaire_code` | `questionnaire_id`, `profile_code` | 问卷内画像唯一 |

### 表：questionnaire_submissions

说明：用户答题提交记录。

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `id` | BIGINT UNSIGNED | 是 | 自增 | 提交 ID |
| `user_id` | BIGINT UNSIGNED | 是 | 无 | 用户 ID |
| `enterprise_id` | BIGINT UNSIGNED | 否 | NULL | 企业 ID |
| `lead_id` | BIGINT UNSIGNED | 否 | NULL | 线索 ID |
| `questionnaire_id` | BIGINT UNSIGNED | 是 | 无 | 问卷 ID |
| `result_profile_id` | BIGINT UNSIGNED | 否 | NULL | 命中的画像 ID |
| `profile_code` | VARCHAR(64) | 否 | NULL | 画像编码快照 |
| `total_score` | INT | 是 | 0 | 总分 |
| `dimension_scores_json` | JSON | 否 | NULL | 维度得分快照 |
| `answers_snapshot_json` | JSON | 否 | NULL | 答案快照 |
| `result_snapshot_json` | JSON | 否 | NULL | 结果页快照 |
| `created_at` | DATETIME(3) | 是 | 当前时间 | 提交时间 |

索引：

| 索引名 | 字段 | 说明 |
|---|---|---|
| `idx_submissions_user` | `user_id`, `created_at` | 用户答题历史 |
| `idx_submissions_lead` | `lead_id` | 线索关联答题 |
| `idx_submissions_profile` | `profile_code` | 画像统计 |

### 表：questionnaire_answers

说明：答题明细。

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `id` | BIGINT UNSIGNED | 是 | 自增 | 明细 ID |
| `submission_id` | BIGINT UNSIGNED | 是 | 无 | 提交 ID |
| `question_id` | BIGINT UNSIGNED | 是 | 无 | 题目 ID |
| `option_id` | BIGINT UNSIGNED | 是 | 无 | 选项 ID |
| `score_json` | JSON | 否 | NULL | 本题得分快照 |
| `created_at` | DATETIME(3) | 是 | 当前时间 | 创建时间 |

索引：

| 索引名 | 字段 | 说明 |
|---|---|---|
| `idx_answers_submission` | `submission_id` | 查询答题明细 |

---

## 2.4 免费用能初筛与服务需求

### 表：screening_requests

说明：免费用能初筛提交记录。

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `id` | BIGINT UNSIGNED | 是 | 自增 | 初筛 ID |
| `user_id` | BIGINT UNSIGNED | 是 | 无 | 用户 ID |
| `enterprise_id` | BIGINT UNSIGNED | 是 | 无 | 企业 ID |
| `lead_id` | BIGINT UNSIGNED | 否 | NULL | 线索 ID |
| `region_text` | VARCHAR(128) | 否 | NULL | 用户选择的地区文本 |
| `enterprise_type` | VARCHAR(64) | 否 | NULL | 企业类型 |
| `contact_phone_masked` | VARCHAR(32) | 否 | NULL | 脱敏联系方式 |
| `bill_upload_status` | VARCHAR(32) | 是 | not_uploaded | not_uploaded、uploaded |
| `status` | VARCHAR(32) | 是 | submitted | submitted、reviewed、invalid |
| `submitted_at` | DATETIME(3) | 是 | 当前时间 | 提交时间 |
| `created_at` | DATETIME(3) | 是 | 当前时间 | 创建时间 |
| `updated_at` | DATETIME(3) | 是 | 当前时间 | 更新时间 |

索引：

| 索引名 | 字段 | 说明 |
|---|---|---|
| `idx_screening_lead` | `lead_id` | 线索关联 |
| `idx_screening_enterprise` | `enterprise_id` | 企业初筛记录 |
| `idx_screening_status` | `status` | 后台筛选 |

### 表：service_requests

说明：服务需求主表。一次提交可包含多个需求类型。

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `id` | BIGINT UNSIGNED | 是 | 自增 | 需求 ID |
| `request_no` | VARCHAR(32) | 是 | 无 | 需求编号 |
| `user_id` | BIGINT UNSIGNED | 是 | 无 | 用户 ID |
| `enterprise_id` | BIGINT UNSIGNED | 是 | 无 | 企业 ID |
| `lead_id` | BIGINT UNSIGNED | 否 | NULL | 线索 ID |
| `primary_need_type` | VARCHAR(32) | 否 | NULL | 主需求类型 |
| `description` | VARCHAR(512) | 否 | NULL | 用户补充描述 |
| `status` | VARCHAR(32) | 是 | submitted | submitted、reviewed、matched、closed |
| `submitted_at` | DATETIME(3) | 是 | 当前时间 | 提交时间 |
| `created_at` | DATETIME(3) | 是 | 当前时间 | 创建时间 |
| `updated_at` | DATETIME(3) | 是 | 当前时间 | 更新时间 |
| `deleted_at` | DATETIME(3) | 否 | NULL | 软删除时间 |

索引：

| 索引名 | 字段 | 说明 |
|---|---|---|
| `uk_service_requests_no` | `request_no` | 需求编号唯一 |
| `idx_service_requests_lead` | `lead_id` | 线索关联 |
| `idx_service_requests_need_status` | `primary_need_type`, `status` | 后台筛选 |

### 表：service_request_items

说明：服务需求类型明细。

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `id` | BIGINT UNSIGNED | 是 | 自增 | 明细 ID |
| `service_request_id` | BIGINT UNSIGNED | 是 | 无 | 需求 ID |
| `need_type` | VARCHAR(32) | 是 | 无 | use_energy、green_power、green_certificate、solar_storage |
| `need_name` | VARCHAR(64) | 是 | 无 | 展示名称 |
| `extra_json` | JSON | 否 | NULL | 扩展信息 |
| `created_at` | DATETIME(3) | 是 | 当前时间 | 创建时间 |

索引：

| 索引名 | 字段 | 说明 |
|---|---|---|
| `idx_service_items_request` | `service_request_id` | 查询需求明细 |
| `idx_service_items_need_type` | `need_type` | 按需求类型统计 |

---

## 2.5 文件与账单

### 表：files

说明：文件元数据。真实文件存在对象存储或本地文件系统。

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `id` | BIGINT UNSIGNED | 是 | 自增 | 文件 ID |
| `uploader_user_id` | BIGINT UNSIGNED | 否 | NULL | 小程序上传用户 |
| `uploader_admin_id` | BIGINT UNSIGNED | 否 | NULL | 后台上传管理员 |
| `biz_type` | VARCHAR(32) | 是 | 无 | bill、share_card、other |
| `storage_provider` | VARCHAR(32) | 是 | local | local、cos、oss |
| `bucket` | VARCHAR(128) | 否 | NULL | 存储桶 |
| `object_key` | VARCHAR(512) | 是 | 无 | 对象存储 Key |
| `original_filename` | VARCHAR(256) | 否 | NULL | 原始文件名 |
| `mime_type` | VARCHAR(128) | 否 | NULL | MIME 类型 |
| `file_size` | BIGINT UNSIGNED | 否 | NULL | 文件大小 |
| `sha256` | CHAR(64) | 否 | NULL | 文件哈希 |
| `sensitivity_level` | VARCHAR(32) | 是 | normal | normal、sensitive |
| `access_policy` | VARCHAR(32) | 是 | private | private、public_read |
| `created_at` | DATETIME(3) | 是 | 当前时间 | 创建时间 |
| `deleted_at` | DATETIME(3) | 否 | NULL | 删除时间 |

索引：

| 索引名 | 字段 | 说明 |
|---|---|---|
| `idx_files_biz_type` | `biz_type` | 按业务类型查询 |
| `idx_files_sha256` | `sha256` | 文件去重 |

### 表：bill_uploads

说明：电费账单上传记录。

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `id` | BIGINT UNSIGNED | 是 | 自增 | 上传记录 ID |
| `enterprise_id` | BIGINT UNSIGNED | 是 | 无 | 企业 ID |
| `lead_id` | BIGINT UNSIGNED | 否 | NULL | 线索 ID |
| `file_id` | BIGINT UNSIGNED | 是 | 无 | 文件 ID |
| `bill_month` | VARCHAR(16) | 否 | NULL | 账单月份，如 2026-06 |
| `upload_source` | VARCHAR(32) | 是 | miniapp | miniapp、admin |
| `parse_status` | VARCHAR(32) | 是 | not_parsed | not_parsed、parsed、failed |
| `parsed_result_json` | JSON | 否 | NULL | 结构化结果预留 |
| `manual_remark` | VARCHAR(512) | 否 | NULL | 人工备注 |
| `created_at` | DATETIME(3) | 是 | 当前时间 | 创建时间 |
| `updated_at` | DATETIME(3) | 是 | 当前时间 | 更新时间 |
| `deleted_at` | DATETIME(3) | 否 | NULL | 软删除时间 |

索引：

| 索引名 | 字段 | 说明 |
|---|---|---|
| `idx_bill_uploads_enterprise` | `enterprise_id`, `created_at` | 企业账单列表 |
| `idx_bill_uploads_lead` | `lead_id` | 线索资料状态 |
| `idx_bill_uploads_parse_status` | `parse_status` | 解析状态筛选 |

### 表：electricity_bills

说明：结构化电费账单。MVP 可先不完全录入，预留后续诊断和报表。

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `id` | BIGINT UNSIGNED | 是 | 自增 | 账单 ID |
| `enterprise_id` | BIGINT UNSIGNED | 是 | 无 | 企业 ID |
| `bill_upload_id` | BIGINT UNSIGNED | 否 | NULL | 来源上传记录 |
| `bill_month` | VARCHAR(16) | 是 | 无 | 账单月份 |
| `total_kwh` | DECIMAL(14,2) | 否 | NULL | 总用电量 |
| `total_amount` | DECIMAL(14,2) | 否 | NULL | 总电费 |
| `peak_kwh` | DECIMAL(14,2) | 否 | NULL | 峰电量 |
| `flat_kwh` | DECIMAL(14,2) | 否 | NULL | 平电量 |
| `valley_kwh` | DECIMAL(14,2) | 否 | NULL | 谷电量 |
| `capacity_fee` | DECIMAL(14,2) | 否 | NULL | 容量费 |
| `demand_fee` | DECIMAL(14,2) | 否 | NULL | 需量费 |
| `raw_data_json` | JSON | 否 | NULL | 原始结构化信息 |
| `created_at` | DATETIME(3) | 是 | 当前时间 | 创建时间 |
| `updated_at` | DATETIME(3) | 是 | 当前时间 | 更新时间 |
| `deleted_at` | DATETIME(3) | 否 | NULL | 软删除时间 |

索引：

| 索引名 | 字段 | 说明 |
|---|---|---|
| `uk_electricity_bill_month` | `enterprise_id`, `bill_month` | 同企业同月份唯一 |
| `idx_electricity_bills_month` | `bill_month` | 月份统计 |

---

## 2.6 分享卡片与渠道

### 表：share_cards

说明：测试结果分享卡片记录。

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `id` | BIGINT UNSIGNED | 是 | 自增 | 分享卡 ID |
| `user_id` | BIGINT UNSIGNED | 是 | 无 | 用户 ID |
| `submission_id` | BIGINT UNSIGNED | 否 | NULL | 答题提交 ID |
| `profile_code` | VARCHAR(64) | 否 | NULL | 画像编码 |
| `file_id` | BIGINT UNSIGNED | 否 | NULL | 卡片图片文件 |
| `scene` | VARCHAR(128) | 否 | NULL | 小程序码 scene |
| `status` | VARCHAR(32) | 是 | generated | generated、failed |
| `created_at` | DATETIME(3) | 是 | 当前时间 | 创建时间 |

索引：

| 索引名 | 字段 | 说明 |
|---|---|---|
| `idx_share_cards_user` | `user_id`, `created_at` | 用户分享卡 |
| `idx_share_cards_submission` | `submission_id` | 结果页分享 |

### 表：share_events

说明：分享、扫码、访问等事件。

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `id` | BIGINT UNSIGNED | 是 | 自增 | 事件 ID |
| `share_card_id` | BIGINT UNSIGNED | 否 | NULL | 分享卡 ID |
| `from_user_id` | BIGINT UNSIGNED | 否 | NULL | 分享人 |
| `visitor_user_id` | BIGINT UNSIGNED | 否 | NULL | 访问人 |
| `event_type` | VARCHAR(32) | 是 | 无 | share、scan、visit、submit |
| `channel_code` | VARCHAR(64) | 否 | NULL | 渠道编码 |
| `extra_json` | JSON | 否 | NULL | 扩展参数 |
| `created_at` | DATETIME(3) | 是 | 当前时间 | 创建时间 |

索引：

| 索引名 | 字段 | 说明 |
|---|---|---|
| `idx_share_events_card` | `share_card_id`, `created_at` | 卡片事件 |
| `idx_share_events_type` | `event_type`, `created_at` | 事件统计 |

---

## 2.7 供应商与转接

### 表：suppliers

说明：供应商 / 服务商资料。

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `id` | BIGINT UNSIGNED | 是 | 自增 | 供应商 ID |
| `name` | VARCHAR(128) | 是 | 无 | 供应商名称 |
| `supplier_type` | VARCHAR(32) | 是 | 无 | retail_power、green_power、certificate、solar_storage、consulting |
| `region_scope_json` | JSON | 否 | NULL | 服务地区 |
| `contact_name` | VARCHAR(64) | 否 | NULL | 联系人 |
| `contact_phone_masked` | VARCHAR(32) | 否 | NULL | 脱敏电话 |
| `contact_phone_cipher` | VARCHAR(512) | 否 | NULL | 加密电话 |
| `status` | VARCHAR(32) | 是 | active | active、disabled |
| `remark` | VARCHAR(512) | 否 | NULL | 备注 |
| `created_at` | DATETIME(3) | 是 | 当前时间 | 创建时间 |
| `updated_at` | DATETIME(3) | 是 | 当前时间 | 更新时间 |
| `deleted_at` | DATETIME(3) | 否 | NULL | 软删除时间 |

索引：

| 索引名 | 字段 | 说明 |
|---|---|---|
| `idx_suppliers_type_status` | `supplier_type`, `status` | 供应商筛选 |

### 表：supplier_transfers

说明：后台“转供应商”操作记录。

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `id` | BIGINT UNSIGNED | 是 | 自增 | 转接 ID |
| `lead_id` | BIGINT UNSIGNED | 是 | 无 | 线索 ID |
| `supplier_id` | BIGINT UNSIGNED | 是 | 无 | 供应商 ID |
| `service_request_id` | BIGINT UNSIGNED | 否 | NULL | 关联需求 |
| `transfer_status` | VARCHAR(32) | 是 | pending | pending、accepted、rejected、completed |
| `transfer_reason` | VARCHAR(512) | 否 | NULL | 转接原因 |
| `operator_admin_id` | BIGINT UNSIGNED | 是 | 无 | 操作管理员 |
| `created_at` | DATETIME(3) | 是 | 当前时间 | 转接时间 |
| `updated_at` | DATETIME(3) | 是 | 当前时间 | 更新时间 |

索引：

| 索引名 | 字段 | 说明 |
|---|---|---|
| `idx_supplier_transfers_lead` | `lead_id`, `created_at` | 线索转接记录 |
| `idx_supplier_transfers_supplier` | `supplier_id`, `transfer_status` | 供应商接收情况 |

---

## 2.8 CRM 跟进与备注

### 表：lead_followups

说明：后台“发起跟进”与跟进记录。

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `id` | BIGINT UNSIGNED | 是 | 自增 | 跟进 ID |
| `lead_id` | BIGINT UNSIGNED | 是 | 无 | 线索 ID |
| `admin_id` | BIGINT UNSIGNED | 是 | 无 | 跟进人 |
| `followup_type` | VARCHAR(32) | 是 | phone | phone、wechat、offline、system |
| `followup_result` | VARCHAR(32) | 是 | contacted | contacted、no_answer、interested、not_interested、invalid |
| `content` | TEXT | 否 | NULL | 跟进内容 |
| `next_followup_at` | DATETIME(3) | 否 | NULL | 下次跟进时间 |
| `created_at` | DATETIME(3) | 是 | 当前时间 | 创建时间 |
| `updated_at` | DATETIME(3) | 是 | 当前时间 | 更新时间 |

索引：

| 索引名 | 字段 | 说明 |
|---|---|---|
| `idx_followups_lead` | `lead_id`, `created_at` | 线索跟进时间线 |
| `idx_followups_admin_next` | `admin_id`, `next_followup_at` | 待办跟进 |

### 表：lead_notes

说明：后台“备注”记录。备注和跟进分开，便于权限和统计。

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `id` | BIGINT UNSIGNED | 是 | 自增 | 备注 ID |
| `lead_id` | BIGINT UNSIGNED | 是 | 无 | 线索 ID |
| `admin_id` | BIGINT UNSIGNED | 是 | 无 | 备注人 |
| `note_type` | VARCHAR(32) | 是 | general | general、risk、supplier、internal |
| `content` | TEXT | 是 | 无 | 备注内容 |
| `created_at` | DATETIME(3) | 是 | 当前时间 | 创建时间 |
| `updated_at` | DATETIME(3) | 是 | 当前时间 | 更新时间 |
| `deleted_at` | DATETIME(3) | 否 | NULL | 软删除时间 |

索引：

| 索引名 | 字段 | 说明 |
|---|---|---|
| `idx_lead_notes_lead` | `lead_id`, `created_at` | 线索备注 |

---

## 2.9 后台权限与安全审计

### 表：admin_users

说明：后台管理员账号。

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `id` | BIGINT UNSIGNED | 是 | 自增 | 管理员 ID |
| `username` | VARCHAR(64) | 是 | 无 | 登录名 |
| `display_name` | VARCHAR(64) | 是 | 无 | 展示名 |
| `password_hash` | VARCHAR(255) | 是 | 无 | 密码哈希 |
| `phone_masked` | VARCHAR(32) | 否 | NULL | 脱敏手机号 |
| `phone_cipher` | VARCHAR(512) | 否 | NULL | 加密手机号 |
| `status` | VARCHAR(32) | 是 | active | active、disabled |
| `last_login_at` | DATETIME(3) | 否 | NULL | 最近登录 |
| `created_at` | DATETIME(3) | 是 | 当前时间 | 创建时间 |
| `updated_at` | DATETIME(3) | 是 | 当前时间 | 更新时间 |
| `deleted_at` | DATETIME(3) | 否 | NULL | 软删除时间 |

索引：

| 索引名 | 字段 | 说明 |
|---|---|---|
| `uk_admin_users_username` | `username` | 登录名唯一 |
| `idx_admin_users_status` | `status` | 状态筛选 |

### 表：admin_roles

说明：后台角色。

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `id` | BIGINT UNSIGNED | 是 | 自增 | 角色 ID |
| `role_code` | VARCHAR(64) | 是 | 无 | 角色编码，如 super_admin、operator |
| `role_name` | VARCHAR(64) | 是 | 无 | 角色名称 |
| `description` | VARCHAR(256) | 否 | NULL | 描述 |
| `created_at` | DATETIME(3) | 是 | 当前时间 | 创建时间 |
| `updated_at` | DATETIME(3) | 是 | 当前时间 | 更新时间 |

索引：

| 索引名 | 字段 | 说明 |
|---|---|---|
| `uk_admin_roles_code` | `role_code` | 角色编码唯一 |

### 表：admin_permissions

说明：后台权限点。

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `id` | BIGINT UNSIGNED | 是 | 自增 | 权限 ID |
| `permission_code` | VARCHAR(128) | 是 | 无 | 权限编码，如 lead:view、lead:transfer |
| `permission_name` | VARCHAR(128) | 是 | 无 | 权限名称 |
| `module_code` | VARCHAR(64) | 是 | 无 | 模块编码 |
| `created_at` | DATETIME(3) | 是 | 当前时间 | 创建时间 |
| `updated_at` | DATETIME(3) | 是 | 当前时间 | 更新时间 |

索引：

| 索引名 | 字段 | 说明 |
|---|---|---|
| `uk_permissions_code` | `permission_code` | 权限编码唯一 |

### 表：admin_user_roles

说明：管理员与角色关系。

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `id` | BIGINT UNSIGNED | 是 | 自增 | 主键 |
| `admin_user_id` | BIGINT UNSIGNED | 是 | 无 | 管理员 ID |
| `role_id` | BIGINT UNSIGNED | 是 | 无 | 角色 ID |
| `created_at` | DATETIME(3) | 是 | 当前时间 | 创建时间 |

索引：

| 索引名 | 字段 | 说明 |
|---|---|---|
| `uk_admin_user_role` | `admin_user_id`, `role_id` | 防止重复授权 |

### 表：admin_role_permissions

说明：角色与权限关系。

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `id` | BIGINT UNSIGNED | 是 | 自增 | 主键 |
| `role_id` | BIGINT UNSIGNED | 是 | 无 | 角色 ID |
| `permission_id` | BIGINT UNSIGNED | 是 | 无 | 权限 ID |
| `created_at` | DATETIME(3) | 是 | 当前时间 | 创建时间 |

索引：

| 索引名 | 字段 | 说明 |
|---|---|---|
| `uk_role_permission` | `role_id`, `permission_id` | 防止重复授权 |

### 表：audit_logs

说明：操作日志。重点记录后台查看敏感信息、下载账单、转供应商、修改线索状态等动作。

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---:|---|---|
| `id` | BIGINT UNSIGNED | 是 | 自增 | 日志 ID |
| `actor_type` | VARCHAR(32) | 是 | admin | admin、user、system |
| `actor_id` | BIGINT UNSIGNED | 否 | NULL | 操作人 ID |
| `action` | VARCHAR(128) | 是 | 无 | 操作编码，如 lead.view_sensitive |
| `target_type` | VARCHAR(64) | 否 | NULL | 操作对象类型 |
| `target_id` | BIGINT UNSIGNED | 否 | NULL | 操作对象 ID |
| `ip_address` | VARCHAR(64) | 否 | NULL | IP |
| `user_agent` | VARCHAR(512) | 否 | NULL | 客户端信息 |
| `request_id` | VARCHAR(64) | 否 | NULL | 请求 ID |
| `detail_json` | JSON | 否 | NULL | 操作详情 |
| `created_at` | DATETIME(3) | 是 | 当前时间 | 创建时间 |

索引：

| 索引名 | 字段 | 说明 |
|---|---|---|
| `idx_audit_actor` | `actor_type`, `actor_id`, `created_at` | 操作人审计 |
| `idx_audit_target` | `target_type`, `target_id`, `created_at` | 对象审计 |
| `idx_audit_action` | `action`, `created_at` | 操作类型统计 |

---

## 3. 后台页面与数据表映射

### 3.1 统计概览

| 指标 | 来源表 | 计算方式 |
|---|---|---|
| 总线索数 | `leads` | `COUNT(*)` |
| 今日新增 | `leads` | `created_at >= 今日 00:00` |
| A 类线索 | `leads` | `lead_grade = 'A'` |
| 待跟进 | `leads` | `lead_status = 'pending_followup'` |
| 已转供应商 | `leads` / `supplier_transfers` | `lead_status = 'transferred_supplier'` 或存在转接记录 |
| 转接率 | `leads` | 已转供应商 / 总线索数 |
| 留资转化率 | `leads` | 有手机号授权或初筛提交 / 访问或答题用户 |

### 3.2 线索列表

| UI 字段 | 来源 |
|---|---|
| 企业 / 来源 | `enterprises.name`、`leads.source_entry` |
| 地区 | `enterprises.region_province`、`region_city` |
| 企业类型 | `enterprises.industry_type` |
| 需求方向 | `leads.primary_need_type`、`service_request_items.need_type` |
| 线索等级 | `leads.lead_grade` |
| 状态 | `leads.lead_status` |
| 是否上传账单 | `leads.has_bill_uploaded`、`bill_uploads` |
| 是否授权联系 | `leads.has_phone_authorized` |

### 3.3 线索详情

| 区块 | 来源表 |
|---|---|
| 企业信息 | `enterprises`、`enterprise_contacts` |
| 测评结果 | `questionnaire_submissions`、`questionnaire_result_profiles` |
| 初筛信息 | `screening_requests` |
| 需求信息 | `service_requests`、`service_request_items` |
| 账单资料 | `bill_uploads`、`files` |
| 跟进记录 | `lead_followups` |
| 转供应商记录 | `supplier_transfers`、`suppliers` |
| 备注 | `lead_notes` |
| 操作日志 | `audit_logs` |

### 3.4 操作区

| 操作 | 写入表 | 同步更新 |
|---|---|---|
| 发起跟进 | `lead_followups` | `leads.lead_status = following` |
| 转供应商 | `supplier_transfers` | `leads.lead_status = transferred_supplier` |
| 备注 | `lead_notes` | `leads.last_activity_at` |
| 查看敏感手机号 | `audit_logs` | 不修改业务表 |
| 下载账单 | `audit_logs` | 不修改业务表 |

---
