<!-- dojo-help: {"domain": "ai4e_core.abilities.eval.evaluation", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.eval.evaluation 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.eval.evaluation", "topic_id": "module:ai4e_core.abilities.eval.evaluation"} -->
# `ai4e_core.abilities.eval.evaluation` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-eval-evaluation-evaluate"></a>
## `ai4e_core.abilities.eval.evaluation.evaluate`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`evaluate(model, batches, predict, objectives, normalization, *, preserve_rng: bool=True, batch_context=None, metric_names=None) -> dict`
- **规范定义名**：`ai4e_core.abilities.eval.evaluation.evaluate`

### 用途

一次前向计算总分、加权分项和 metric_names 指定的物理指标。

metric_names=None 保留原三项，空序列仅计算损失；未知或重复项在
前向前抛 ValueError。返回格式不变，未选项不进入 metrics。

### 导入与签名

```python
from ai4e_core.abilities.eval.evaluation import evaluate
```

```text
evaluate(model, batches, predict, objectives, normalization, *, preserve_rng: bool=True, batch_context=None, metric_names=None) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model` | `未标注` | `必填` |
| `batches` | `未标注` | `必填` |
| `predict` | `未标注` | `必填` |
| `objectives` | `未标注` | `必填` |
| `normalization` | `未标注` | `必填` |
| `preserve_rng` | `bool` | `True` |
| `batch_context` | `未标注` | `None` |
| `metric_names` | `未标注` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.eval.evaluation import evaluate

print(signature(evaluate))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`, `safediffcon`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.sampling`, `recipe_extensions.wdno`, `safediffcon.burgers`, `safediffcon.tokamak`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_core.abilities.eval.evaluation`
- 仓库相对路径：`packages/ai4e-core/abilities/eval/evaluation.py:14`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.eval.evaluation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
