# visDatasets 文件索引

职责：格式解析、数据画像、质量体检、统计和数据内容查看；不拥有资产表、上传或资产页面。PRD：[`visDatasets.md`](../../docs/PRD/visDatasets.md)。

## 模块设计

`visDatasets`是数据内容理解限界上下文，不是资产目录。解析器、画像、质量问题和值统计属于本模块Domain/Application；需要保存分析结果时经`dataAssets.__init__`公开用例回写，不建立本模块资产Repository。前端只暴露分析API供资产详情等聚合Page使用，不拥有数据资产路由。

## 后端文件

| 文件 | 作用 |
| --- | --- |
| [`__init__.py`](../../backend/modules/visDatasets/__init__.py) | 数据集解析能力公开门面 |
| [`api.py`](../../backend/modules/visDatasets/api.py) | 显式解析、分析和G-S fixture Router |
| [`application.py`](../../backend/modules/visDatasets/application.py) | 数据体检应用门面 |
| [`domain.py`](../../backend/modules/visDatasets/domain.py) | 数据质量问题领域定义 |
| [`inspection.py`](../../backend/modules/visDatasets/inspection.py) | 文件体检、数据质量和统计检测 |
| [`pipeline.py`](../../backend/modules/visDatasets/pipeline.py) | 多格式解析、画像、语义推断和结构化管线；通过dataAssets公开门面保存结果 |

## 前端文件

| 文件 | 作用 |
| --- | --- |
| [`index.js`](../../frontend/src/modules/visDatasets/index.js) | 解析与画像能力公开门面 |
| [`module.js`](../../frontend/src/modules/visDatasets/module.js) | 无独立页面的模块注册元数据 |
| [`api.js`](../../frontend/src/modules/visDatasets/api.js) | 显式解析和重新分析API |

测试：[`test_vis_datasets.py`](../../backend/tests/modules/test_vis_datasets.py)、[`test_contract.py`](../../backend/tests/test_contract.py)、[`test_excel_implemented_features.py`](../../backend/tests/test_excel_implemented_features.py)及数据资产详情页/Excel功能E2E。

## Dojo 当前实现文件

- `backend/modules/visDatasets/__init__.py`：数据集解析、画像、体检、统计和内容查看模块公开入口。
- `backend/modules/visDatasets/api.py`：数据集解析、画像和质量检测的HTTP适配层。
- `backend/modules/visDatasets/application.py`：数据集解析、画像和检测用例的应用门面。
- `backend/modules/visDatasets/domain.py`：数据格式、数据语义、画像与检测状态的领域定义。
- `backend/modules/visDatasets/inspection.py`：数据集业务检测入口，与服务健康检查严格分离。
- `backend/modules/visDatasets/physicalDataset.py`：完整网格、显式点云和时间数据读取；列出授权文件中的命名二维块与文字分区，不合并多块。命名块按路径、阅读器和修改时间缓存。
- `backend/modules/visDatasets/pipeline.py`：数据集文件解析、画像、检测和可视化推荐的数据处理管线。
- `frontend/src/modules/visDatasets/api.js`：独立应用交互与调用适配。
- `frontend/src/modules/visDatasets/index.js`：独立应用交互与调用适配。
- `frontend/src/modules/visDatasets/module.js`：独立应用交互与调用适配。
