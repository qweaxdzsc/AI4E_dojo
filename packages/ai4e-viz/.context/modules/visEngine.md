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

测试：[`test_vis_engine.py`](../../backend/tests/modules/test_vis_engine.py)、[`test_architecture.py`](../../backend/tests/test_architecture.py)与跨模块 [`test_excel_implemented_features.py`](../../backend/tests/test_excel_implemented_features.py)。业务云图、时序、任务参数和 Trame 状态必须留在 `visPhysField`。

## Dojo 当前实现文件

- `backend/modules/visEngine/__init__.py`：纯可视化内核公开门面。
- `backend/modules/visEngine/cache.py`：VTK内核对象的进程内有界缓存原语。
- `backend/modules/visEngine/filters.py`：VTK 过滤原语；流线消费统一种子，切面/剖切只收原点和法向。
- `backend/modules/visEngine/seeds.py`：由线段、球体、平面或外来表面构造种子；缺省按线段兼容旧起终点。新建默认起点按包围盒落在域内。
- `backend/modules/visEngine/planeWidget.py`：平面预览几何与拖动后的原点/法向，不执行切开。
- `backend/modules/visEngine/performance.py`：渲染数据抽样和性能优化纯函数。
- `backend/modules/visEngine/physicalField.py`：物理场底层数值内核。
- `backend/modules/visEngine/renderPasses.py`：远程渲染光照原语，平台支持由运行探测和验收决定。
- `backend/modules/visEngine/sampling.py`：空间插值与实体查询是两个独立的数值操作。
