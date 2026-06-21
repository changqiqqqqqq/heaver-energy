"""业务枚举常量。

这里使用字符串常量而不是数据库 ENUM，方便后续产品口径调整时只改配置和校验。
"""

SCORE_DIMENSIONS = ("CP", "MA", "SR", "EP", "AM", "LV")

PROFILE_CODES = (
    "hidden_waste",
    "energy_awakened",
    "supplier_confused",
    "cost_sensitive",
    "growth_expansion",
    "stable_operation",
)

PROFILE_PRIORITY = {code: index for index, code in enumerate(PROFILE_CODES)}

LEAD_GRADES = ("A", "B", "C", "D")

LEAD_STATUSES = (
    "pending_followup",
    "following",
    "transferred_supplier",
    "content_saved",
    "closed",
)

NEED_TYPES = (
    "use_energy",
    "energy_consulting",
    "supplier_recommendation",
    "quote_review",
    "supplier_screening",
    "contract_review",
    "green_power",
    "green_certificate",
    "solar_storage",
)

FOLLOWUP_TYPES = ("phone", "wechat", "community", "offline", "system")
FOLLOWUP_RESULTS = ("contacted", "no_answer", "interested", "not_interested", "invalid")

