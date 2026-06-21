# MVP 小程序前端开发对接文档

版本：v0.1
范围：`docs/product/小程序页面/mvp` 页面设计稿与 `services/api` 小程序端接口对接
结论：主链路可以与当前后端衔接；测评题库种子数据、两类结果页视觉稿、消息/顾问聊天、真实文件上传能力需要补齐或先按 MVP 降级处理。

---

## 1. 页面识别与对接结论

设计稿目录中共有 15 个 SVG，覆盖了小程序 MVP 的核心获客闭环：

```text
首页测评入口
  -> 电费瘦身小测试答题页
  -> 结果页
  -> 免费报告 / 顾问咨询 / 分享卡
  -> 消息列表 / 顾问聊天
```

辅助总览图：`docs/product/小程序页面/mvp-overview.png`。

### 1.1 页面与设计稿对应

| 设计稿 | 页面含义 | 后端衔接状态 | 说明 |
|---|---|---|---|
| `Background.svg` | 首页，测评入口 | 可衔接 | 点击“我现在开始”进入问卷页；可先调用登录，也可进入答题时再登录。 |
| `Frame 21.svg` | 电费瘦身小测试答题页 | 可衔接 | 使用 `/api/app/questionnaires/current` 拉取题目，提交到 `/api/app/questionnaires/{id}/submissions`。 |
| `Background (3).svg` | 结果页：增长扩张型 | 可衔接 | 对应 `profile_code = growth_expansion`。 |
| `Background (4).svg` | 结果页：隐性浪费型 | 可衔接 | 对应 `profile_code = hidden_waste`。 |
| `Group 1.svg` | 结果页：稳健经营型 | 可衔接 | 对应 `profile_code = stable_operation`。 |
| `Group 2.svg` | 结果页：成本敏感型 | 可衔接 | 对应 `profile_code = cost_sensitive`。 |
| `Background+Shadow*.svg`、`Group 9.svg` | 结果分享卡/海报 | 前端本地实现 | 当前后端暂无分享卡生成和分享事件接口；MVP 可用 Canvas 本地生成。 |
| `Background (5).svg` | 免费报告/免费初筛表单 | 可衔接 | 提交 `/api/app/screening-requests`；若上传账单，还需文件流程。 |
| `Background (6).svg` | 顾问咨询/服务需求 | 可衔接 | 提交 `/api/app/service-requests`。 |
| `Background (1).svg` | 消息中心 | 需降级或补接口 | 当前后端无小程序消息列表接口；MVP 可先展示静态通知或后续补 `app_messages`。 |
| `Background (2).svg` | 顾问聊天 | 需降级或补接口 | 当前后端无 IM/聊天接口；MVP 建议跳转微信客服、企微客服或提交服务需求。 |

### 1.2 当前缺口

| 缺口 | 影响 | MVP 处理建议 |
|---|---|---|
| 后端已有 6 类画像，设计稿只覆盖 4 类 | `energy_awakened`、`supplier_confused` 命中后缺页面样式 | 先复用橙/蓝主题模板，后续补设计稿。 |
| 问卷题库种子数据未在前端目录体现 | 没有已发布 `business_health` 问卷时，答题页无法拉题 | 联调前用后台接口或种子脚本导入并发布问卷。 |
| 文件接口只登记元数据，不上传二进制 | 账单上传无法只靠 `/api/app/files` 完成真实文件存储 | MVP 可先隐藏上传或接入对象存储直传；后端后续补签名上传接口。 |
| 消息中心无 app 端接口 | 消息页无法展示真实运营通知 | 先静态占位，后续补消息表和接口。 |
| 顾问聊天无 app 端接口 | 不能做实时对话 | 先跳转微信客服/企微或提交服务需求。 |
| 分享事件无后端记录 | 无法统计分享回流 | MVP 可只生成分享卡；P2 补 `share_events`。 |

---

## 2. 前端信息架构

建议页面目录：

```text
pages/
  home/index                 首页测评入口
  quiz/index                 答题页
  result/index               测评结果页
  report/index               免费报告/初筛表单
  consult/index              顾问咨询/服务需求
  messages/index             消息中心
  chat/index                 顾问聊天降级页
  poster/index               分享海报生成页
  mine/index                 我的

services/
  request.ts                 请求封装
  auth.ts                    登录与手机号授权
  questionnaire.ts           问卷接口
  lead-intake.ts             初筛、服务需求、账单接口

stores/
  auth.ts                    token 与用户信息
  quiz.ts                    当前问卷、答案、结果缓存
```

底部 Tab 建议：

| Tab | 页面 | MVP 功能 |
|---|---|---|
| 首页 | `pages/home/index` | 测评入口、营销主视觉 |
| 消息 | `pages/messages/index` | 初期静态/空状态；后续接真实消息 |
| 我的 | `pages/mine/index` | 用户信息、历史结果入口、授权状态 |

---

## 3. 通用对接规范

### 3.1 基础地址

本地联调：

```text
http://127.0.0.1:8000
```

微信开发者工具可开启“不校验合法域名”。真机和生产环境需要 HTTPS 域名，并在小程序后台配置 request 合法域名。

### 3.2 响应结构

后端统一返回：

```ts
type ApiResponse<T> = {
  code: number
  message: string
  data: T | null
}
```

前端请求封装要求：

1. 成功只读取 `response.data.data`。
2. `code !== 0` 或 HTTP 非 2xx 时进入统一错误处理。
3. 除登录、获取当前问卷外，业务提交接口默认带 `Authorization: Bearer <token>`。
4. 提交按钮必须防重复点击，避免同一表单重复创建。
5. 对问卷题目做本地缓存，缓存 key 建议为 `questionnaire.code + version`。

### 3.3 登录与手机号授权

启动或进入答题前执行微信登录：

```text
wx.login()
  -> POST /api/app/auth/wechat-login
  -> 保存 access_token
```

请求体：

```json
{
  "code": "wx.login 返回 code",
  "nickname": "可选",
  "avatar_url": "可选"
}
```

手机号授权：

```text
wx.getPhoneNumber()
  -> POST /api/app/auth/phone-authorize
```

生产请求体：

```json
{
  "phone_code": "getPhoneNumber 返回 code",
  "consent_version": "v1",
  "granted": true
}
```

本地 mock 可用：

```json
{
  "dev_phone_number": "13812345678",
  "consent_version": "v1",
  "granted": true
}
```

---

## 4. 页面开发顺序

### 阶段 0：联调前置

目标：先让前端具备稳定请求能力。

开发内容：

1. 配置环境变量：`dev` 指向 `http://127.0.0.1:8000`，`prod` 指向正式 HTTPS 域名。
2. 封装 `request<T>()`，自动注入 token、处理 401、处理错误提示。
3. 封装 `login()`、`ensureLogin()`、`getMe()`、`authorizePhone()`。
4. 确认后端 `/api/health/db` 返回 `database: connected`。
5. 导入并发布 `business_health` 问卷数据。

验收：

1. 小程序能完成登录并拿到 token。
2. `GET /api/app/questionnaires/current?code=business_health` 能返回题目。

### 阶段 1：首页

对应设计稿：`Background.svg`。

开发内容：

1. 实现品牌区、标题、测评卡片、开始按钮。
2. 点击“我现在开始”：
   - 若未登录，先 `wx.login` 后跳转。
   - 跳转 `pages/quiz/index?code=business_health`。
3. 承接分享参数：
   - `scene`、`shareUserId`、`leadId` 可先记录在本地。
   - 后端分享事件接口未完成前，不强依赖上报。

### 阶段 2：答题页

对应设计稿：`Frame 21.svg`。

接口：

| 方法 | 路径 | 用途 |
|---|---|---|
| GET | `/api/app/questionnaires/current?code=business_health` | 获取当前已发布问卷 |
| POST | `/api/app/questionnaires/{questionnaire_id}/submissions` | 提交答案 |

前端状态：

```ts
type QuizState = {
  questionnaireId: number
  currentIndex: number
  answers: Record<number, number[]>
  submitting: boolean
}
```

提交体：

```json
{
  "enterprise_id": null,
  "lead_id": null,
  "answers": [
    { "question_id": 11, "option_ids": [102] }
  ]
}
```

交互规则：

1. 题目按 `sort_order` 排序展示。
2. `single_choice` 单选，`multiple_choice` 多选。
3. 底部按钮文案：非最后一题为“下一题”，最后一题为“查看结果”。
4. 必答题未选时不允许下一步。
5. 提交成功后保存 `submission_id`、`lead_id`，跳转结果页。
6. 网络失败时保留当前答案，允许重试。

### 阶段 3：结果页

对应设计稿：`Background (3).svg`、`Background (4).svg`、`Group 1.svg`、`Group 2.svg`。

结果数据来自提交响应：

```ts
type QuestionnaireSubmission = {
  id: number
  questionnaire_id: number
  lead_id: number | null
  profile_code: string | null
  profile_name: string | null
  lead_grade: 'A' | 'B' | 'C' | 'D' | null
  total_score: number
  dimension_scores: Record<string, number>
  dimension_stars: Record<string, number>
  answer_tags: Record<string, unknown>
  result: {
    profile_code: string
    profile_name: string
    theme_color?: string
    summary?: string
    recommendations: string[]
    result_page?: {
      headline?: string
      benchmark?: string
      benchmark_source?: string
      signals: string[]
      cta: Record<string, unknown>
      disclaimer?: string
    }
  } | null
}
```

画像样式映射：

| profile_code | 展示名 | 设计稿 | 主题建议 |
|---|---|---|---|
| `hidden_waste` | 隐性浪费型 | `Background (4).svg` | 橙黄 |
| `growth_expansion` | 增长扩张型 | `Background (3).svg` | 蓝紫 |
| `cost_sensitive` | 成本敏感型 | `Group 2.svg` | 橙色 |
| `stable_operation` | 稳健经营型 | `Group 1.svg` | 绿色 |
| `energy_awakened` | 能源觉醒型 | 待补 | 暂复用蓝紫或绿色模板 |
| `supplier_confused` | 供应商困惑型 | 待补 | 暂复用橙色模板 |

结果页 CTA：

| 按钮 | 跳转 | 后端 |
|---|---|---|
| 领取专属商电优化报告 | `pages/report/index?leadId=&submissionId=` | `/api/app/screening-requests` |
| 我想让顾问帮我看看 | `pages/consult/index?leadId=&submissionId=` | `/api/app/service-requests` |
| 保存 | `pages/poster/index` 或本地相册 | 前端 Canvas |
| 分享 | 小程序分享能力 | 后端暂无分享事件接口 |

### 阶段 4：分享卡/海报

对应设计稿：`Background+Shadow*.svg`、`Group 9.svg`。

MVP 实现：

1. 使用 Canvas 根据 `profile_code`、`profile_name`、`summary` 生成海报。
2. 二维码可先使用小程序当前页面码或普通分享路径。
3. `onShareAppMessage` 携带：

```text
/pages/home/index?from=share&profileCode=cost_sensitive&leadId=xxx
```

后续增强：

1. 后端补分享事件接口。
2. 生成永久小程序码并关联 `lead_id`。

### 阶段 5：免费报告/初筛表单

对应设计稿：`Background (5).svg`。

接口：

```text
POST /api/app/screening-requests
```

请求体：

```json
{
  "lead_id": 2001,
  "submission_id": 1001,
  "enterprise_id": null,
  "region_text": "江苏 苏州",
  "enterprise_name": "某某制造有限公司",
  "enterprise_type": "制造业",
  "monthly_kwh_range": "10万-50万度",
  "contact_name": "张总",
  "contact_phone": "13812345678",
  "extra": {
    "from_page": "result",
    "profile_code": "cost_sensitive"
  }
}
```

交互规则：

1. 表单提交前建议先请求手机号授权；用户拒绝时允许手填手机号。
2. 企业名称、手机号为 MVP 必填；地区、行业、月用电量建议必填。
3. 提交成功展示成功状态，并提示顾问会联系。
4. 如果用户上传账单，走阶段 7 文件流程。

### 阶段 6：顾问咨询/服务需求

对应设计稿：`Background (6).svg`。

接口：

```text
POST /api/app/service-requests
```

后端允许的 `need_type`：

```text
use_energy
energy_consulting
supplier_recommendation
quote_review
supplier_screening
contract_review
green_power
green_certificate
solar_storage
```

请求体示例：

```json
{
  "lead_id": 2001,
  "enterprise_id": null,
  "submission_id": 1001,
  "primary_need_type": "energy_consulting",
  "description": "想了解是否有优化空间",
  "items": [
    {
      "need_type": "energy_consulting",
      "need_name": "快速商电成本核查",
      "extra": {
        "source": "consult_page"
      }
    }
  ]
}
```

前端选项映射建议：

| 设计稿选项 | need_type | need_name |
|---|---|---|
| 快速商电成本核查 | `energy_consulting` | 快速商电成本核查 |
| 了解储能方案 | `solar_storage` | 了解储能方案 |
| 评估绿电/用能收益 | `use_energy` | 评估用能优化收益 |

### 阶段 7：账单/文件上传

对应入口：免费报告页中的上传账单区域。

当前后端接口：

| 方法 | 路径 | 用途 |
|---|---|---|
| POST | `/api/app/files` | 创建文件元数据 |
| POST | `/api/app/bills` | 创建账单上传记录 |

当前限制：

1. `/api/app/files` 只保存 `object_key` 等元数据，不接收二进制文件。
2. 小程序真实文件上传需要对象存储直传凭证或后端 multipart 上传接口。

MVP 两种方案：

| 方案 | 做法 | 适用 |
|---|---|---|
| 降级方案 | 暂不开放真实账单上传，只收集初筛表单 | 最快联调上线 |
| 直传方案 | 前端上传到 OSS/COS，再把 `object_key` 提交 `/files` 和 `/bills` | 需要补上传凭证接口 |

元数据提交流程：

```text
选择文件
  -> 上传到对象存储，得到 object_key
  -> POST /api/app/files
  -> POST /api/app/bills
```

### 阶段 8：消息中心与顾问聊天

对应设计稿：`Background (1).svg`、`Background (2).svg`。

当前状态：后端暂无小程序端消息列表、消息详情、实时聊天接口。

MVP 建议：

1. 消息中心先展示静态消息、空状态、服务进度占位。
2. 顾问聊天页点击输入框或按钮时跳转微信客服/企微客服。
3. 若用户提交了顾问咨询，显示“已提交，顾问将尽快联系”的状态。

后续接口建议：

| 方法 | 路径 | 用途 |
|---|---|---|
| GET | `/api/app/messages` | 消息列表 |
| GET | `/api/app/messages/{id}` | 消息详情 |
| POST | `/api/app/messages/{id}/read` | 标记已读 |
| POST | `/api/app/chat/sessions` | 创建顾问会话 |

---

## 5. 前后端接口清单

### 5.1 可直接使用的小程序接口

| 方法 | 路径 | 页面 | 是否鉴权 |
|---|---|---|---|
| POST | `/api/app/auth/wechat-login` | 全局登录 | 否 |
| POST | `/api/app/auth/phone-authorize` | 报告页/初筛页 | 是 |
| GET | `/api/app/auth/me` | 我的页 | 是 |
| POST | `/api/app/enterprises` | 初筛页可选 | 是 |
| GET | `/api/app/questionnaires/current` | 答题页 | 否 |
| GET | `/api/app/questionnaires/{questionnaire_id}` | 答题页 | 否 |
| POST | `/api/app/questionnaires/{questionnaire_id}/submissions` | 答题页 | 是 |
| GET | `/api/app/questionnaires/submissions/{submission_id}` | 结果页/历史结果 | 是 |
| POST | `/api/app/screening-requests` | 免费报告页 | 是 |
| POST | `/api/app/service-requests` | 顾问咨询页 | 是 |
| POST | `/api/app/files` | 账单上传 | 是 |
| POST | `/api/app/bills` | 账单上传 | 是 |

### 5.2 推荐前端 service 方法

```ts
export const authApi = {
  loginWithWechat,
  authorizePhone,
  getMe,
}

export const questionnaireApi = {
  getCurrentQuestionnaire,
  getQuestionnaire,
  submitQuestionnaire,
  getSubmission,
}

export const leadIntakeApi = {
  submitScreening,
  submitServiceRequest,
  createFile,
  createBillUpload,
}
```

---

## 6. 数据缓存与性能建议

1. 问卷题目缓存到本地，进入答题页优先读缓存，再后台刷新。
2. 答案实时保存到本地，用户中途退出后可恢复。
3. 提交接口加 `submitting` 锁，防止重复提交。
4. SVG 设计元素转为小程序可用图片资源后放 CDN 或小程序分包，避免首页包体过大。
5. 结果页只依赖一次提交响应；刷新结果页时再调用 `GET /submissions/{id}`。
6. 非首屏页面采用分包：`report`、`consult`、`poster`、`chat` 可放到业务分包。
7. 接口失败统一提示，并给重试按钮；不要清空用户已填写内容。

---

## 7. 联调验收顺序

### 7.1 后端准备

1. MySQL 已执行 `alembic upgrade head`。
2. `/api/health/db` 返回 connected。
3. 导入并发布 `business_health` 问卷。
4. 确认 6 类 `profile_code` 都有 `result_page_json` 或前端兜底文案。

### 7.2 小程序联调

1. 登录：`wx.login` 后拿到 token。
2. 拉题：答题页能获取 10 题。
3. 提交：答完后返回 `submission_id`、`lead_id`、`profile_code`、`lead_grade`。
4. 结果：四类已有设计稿画像能正确切换样式，两类缺稿画像能走兜底模板。
5. 免费报告：提交后后端新增 `screening_requests`，并关联同一 `lead_id`。
6. 顾问咨询：提交后后端新增 `service_requests`，并关联同一 `lead_id`。
7. 账单：若启用上传，`files` 与 `bill_uploads` 都能创建，线索 `has_bill_uploaded` 更新。
8. 后台验证：`/api/admin/leads` 能看到线索，详情能看到提交、初筛、服务需求。

---

## 8. 上线最小范围

建议第一版上线范围：

1. 首页。
2. 答题页。
3. 结果页，含 4 类已设计画像 + 2 类兜底模板。
4. 免费报告表单。
5. 顾问咨询表单。
6. 分享卡本地生成。
7. 消息中心静态占位。
8. 顾问聊天跳转客服或提交需求。

暂缓：

1. 真实 IM 聊天。
2. 消息中心真实通知。
3. 分享事件统计。
4. 账单 OCR/解析。
5. 后端生成分享海报。

---

## 9. 最终判断

当前小程序设计稿与后端主链路可以衔接，尤其是“测评、结果、初筛、服务需求、后台线索承接”已经具备 API 基础。前端可以立即按上述顺序开发。

需要在开发前明确两件事：

1. 先导入已发布的 `business_health` 问卷配置，否则答题页没有动态题目来源。
2. `energy_awakened` 与 `supplier_confused` 两类结果页暂无独立设计稿，需要产品/设计确认是补稿还是沿用兜底模板。
