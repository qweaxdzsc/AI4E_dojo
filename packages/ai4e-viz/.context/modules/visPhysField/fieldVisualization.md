# fieldVisualization 文件索引

职责：视角、云图、矢量、切面/流线/等值分析、Probe、色带、显示样式、时序、动画与多结果。

## 二级模块设计

本模块只实现物理场“如何显示和交互”的业务规则，不拥有独立Router、Application、Repository、URL或Trame Server。后端命令由一级Application调度，纯计算按需调用`visEngine`；前端Hook和Component全部消费一级API/Provider/Store，不建立独立公开门面。

## 后端文件

| 文件 | 作用 |
| --- | --- |
| [`__init__.py`](../../../backend/modules/visPhysField/modules/fieldVisualization/__init__.py) | 二级包内部聚合，不作为跨一级模块门面 |
| [`view.py`](../../../backend/modules/visPhysField/modules/fieldVisualization/view.py) | 旋转、平移、缩放、视图和适窗命令 |
| [`scalarCloud.py`](../../../backend/modules/visPhysField/modules/fieldVisualization/scalarCloud.py) | 标量云图业务规则 |
| [`vectorField.py`](../../../backend/modules/visPhysField/modules/fieldVisualization/vectorField.py) | 矢量图业务规则 |
| [`cutAnalysis.py`](../../../backend/modules/visPhysField/modules/fieldVisualization/cutAnalysis.py) | 切面、流线、等值面和等高线分析；流线可另交种子网格 |
| [`probe.py`](../../../backend/modules/visPhysField/modules/fieldVisualization/probe.py) | Probe 查询与取值规则 |
| [`colorMapping.py`](../../../backend/modules/visPhysField/modules/fieldVisualization/colorMapping.py) | 色带、层数与范围配置 |
| [`displayStyle.py`](../../../backend/modules/visPhysField/modules/fieldVisualization/displayStyle.py) | 透明度、面/网格、光照和阴影样式 |
| [`timeline.py`](../../../backend/modules/visPhysField/modules/fieldVisualization/timeline.py) | 时序播放命令与状态 |
| [`timelineAnimation.py`](../../../backend/modules/visPhysField/modules/fieldVisualization/timelineAnimation.py) | Miller 时序拓扑复用和动画控制 |
| [`animation.py`](../../../backend/modules/visPhysField/modules/fieldVisualization/animation.py) | 动画录制业务配置 |
| [`multiResult.py`](../../../backend/modules/visPhysField/modules/fieldVisualization/multiResult.py) | 多结果、多窗口、全体相机联动与显隐 |

## 前端文件

| 文件 | 作用 |
| --- | --- |
| [`model.js`](../../../frontend/src/modules/visPhysField/modules/fieldVisualization/model.js) | 显示状态和值对象 |
| [`hooks/useFieldView.js`](../../../frontend/src/modules/visPhysField/modules/fieldVisualization/hooks/useFieldView.js) | 通过一级 usePhysField 编排视图命令 |
| [`components/ViewControls.jsx`](../../../frontend/src/modules/visPhysField/modules/fieldVisualization/components/ViewControls.jsx) | 当前视角和场显示控制面板 |

测试：[`test_vis_phys_field.py`](../../../backend/tests/modules/test_vis_phys_field.py)、[`test_miller_animation.py`](../../../backend/tests/test_miller_animation.py)、前端契约与 Trame E2E。
