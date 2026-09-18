# dataOverview 文件索引

职责：二维表格、基础图表和多维云图概览，共享一级 API、Provider 与数据状态。

## 二级模块设计

本模块负责把物理场结果组织为表格和图表所需的业务视图模型，不拥有通用Renderer基座，也不建立独立网络层。后端由一级Application提供数据和错误上下文，前端组件经一级Provider读取同一会话状态；无业务含义的图表技术适配仍归前端Infrastructure。

## 后端文件

| 文件 | 作用 |
| --- | --- |
| [`__init__.py`](../../../backend/modules/visPhysField/modules/dataOverview/__init__.py) | 二级包内部聚合 |
| [`table.py`](../../../backend/modules/visPhysField/modules/dataOverview/table.py) | 二维表格数据组织 |
| [`basicCharts.py`](../../../backend/modules/visPhysField/modules/dataOverview/basicCharts.py) | 散点、折线、柱状图与沿线弧长侧栏缩略图 |
| [`lineChart.py`](../../../backend/modules/visPhysField/modules/dataOverview/lineChart.py) | Line Chart View 的 X/Y 轴、视口折线标记与 CSV |
| [`multiDimensionalCloud.py`](../../../backend/modules/visPhysField/modules/dataOverview/multiDimensionalCloud.py) | 多维云图数据映射 |

## 前端文件

| 文件 | 作用 |
| --- | --- |
| [`model.js`](../../../frontend/src/modules/visPhysField/modules/dataOverview/model.js) | 概览类型、列和图表模型 |
| [`hooks/useDataOverview.js`](../../../frontend/src/modules/visPhysField/modules/dataOverview/hooks/useDataOverview.js) | 通过一级状态编排概览 Query |
| [`components/DataOverviewTable.jsx`](../../../frontend/src/modules/visPhysField/modules/dataOverview/components/DataOverviewTable.jsx) | 当前二维表格展现组件 |

测试：[`test_vis_phys_field.py`](../../../backend/tests/modules/test_vis_phys_field.py)、前端契约与工作区 E2E。
