-- 经营体质测试 v1 评分与星级规则初始化
-- 来源：docs/product/推广、产品、运营一体建设思路.docx 的“二、产品设计”
-- 说明：
-- 1. 现有后端使用 questionnaire_options.score_json 保存选项加分。
-- 2. 星级规则当前在后端代码中计算，本脚本额外写入 result_config_json 与 questionnaire_star_rules，便于后台维护和排查。
-- 3. 脚本可重复执行，会按 business_health/v1 更新题目、选项、画像、评分字典和星级规则。

SET NAMES utf8mb4;
SET time_zone = '+08:00';

CREATE DATABASE IF NOT EXISTS `heaver_energy`
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;

USE `heaver_energy`;

START TRANSACTION;

CREATE TABLE IF NOT EXISTS `questionnaire_sets` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '问卷 ID',
  `code` VARCHAR(64) NOT NULL COMMENT '问卷编码',
  `name` VARCHAR(128) NOT NULL COMMENT '问卷名称',
  `version` VARCHAR(32) NOT NULL DEFAULT 'v1' COMMENT '版本',
  `description` VARCHAR(512) NULL DEFAULT NULL COMMENT '描述',
  `status` VARCHAR(32) NOT NULL DEFAULT 'draft' COMMENT 'draft、published、archived',
  `result_config_json` JSON NULL COMMENT '全局结果配置，如星级区间、线索分级、默认 CTA',
  `published_at` DATETIME(3) NULL DEFAULT NULL COMMENT '发布时间',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间',
  `deleted_at` DATETIME(3) NULL DEFAULT NULL COMMENT '软删除时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_questionnaire_code_version` (`code`, `version`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='测试问卷版本';

CREATE TABLE IF NOT EXISTS `questionnaire_questions` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '题目 ID',
  `questionnaire_id` BIGINT UNSIGNED NOT NULL COMMENT '问卷 ID',
  `question_code` VARCHAR(32) NULL DEFAULT NULL COMMENT '题号编码，如 Q1',
  `title` VARCHAR(256) NOT NULL COMMENT '题目标题',
  `subtitle` VARCHAR(256) NULL DEFAULT NULL COMMENT '题目副标题',
  `dimension_code` VARCHAR(64) NULL DEFAULT NULL COMMENT '主维度提示',
  `question_type` VARCHAR(32) NOT NULL DEFAULT 'single_choice' COMMENT 'single_choice、multiple_choice',
  `score_mode` VARCHAR(32) NOT NULL DEFAULT 'score' COMMENT 'score、tag_only',
  `sort_order` INT NOT NULL DEFAULT 0 COMMENT '排序',
  `is_required` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否必答',
  `status` VARCHAR(32) NOT NULL DEFAULT 'active' COMMENT 'active、disabled',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_questions_questionnaire_sort` (`questionnaire_id`, `sort_order`),
  UNIQUE KEY `uk_questions_questionnaire_code` (`questionnaire_id`, `question_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='问卷题目';

CREATE TABLE IF NOT EXISTS `questionnaire_options` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '选项 ID',
  `question_id` BIGINT UNSIGNED NOT NULL COMMENT '题目 ID',
  `option_label` VARCHAR(8) NULL DEFAULT NULL COMMENT 'A、B、C、D',
  `title` VARCHAR(256) NOT NULL COMMENT '选项文案',
  `subtitle` VARCHAR(256) NULL DEFAULT NULL COMMENT '选项副文案',
  `score_json` JSON NULL COMMENT '各维度加分，如 {"CP": 2, "EP": 3}',
  `tags_json` JSON NULL COMMENT '选项标签和运营含义',
  `profile_bias` VARCHAR(64) NULL DEFAULT NULL COMMENT '倾向画像',
  `sort_order` INT NOT NULL DEFAULT 0 COMMENT '排序',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_options_question_sort` (`question_id`, `sort_order`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='题目选项和评分配置';

CREATE TABLE IF NOT EXISTS `questionnaire_result_profiles` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '画像 ID',
  `questionnaire_id` BIGINT UNSIGNED NOT NULL COMMENT '问卷 ID',
  `profile_code` VARCHAR(64) NOT NULL COMMENT '画像编码',
  `profile_name` VARCHAR(64) NOT NULL COMMENT '画像名称',
  `priority` INT NOT NULL DEFAULT 100 COMMENT '命中优先级，数字越小越靠前',
  `lead_grade_suggestion` VARCHAR(16) NULL DEFAULT NULL COMMENT '默认建议线索等级',
  `theme_color` VARCHAR(32) NULL DEFAULT NULL COMMENT '前端主题色',
  `tags_json` JSON NULL COMMENT '画像标签',
  `summary` VARCHAR(512) NULL DEFAULT NULL COMMENT '结果说明',
  `recommendations_json` JSON NULL COMMENT '建议列表',
  `rule_json` JSON NULL COMMENT '命中规则',
  `result_page_json` JSON NULL COMMENT '结果页文案配置',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_profile_questionnaire_code` (`questionnaire_id`, `profile_code`),
  KEY `idx_profile_questionnaire_priority` (`questionnaire_id`, `priority`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='测试结果画像配置';

CREATE TABLE IF NOT EXISTS `questionnaire_score_dimensions` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `questionnaire_id` BIGINT UNSIGNED NOT NULL COMMENT '问卷 ID',
  `dimension_code` VARCHAR(16) NOT NULL COMMENT '维度编码：CP、MA、SR、EP、AM、LV',
  `dimension_name` VARCHAR(64) NOT NULL COMMENT '维度名称',
  `description` VARCHAR(512) NULL DEFAULT NULL COMMENT '维度说明',
  `high_score_meaning` VARCHAR(512) NULL DEFAULT NULL COMMENT '高分含义',
  `sort_order` INT NOT NULL DEFAULT 0 COMMENT '展示排序',
  `status` VARCHAR(32) NOT NULL DEFAULT 'active' COMMENT 'active、disabled',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_score_dimension_questionnaire_code` (`questionnaire_id`, `dimension_code`),
  KEY `idx_score_dimensions_questionnaire` (`questionnaire_id`, `sort_order`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='问卷评分维度字典';

CREATE TABLE IF NOT EXISTS `questionnaire_star_rules` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `questionnaire_id` BIGINT UNSIGNED NOT NULL COMMENT '问卷 ID',
  `min_score` INT NOT NULL COMMENT '区间最小分，包含',
  `max_score` INT NULL DEFAULT NULL COMMENT '区间最大分，包含；NULL 表示无上限',
  `star_level` INT NOT NULL COMMENT '星级：1-5',
  `display_name` VARCHAR(64) NOT NULL COMMENT '展示文案',
  `description` VARCHAR(256) NULL DEFAULT NULL COMMENT '说明',
  `sort_order` INT NOT NULL DEFAULT 0 COMMENT '排序',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_star_rule_questionnaire_level` (`questionnaire_id`, `star_level`),
  KEY `idx_star_rules_questionnaire_score` (`questionnaire_id`, `min_score`, `max_score`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='问卷分数到星级的换算规则';

CREATE TABLE IF NOT EXISTS `questionnaire_lead_grade_rules` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `questionnaire_id` BIGINT UNSIGNED NOT NULL COMMENT '问卷 ID',
  `grade_code` VARCHAR(16) NOT NULL COMMENT '线索等级 A/B/C/D',
  `grade_name` VARCHAR(64) NOT NULL COMMENT '等级名称',
  `rule_json` JSON NOT NULL COMMENT '线索等级判断规则',
  `operation_action` VARCHAR(512) NULL DEFAULT NULL COMMENT '运营动作',
  `sort_order` INT NOT NULL DEFAULT 0 COMMENT '排序',
  `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `updated_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_lead_grade_questionnaire_code` (`questionnaire_id`, `grade_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='问卷线索分级规则';

SET @col_exists := (
  SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'questionnaire_sets' AND COLUMN_NAME = 'result_config_json'
);
SET @ddl := IF(@col_exists = 0, 'ALTER TABLE `questionnaire_sets` ADD COLUMN `result_config_json` JSON NULL COMMENT ''全局结果配置，如星级区间、线索分级、默认 CTA'' AFTER `status`', 'SELECT 1');
PREPARE stmt FROM @ddl;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @col_exists := (
  SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'questionnaire_questions' AND COLUMN_NAME = 'question_code'
);
SET @ddl := IF(@col_exists = 0, 'ALTER TABLE `questionnaire_questions` ADD COLUMN `question_code` VARCHAR(32) NULL COMMENT ''题号编码，如 Q1'' AFTER `questionnaire_id`', 'SELECT 1');
PREPARE stmt FROM @ddl;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @col_exists := (
  SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'questionnaire_questions' AND COLUMN_NAME = 'score_mode'
);
SET @ddl := IF(@col_exists = 0, 'ALTER TABLE `questionnaire_questions` ADD COLUMN `score_mode` VARCHAR(32) NOT NULL DEFAULT ''score'' COMMENT ''score、tag_only'' AFTER `question_type`', 'SELECT 1');
PREPARE stmt FROM @ddl;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @col_exists := (
  SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'questionnaire_options' AND COLUMN_NAME = 'tags_json'
);
SET @ddl := IF(@col_exists = 0, 'ALTER TABLE `questionnaire_options` ADD COLUMN `tags_json` JSON NULL COMMENT ''选项标签和运营含义'' AFTER `score_json`', 'SELECT 1');
PREPARE stmt FROM @ddl;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @col_exists := (
  SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'questionnaire_result_profiles' AND COLUMN_NAME = 'priority'
);
SET @ddl := IF(@col_exists = 0, 'ALTER TABLE `questionnaire_result_profiles` ADD COLUMN `priority` INT NOT NULL DEFAULT 100 COMMENT ''命中优先级，数字越小越靠前'' AFTER `profile_name`', 'SELECT 1');
PREPARE stmt FROM @ddl;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @col_exists := (
  SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'questionnaire_result_profiles' AND COLUMN_NAME = 'result_page_json'
);
SET @ddl := IF(@col_exists = 0, 'ALTER TABLE `questionnaire_result_profiles` ADD COLUMN `result_page_json` JSON NULL COMMENT ''结果页文案配置'' AFTER `rule_json`', 'SELECT 1');
PREPARE stmt FROM @ddl;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @idx_exists := (
  SELECT COUNT(*) FROM information_schema.STATISTICS
  WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'questionnaire_questions' AND INDEX_NAME = 'uk_questions_questionnaire_code'
);
SET @ddl := IF(@idx_exists = 0, 'CREATE UNIQUE INDEX `uk_questions_questionnaire_code` ON `questionnaire_questions` (`questionnaire_id`, `question_code`)', 'SELECT 1');
PREPARE stmt FROM @ddl;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SET @idx_exists := (
  SELECT COUNT(*) FROM information_schema.STATISTICS
  WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'questionnaire_result_profiles' AND INDEX_NAME = 'idx_profile_questionnaire_priority'
);
SET @ddl := IF(@idx_exists = 0, 'CREATE INDEX `idx_profile_questionnaire_priority` ON `questionnaire_result_profiles` (`questionnaire_id`, `priority`)', 'SELECT 1');
PREPARE stmt FROM @ddl;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

SELECT @questionnaire_id := `id`
FROM `questionnaire_sets`
WHERE `code` = 'business_health' AND `version` = 'v1' AND `deleted_at` IS NULL
ORDER BY `id`
LIMIT 1;

INSERT INTO `questionnaire_sets` (
  `code`, `name`, `version`, `description`, `status`, `published_at`, `created_at`, `updated_at`
)
SELECT
  'business_health',
  '经营体质测试',
  'v1',
  '根据产品设计沉淀的六维评分、画像判断、星级换算与线索分级问卷。',
  'published',
  CURRENT_TIMESTAMP(3),
  CURRENT_TIMESTAMP(3),
  CURRENT_TIMESTAMP(3)
WHERE @questionnaire_id IS NULL;

SELECT @questionnaire_id := `id`
FROM `questionnaire_sets`
WHERE `code` = 'business_health' AND `version` = 'v1' AND `deleted_at` IS NULL
ORDER BY `id`
LIMIT 1;

UPDATE `questionnaire_sets`
SET
  `name` = '经营体质测试',
  `description` = '根据产品设计沉淀的六维评分、画像判断、星级换算与线索分级问卷。',
  `status` = 'published',
  `published_at` = COALESCE(`published_at`, CURRENT_TIMESTAMP(3)),
  `result_config_json` = JSON_OBJECT(
    'source_doc', 'docs/product/推广、产品、运营一体建设思路.docx',
    'score_method', JSON_OBJECT(
      'type', 'option_dimension_additive',
      'description', 'Q1 只打区域标签，不参与计分；Q2-Q10 按选项 score_json 对 CP、MA、SR、EP、AM、LV 六个维度累加。',
      'valid_dimensions', JSON_ARRAY('CP', 'MA', 'SR', 'EP', 'AM', 'LV')
    ),
    'dimensions', JSON_ARRAY(
      JSON_OBJECT('code', 'CP', 'name', '成本压力指数', 'high_score_meaning', '降本诉求明显，优先推成本自查、诊断、初筛。'),
      JSON_OBJECT('code', 'MA', 'name', '管理模糊指数', 'high_score_meaning', '问题不清、路径不清，需要诊断梳理。'),
      JSON_OBJECT('code', 'SR', 'name', '供应商信息差指数', 'high_score_meaning', '存在供应商匹配、报价审核、方案比较机会。'),
      JSON_OBJECT('code', 'EP', 'name', '用能优化潜力指数', 'high_score_meaning', '售电、绿电、光伏、储能、节能、运维等能源机会更强。'),
      JSON_OBJECT('code', 'AM', 'name', '行动成熟度指数', 'high_score_meaning', '决策和联系意愿高，应优先跟进。'),
      JSON_OBJECT('code', 'LV', 'name', '线索价值系数', 'high_score_meaning', '企业规模、类型、区域或项目价值较高，可投入更多人工资源。')
    ),
    'star_rules', JSON_ARRAY(
      JSON_OBJECT('min_score', 0, 'max_score', 2, 'star_level', 1, 'description', '暂时不明显'),
      JSON_OBJECT('min_score', 3, 'max_score', 5, 'star_level', 2, 'description', '存在轻微信号'),
      JSON_OBJECT('min_score', 6, 'max_score', 8, 'star_level', 3, 'description', '值得关注'),
      JSON_OBJECT('min_score', 9, 'max_score', 11, 'star_level', 4, 'description', '比较明显'),
      JSON_OBJECT('min_score', 12, 'max_score', NULL, 'star_level', 5, 'description', '建议优先处理')
    ),
    'profile_match_priority', JSON_ARRAY('hidden_waste', 'energy_awakened', 'supplier_confused', 'cost_sensitive', 'growth_expansion', 'stable_operation'),
    'lead_grade_rules', JSON_ARRAY(
      JSON_OBJECT('grade', 'A', 'name', '高意向', 'condition', 'AM>=8 且 LV>=4', 'action', '7 天内跟进，推动顾问预约。'),
      JSON_OBJECT('grade', 'B', 'name', '近期意向', 'condition', 'AM 5-7 或 LV>=3', 'action', '1 周内联系，推动免费初筛。'),
      JSON_OBJECT('grade', 'C', 'name', '培育型', 'condition', 'AM 2-4', 'action', '进入内容培育序列。'),
      JSON_OBJECT('grade', 'D', 'name', '观望型', 'condition', 'AM 0-1', 'action', '轻触达，推送文章或案例。')
    )
  ),
  `updated_at` = CURRENT_TIMESTAMP(3)
WHERE `id` = @questionnaire_id;

DELETE FROM `questionnaire_score_dimensions` WHERE `questionnaire_id` = @questionnaire_id;
INSERT INTO `questionnaire_score_dimensions` (`questionnaire_id`, `dimension_code`, `dimension_name`, `description`, `high_score_meaning`, `sort_order`)
VALUES
(@questionnaire_id, 'CP', '成本压力指数', '衡量企业对降本、成本压力、成本结构问题的敏感程度。', '降本诉求明显，适合推成本自查、成本诊断和免费初筛。', 1),
(@questionnaire_id, 'MA', '管理模糊指数', '衡量用户是否知道问题在哪里、是否知道优化路径。', '路径不清、问题不清，需要诊断梳理。', 2),
(@questionnaire_id, 'SR', '供应商信息差指数', '衡量供应商选择、报价判断、合同边界等服务需求。', '存在供应商匹配、报价审核、方案比较机会。', 3),
(@questionnaire_id, 'EP', '用能优化潜力指数', '衡量售电、绿电、光伏、储能、节能、运维等能源侧机会。', '能源优化潜力强，适合推荐用能诊断和相关服务。', 4),
(@questionnaire_id, 'AM', '行动成熟度指数', '衡量用户近期行动意愿、决策成熟度和联系意愿。', '应优先人工跟进。', 5),
(@questionnaire_id, 'LV', '线索价值系数', '衡量企业规模、场景、区域与项目潜在价值。', '可投入更多顾问和运营资源。', 6);

DELETE FROM `questionnaire_star_rules` WHERE `questionnaire_id` = @questionnaire_id;
INSERT INTO `questionnaire_star_rules` (`questionnaire_id`, `min_score`, `max_score`, `star_level`, `display_name`, `description`, `sort_order`)
VALUES
(@questionnaire_id, 0, 2, 1, '1 星', '暂时不明显', 1),
(@questionnaire_id, 3, 5, 2, '2 星', '存在轻微信号', 2),
(@questionnaire_id, 6, 8, 3, '3 星', '值得关注', 3),
(@questionnaire_id, 9, 11, 4, '4 星', '比较明显', 4),
(@questionnaire_id, 12, NULL, 5, '5 星', '建议优先处理', 5);

DELETE FROM `questionnaire_lead_grade_rules` WHERE `questionnaire_id` = @questionnaire_id;
INSERT INTO `questionnaire_lead_grade_rules` (`questionnaire_id`, `grade_code`, `grade_name`, `rule_json`, `operation_action`, `sort_order`)
VALUES
(@questionnaire_id, 'A', '高意向', JSON_OBJECT('all', JSON_ARRAY(JSON_OBJECT('dimension', 'AM', 'operator', '>=', 'value', 8), JSON_OBJECT('dimension', 'LV', 'operator', '>=', 'value', 4))), '7 天内跟进，推动顾问预约。', 1),
(@questionnaire_id, 'B', '近期意向', JSON_OBJECT('any', JSON_ARRAY(JSON_OBJECT('dimension', 'AM', 'operator', 'between', 'min', 5, 'max', 7), JSON_OBJECT('dimension', 'LV', 'operator', '>=', 'value', 3))), '1 周内联系，推动免费初筛。', 2),
(@questionnaire_id, 'C', '培育型', JSON_OBJECT('all', JSON_ARRAY(JSON_OBJECT('dimension', 'AM', 'operator', 'between', 'min', 2, 'max', 4))), '进入内容培育序列。', 3),
(@questionnaire_id, 'D', '观望型', JSON_OBJECT('all', JSON_ARRAY(JSON_OBJECT('dimension', 'AM', 'operator', 'between', 'min', 0, 'max', 1))), '轻触达，推送文章或案例。', 4);

UPDATE `questionnaire_questions`
SET `status` = 'disabled', `updated_at` = CURRENT_TIMESTAMP(3)
WHERE `questionnaire_id` = @questionnaire_id
  AND (`question_code` IS NULL OR `question_code` NOT IN ('Q1','Q2','Q3','Q4','Q5','Q6','Q7','Q8','Q9','Q10'));

-- Q1：区域标签题，不参与评分。
UPDATE `questionnaire_questions`
SET `title` = '你的企业主要在哪个区域？', `subtitle` = '用于后续匹配区域政策和顾问资源', `dimension_code` = 'region', `question_type` = 'single_choice', `score_mode` = 'tag_only', `sort_order` = 1, `is_required` = 1, `status` = 'active', `updated_at` = CURRENT_TIMESTAMP(3)
WHERE `questionnaire_id` = @questionnaire_id AND `question_code` = 'Q1';
INSERT INTO `questionnaire_questions` (`questionnaire_id`, `question_code`, `title`, `subtitle`, `dimension_code`, `question_type`, `score_mode`, `sort_order`, `is_required`, `status`)
SELECT @questionnaire_id, 'Q1', '你的企业主要在哪个区域？', '用于后续匹配区域政策和顾问资源', 'region', 'single_choice', 'tag_only', 1, 1, 'active'
WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_questions` WHERE `questionnaire_id` = @questionnaire_id AND `question_code` = 'Q1');
SELECT @q1_id := `id` FROM `questionnaire_questions` WHERE `questionnaire_id` = @questionnaire_id AND `question_code` = 'Q1' LIMIT 1;

UPDATE `questionnaire_options` SET `title` = '华东', `subtitle` = NULL, `score_json` = JSON_OBJECT(), `tags_json` = JSON_OBJECT('region_tag', 'east_china', 'operation_meaning', '匹配华东区域售电、绿电、光伏政策和服务商资源'), `profile_bias` = NULL, `sort_order` = 1, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q1_id AND `option_label` = 'A';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `sort_order`) SELECT @q1_id, 'A', '华东', JSON_OBJECT(), JSON_OBJECT('region_tag', 'east_china', 'operation_meaning', '匹配华东区域售电、绿电、光伏政策和服务商资源'), 1 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q1_id AND `option_label` = 'A');
UPDATE `questionnaire_options` SET `title` = '华南', `subtitle` = NULL, `score_json` = JSON_OBJECT(), `tags_json` = JSON_OBJECT('region_tag', 'south_china', 'operation_meaning', '匹配华南区域能源服务资源'), `profile_bias` = NULL, `sort_order` = 2, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q1_id AND `option_label` = 'B';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `sort_order`) SELECT @q1_id, 'B', '华南', JSON_OBJECT(), JSON_OBJECT('region_tag', 'south_china', 'operation_meaning', '匹配华南区域能源服务资源'), 2 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q1_id AND `option_label` = 'B');
UPDATE `questionnaire_options` SET `title` = '华北 / 西北', `subtitle` = NULL, `score_json` = JSON_OBJECT(), `tags_json` = JSON_OBJECT('region_tag', 'north_northwest', 'operation_meaning', '匹配华北和西北区域政策、绿电及售电资源'), `profile_bias` = NULL, `sort_order` = 3, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q1_id AND `option_label` = 'C';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `sort_order`) SELECT @q1_id, 'C', '华北 / 西北', JSON_OBJECT(), JSON_OBJECT('region_tag', 'north_northwest', 'operation_meaning', '匹配华北和西北区域政策、绿电及售电资源'), 3 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q1_id AND `option_label` = 'C');
UPDATE `questionnaire_options` SET `title` = '其他区域', `subtitle` = NULL, `score_json` = JSON_OBJECT(), `tags_json` = JSON_OBJECT('region_tag', 'other', 'operation_meaning', '进入通用顾问分配池'), `profile_bias` = NULL, `sort_order` = 4, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q1_id AND `option_label` = 'D';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `sort_order`) SELECT @q1_id, 'D', '其他区域', JSON_OBJECT(), JSON_OBJECT('region_tag', 'other', 'operation_meaning', '进入通用顾问分配池'), 4 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q1_id AND `option_label` = 'D');

-- Q2：月用电量。
UPDATE `questionnaire_questions` SET `title` = '你的企业每月大概用多少电？', `subtitle` = '用于判断用能优化潜力和线索价值', `dimension_code` = 'EP_LV', `question_type` = 'single_choice', `score_mode` = 'score', `sort_order` = 2, `is_required` = 1, `status` = 'active', `updated_at` = CURRENT_TIMESTAMP(3) WHERE `questionnaire_id` = @questionnaire_id AND `question_code` = 'Q2';
INSERT INTO `questionnaire_questions` (`questionnaire_id`, `question_code`, `title`, `subtitle`, `dimension_code`, `question_type`, `score_mode`, `sort_order`, `is_required`, `status`) SELECT @questionnaire_id, 'Q2', '你的企业每月大概用多少电？', '用于判断用能优化潜力和线索价值', 'EP_LV', 'single_choice', 'score', 2, 1, 'active' WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_questions` WHERE `questionnaire_id` = @questionnaire_id AND `question_code` = 'Q2');
SELECT @q2_id := `id` FROM `questionnaire_questions` WHERE `questionnaire_id` = @questionnaire_id AND `question_code` = 'Q2' LIMIT 1;

UPDATE `questionnaire_options` SET `title` = '1 万度以下', `score_json` = JSON_OBJECT('EP', 1, 'LV', 1), `tags_json` = JSON_OBJECT('monthly_kwh_range', 'lt_10000', 'scale_tag', 'small'), `profile_bias` = NULL, `sort_order` = 1, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q2_id AND `option_label` = 'A';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `sort_order`) SELECT @q2_id, 'A', '1 万度以下', JSON_OBJECT('EP', 1, 'LV', 1), JSON_OBJECT('monthly_kwh_range', 'lt_10000', 'scale_tag', 'small'), 1 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q2_id AND `option_label` = 'A');
UPDATE `questionnaire_options` SET `title` = '1 万～5 万度', `score_json` = JSON_OBJECT('EP', 2, 'LV', 2), `tags_json` = JSON_OBJECT('monthly_kwh_range', '10000_50000', 'scale_tag', 'medium'), `profile_bias` = NULL, `sort_order` = 2, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q2_id AND `option_label` = 'B';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `sort_order`) SELECT @q2_id, 'B', '1 万～5 万度', JSON_OBJECT('EP', 2, 'LV', 2), JSON_OBJECT('monthly_kwh_range', '10000_50000', 'scale_tag', 'medium'), 2 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q2_id AND `option_label` = 'B');
UPDATE `questionnaire_options` SET `title` = '5 万～20 万度', `score_json` = JSON_OBJECT('EP', 3, 'LV', 3), `tags_json` = JSON_OBJECT('monthly_kwh_range', '50000_200000', 'scale_tag', 'high_value'), `profile_bias` = 'energy_awakened', `sort_order` = 3, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q2_id AND `option_label` = 'C';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `profile_bias`, `sort_order`) SELECT @q2_id, 'C', '5 万～20 万度', JSON_OBJECT('EP', 3, 'LV', 3), JSON_OBJECT('monthly_kwh_range', '50000_200000', 'scale_tag', 'high_value'), 'energy_awakened', 3 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q2_id AND `option_label` = 'C');
UPDATE `questionnaire_options` SET `title` = '20 万度以上', `score_json` = JSON_OBJECT('EP', 4, 'LV', 4), `tags_json` = JSON_OBJECT('monthly_kwh_range', 'gt_200000', 'scale_tag', 'high_value'), `profile_bias` = 'energy_awakened', `sort_order` = 4, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q2_id AND `option_label` = 'D';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `profile_bias`, `sort_order`) SELECT @q2_id, 'D', '20 万度以上', JSON_OBJECT('EP', 4, 'LV', 4), JSON_OBJECT('monthly_kwh_range', 'gt_200000', 'scale_tag', 'high_value'), 'energy_awakened', 4 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q2_id AND `option_label` = 'D');

-- Q3：企业场景。
UPDATE `questionnaire_questions` SET `title` = '你的企业主要属于哪类经营场景？', `subtitle` = '用于判断行业场景和能源服务机会', `dimension_code` = 'EP_LV', `question_type` = 'single_choice', `score_mode` = 'score', `sort_order` = 3, `is_required` = 1, `status` = 'active', `updated_at` = CURRENT_TIMESTAMP(3) WHERE `questionnaire_id` = @questionnaire_id AND `question_code` = 'Q3';
INSERT INTO `questionnaire_questions` (`questionnaire_id`, `question_code`, `title`, `subtitle`, `dimension_code`, `question_type`, `score_mode`, `sort_order`, `is_required`, `status`) SELECT @questionnaire_id, 'Q3', '你的企业主要属于哪类经营场景？', '用于判断行业场景和能源服务机会', 'EP_LV', 'single_choice', 'score', 3, 1, 'active' WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_questions` WHERE `questionnaire_id` = @questionnaire_id AND `question_code` = 'Q3');
SELECT @q3_id := `id` FROM `questionnaire_questions` WHERE `questionnaire_id` = @questionnaire_id AND `question_code` = 'Q3' LIMIT 1;

UPDATE `questionnaire_options` SET `title` = '门店 / 餐饮 / 零售 / 办公', `score_json` = JSON_OBJECT('LV', 1, 'EP', 1), `tags_json` = JSON_OBJECT('enterprise_scene', 'store_retail_office'), `profile_bias` = NULL, `sort_order` = 1, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q3_id AND `option_label` = 'A';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `sort_order`) SELECT @q3_id, 'A', '门店 / 餐饮 / 零售 / 办公', JSON_OBJECT('LV', 1, 'EP', 1), JSON_OBJECT('enterprise_scene', 'store_retail_office'), 1 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q3_id AND `option_label` = 'A');
UPDATE `questionnaire_options` SET `title` = '工厂 / 生产制造', `score_json` = JSON_OBJECT('LV', 3, 'EP', 3), `tags_json` = JSON_OBJECT('enterprise_scene', 'factory_manufacturing'), `profile_bias` = 'energy_awakened', `sort_order` = 2, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q3_id AND `option_label` = 'B';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `profile_bias`, `sort_order`) SELECT @q3_id, 'B', '工厂 / 生产制造', JSON_OBJECT('LV', 3, 'EP', 3), JSON_OBJECT('enterprise_scene', 'factory_manufacturing'), 'energy_awakened', 2 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q3_id AND `option_label` = 'B');
UPDATE `questionnaire_options` SET `title` = '仓储 / 物流 / 酒店 / 商业体', `score_json` = JSON_OBJECT('LV', 2, 'EP', 2), `tags_json` = JSON_OBJECT('enterprise_scene', 'warehouse_hotel_commerce'), `profile_bias` = NULL, `sort_order` = 3, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q3_id AND `option_label` = 'C';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `sort_order`) SELECT @q3_id, 'C', '仓储 / 物流 / 酒店 / 商业体', JSON_OBJECT('LV', 2, 'EP', 2), JSON_OBJECT('enterprise_scene', 'warehouse_hotel_commerce'), 3 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q3_id AND `option_label` = 'C');
UPDATE `questionnaire_options` SET `title` = '园区企业 / 多业态经营', `score_json` = JSON_OBJECT('LV', 3, 'EP', 3), `tags_json` = JSON_OBJECT('enterprise_scene', 'park_multi_business', 'profile_tags', JSON_ARRAY('growth_expansion')), `profile_bias` = 'growth_expansion', `sort_order` = 4, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q3_id AND `option_label` = 'D';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `profile_bias`, `sort_order`) SELECT @q3_id, 'D', '园区企业 / 多业态经营', JSON_OBJECT('LV', 3, 'EP', 3), JSON_OBJECT('enterprise_scene', 'park_multi_business', 'profile_tags', JSON_ARRAY('growth_expansion')), 'growth_expansion', 4 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q3_id AND `option_label` = 'D');

-- Q4：经营感受。
UPDATE `questionnaire_questions` SET `title` = '最近一年，你对企业经营成本的感受更接近哪一种？', `subtitle` = '用于判断成本压力、管理模糊和行动意愿', `dimension_code` = 'CP_MA_AM', `question_type` = 'single_choice', `score_mode` = 'score', `sort_order` = 4, `is_required` = 1, `status` = 'active', `updated_at` = CURRENT_TIMESTAMP(3) WHERE `questionnaire_id` = @questionnaire_id AND `question_code` = 'Q4';
INSERT INTO `questionnaire_questions` (`questionnaire_id`, `question_code`, `title`, `subtitle`, `dimension_code`, `question_type`, `score_mode`, `sort_order`, `is_required`, `status`) SELECT @questionnaire_id, 'Q4', '最近一年，你对企业经营成本的感受更接近哪一种？', '用于判断成本压力、管理模糊和行动意愿', 'CP_MA_AM', 'single_choice', 'score', 4, 1, 'active' WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_questions` WHERE `questionnaire_id` = @questionnaire_id AND `question_code` = 'Q4');
SELECT @q4_id := `id` FROM `questionnaire_questions` WHERE `questionnaire_id` = @questionnaire_id AND `question_code` = 'Q4' LIMIT 1;

UPDATE `questionnaire_options` SET `title` = '生意整体还稳定，但水电、人力、租金这些固定成本压力越来越大', `score_json` = JSON_OBJECT('CP', 3, 'AM', 1), `tags_json` = JSON_OBJECT('cost_feeling', 'stable_but_fixed_cost_pressure'), `profile_bias` = 'cost_sensitive', `sort_order` = 1, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q4_id AND `option_label` = 'A';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `profile_bias`, `sort_order`) SELECT @q4_id, 'A', '生意整体还稳定，但水电、人力、租金这些固定成本压力越来越大', JSON_OBJECT('CP', 3, 'AM', 1), JSON_OBJECT('cost_feeling', 'stable_but_fixed_cost_pressure'), 'cost_sensitive', 1 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q4_id AND `option_label` = 'A');
UPDATE `questionnaire_options` SET `title` = '订单或门店在增长，但感觉成本也跟着涨得很快', `score_json` = JSON_OBJECT('CP', 2, 'MA', 1), `tags_json` = JSON_OBJECT('cost_feeling', 'growth_cost_rising', 'profile_tags', JSON_ARRAY('growth_expansion')), `profile_bias` = 'growth_expansion', `sort_order` = 2, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q4_id AND `option_label` = 'B';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `profile_bias`, `sort_order`) SELECT @q4_id, 'B', '订单或门店在增长，但感觉成本也跟着涨得很快', JSON_OBJECT('CP', 2, 'MA', 1), JSON_OBJECT('cost_feeling', 'growth_cost_rising', 'profile_tags', JSON_ARRAY('growth_expansion')), 'growth_expansion', 2 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q4_id AND `option_label` = 'B');
UPDATE `questionnaire_options` SET `title` = '感觉有些钱在悄悄漏掉，但说不清漏在哪里', `score_json` = JSON_OBJECT('CP', 2, 'MA', 4), `tags_json` = JSON_OBJECT('cost_feeling', 'unclear_leakage', 'profile_tags', JSON_ARRAY('hidden_waste')), `profile_bias` = 'hidden_waste', `sort_order` = 3, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q4_id AND `option_label` = 'C';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `profile_bias`, `sort_order`) SELECT @q4_id, 'C', '感觉有些钱在悄悄漏掉，但说不清漏在哪里', JSON_OBJECT('CP', 2, 'MA', 4), JSON_OBJECT('cost_feeling', 'unclear_leakage', 'profile_tags', JSON_ARRAY('hidden_waste')), 'hidden_waste', 3 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q4_id AND `option_label` = 'C');
UPDATE `questionnaire_options` SET `title` = '目前还好，只是想提前看看有没有优化空间', `score_json` = JSON_OBJECT('AM', 1), `tags_json` = JSON_OBJECT('cost_feeling', 'proactive_check'), `profile_bias` = 'stable_operation', `sort_order` = 4, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q4_id AND `option_label` = 'D';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `profile_bias`, `sort_order`) SELECT @q4_id, 'D', '目前还好，只是想提前看看有没有优化空间', JSON_OBJECT('AM', 1), JSON_OBJECT('cost_feeling', 'proactive_check'), 'stable_operation', 4 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q4_id AND `option_label` = 'D');

-- Q5：漏钱线索。
UPDATE `questionnaire_questions` SET `title` = '如果说企业可能有“漏钱”的地方，你第一反应是哪一块？', `subtitle` = '用于识别主要需求线索', `dimension_code` = 'CP_EP_SR_MA', `question_type` = 'single_choice', `score_mode` = 'score', `sort_order` = 5, `is_required` = 1, `status` = 'active', `updated_at` = CURRENT_TIMESTAMP(3) WHERE `questionnaire_id` = @questionnaire_id AND `question_code` = 'Q5';
INSERT INTO `questionnaire_questions` (`questionnaire_id`, `question_code`, `title`, `subtitle`, `dimension_code`, `question_type`, `score_mode`, `sort_order`, `is_required`, `status`) SELECT @questionnaire_id, 'Q5', '如果说企业可能有“漏钱”的地方，你第一反应是哪一块？', '用于识别主要需求线索', 'CP_EP_SR_MA', 'single_choice', 'score', 5, 1, 'active' WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_questions` WHERE `questionnaire_id` = @questionnaire_id AND `question_code` = 'Q5');
SELECT @q5_id := `id` FROM `questionnaire_questions` WHERE `questionnaire_id` = @questionnaire_id AND `question_code` = 'Q5' LIMIT 1;

UPDATE `questionnaire_options` SET `title` = '水电、能耗、设备运行成本', `score_json` = JSON_OBJECT('CP', 2, 'EP', 2), `tags_json` = JSON_OBJECT('need_types', JSON_ARRAY('use_energy'), 'need_tags', JSON_ARRAY('energy_cost')), `profile_bias` = 'energy_awakened', `sort_order` = 1, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q5_id AND `option_label` = 'A';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `profile_bias`, `sort_order`) SELECT @q5_id, 'A', '水电、能耗、设备运行成本', JSON_OBJECT('CP', 2, 'EP', 2), JSON_OBJECT('need_types', JSON_ARRAY('use_energy'), 'need_tags', JSON_ARRAY('energy_cost')), 'energy_awakened', 1 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q5_id AND `option_label` = 'A');
UPDATE `questionnaire_options` SET `title` = '租金、人力、物业等固定成本', `score_json` = JSON_OBJECT('CP', 2), `tags_json` = JSON_OBJECT('need_tags', JSON_ARRAY('fixed_cost')), `profile_bias` = 'cost_sensitive', `sort_order` = 2, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q5_id AND `option_label` = 'B';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `profile_bias`, `sort_order`) SELECT @q5_id, 'B', '租金、人力、物业等固定成本', JSON_OBJECT('CP', 2), JSON_OBJECT('need_tags', JSON_ARRAY('fixed_cost')), 'cost_sensitive', 2 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q5_id AND `option_label` = 'B');
UPDATE `questionnaire_options` SET `title` = '采购、外包、供应商服务费用', `score_json` = JSON_OBJECT('CP', 2, 'SR', 3), `tags_json` = JSON_OBJECT('need_types', JSON_ARRAY('quote_review', 'supplier_screening'), 'need_tags', JSON_ARRAY('supplier_cost')), `profile_bias` = 'supplier_confused', `sort_order` = 3, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q5_id AND `option_label` = 'C';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `profile_bias`, `sort_order`) SELECT @q5_id, 'C', '采购、外包、供应商服务费用', JSON_OBJECT('CP', 2, 'SR', 3), JSON_OBJECT('need_types', JSON_ARRAY('quote_review', 'supplier_screening'), 'need_tags', JSON_ARRAY('supplier_cost')), 'supplier_confused', 3 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q5_id AND `option_label` = 'C');
UPDATE `questionnaire_options` SET `title` = '说不清，整体感觉成本结构不透明', `score_json` = JSON_OBJECT('CP', 2, 'MA', 3), `tags_json` = JSON_OBJECT('need_tags', JSON_ARRAY('unclear_cost_structure'), 'profile_tags', JSON_ARRAY('hidden_waste')), `profile_bias` = 'hidden_waste', `sort_order` = 4, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q5_id AND `option_label` = 'D';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `profile_bias`, `sort_order`) SELECT @q5_id, 'D', '说不清，整体感觉成本结构不透明', JSON_OBJECT('CP', 2, 'MA', 3), JSON_OBJECT('need_tags', JSON_ARRAY('unclear_cost_structure'), 'profile_tags', JSON_ARRAY('hidden_waste')), 'hidden_waste', 4 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q5_id AND `option_label` = 'D');

-- Q6：过去一年降本情况。
UPDATE `questionnaire_questions` SET `title` = '过去一年，你们有没有系统做过降本或经营优化？', `subtitle` = '用于判断行动成熟度和管理模糊度', `dimension_code` = 'CP_MA_AM', `question_type` = 'single_choice', `score_mode` = 'score', `sort_order` = 6, `is_required` = 1, `status` = 'active', `updated_at` = CURRENT_TIMESTAMP(3) WHERE `questionnaire_id` = @questionnaire_id AND `question_code` = 'Q6';
INSERT INTO `questionnaire_questions` (`questionnaire_id`, `question_code`, `title`, `subtitle`, `dimension_code`, `question_type`, `score_mode`, `sort_order`, `is_required`, `status`) SELECT @questionnaire_id, 'Q6', '过去一年，你们有没有系统做过降本或经营优化？', '用于判断行动成熟度和管理模糊度', 'CP_MA_AM', 'single_choice', 'score', 6, 1, 'active' WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_questions` WHERE `questionnaire_id` = @questionnaire_id AND `question_code` = 'Q6');
SELECT @q6_id := `id` FROM `questionnaire_questions` WHERE `questionnaire_id` = @questionnaire_id AND `question_code` = 'Q6' LIMIT 1;

UPDATE `questionnaire_options` SET `title` = '已经做过不少，效果还可以', `score_json` = JSON_OBJECT('AM', 1), `tags_json` = JSON_OBJECT('cost_reduction_history', 'done_well'), `profile_bias` = 'stable_operation', `sort_order` = 1, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q6_id AND `option_label` = 'A';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `profile_bias`, `sort_order`) SELECT @q6_id, 'A', '已经做过不少，效果还可以', JSON_OBJECT('AM', 1), JSON_OBJECT('cost_reduction_history', 'done_well'), 'stable_operation', 1 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q6_id AND `option_label` = 'A');
UPDATE `questionnaire_options` SET `title` = '做过一些，但不知道有没有真正降下来', `score_json` = JSON_OBJECT('CP', 1, 'MA', 2), `tags_json` = JSON_OBJECT('cost_reduction_history', 'done_but_unclear'), `profile_bias` = 'hidden_waste', `sort_order` = 2, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q6_id AND `option_label` = 'B';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `profile_bias`, `sort_order`) SELECT @q6_id, 'B', '做过一些，但不知道有没有真正降下来', JSON_OBJECT('CP', 1, 'MA', 2), JSON_OBJECT('cost_reduction_history', 'done_but_unclear'), 'hidden_waste', 2 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q6_id AND `option_label` = 'B');
UPDATE `questionnaire_options` SET `title` = '想做，但不知道从哪里开始', `score_json` = JSON_OBJECT('CP', 1, 'MA', 4), `tags_json` = JSON_OBJECT('cost_reduction_history', 'want_but_no_path', 'profile_tags', JSON_ARRAY('hidden_waste')), `profile_bias` = 'hidden_waste', `sort_order` = 3, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q6_id AND `option_label` = 'C';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `profile_bias`, `sort_order`) SELECT @q6_id, 'C', '想做，但不知道从哪里开始', JSON_OBJECT('CP', 1, 'MA', 4), JSON_OBJECT('cost_reduction_history', 'want_but_no_path', 'profile_tags', JSON_ARRAY('hidden_waste')), 'hidden_waste', 3 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q6_id AND `option_label` = 'C');
UPDATE `questionnaire_options` SET `title` = '压力已经比较明显，近期必须想办法', `score_json` = JSON_OBJECT('CP', 4, 'AM', 4), `tags_json` = JSON_OBJECT('cost_reduction_history', 'urgent_pressure'), `profile_bias` = 'cost_sensitive', `sort_order` = 4, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q6_id AND `option_label` = 'D';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `profile_bias`, `sort_order`) SELECT @q6_id, 'D', '压力已经比较明显，近期必须想办法', JSON_OBJECT('CP', 4, 'AM', 4), JSON_OBJECT('cost_reduction_history', 'urgent_pressure'), 'cost_sensitive', 4 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q6_id AND `option_label` = 'D');

-- Q7：供应商寻找方式。
UPDATE `questionnaire_questions` SET `title` = '你们平时找供应商或服务商，通常更接近哪种方式？', `subtitle` = '用于判断供应商信息差和行动成熟度', `dimension_code` = 'SR_MA_AM', `question_type` = 'single_choice', `score_mode` = 'score', `sort_order` = 7, `is_required` = 1, `status` = 'active', `updated_at` = CURRENT_TIMESTAMP(3) WHERE `questionnaire_id` = @questionnaire_id AND `question_code` = 'Q7';
INSERT INTO `questionnaire_questions` (`questionnaire_id`, `question_code`, `title`, `subtitle`, `dimension_code`, `question_type`, `score_mode`, `sort_order`, `is_required`, `status`) SELECT @questionnaire_id, 'Q7', '你们平时找供应商或服务商，通常更接近哪种方式？', '用于判断供应商信息差和行动成熟度', 'SR_MA_AM', 'single_choice', 'score', 7, 1, 'active' WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_questions` WHERE `questionnaire_id` = @questionnaire_id AND `question_code` = 'Q7');
SELECT @q7_id := `id` FROM `questionnaire_questions` WHERE `questionnaire_id` = @questionnaire_id AND `question_code` = 'Q7' LIMIT 1;

UPDATE `questionnaire_options` SET `title` = '主要靠朋友介绍或熟人推荐', `score_json` = JSON_OBJECT('SR', 3, 'MA', 1), `tags_json` = JSON_OBJECT('supplier_search', 'friend_referral'), `profile_bias` = 'supplier_confused', `sort_order` = 1, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q7_id AND `option_label` = 'A';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `profile_bias`, `sort_order`) SELECT @q7_id, 'A', '主要靠朋友介绍或熟人推荐', JSON_OBJECT('SR', 3, 'MA', 1), JSON_OBJECT('supplier_search', 'friend_referral'), 'supplier_confused', 1 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q7_id AND `option_label` = 'A');
UPDATE `questionnaire_options` SET `title` = '会比价，但很多报价看不太懂', `score_json` = JSON_OBJECT('SR', 4, 'AM', 2), `tags_json` = JSON_OBJECT('supplier_search', 'compare_but_unclear', 'need_types', JSON_ARRAY('quote_review')), `profile_bias` = 'supplier_confused', `sort_order` = 2, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q7_id AND `option_label` = 'B';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `profile_bias`, `sort_order`) SELECT @q7_id, 'B', '会比价，但很多报价看不太懂', JSON_OBJECT('SR', 4, 'AM', 2), JSON_OBJECT('supplier_search', 'compare_but_unclear', 'need_types', JSON_ARRAY('quote_review')), 'supplier_confused', 2 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q7_id AND `option_label` = 'B');
UPDATE `questionnaire_options` SET `title` = '有固定供应商，但很少复盘是否合适', `score_json` = JSON_OBJECT('SR', 3, 'AM', 2), `tags_json` = JSON_OBJECT('supplier_search', 'fixed_supplier_no_review'), `profile_bias` = 'supplier_confused', `sort_order` = 3, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q7_id AND `option_label` = 'C';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `profile_bias`, `sort_order`) SELECT @q7_id, 'C', '有固定供应商，但很少复盘是否合适', JSON_OBJECT('SR', 3, 'AM', 2), JSON_OBJECT('supplier_search', 'fixed_supplier_no_review'), 'supplier_confused', 3 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q7_id AND `option_label` = 'C');
UPDATE `questionnaire_options` SET `title` = '正在找新的供应商或替代方案', `score_json` = JSON_OBJECT('SR', 4, 'AM', 4), `tags_json` = JSON_OBJECT('supplier_search', 'looking_for_new_supplier', 'need_types', JSON_ARRAY('supplier_recommendation')), `profile_bias` = 'supplier_confused', `sort_order` = 4, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q7_id AND `option_label` = 'D';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `profile_bias`, `sort_order`) SELECT @q7_id, 'D', '正在找新的供应商或替代方案', JSON_OBJECT('SR', 4, 'AM', 4), JSON_OBJECT('supplier_search', 'looking_for_new_supplier', 'need_types', JSON_ARRAY('supplier_recommendation')), 'supplier_confused', 4 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q7_id AND `option_label` = 'D');

-- Q8：供应商帮助方式。
UPDATE `questionnaire_questions` SET `title` = '如果有第三方能帮你看供应商，你最希望解决什么？', `subtitle` = '用于识别供应商侧具体服务需求', `dimension_code` = 'SR_AM', `question_type` = 'single_choice', `score_mode` = 'score', `sort_order` = 8, `is_required` = 1, `status` = 'active', `updated_at` = CURRENT_TIMESTAMP(3) WHERE `questionnaire_id` = @questionnaire_id AND `question_code` = 'Q8';
INSERT INTO `questionnaire_questions` (`questionnaire_id`, `question_code`, `title`, `subtitle`, `dimension_code`, `question_type`, `score_mode`, `sort_order`, `is_required`, `status`) SELECT @questionnaire_id, 'Q8', '如果有第三方能帮你看供应商，你最希望解决什么？', '用于识别供应商侧具体服务需求', 'SR_AM', 'single_choice', 'score', 8, 1, 'active' WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_questions` WHERE `questionnaire_id` = @questionnaire_id AND `question_code` = 'Q8');
SELECT @q8_id := `id` FROM `questionnaire_questions` WHERE `questionnaire_id` = @questionnaire_id AND `question_code` = 'Q8' LIMIT 1;

UPDATE `questionnaire_options` SET `title` = '推荐靠谱供应商', `score_json` = JSON_OBJECT('SR', 3, 'AM', 3), `tags_json` = JSON_OBJECT('need_types', JSON_ARRAY('supplier_recommendation'), 'need_tags', JSON_ARRAY('supplier_match')), `profile_bias` = 'supplier_confused', `sort_order` = 1, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q8_id AND `option_label` = 'A';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `profile_bias`, `sort_order`) SELECT @q8_id, 'A', '推荐靠谱供应商', JSON_OBJECT('SR', 3, 'AM', 3), JSON_OBJECT('need_types', JSON_ARRAY('supplier_recommendation'), 'need_tags', JSON_ARRAY('supplier_match')), 'supplier_confused', 1 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q8_id AND `option_label` = 'A');
UPDATE `questionnaire_options` SET `title` = '帮我判断报价是否合理', `score_json` = JSON_OBJECT('SR', 4, 'AM', 3), `tags_json` = JSON_OBJECT('need_types', JSON_ARRAY('quote_review'), 'need_tags', JSON_ARRAY('quote_review')), `profile_bias` = 'supplier_confused', `sort_order` = 2, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q8_id AND `option_label` = 'B';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `profile_bias`, `sort_order`) SELECT @q8_id, 'B', '帮我判断报价是否合理', JSON_OBJECT('SR', 4, 'AM', 3), JSON_OBJECT('need_types', JSON_ARRAY('quote_review'), 'need_tags', JSON_ARRAY('quote_review')), 'supplier_confused', 2 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q8_id AND `option_label` = 'B');
UPDATE `questionnaire_options` SET `title` = '帮我筛掉不靠谱供应商', `score_json` = JSON_OBJECT('SR', 3, 'AM', 2), `tags_json` = JSON_OBJECT('need_types', JSON_ARRAY('supplier_screening'), 'need_tags', JSON_ARRAY('supplier_screening')), `profile_bias` = 'supplier_confused', `sort_order` = 3, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q8_id AND `option_label` = 'C';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `profile_bias`, `sort_order`) SELECT @q8_id, 'C', '帮我筛掉不靠谱供应商', JSON_OBJECT('SR', 3, 'AM', 2), JSON_OBJECT('need_types', JSON_ARRAY('supplier_screening'), 'need_tags', JSON_ARRAY('supplier_screening')), 'supplier_confused', 3 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q8_id AND `option_label` = 'C');
UPDATE `questionnaire_options` SET `title` = '帮我看合同和服务边界', `score_json` = JSON_OBJECT('SR', 3, 'AM', 2), `tags_json` = JSON_OBJECT('need_types', JSON_ARRAY('contract_review'), 'need_tags', JSON_ARRAY('contract_boundary')), `profile_bias` = 'supplier_confused', `sort_order` = 4, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q8_id AND `option_label` = 'D';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `profile_bias`, `sort_order`) SELECT @q8_id, 'D', '帮我看合同和服务边界', JSON_OBJECT('SR', 3, 'AM', 2), JSON_OBJECT('need_types', JSON_ARRAY('contract_review'), 'need_tags', JSON_ARRAY('contract_boundary')), 'supplier_confused', 4 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q8_id AND `option_label` = 'D');

-- Q9：用能现状。
UPDATE `questionnaire_questions` SET `title` = '关于电费和用能，你现在更像哪一种情况？', `subtitle` = '用于判断用能优化潜力', `dimension_code` = 'EP_CP_AM', `question_type` = 'single_choice', `score_mode` = 'score', `sort_order` = 9, `is_required` = 1, `status` = 'active', `updated_at` = CURRENT_TIMESTAMP(3) WHERE `questionnaire_id` = @questionnaire_id AND `question_code` = 'Q9';
INSERT INTO `questionnaire_questions` (`questionnaire_id`, `question_code`, `title`, `subtitle`, `dimension_code`, `question_type`, `score_mode`, `sort_order`, `is_required`, `status`) SELECT @questionnaire_id, 'Q9', '关于电费和用能，你现在更像哪一种情况？', '用于判断用能优化潜力', 'EP_CP_AM', 'single_choice', 'score', 9, 1, 'active' WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_questions` WHERE `questionnaire_id` = @questionnaire_id AND `question_code` = 'Q9');
SELECT @q9_id := `id` FROM `questionnaire_questions` WHERE `questionnaire_id` = @questionnaire_id AND `question_code` = 'Q9' LIMIT 1;

UPDATE `questionnaire_options` SET `title` = '电费不低，但平时没人专门分析', `score_json` = JSON_OBJECT('EP', 4, 'CP', 2, 'AM', 2), `tags_json` = JSON_OBJECT('energy_status', 'high_bill_no_analysis', 'need_types', JSON_ARRAY('use_energy')), `profile_bias` = 'energy_awakened', `sort_order` = 1, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q9_id AND `option_label` = 'A';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `profile_bias`, `sort_order`) SELECT @q9_id, 'A', '电费不低，但平时没人专门分析', JSON_OBJECT('EP', 4, 'CP', 2, 'AM', 2), JSON_OBJECT('energy_status', 'high_bill_no_analysis', 'need_types', JSON_ARRAY('use_energy')), 'energy_awakened', 1 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q9_id AND `option_label` = 'A');
UPDATE `questionnaire_options` SET `title` = '听过光伏、售电、储能等，但不确定适不适合', `score_json` = JSON_OBJECT('EP', 3, 'AM', 1), `tags_json` = JSON_OBJECT('energy_status', 'heard_but_uncertain', 'need_types', JSON_ARRAY('green_power', 'solar_storage')), `profile_bias` = 'energy_awakened', `sort_order` = 2, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q9_id AND `option_label` = 'B';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `profile_bias`, `sort_order`) SELECT @q9_id, 'B', '听过光伏、售电、储能等，但不确定适不适合', JSON_OBJECT('EP', 3, 'AM', 1), JSON_OBJECT('energy_status', 'heard_but_uncertain', 'need_types', JSON_ARRAY('green_power', 'solar_storage')), 'energy_awakened', 2 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q9_id AND `option_label` = 'B');
UPDATE `questionnaire_options` SET `title` = '已经做过一些优化，还想看看是否有空间', `score_json` = JSON_OBJECT('EP', 3, 'AM', 3), `tags_json` = JSON_OBJECT('energy_status', 'optimized_but_wants_more', 'need_types', JSON_ARRAY('energy_consulting')), `profile_bias` = 'energy_awakened', `sort_order` = 3, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q9_id AND `option_label` = 'C';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `profile_bias`, `sort_order`) SELECT @q9_id, 'C', '已经做过一些优化，还想看看是否有空间', JSON_OBJECT('EP', 3, 'AM', 3), JSON_OBJECT('energy_status', 'optimized_but_wants_more', 'need_types', JSON_ARRAY('energy_consulting')), 'energy_awakened', 3 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q9_id AND `option_label` = 'C');
UPDATE `questionnaire_options` SET `title` = '目前用能不是重点问题', `score_json` = JSON_OBJECT('EP', 0), `tags_json` = JSON_OBJECT('energy_status', 'not_focus'), `profile_bias` = 'stable_operation', `sort_order` = 4, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q9_id AND `option_label` = 'D';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `profile_bias`, `sort_order`) SELECT @q9_id, 'D', '目前用能不是重点问题', JSON_OBJECT('EP', 0), JSON_OBJECT('energy_status', 'not_focus'), 'stable_operation', 4 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q9_id AND `option_label` = 'D');

-- Q10：行动时间。
UPDATE `questionnaire_questions` SET `title` = '如果发现确实有优化空间，你希望什么时候进一步了解？', `subtitle` = '用于判断行动成熟度和运营优先级', `dimension_code` = 'AM', `question_type` = 'single_choice', `score_mode` = 'score', `sort_order` = 10, `is_required` = 1, `status` = 'active', `updated_at` = CURRENT_TIMESTAMP(3) WHERE `questionnaire_id` = @questionnaire_id AND `question_code` = 'Q10';
INSERT INTO `questionnaire_questions` (`questionnaire_id`, `question_code`, `title`, `subtitle`, `dimension_code`, `question_type`, `score_mode`, `sort_order`, `is_required`, `status`) SELECT @questionnaire_id, 'Q10', '如果发现确实有优化空间，你希望什么时候进一步了解？', '用于判断行动成熟度和运营优先级', 'AM', 'single_choice', 'score', 10, 1, 'active' WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_questions` WHERE `questionnaire_id` = @questionnaire_id AND `question_code` = 'Q10');
SELECT @q10_id := `id` FROM `questionnaire_questions` WHERE `questionnaire_id` = @questionnaire_id AND `question_code` = 'Q10' LIMIT 1;

UPDATE `questionnaire_options` SET `title` = '7 天内想先聊聊或拿一份初步建议', `score_json` = JSON_OBJECT('AM', 4), `tags_json` = JSON_OBJECT('action_timing', 'within_7_days', 'operation_priority', 'high'), `profile_bias` = NULL, `sort_order` = 1, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q10_id AND `option_label` = 'A';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `sort_order`) SELECT @q10_id, 'A', '7 天内想先聊聊或拿一份初步建议', JSON_OBJECT('AM', 4), JSON_OBJECT('action_timing', 'within_7_days', 'operation_priority', 'high'), 1 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q10_id AND `option_label` = 'A');
UPDATE `questionnaire_options` SET `title` = '1 个月内会考虑做一次梳理', `score_json` = JSON_OBJECT('AM', 3), `tags_json` = JSON_OBJECT('action_timing', 'within_1_month', 'operation_priority', 'medium_high'), `profile_bias` = NULL, `sort_order` = 2, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q10_id AND `option_label` = 'B';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `sort_order`) SELECT @q10_id, 'B', '1 个月内会考虑做一次梳理', JSON_OBJECT('AM', 3), JSON_OBJECT('action_timing', 'within_1_month', 'operation_priority', 'medium_high'), 2 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q10_id AND `option_label` = 'B');
UPDATE `questionnaire_options` SET `title` = '3 个月内可能看看案例或加群了解', `score_json` = JSON_OBJECT('AM', 2), `tags_json` = JSON_OBJECT('action_timing', 'within_3_months', 'operation_priority', 'nurture'), `profile_bias` = NULL, `sort_order` = 3, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q10_id AND `option_label` = 'C';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `sort_order`) SELECT @q10_id, 'C', '3 个月内可能看看案例或加群了解', JSON_OBJECT('AM', 2), JSON_OBJECT('action_timing', 'within_3_months', 'operation_priority', 'nurture'), 3 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q10_id AND `option_label` = 'C');
UPDATE `questionnaire_options` SET `title` = '现在只是随便看看，先学习一下', `score_json` = JSON_OBJECT('AM', 0), `tags_json` = JSON_OBJECT('action_timing', 'learning_only', 'operation_priority', 'low'), `profile_bias` = 'stable_operation', `sort_order` = 4, `updated_at` = CURRENT_TIMESTAMP(3) WHERE `question_id` = @q10_id AND `option_label` = 'D';
INSERT INTO `questionnaire_options` (`question_id`, `option_label`, `title`, `score_json`, `tags_json`, `profile_bias`, `sort_order`) SELECT @q10_id, 'D', '现在只是随便看看，先学习一下', JSON_OBJECT('AM', 0), JSON_OBJECT('action_timing', 'learning_only', 'operation_priority', 'low'), 'stable_operation', 4 WHERE NOT EXISTS (SELECT 1 FROM `questionnaire_options` WHERE `question_id` = @q10_id AND `option_label` = 'D');

DELETE FROM `questionnaire_result_profiles` WHERE `questionnaire_id` = @questionnaire_id;
INSERT INTO `questionnaire_result_profiles` (
  `questionnaire_id`, `profile_code`, `profile_name`, `priority`, `lead_grade_suggestion`, `theme_color`, `tags_json`, `summary`, `recommendations_json`, `rule_json`, `result_page_json`
)
VALUES
(@questionnaire_id, 'hidden_waste', '隐性浪费型', 1, 'B', '#EF4444',
 JSON_ARRAY('成本结构不清', '隐性浪费', '优先诊断'),
 '你的企业可能不是没有优化空间，而是很多成本问题藏在日常流程里，需要先把成本结构和用能账单梳理清楚。',
 JSON_ARRAY('先做一次经营成本与用能结构初筛', '重点关注电费、设备运行、供应商服务边界', '建议由顾问协助拆解成本结构'),
 JSON_OBJECT('priority', 1, 'conditions', JSON_ARRAY('MA 为 CP/MA/SR/EP 中最高且 MA>=5', '或 CP>=3 形成隐性浪费信号'), 'exclude', JSON_ARRAY()),
 JSON_OBJECT(
   'headline', '你的企业可能存在看不见的经营漏点',
   'benchmark', '同类企业常见 3 类隐性漏点：账单结构不清、供应商边界不清、设备运行习惯不清。',
   'benchmark_source', '基于相似企业诊断经验的运营参考，并非用户专属结论。',
   'signals', JSON_ARRAY('成本变动能看到结果，但说不清原因', '做过一些优化，却不知道是否真的降下来', '企业经营稳定，但细节复盘不足'),
   'cta', JSON_OBJECT('text', '领取免费初筛', 'action', 'screening_request'),
   'disclaimer', '结果仅用于经营体质初筛，实际节省空间需结合账单和现场情况判断。'
 )),
(@questionnaire_id, 'energy_awakened', '能源觉醒型', 2, 'B', '#0EA5E9',
 JSON_ARRAY('用能优化', '售电绿电', '光伏储能'),
 '你的企业已经出现较明显的用能优化信号，电费、峰谷结构、售电绿电、光伏储能等方向值得进一步评估。',
 JSON_ARRAY('上传电费单做用能初筛', '评估售电、绿电、光伏、储能适配性', '优先查看月用电量和峰谷用电结构'),
 JSON_OBJECT('priority', 2, 'conditions', JSON_ARRAY('EP 为 CP/MA/SR/EP 中最高且 EP>=5'), 'auxiliary', JSON_ARRAY('Q2 选择 5 万度以上时增强能源机会判断')),
 JSON_OBJECT(
   'headline', '你的企业存在进一步优化用能成本的机会',
   'benchmark', '同类用能企业通过账单结构优化、售电绿电或光储方案，常见优化空间约 10%-25%。',
   'benchmark_source', '基于相似企业经验区间，非承诺节省结果。',
   'signals', JSON_ARRAY('月用电量较高', '电费不低但缺少专门分析', '听过能源服务但不确定适配性'),
   'cta', JSON_OBJECT('text', '上传电费单初筛', 'action', 'bill_upload'),
   'disclaimer', '实际优化空间需以电费单、负荷曲线和当地政策为准。'
 )),
(@questionnaire_id, 'supplier_confused', '供应商困惑型', 3, 'B', '#8B5CF6',
 JSON_ARRAY('供应商信息差', '报价审核', '合同边界'),
 '你的企业在供应商选择、报价判断或合同边界上存在信息差，适合先做供应商和报价结构梳理。',
 JSON_ARRAY('梳理现有供应商和报价单', '对比服务边界和合同条款', '必要时匹配靠谱供应商资源'),
 JSON_OBJECT('priority', 3, 'conditions', JSON_ARRAY('SR 为 CP/MA/SR/EP 中最高且 SR>=6'), 'exclude', JSON_ARRAY('EP>=5 时优先进入能源觉醒型')),
 JSON_OBJECT(
   'headline', '你的企业可能在供应商选择上存在信息差',
   'benchmark', '超过 70% 的企业在供应商报价、合同边界或服务承诺上缺少横向比较。',
   'benchmark_source', '基于运营服务经验总结。',
   'signals', JSON_ARRAY('主要依赖熟人推荐', '能比价但看不懂报价结构', '固定供应商很少复盘'),
   'cta', JSON_OBJECT('text', '申请报价/供应商初筛', 'action', 'service_request'),
   'disclaimer', '供应商建议需结合地区、资质、服务范围和合同约定综合判断。'
 )),
(@questionnaire_id, 'cost_sensitive', '成本敏感型', 4, 'B', '#F59E0B',
 JSON_ARRAY('成本压力', '降本诉求', '初筛优先'),
 '你的企业已经出现较明显的成本压力信号，适合先做系统成本梳理，找到优先处理的成本项。',
 JSON_ARRAY('先识别固定成本和能源成本压力来源', '结合账单与供应商费用做初筛', '优先推动一次低门槛诊断'),
 JSON_OBJECT('priority', 4, 'conditions', JSON_ARRAY('CP>=6'), 'exclude', JSON_ARRAY('MA>=5 时优先进入隐性浪费型')),
 JSON_OBJECT(
   'headline', '你的企业对经营成本变化比较敏感',
   'benchmark', '相似企业在固定成本、能源费用和供应商服务上的可优化空间常见约 8%-18%。',
   'benchmark_source', '基于相似企业经验区间，非承诺节省结果。',
   'signals', JSON_ARRAY('固定成本压力变大', '近期有明确降本诉求', '部分成本项缺少系统复盘'),
   'cta', JSON_OBJECT('text', '领取成本初筛', 'action', 'screening_request'),
   'disclaimer', '结果仅用于初筛，真实优化空间需结合经营数据和账单判断。'
 )),
(@questionnaire_id, 'growth_expansion', '增长扩张型', 5, 'B', '#10B981',
 JSON_ARRAY('增长扩张', '成本同步上升', '流程复盘'),
 '你的企业处在增长或多业态阶段，成本容易随规模同步放大，需要在扩张前把成本结构和供应商体系理顺。',
 JSON_ARRAY('关注扩张带来的固定成本放大', '提前复盘电费、供应商和服务合同', '建立可复制的成本管理模板'),
 JSON_OBJECT('priority', 5, 'conditions', JSON_ARRAY('MA>=3 且 LV>=3', '或命中增长扩张标签'), 'auxiliary', JSON_ARRAY('Q4 选择订单或门店增长')),
 JSON_OBJECT(
   'headline', '你的企业增长同时也在放大成本管理难度',
   'benchmark', '扩张型企业如果缺少成本模板，新增门店或项目的成本超支风险可能放大 2-3 倍。',
   'benchmark_source', '基于扩张型企业运营经验总结。',
   'signals', JSON_ARRAY('订单或门店增长明显', '成本也同步变快', '多场景经营需要统一管理口径'),
   'cta', JSON_OBJECT('text', '获取扩张成本梳理', 'action', 'screening_request'),
   'disclaimer', '扩张风险判断需结合实际门店、项目和管理半径。'
 )),
(@questionnaire_id, 'stable_operation', '稳健经营型', 6, 'C', '#64748B',
 JSON_ARRAY('经营稳定', '轻量培育', '持续观察'),
 '你的企业当前成本压力和管理模糊信号不强，可以先通过案例、清单和轻量自查保持关注。',
 JSON_ARRAY('保存经营成本自查清单', '关注账单和供应商合同周期', '后续有明显成本变化时再申请初筛'),
 JSON_OBJECT('priority', 6, 'conditions', JSON_ARRAY('CP/MA/SR/EP 信号整体较低，或未命中前序画像'), 'fallback', true),
 JSON_OBJECT(
   'headline', '你的企业当前经营状态相对稳健',
   'benchmark', '超过 60% 的稳健经营企业也会因习惯性合同、账单结构或供应商惯性产生长期小额多付。',
   'benchmark_source', '基于运营服务经验总结。',
   'signals', JSON_ARRAY('当前没有明显压力', '更多是提前了解优化空间', '适合先做轻量自查'),
   'cta', JSON_OBJECT('text', '保存自查清单', 'action', 'content_save'),
   'disclaimer', '结果仅代表当前答题信号，不代表企业不存在优化空间。'
 ));

COMMIT;

SELECT
  @questionnaire_id AS questionnaire_id,
  (SELECT COUNT(*) FROM `questionnaire_score_dimensions` WHERE `questionnaire_id` = @questionnaire_id) AS dimension_count,
  (SELECT COUNT(*) FROM `questionnaire_star_rules` WHERE `questionnaire_id` = @questionnaire_id) AS star_rule_count,
  (SELECT COUNT(*) FROM `questionnaire_questions` WHERE `questionnaire_id` = @questionnaire_id AND `status` = 'active') AS active_question_count,
  (SELECT COUNT(*) FROM `questionnaire_options` qo INNER JOIN `questionnaire_questions` qq ON qo.`question_id` = qq.`id` WHERE qq.`questionnaire_id` = @questionnaire_id AND qq.`status` = 'active') AS option_count,
  (SELECT COUNT(*) FROM `questionnaire_result_profiles` WHERE `questionnaire_id` = @questionnaire_id) AS profile_count;
