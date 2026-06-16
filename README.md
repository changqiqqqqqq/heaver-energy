# 河狸数字能源 MVP

本仓库按产品文档先搭建整体项目结构，暂不实现业务功能。

## 工程划分

- `apps/miniapp`：Taro + React 小程序端。
- `apps/admin-web`：React Web 管理后台。
- `services/api`：FastAPI 模块化单体后端。
- `docs`：接口、数据库、产品文档。
- `deploy`：Docker、Nginx 等部署配置预留。

## API 分层

- 小程序端接口：`/api/app/*`
- 后台端接口：`/api/admin/*`
- 健康检查：`/api/health`

## 当前阶段

当前仅完成骨架、占位入口和模块边界，后续可按文档中的 MVP 开发顺序逐步填充功能。

