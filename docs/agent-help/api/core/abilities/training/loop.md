<!-- dojo-help: {"domain": "ai4e_core.abilities.training.loop", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.training.loop 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.training.loop", "topic_id": "module:ai4e_core.abilities.training.loop"} -->
# `ai4e_core.abilities.training.loop` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-training-loop-fit"></a>
## `ai4e_core.abilities.training.loop.fit`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`fit(model, optimizer, batches, step, evaluate, run, *, config, contract, ema=None, scaler=None, scheduler=None, evaluate_repeat=None, callbacks=(), preserve_selection=False)`
- **规范定义名**：`ai4e_core.abilities.training.loop.fit`

### 用途

组织一次可恢复训练；业务与模型通过显式调用接口注入。

### 导入与签名

```python
from ai4e_core.abilities.training.loop import fit
```

```text
fit(model, optimizer, batches, step, evaluate, run, *, config, contract, ema=None, scaler=None, scheduler=None, evaluate_repeat=None, callbacks=(), preserve_selection=False)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model` | `未标注` | `必填` |
| `optimizer` | `未标注` | `必填` |
| `batches` | `未标注` | `必填` |
| `step` | `未标注` | `必填` |
| `evaluate` | `未标注` | `必填` |
| `run` | `未标注` | `必填` |
| `config` | `未标注` | `必填关键字参数` |
| `contract` | `未标注` | `必填关键字参数` |
| `ema` | `未标注` | `None` |
| `scaler` | `未标注` | `None` |
| `scheduler` | `未标注` | `None` |
| `evaluate_repeat` | `未标注` | `None` |
| `callbacks` | `未标注` | `()` |
| `preserve_selection` | `未标注` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`InterruptedError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.training.loop import fit

print(signature(fit))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`, `surrogate_modeling/double_cylinder`, `surrogate_modeling/nasa_crm`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `recipe_extensions.field_mapping`, `recipe_extensions.pod_surrogate_replacement`, `recipe_extensions.sampling`, `surrogate_modeling.double_cylinder`, `surrogate_modeling.nasa_crm`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_core.abilities.training.loop`
- 仓库相对路径：`packages/ai4e-core/abilities/training/loop.py:19`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.loop')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
