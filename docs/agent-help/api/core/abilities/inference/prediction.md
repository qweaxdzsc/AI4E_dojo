<!-- dojo-help: {"domain": "ai4e_core.abilities.inference.prediction", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.inference.prediction 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.inference.prediction", "topic_id": "module:ai4e_core.abilities.inference.prediction"} -->
# `ai4e_core.abilities.inference.prediction` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-inference-prediction-named-array-batch"></a>
## `ai4e_core.abilities.inference.prediction.named_array_batch`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`named_array_batch(arrays, ids, *, device, names)`
- **规范定义名**：`ai4e_core.abilities.inference.prediction.named_array_batch`

### 用途

具名数组按同一索引取批，始终转换 float32 并保持字段对齐。

### 导入与签名

```python
from ai4e_core.abilities.inference.prediction import named_array_batch
```

```text
named_array_batch(arrays, ids, *, device, names)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `arrays` | `未标注` | `必填` |
| `ids` | `未标注` | `必填` |
| `device` | `未标注` | `必填关键字参数` |
| `names` | `未标注` | `必填关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.inference.prediction import named_array_batch

print(signature(named_array_batch))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`geotransolver/bumper_beam`, `geotransolver/darcy`
- 案例：`geotransolver.bumper_beam`, `geotransolver.darcy`

### 源码位置

- 模块：`ai4e_core.abilities.inference.prediction`
- 仓库相对路径：`packages/ai4e-core/abilities/inference/prediction.py:17`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.inference.prediction')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-inference-prediction-predict"></a>
## `ai4e_core.abilities.inference.prediction.predict`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`predict(model, inputs: Any, *args: Any, operation: Callable, preserve_rng: bool=True, **kwargs) -> Any`
- **规范定义名**：`ai4e_core.abilities.inference.prediction.predict`

### 用途

调用注入的预测函数，禁止梯度并恢复模式；不改写函数的输出语义。

### 导入与签名

```python
from ai4e_core.abilities.inference.prediction import predict
```

```text
predict(model, inputs: Any, *args: Any, operation: Callable, preserve_rng: bool=True, **kwargs) -> Any
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model` | `未标注` | `必填` |
| `inputs` | `Any` | `必填` |
| `*args` | `Any` | `可变位置参数` |
| `operation` | `Callable` | `必填关键字参数` |
| `preserve_rng` | `bool` | `True` |
| `**kwargs` | `未标注` | `可变关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Any`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.inference.prediction import predict

print(signature(predict))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `pcno_cylinder`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.sampling`, `recipe_extensions.wdno`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_core.abilities.inference.prediction`
- 仓库相对路径：`packages/ai4e-core/abilities/inference/prediction.py:9`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.inference.prediction')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-inference-prediction-predict-named-batches"></a>
## `ai4e_core.abilities.inference.prediction.predict_named_batches`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`predict_named_batches(model, count, batch, *, input_names, decode, batch_size)`
- **规范定义名**：`ai4e_core.abilities.inference.prediction.predict_named_batches`

### 用途

包含不足整批的末批，恢复模型模式及随机状态，返回 CPU 张量。

### 导入与签名

```python
from ai4e_core.abilities.inference.prediction import predict_named_batches
```

```text
predict_named_batches(model, count, batch, *, input_names, decode, batch_size)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model` | `未标注` | `必填` |
| `count` | `未标注` | `必填` |
| `batch` | `未标注` | `必填` |
| `input_names` | `未标注` | `必填关键字参数` |
| `decode` | `未标注` | `必填关键字参数` |
| `batch_size` | `未标注` | `必填关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.inference.prediction import predict_named_batches

print(signature(predict_named_batches))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.inference.prediction`
- 仓库相对路径：`packages/ai4e-core/abilities/inference/prediction.py:31`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.inference.prediction')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
