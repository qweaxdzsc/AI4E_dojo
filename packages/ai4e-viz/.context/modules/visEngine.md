# visEngine 文件索引

职责：无业务含义的 VTK/数值内核、缓存和性能原语；无前端、Router、Repository、URL、任务和报告语义。PRD：[`visEngine.md`](../../docs/PRD/visEngine.md)。

## 模块设计

`visEngine`不是产品业务限界上下文的承载层，而是受严格约束的纯内核模块。公开函数必须对输入输出、单位和性能边界有明确约定，并保持无网络、无数据库、无Trame Server和无业务状态；`visPhysField`等调用方负责把业务命令转换为内核参数。云图、时序和显示配置即使依赖VTK，也不得下沉到这里。

| 后端文件 | 作用 |
| --- | --- |
| [`__init__.py`](../../backend/modules/visEngine/__init__.py) | 纯内核公开门面 |
| [`physicalField.py`](../../backend/modules/visEngine/physicalField.py) | 物理场数组/标量纯计算原语 |
| [`cache.py`](../../backend/modules/visEngine/cache.py) | 有界内核缓存和淘汰策略 |
| [`performance.py`](../../backend/modules/visEngine/performance.py) | 抽样与性能辅助纯函数 |
| [`seeds.py`](../../backend/modules/visEngine/seeds.py) | 线段/球体/平面/表面种子与文字分区抽取 |
| [`planeWidget.py`](../../backend/modules/visEngine/planeWidget.py) | 切面可视平面片、三轴手柄、旋转环与拖动算术 |
| [`seedWidget.py`](../../backend/modules/visEngine/seedWidget.py) | 流线种子手柄几何仍保留；本期工作台不绑定拖动 |
| [`lineWidget.py`](../../backend/modules/visEngine/lineWidget.py) | 线段提取两端手柄几何 |

测试：[`test_vis_engine.py`](../../backend/tests/modules/test_vis_engine.py)、[`test_architecture.py`](../../backend/tests/test_architecture.py)、[`test_phys_filters.py`](../../backend/tests/modules/test_phys_filters.py)、[`test_phys_plot_over_line.py`](../../backend/tests/modules/test_phys_plot_over_line.py)与跨模块 [`test_excel_implemented_features.py`](../../backend/tests/test_excel_implemented_features.py)。业务云图、时序、任务参数和 Trame 状态必须留在 `visPhysField`。

## Dojo 当前实现文件

- `backend/modules/visEngine/__init__.py`：纯可视化内核公开门面。
- `backend/modules/visEngine/cache.py`：VTK内核对象的进程内有界缓存原语。
- `backend/modules/visEngine/filters.py`：VTK 过滤原语；流线消费统一种子，切面/剖切按皱折与三角化分支；标量着色按数据/字段修改状态与分量有界缓存。流线显示可将折线保持为线或生成圆管（半径、圆周面数）。
- `backend/modules/visEngine/seeds.py`：由线段、球体、平面或外来表面构造种子；缺省按线段兼容旧起终点。新建默认起点按包围盒落在域内。
- `backend/modules/visEngine/planeWidget.py`：平面预览几何与拖动后的原点/法向，不执行切开。
- `backend/modules/visEngine/seedWidget.py`：种子手柄几何仍保留，本期不向工作台提供拖动。
- `backend/modules/visEngine/lineWidget.py`：线段两端手柄几何，只回填端点。
- `backend/modules/visEngine/performance.py`：渲染数据抽样和性能优化纯函数。
- `backend/modules/visEngine/physicalField.py`：物理场底层数值内核。
- `backend/modules/visEngine/renderPasses.py`：ParaView/VTK 默认 Light Kit（五灯、强度与方位）及 Linux 远程阴影通道；阴影默认关。
- `backend/modules/visEngine/sampling.py`：空间插值、实体查询与沿线等距采样；沿线返回弧长和各场数值。


`planeWidget.py`：灰白辅助平面、三轴箭头和三轴旋转环；`filters.py`：自动等高线及等值标量保留。

`seeds.py`：球面种子使用独立固定随机序列，预览和积分逐点一致。

2026-09-16 显示设置：对应模块 PRD 已更新色标/范围/背景、矢量采样或透明输出职责。专项测试 `backend/tests/modules/test_phys_display_settings.py`；前端透明表单 `frontend/src/test/transparentExport.test.jsx`，真实入口 `tests/integration/viz_interaction_browser.cjs`（Dojo 根）。
