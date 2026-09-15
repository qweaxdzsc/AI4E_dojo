# dataAssets 文件索引

职责：资产登记、上传、SHA-256去重、列表/详情、分类版本、原始文件定位，以及`artifacts`和`artifact_classification_history`表。PRD：[`dataAssets.md`](../../docs/PRD/dataAssets.md)。

## 模块设计

`dataAssets`是资产生命周期聚合根和文件所有权边界。上传、去重、资产状态、分类历史与文件落盘在同一应用事务中编排；SQLite表和写入只由本模块Repository处理。`visDatasets`可以通过公开门面返回解析/画像结果，但不得反向拥有资产表。前端详情Page通过各模块`index.js`组合本模块资产对象、`visDatasets`分析和`visTaskManage`推荐。

## 后端文件

| 文件 | 作用 |
| --- | --- |
| [`__init__.py`](../../backend/modules/dataAssets/__init__.py) | 跨模块唯一公开门面 |
| [`api.py`](../../backend/modules/dataAssets/api.py) | 资产列表、详情、分类、文件与上传Router |
| [`application.py`](../../backend/modules/dataAssets/application.py) | 资产生命周期、去重、文件登记及跨visDatasets分析编排 |
| [`repository.py`](../../backend/modules/dataAssets/repository.py) | 资产表、分类历史、SQL映射与上传字节原子落盘 |

## 前端文件

| 文件 | 作用 |
| --- | --- |
| [`index.js`](../../frontend/src/modules/dataAssets/index.js) | 页面与资产读取能力公开门面 |
| [`module.js`](../../frontend/src/modules/dataAssets/module.js) | 数据资产导航与路由元数据 |
| [`model.js`](../../frontend/src/modules/dataAssets/model.js) | 数据资产DTO到前端实体转换 |
| [`api.js`](../../frontend/src/modules/dataAssets/api.js) | 列表、详情、分类和上传API防腐层 |
| [`pages/DataAssets.jsx`](../../frontend/src/modules/dataAssets/pages/DataAssets.jsx) | 数据资产列表、筛选、统计与上传业务视图 |
| [`pages/DataAssetsPage.jsx`](../../frontend/src/modules/dataAssets/pages/DataAssetsPage.jsx) | 列表路由页面壳 |
| [`pages/ArtifactDetail.jsx`](../../frontend/src/modules/dataAssets/pages/ArtifactDetail.jsx) | 资产详情聚合页，组合visDatasets分析与visTaskManage推荐 |
| [`pages/ArtifactDetailPage.jsx`](../../frontend/src/modules/dataAssets/pages/ArtifactDetailPage.jsx) | 详情路由页面壳 |

测试：[`test_data_assets.py`](../../backend/tests/modules/test_data_assets.py)、[`test_contract.py`](../../backend/tests/test_contract.py)、[`contracts.test.jsx`](../../frontend/src/test/contracts.test.jsx)与上传推荐/Excel功能E2E；Excel专项通过真实资产进入预览、保存和报告引用链路。

## Dojo 当前实现文件

- `backend/modules/dataAssets/__init__.py`：数据资产一级模块公开门面。
- `backend/modules/dataAssets/api.py`：数据资产列表、详情、分类、文件读取和上传的HTTP适配层。
- `backend/modules/dataAssets/application.py`：数据资产登记、上传、分类和文件定位的应用用例。
- `backend/modules/dataAssets/externalSources.py`：外部来源是只读绑定，实际位置只存在运行上下文，不进入保存配置。
- `backend/modules/dataAssets/repository.py`：数据资产元数据、分类历史和画像结果Repository实现。
- `frontend/src/modules/dataAssets/api.js`：独立应用交互与调用适配。
- `frontend/src/modules/dataAssets/index.js`：独立应用交互与调用适配。
- `frontend/src/modules/dataAssets/model.js`：独立应用交互与调用适配。
- `frontend/src/modules/dataAssets/module.js`：独立应用交互与调用适配。
- `frontend/src/modules/dataAssets/pages/ArtifactDetail.jsx`：独立应用交互与调用适配。
- `frontend/src/modules/dataAssets/pages/ArtifactDetailPage.jsx`：独立应用交互与调用适配。
- `frontend/src/modules/dataAssets/pages/DataAssets.jsx`：独立应用交互与调用适配。
- `frontend/src/modules/dataAssets/pages/DataAssetsPage.jsx`：独立应用交互与调用适配。
