# 后端 Server 与 Infrastructure 文件索引

调用方向：`server.api → modules.<module>.api → application → domain/repository/adapters`；Repository 再使用 Infrastructure。十三级业务模块逐文件见 [总索引](../index.md)。

## Server

| 文件 | 作用 |
| --- | --- |
| [`server/__init__.py`](../../backend/server/__init__.py) | Server 包声明 |
| [`server/api.py`](../../backend/server/api.py) | FastAPI 唯一装配入口、Router 注册与技术健康 |
| [`server/moduleRegistry.py`](../../backend/server/moduleRegistry.py) | 十三级模块能力元数据和注册顺序 |
| [`server/trame.py`](../../backend/server/trame.py) | Trame 进程级技术装配入口，不含物理场业务 |
| [`run_project.py`](../../run_project.py) | 三服务统一启动、健康探测和旧 API 入口拒绝策略 |

## Infrastructure 根与持久化

| 文件 | 作用 |
| --- | --- |
| [`infrastructure/__init__.py`](../../backend/infrastructure/__init__.py) | 公共技术基座包声明 |
| [`infrastructure/config.py`](../../backend/infrastructure/config.py) | 环境、`var/` 和数据库路径真源 |
| [`infrastructure/errors.py`](../../backend/infrastructure/errors.py) | 无业务含义的公共异常模型 |
| [`persistence/__init__.py`](../../backend/infrastructure/persistence/__init__.py) | SQLite 原语公开入口 |
| [`persistence/sqlite.py`](../../backend/infrastructure/persistence/sqlite.py) | 连接、WAL、外键与事务原语 |
| [`persistence/migration.py`](../../backend/infrastructure/persistence/migration.py) | 模块迁移调用的公共迁移机制，不拥有业务表 SQL |

## Storage

| 文件 | 作用 |
| --- | --- |
| [`storage/__init__.py`](../../backend/infrastructure/storage/__init__.py) | 文件存储技术门面 |
| [`storage/blobStore.py`](../../backend/infrastructure/storage/blobStore.py) | SHA-256 对象落盘 |
| [`storage/pathResolver.py`](../../backend/infrastructure/storage/pathResolver.py) | storage key 与受控路径解析 |
| [`storage/cleanup.py`](../../backend/infrastructure/storage/cleanup.py) | 可重建缓存的受控清理原语 |

## Observability

| 文件 | 作用 |
| --- | --- |
| [`observability/__init__.py`](../../backend/infrastructure/observability/__init__.py) | 可观测性技术门面 |
| [`observability/logging.py`](../../backend/infrastructure/observability/logging.py) | 结构化 JSONL 与轮转 |
| [`observability/telemetry.py`](../../backend/infrastructure/observability/telemetry.py) | 失败不阻断业务的本地埋点 |
| [`observability/metrics.py`](../../backend/infrastructure/observability/metrics.py) | 轻量技术指标 |
| [`observability/health.py`](../../backend/infrastructure/observability/health.py) | SQLite、磁盘与 Renderer 技术健康 |

架构门禁：[`backend/tests/test_architecture.py`](../../backend/tests/test_architecture.py)。Server/Infrastructure 文件新增、删除或改职责时，同步本索引、相关 PRD/变更记录和测试；错误写根 [`error.log`](../../error.log)。

跨模块功能回归：[`test_excel_implemented_features.py`](../../backend/tests/test_excel_implemented_features.py) 按Excel序号验证重构前已有的数据画像、Renderer、转换器、时序和引擎能力；状态边界见 [`EXCEL_FEATURE_TEST_MATRIX.md`](../../docs/testing/EXCEL_FEATURE_TEST_MATRIX.md)。

## Dojo 独立应用适配文件

- `backend/server/runtime.py`：每实例可信上下文注册、四会话和导出生命周期。
- `backend/server/dev.py`：开发启动与外部context注入。
- `cli.py`：单层安装包独立启动，不导入task/core。
- `build_hook.py`：发布时按需打包已构建的前端静态资源。
