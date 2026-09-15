# 目录重构迁移记录

- [`architecture.md`](../architecture/architecture.md)：经当前十三级模块事实校对后的总体架构、目录、持久化、注释和验收设计。
- [`MODULAR_REFACTOR_PLAN.md`](MODULAR_REFACTOR_PLAN.md)：逐批迁移、旧文件删除、测试结果和运行数据恢复的执行证据。

本次重构采用兼容迁移：先建立模块门面和架构门禁，再切换旧入口依赖，最后移动源码。
旧公开 URL、HashRouter 路径、SQLite 表和字段保持不变。

前端只保留根 `frontend/`，业务页面、API、Model、Hook 和组件均位于同名模块内；旧全局
页面与兼容链接已在引用归零后删除。

旧数据库已通过 SQLite Backup API 一致性迁入 `var/db/ai4e_vis.sqlite3`，清理前副本位于
`var/backups/legacy-ai4e-vis-before-cleanup-20260829.sqlite3`。旧 `backend/state` 已删除；
测试必须通过 `QODER_ASSET_DB`、`QODER_SPEC_DB`、`QODER_REPORT_DB` 指向临时数据库。
