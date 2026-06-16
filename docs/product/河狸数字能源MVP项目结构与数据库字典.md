# 河狸数字能源 MVP 项目结构与实施建议

版本：v0.1  
技术栈：Taro + React、小程序优先；FastAPI；MySQL；Redis  
目标：先跑通获客、测评、初筛、服务需求、后台线索管理和基础数据安全闭环。

---

## 1. MVP 功能范围

### 1.1 小程序端

第一版小程序聚焦企业客户获客与需求收集：

1. 微信登录 + 手机号授权
2. 经营体质测试
   - 题库展示
   - 选项答题
   - 评分计算
   - 结果页
   - 分享卡片
3. 免费用能初筛
   - 地区
   - 企业类型
   - 企业简称
   - 联系方式
   - 账单上传
4. 服务需求提交
   - 电费优化
   - 售电 / 绿电服务商
   - 绿证 / 绿电了解
   - 光伏 / 储能 / 节能评估
5. 隐私协议与账单敏感信息提示

### 1.2 管理后台

第一版后台聚焦线索管理，不做复杂 CRM：

1. 管理员登录
2. 统计概览
   - 总线索数
   - 今日新增
   - A 类线索数
   - 待跟进数
   - 已转供应商数
   - 转接率
   - 留资转化率
3. 线索筛选
   - 全部
   - A 类 / B 类 / C 类
   - 用能需求
   - 绿证
   - 未跟进
4. 线索列表
   - 企业 / 来源
   - 需求方向
   - 线索等级
   - 状态
5. 线索详情
   - 地区
   - 企业类型
   - 月成本规模
   - 来源入口
   - 资料上传状态
   - 授权状态
   - 测评结果
   - 服务需求
6. 操作区
   - 发起跟进
   - 转供应商
   - 备注
7. 权限控制与操作日志

### 1.3 暂不纳入 MVP

第一版暂不做以下能力，但表结构预留扩展空间：

1. 异步任务队列
2. 自动 OCR
3. 自动电费诊断算法
4. 在线报价
5. 合同管理
6. 付款与订单
7. 企业端 Web 工作台
8. 供应商独立平台

---

## 2. 总体架构建议

### 2.1 推荐工程形态

MVP 阶段建议采用：

```text
前端小程序：Taro + React，单独工程
后台前端：React Web，单独工程
后端接口：FastAPI，单服务模块化单体
数据库：MySQL 8.x
缓存：Redis
文件存储：本地开发 + 云对象存储预留
```

后台管理系统建议“前端单独做、后端不单独拆服务”。也就是：

```text
小程序前端  -> /api/app/*
后台前端    -> /api/admin/*
同一个 FastAPI 后端
同一个 MySQL 数据库
```

这样做的原因：

1. 当前 MVP 的核心是验证业务闭环，不是验证微服务治理能力。
2. 后台与小程序会共享企业、线索、测评、账单、服务需求等核心模型。
3. 单后端更容易控制数据一致性、权限和审计日志。
4. 后续如果业务增长，可以按模块拆成独立服务。

### 2.2 后续演进路径

```text
阶段 1：MVP
Taro 小程序 + React 后台 + FastAPI 模块化单体

阶段 2：增强运营
增加 OCR、报告生成、消息通知、供应商报价

阶段 3：平台化
拆出供应商端、企业客户 Web 端、更多角色权限

阶段 4：服务化
将 OCR、诊断计算、通知、供应商匹配拆成独立服务
```

### 2.3 MVP 服务器选型建议

MVP 正式上线阶段建议优先采用单台轻量应用服务器承载后端服务、管理后台、数据库和缓存，后续根据数据量、访问量和运维要求再拆分 RDS、Redis 托管版和对象存储。

推荐服务器配置：

| 配置项 | 建议值 |
|---|---|
| 云厂商 / 产品 | 腾讯云轻量应用服务器 |
| 操作系统 | Ubuntu 22.04 LTS |
| 地域 | 北京或上海 / 广州，按客户主要区域选择 |
| 套餐类型 | 通用型 |
| CPU | 2 核 |
| 内存 | 8 GB |
| 系统盘 | 120 GB SSD |
| 公网带宽 | 8 Mbps |
| 月流量包 | 1200 GB / 月 |
| 登录方式 | SSH 密钥登录 |

部署建议：

1. 使用 Docker Compose 部署 `Nginx + FastAPI + MySQL 8 + Redis`。
2. MVP 初期 MySQL 和 Redis 可与 API 同机部署，暂不强制单独购买 RDS 或 Redis 托管版。
3. 账单文件初期可本地存储，但正式收集客户账单后建议尽快迁移到 COS / OSS，并保留 `files.storage_provider` 扩展字段。
4. 服务器安全组只开放 `22`、`80`、`443`，数据库和 Redis 不开放公网端口。
5. 必须开启云硬盘快照和 MySQL 每日备份；如果后续进入持续投放或客户数据增长阶段，再迁移到云数据库 RDS MySQL。
6. 8 Mbps 带宽足以支撑 MVP 的 API、管理后台和小程序请求；大文件下载、账单查看和分享卡片图片应优先通过对象存储承载。

---

## 3. 项目目录结构

建议采用一个代码仓库管理多个工程，便于统一文档、接口协议和部署脚本。

```text
heaver-energy/
  apps/
    miniapp/
      package.json
      project.config.json
      src/
        app.config.ts
        app.tsx
        pages/
          home/
          questionnaire/
          questionnaire-result/
          screening/
          service-request/
          share-card/
          profile/
        components/
          AppButton/
          EnergyCard/
          QuestionOption/
          UploadBill/
          PrivacyPanel/
        services/
          http.ts
          auth.api.ts
          questionnaire.api.ts
          screening.api.ts
          service-request.api.ts
          file.api.ts
        store/
          user.store.ts
          questionnaire.store.ts
        utils/
          mask.ts
          validators.ts

    admin-web/
      package.json
      src/
        main.tsx
        router/
        layouts/
          AdminLayout/
        pages/
          login/
          dashboard/
          leads/
          lead-detail/
          suppliers/
          settings/
        components/
          StatCard/
          LeadTable/
          LeadFilterTabs/
          FollowupDrawer/
          TransferSupplierModal/
        services/
          http.ts
          auth.api.ts
          lead.api.ts
          supplier.api.ts
          statistics.api.ts
        store/
          auth.store.ts
        utils/
          format.ts

  services/
    api/
      pyproject.toml
      alembic.ini
      app/
        main.py
        api/
          app_router.py
          admin_router.py
          health.py
        core/
          config.py
          security.py
          permissions.py
          logging.py
          exceptions.py
        db/
          session.py
          base.py
          migrations/
        common/
          pagination.py
          response.py
          enums.py
          datetime.py
        modules/
          auth/
            model.py
            schema.py
            repository.py
            service.py
            router_app.py
            router_admin.py
          user/
          enterprise/
          questionnaire/
          lead/
          service_request/
          bill/
          file/
          supplier/
          crm/
          statistics/
          security_audit/
        tests/
          unit/
          integration/

  docs/
    api/
    db/
    product/

  deploy/
    docker/
    nginx/
```

### 3.1 后端模块职责

| 模块 | 职责 | 主要服务对象 |
|---|---|---|
| `auth` | 微信登录、后台登录、Token、手机号授权 | 小程序、后台 |
| `user` | 小程序用户、授权信息、隐私同意 | 小程序 |
| `enterprise` | 企业主体、联系人、企业站点 | 小程序、后台 |
| `questionnaire` | 题库、选项、评分、结果画像、答题记录 | 小程序、后台 |
| `lead` | 线索汇总、等级、状态、来源、后台筛选 | 后台 |
| `screening` | 免费用能初筛表单 | 小程序、后台 |
| `service_request` | 服务需求提交与需求类型 | 小程序、后台 |
| `bill` | 账单上传记录、账单结构化字段预留 | 小程序、后台 |
| `file` | 文件元数据、访问权限、脱敏标记 | 小程序、后台 |
| `supplier` | 供应商资料、服务范围、转接记录 | 后台 |
| `crm` | 跟进记录、备注、分配负责人 | 后台 |
| `statistics` | 线索统计、转化率、后台看板 | 后台 |
| `security_audit` | 权限、角色、操作日志、隐私协议记录 | 后台 |

### 3.2 API 路径规范

```text
/api/app/auth/*
/api/app/questionnaires/*
/api/app/screening-requests/*
/api/app/service-requests/*
/api/app/files/*

/api/admin/auth/*
/api/admin/dashboard/*
/api/admin/leads/*
/api/admin/suppliers/*
/api/admin/questionnaires/*
/api/admin/audit-logs/*
```

### 3.3 模块内部结构规范

每个后端业务模块建议保持相同结构：

```text
modules/lead/
  model.py          SQLAlchemy ORM 模型
  schema.py         Pydantic 请求 / 响应模型
  repository.py     数据访问
  service.py        业务逻辑
  router_app.py     小程序端接口，可选
  router_admin.py   后台端接口，可选
```

原则：

1. `router` 只处理入参、鉴权和响应。
2. `service` 处理业务规则。
3. `repository` 只处理数据库查询。
4. 不在 `admin` 中复制业务逻辑，后台只是业务能力的管理入口。

---

## 4. 数据库设计文档

数据库设计原则、数据库字典和后台页面与数据表映射已拆分至 [河狸数字能源MVP数据库设计与字典.md](../db/河狸数字能源MVP数据库设计与字典.md)。

---

## 5. 线索等级与状态建议

### 5.1 线索等级

MVP 可以先用简单规则，后续再改成可配置评分。

| 等级 | 建议规则 |
|---|---|
| A | 已授权手机号 + 有明确服务需求 + 上传账单或月成本规模较高 |
| B | 已授权手机号 + 有测试结果或服务需求，但资料不完整 |
| C | 只有访问、测试或泛咨询，暂未留资或需求弱 |

### 5.2 线索状态

| 状态值 | 含义 |
|---|---|
| `pending_followup` | 待跟进 |
| `following` | 跟进中 |
| `transferred_supplier` | 已转供应商 |
| `content_saved` | 内容留存，暂未进入销售跟进 |
| `closed` | 已关闭 |

### 5.3 需求类型

| 类型值 | 含义 |
|---|---|
| `use_energy` | 电费优化 / 用能初筛 |
| `green_power` | 售电 / 绿电服务商 |
| `green_certificate` | 绿证 / 绿电了解 |
| `solar_storage` | 光伏 / 储能 / 节能评估 |

### 5.4 测评画像

| 画像值 | 含义 |
|---|---|
| `stable_operation` | 稳健经营型 |
| `cost_sensitive` | 成本敏感型 |
| `growth_expansion` | 增长扩张型 |
| `hidden_waste` | 隐性浪费型 |

---

## 6. 数据安全设计

### 6.1 敏感数据原则

1. 手机号不建议明文保存。
2. 列表页默认展示脱敏手机号。
3. 查看完整联系方式必须有权限，并写入 `audit_logs`。
4. 账单文件标记为 `sensitivity_level = sensitive`。
5. 文件默认私有访问，通过后端签名 URL 临时访问。
6. 账单下载、查看、转发都要写审计日志。

### 6.2 推荐权限点

| 权限编码 | 说明 |
|---|---|
| `dashboard:view` | 查看数据概览 |
| `lead:view` | 查看线索列表 |
| `lead:view_detail` | 查看线索详情 |
| `lead:view_sensitive` | 查看手机号、下载账单等敏感信息 |
| `lead:followup` | 添加跟进 |
| `lead:transfer_supplier` | 转供应商 |
| `lead:note` | 添加备注 |
| `supplier:manage` | 管理供应商 |
| `questionnaire:manage` | 管理题库和结果配置 |
| `audit:view` | 查看审计日志 |

### 6.3 MVP 最小角色

| 角色 | 权限 |
|---|---|
| 超级管理员 | 全部权限 |
| 运营人员 | 查看线索、跟进、备注、查看有限敏感信息 |
| 业务负责人 | 查看统计、线索、转供应商 |

---

## 7. Redis 使用建议

MVP 不引入异步任务时，Redis 仍然有价值，但使用范围要克制。

| 用途 | Key 示例 | TTL |
|---|---|---|
| 小程序登录态 | `session:app:{token}` | 7 天 |
| 后台登录态 | `session:admin:{token}` | 12 小时 |
| 验证码 / 短期授权 | `auth:phone:{code}` | 5 分钟 |
| 防重复提交 | `lock:submit:{user_id}:{scene}` | 10 秒 |
| 后台统计缓存 | `stat:dashboard:{date}` | 1-5 分钟 |

---

## 8. MVP 开发顺序建议

### 第 1 步：基础设施

1. FastAPI 项目骨架
2. MySQL 连接与 Alembic 迁移
3. Redis 连接
4. 统一响应格式
5. 错误处理
6. 日志和 request_id

### 第 2 步：用户与登录

1. 微信登录
2. 手机号授权
3. 用户隐私协议记录
4. 小程序 Token
5. 后台管理员登录

### 第 3 步：测评闭环

1. 题库接口
2. 提交答题
3. 评分计算
4. 结果画像
5. 生成分享卡片记录

### 第 4 步：企业留资与需求

1. 企业信息提交
2. 初筛提交
3. 账单上传
4. 服务需求提交
5. 线索自动创建或更新

### 第 5 步：后台线索管理

1. 统计概览
2. 线索列表
3. 筛选和搜索
4. 线索详情
5. 发起跟进
6. 转供应商
7. 添加备注

### 第 6 步：安全与审计

1. 角色权限
2. 敏感字段脱敏
3. 文件私有访问
4. 操作日志
5. 基础数据备份策略

---

## 9. MVP 交付边界

第一版上线时，建议至少达到以下标准：

1. 小程序用户可以完成登录、测评、结果查看、分享、初筛和需求提交。
2. 后台可以看到完整线索列表和详情。
3. 后台可以完成跟进、转供应商、备注。
4. 上传的账单文件可以在后台安全查看。
5. 管理员权限和敏感操作日志可用。
6. 数据库结构支持后续 OCR、诊断报告、供应商报价和企业工作台扩展。


