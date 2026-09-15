# visGeometry 文件索引

职责：几何表现、视角归一化和 O3DV 适配。PRD：[`visGeometry.md`](../../docs/PRD/visGeometry.md)。

## 模块设计

`visGeometry`拥有几何表现与交互语义，O3DV只是模块专属出站适配器。Application通过`dataAssets`取得受控文件、按需调用`visConvertor`公开用例，再产出O3DV表现；转换器实现和原始资产持久化不进入本模块。前端以可复用GeometryViewer为主，当前无需为凑结构建立独立Page。

## 后端文件

| 文件 | 作用 |
| --- | --- |
| [`__init__.py`](../../backend/modules/visGeometry/__init__.py) | 几何公开应用门面 |
| [`api.py`](../../backend/modules/visGeometry/api.py) | GLB 与表现 Router |
| [`application.py`](../../backend/modules/visGeometry/application.py) | 数据集文件、转换器和表现用例编排 |
| [`domain.py`](../../backend/modules/visGeometry/domain.py) | 几何视角、格式和表现规则 |
| [`o3dv.py`](../../backend/modules/visGeometry/o3dv.py) | O3DV GLB 派生与静态降级适配 |

## 前端文件

| 文件 | 作用 |
| --- | --- |
| [`index.js`](../../frontend/src/modules/visGeometry/index.js) | GeometryViewer 与 URL 公开门面 |
| [`module.js`](../../frontend/src/modules/visGeometry/module.js) | 无主导航的模块元数据 |
| [`model.js`](../../frontend/src/modules/visGeometry/model.js) | 几何表现与查看状态模型 |
| [`api.js`](../../frontend/src/modules/visGeometry/api.js) | O3DV/表现 Endpoint 和 DTO 转换 |
| [`components/GeometryViewer.jsx`](../../frontend/src/modules/visGeometry/components/GeometryViewer.jsx) | 自托管 O3DV 几何查看组件 |

测试：[`test_vis_geometry.py`](../../backend/tests/modules/test_vis_geometry.py)、[`test_contract.py`](../../backend/tests/test_contract.py)、[`test_excel_implemented_features.py`](../../backend/tests/test_excel_implemented_features.py) 和Excel功能E2E。


## Dojo 当前实现文件

- `backend/modules/visGeometry/__init__.py`：几何可视化一级模块的公开门面。
- `backend/modules/visGeometry/api.py`：几何可视化及 O3DV 派生表现的 HTTP 适配层。
- `backend/modules/visGeometry/application.py`：几何视角、选择、隐藏、剖切、外观和测量用例编排。
- `backend/modules/visGeometry/domain.py`：几何可视化领域对象和纯业务规则。
- `backend/modules/visGeometry/o3dv.py`：O3DV模块专属适配器。
- `frontend/src/modules/visGeometry/api.js`：独立应用交互与调用适配。
- `frontend/src/modules/visGeometry/components/GeometryViewer.jsx`：独立应用交互与调用适配。
- `frontend/src/modules/visGeometry/index.js`：独立应用交互与调用适配。
- `frontend/src/modules/visGeometry/model.js`：独立应用交互与调用适配。
- `frontend/src/modules/visGeometry/module.js`：独立应用交互与调用适配。
