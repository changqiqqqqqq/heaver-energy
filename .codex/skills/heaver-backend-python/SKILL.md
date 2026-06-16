---
name: heaver-backend-python
description: 当 Codex 处理河狸能源后端 Python 项目 services/api 时使用，包括 FastAPI 路由、service、repository、Pydantic schema、SQLAlchemy model、Alembic migration、pytest 测试、后端代码审查或后端编码规范更新。使用本 skill 时必须遵循本项目 Python 编码规范、模块化单体分层、API 路径规范、数据库命名规则，并确保新增注释和 docstring 使用中文。
---

# 河狸后端 Python 规范

## 核心上下文

在 `services/api` 中按 Python 3.11+ 的 FastAPI 模块化单体项目工作。保持技术栈与现有项目一致：FastAPI、Pydantic、SQLAlchemy、Alembic、MySQL、Redis、pytest。

修改后端代码前，先查看附近实现和相关项目文档：

- `services/api/pyproject.toml`
- `services/api/app/`
- `docs/product/河狸数字能源MVP项目结构与数据库字典.md`
- `docs/db/河狸数字能源MVP数据库设计与字典.md`

优先遵循仓库已有模式，不要套用与本项目风格不一致的通用 FastAPI 示例。

## 模块结构

每个业务模块放在 `services/api/app/modules/<module>/` 下，并保持标准结构：

```text
model.py          SQLAlchemy ORM 模型
schema.py         Pydantic 请求 / 响应模型
repository.py     数据访问
service.py        业务逻辑
router_app.py     小程序端接口，按需提供
router_admin.py   后台端接口，按需提供
```

严格遵守分层边界：

- `router` 只处理入参解析、依赖注入、认证鉴权和响应封装。
- `service` 处理业务规则、状态流转、带业务含义的校验和流程编排。
- `repository` 只处理数据库查询和持久化。
- `schema` 放 Pydantic DTO，`model` 放 SQLAlchemy ORM 模型。
- 不要在小程序端和后台端重复业务逻辑；共用规则应下沉到 `service`。

## API 规范

沿用现有路由分组：

- 小程序端接口放在 `/api/app/*`。
- 后台端接口放在 `/api/admin/*`。
- 健康检查放在 `/api/health`。

模块路由通过 `services/api/app/api/app_router.py` 或 `services/api/app/api/admin_router.py` 注册。路由前缀优先使用复数、资源化命名；已有模块存在约定时跟随已有约定。

路由 tags 使用当前风格，例如 `app-users`、`admin-leads`、`admin-dashboard`。

## Python 编码规则

使用项目级 Python 风格：

- 使用 Python 3.11 语法，包括 `X | None` 和 `list[str]` 这类内置泛型。
- 变量、函数、模块使用 `snake_case`；类使用 `PascalCase`；常量使用 `UPPER_SNAKE_CASE`。
- 函数保持小而聚焦；只有在能提升可读性时才拆出私有辅助函数。
- 优先使用来自 `app...` 的显式导入；避免项目模块之间使用相对导入。
- 对公开的 service、repository、router 和辅助函数提供类型标注。
- 避免可变默认参数、宽泛的 `except Exception`、隐藏全局状态和不明显的数据库副作用。
- 谨慎新增依赖；确实需要新增后端依赖时，同步更新 `services/api/pyproject.toml`。
- 保持现有格式和 import 分组；以后若配置 formatter 或 linter，则遵循项目工具配置。

## 数据库规则

新增或修改持久化逻辑时遵循数据库文档：

- 表名和字段名使用小写 `snake_case`。
- 主键按场景使用 `BIGINT UNSIGNED AUTO_INCREMENT` 语义。
- 状态字段优先使用 `VARCHAR(32)`，避免 MySQL `ENUM`。
- 金额使用 `DECIMAL(12,2)`，时间使用 `DATETIME(3)`。
- 配置、快照、扩展字段使用 JSON。
- 业务表按需包含通用字段：`id`、`created_at`、`updated_at`、`deleted_at`。
- 表存在 `deleted_at` 时，保持软删除语义。
- Alembic 迁移要与 SQLAlchemy 模型和数据库文档保持一致。

## 中文注释

新增注释和 docstring 必须使用中文。

适用范围包括：

- 新增或大幅改写的模块 docstring、类 docstring、函数 docstring。
- 解释业务规则、权限、状态流转、数据脱敏、审计日志、复杂查询和边界情况的行内注释。
- 新增数据库产物时的 SQL 注释、迁移注释和字段说明。

注释要有信息量且保持简洁：

- 解释“为什么”和业务含义，不要解释显而易见的语法。
- 不要添加只重复函数名、变量名或代码字面含义的噪声注释。
- 未触碰的英文注释可以保留；新增或重写的注释必须是中文。

## 实施流程

1. 确认目标模块，并查看相邻模块中同一层的实现方式。
2. 按层更新文件：接口或数据形态变化时先改 `schema` / `model`，再改 `repository`、`service`、`router` 和路由注册。
3. 在 `router` 层区分后台端与小程序端行为；底层业务规则相同时通过 `service` 复用。
4. 行为变化时，在 `services/api/app/tests` 下补充或更新聚焦测试。
5. 可行时从 `services/api` 运行目标检查，例如 `..\..\.venv\Scripts\python.exe -m pytest`。
6. 交付时说明后端行为变化、已运行的测试，以及是否还有迁移或文档需要处理。
