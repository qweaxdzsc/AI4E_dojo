# 模块组：三维物理场与内核

## 一级模块与二级业务

[`backend/modules/visPhysField/`](../../backend/modules/visPhysField/) 是一个不可拆散的一级模块，共享 `api.py`、`application.py`、`domain.py`、`repository.py` 和 Trame 会话。

二级业务全部位于 `modules/`：

- `fieldVisualization`：视角、云图、矢量、切面/流线/等值分析、Probe、色带、显示样式、时序、动画和多结果。
- `dataExtraction`：空间、时序和聚合提取。
- `dataOverview`：表格、基础图表和多维云图。

二级目录禁止自己的 Router、Application 门面、Repository、数据库连接、Trame Server、URL、端口和跨一级模块公开接口。

## Trame 与 Engine 边界

- [`trameServer.py`](../../backend/modules/visPhysField/trameServer.py) 是统一运行适配器，九类场景共享会话和状态传输。
- [`timelineAnimation.py`](../../backend/modules/visPhysField/modules/fieldVisualization/timelineAnimation.py) 管 Miller 时序业务。
- [`visEngine`](../../backend/modules/visEngine/) 只提供过滤、种子、平面预览、默认 Light Kit、远程阴影、`physicalField.py`、`cache.py`、`performance.py` 的纯内核能力，不依赖 FastAPI、Trame Server、SQLite 或业务模块。

前端对应 [`frontend/src/modules/visPhysField/`](../../frontend/src/modules/visPhysField/)，二级模块共享 `PhysFieldProvider`、一级 API 与连接。

## 测试入口

- `backend/tests/modules/test_vis_phys_field.py`
- `backend/tests/modules/test_vis_engine.py`
- `backend/tests/test_miller_animation.py`
- 前端架构检查验证二级禁止项；Playwright 验证真实 Trame 交互与 Miller 播放。
