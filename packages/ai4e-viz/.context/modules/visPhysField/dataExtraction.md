# dataExtraction 文件索引

职责：点、线、面、体空间提取，时序提取和聚合提取，共享一级持久化与 Trame 会话。

## 二级模块设计

本模块围绕提取范围、采样方式和提取结果表达业务规则；空间、时序和聚合文件是同一二级能力的内部拆分。提取命令、事务、结果持久化和Trame状态统一由`visPhysField`一级Application/Repository/会话负责，前端只经一级API与Provider发出命令。

## 后端文件

| 文件 | 作用 |
| --- | --- |
| [`__init__.py`](../../../backend/modules/visPhysField/modules/dataExtraction/__init__.py) | 二级包内部聚合 |
| [`spatial.py`](../../../backend/modules/visPhysField/modules/dataExtraction/spatial.py) | 点/线/面/体空间提取规则 |
| [`temporal.py`](../../../backend/modules/visPhysField/modules/dataExtraction/temporal.py) | 时序提取规则 |
| [`aggregate.py`](../../../backend/modules/visPhysField/modules/dataExtraction/aggregate.py) | 聚合提取规则 |

## 前端文件

| 文件 | 作用 |
| --- | --- |
| [`model.js`](../../../frontend/src/modules/visPhysField/modules/dataExtraction/model.js) | 提取范围、方式和结果模型 |
| [`hooks/useDataExtraction.js`](../../../frontend/src/modules/visPhysField/modules/dataExtraction/hooks/useDataExtraction.js) | 通过一级 API/Provider 编排提取命令 |
| [`components/DataExtractionPanel.jsx`](../../../frontend/src/modules/visPhysField/modules/dataExtraction/components/DataExtractionPanel.jsx) | 数据提取参数与结果面板 |

测试：[`test_vis_phys_field.py`](../../../backend/tests/modules/test_vis_phys_field.py)、[`test_phys_plot_over_line.py`](../../../backend/tests/modules/test_phys_plot_over_line.py)、前端契约与 Trame E2E。工作台线段提取走一级 `commands.py` 的 `plot_over_line`、`extractionPanel.py` 与视口 Line Chart View。
