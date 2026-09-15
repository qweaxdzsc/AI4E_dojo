# 模块：运行存储与可观测性

## 运行目录

```text
var/
├── db/ai4e_vis.sqlite3
├── objects/datasets/
├── derived/{profiles,conversions,previews,snapshots,animations}/
├── exports/{visualizations,reports}/
├── quarantine/  tmp/
├── logs/  telemetry/  runtime/
└── backups/
```

[`backend/infrastructure/config.py`](../../backend/infrastructure/config.py) 是运行根与数据库位置真源；[`storage/pathResolver.py`](../../backend/infrastructure/storage/pathResolver.py) 负责相对 storage key；[`storage/blobStore.py`](../../backend/infrastructure/storage/blobStore.py) 负责 SHA-256 对象写入。

## 数据库所有权

- 公共连接、WAL、外键和事务：`infrastructure/persistence`。
- 业务表、SQL、索引与映射：所属一级模块 Repository。
- `dataAssets`独占`artifacts`、分类历史和上传文件落盘；`visDatasets`只通过其公开门面保存分析结果。
- Router、Server 和 `visEngine` 禁止直接执行 SQL；新表必须带模块前缀。
- 测试必须通过环境变量指向临时数据库，禁止写真实 `var/db`。

## 可观测性

- `observability/logging.py`：结构化 JSONL 与轮转。
- `telemetry.py`：失败不影响业务的本地埋点。
- `metrics.py`：轻量技术指标。
- `health.py`：数据库、磁盘和 Renderer 技术健康；数据质量检测仍归 `visDatasets`。

## 迁移与验证

- [`backend/scripts/migrate_runtime_database.py`](../../backend/scripts/migrate_runtime_database.py)：SQLite Backup API 一致性备份。
- [`backend/scripts/prune_runtime_storage.py`](../../backend/scripts/prune_runtime_storage.py)：默认 dry-run 的可重建文件治理。
- [`docs/data-provenance-and-storage.md`](../../docs/data-provenance-and-storage.md)：数据来源和可删除性说明。

迁移必须先备份，再核对 `PRAGMA integrity_check`、表/索引/记录数和对象 SHA-256；不得把用户数据库或上传资产当缓存删除。

统一启动器只接受健康端点声明 `entrypoint=server.api`、`runtime_layout=var-v1` 的当前 API；
旧 `api_app.py` 即使端口健康也必须拒绝，避免页面再次连接已废弃的 `backend/state` 数据库。
旧进程期间产生的报告先用 SQLite Backup API 形成一致性快照，再通过 `reportManage`
Repository 的恢复入口合并，禁止直接复制 WAL 文件或覆盖当前库。

## Dojo 独立应用适配文件

- `backend/infrastructure/storage/atomic.py`：受控路径、文件锁、JSON 原子提交；无业务资产语义。
- `backend/infrastructure/process/channel.py`：带请求ID的独立进程通信及超时。
- `backend/infrastructure/process/supervisor.py`：端口分配、终止和回收。
- `backend/infrastructure/web/proxy.py`：Trame HTTP/WebSocket 转发。
