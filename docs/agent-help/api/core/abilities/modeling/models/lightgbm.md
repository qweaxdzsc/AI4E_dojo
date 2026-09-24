<!-- dojo-help: {"domain": "ai4e_core.abilities.modeling.models.lightgbm", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.modeling.models.lightgbm 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.modeling.models.lightgbm", "topic_id": "module:ai4e_core.abilities.modeling.models.lightgbm"} -->
# `ai4e_core.abilities.modeling.models.lightgbm` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-modeling-models-lightgbm-lightgbmpredictor"></a>
## `ai4e_core.abilities.modeling.models.lightgbm.LightGBMPredictor`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`LightGBMPredictor(*, model_strings, feature_names, target_names, params: dict, training_digest: str, backend_version: str)`
- **规范定义名**：`ai4e_core.abilities.modeling.models.lightgbm.LightGBMPredictor`

### 用途

每个目标一个官方回归Booster；预测输出始终为[N,Q]。

输入只接有限连续数值特征，列次序由调用方按feature_names显式保持。
不继承nn.Module，不提供梯度或概率方差。构造/读取不建树。

### 导入与签名

```python
from ai4e_core.abilities.modeling.models.lightgbm import LightGBMPredictor
```

```text
LightGBMPredictor(*, model_strings, feature_names, target_names, params: dict, training_digest: str, backend_version: str)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model_strings` | `未标注` | `必填关键字参数` |
| `feature_names` | `未标注` | `必填关键字参数` |
| `target_names` | `未标注` | `必填关键字参数` |
| `params` | `dict` | `必填关键字参数` |
| `training_digest` | `str` | `必填关键字参数` |
| `backend_version` | `str` | `必填关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`LightGBMPredictor`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FloatingPointError`, `TypeError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.models.lightgbm import LightGBMPredictor

print(signature(LightGBMPredictor))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.models.lightgbm`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/models/lightgbm.py:30`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.models.lightgbm')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-models-lightgbm-lightgbmpredictor-from-state"></a>
## `ai4e_core.abilities.modeling.models.lightgbm.LightGBMPredictor.from_state`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`from_state(cls, state: dict) -> LightGBMPredictor`
- **规范定义名**：`ai4e_core.abilities.modeling.models.lightgbm.LightGBMPredictor.from_state`

### 用途

严格版本/字段/模型次序读取；只恢复预测与原生轮次追加能力。

### 导入与签名

```python
from ai4e_core.abilities.modeling.models.lightgbm import LightGBMPredictor
```

```text
from_state(cls, state: dict) -> LightGBMPredictor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `state` | `dict` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`LightGBMPredictor`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.models.lightgbm import LightGBMPredictor

print(signature(LightGBMPredictor.from_state))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.models.lightgbm`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/models/lightgbm.py:133`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.models.lightgbm')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-models-lightgbm-lightgbmpredictor-get-state"></a>
## `ai4e_core.abilities.modeling.models.lightgbm.LightGBMPredictor.get_state`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`get_state(self) -> dict`
- **规范定义名**：`ai4e_core.abilities.modeling.models.lightgbm.LightGBMPredictor.get_state`

### 用途

交付模型文本、字段次序和接续元信息，不写文件或使用pickle。

### 导入与签名

```python
from ai4e_core.abilities.modeling.models.lightgbm import LightGBMPredictor
```

```text
get_state(self) -> dict
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.models.lightgbm import LightGBMPredictor

print(signature(LightGBMPredictor.get_state))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.models.lightgbm`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/models/lightgbm.py:116`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.models.lightgbm')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-models-lightgbm-lightgbmpredictor-iterations"></a>
## `ai4e_core.abilities.modeling.models.lightgbm.LightGBMPredictor.iterations`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`iterations(self) -> tuple[int, ...]`
- **规范定义名**：`ai4e_core.abilities.modeling.models.lightgbm.LightGBMPredictor.iterations`

### 用途

返回每个目标实际完成的原生轮次，不用请求轮次代替。

### 导入与签名

```python
from ai4e_core.abilities.modeling.models.lightgbm import LightGBMPredictor
```

```text
iterations(self) -> tuple[int, ...]
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`tuple[int, ...]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.models.lightgbm import LightGBMPredictor

print(signature(LightGBMPredictor.iterations))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.models.lightgbm`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/models/lightgbm.py:85`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.models.lightgbm')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-models-lightgbm-lightgbmpredictor-params"></a>
## `ai4e_core.abilities.modeling.models.lightgbm.LightGBMPredictor.params`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`params(self) -> dict`
- **规范定义名**：`ai4e_core.abilities.modeling.models.lightgbm.LightGBMPredictor.params`

### 用途

返回冻结有效参数的副本。

### 导入与签名

```python
from ai4e_core.abilities.modeling.models.lightgbm import LightGBMPredictor
```

```text
params(self) -> dict
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.models.lightgbm import LightGBMPredictor

print(signature(LightGBMPredictor.params))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`surrogate_modeling/double_cylinder`, `surrogate_modeling/nasa_crm`
- 案例：`recipe_extensions.operator_branch_replacement`, `recipe_extensions.pod_surrogate_replacement`, `surrogate_modeling.double_cylinder`, `surrogate_modeling.nasa_crm`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.models.lightgbm`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/models/lightgbm.py:80`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.models.lightgbm')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-models-lightgbm-lightgbmpredictor-predict"></a>
## `ai4e_core.abilities.modeling.models.lightgbm.LightGBMPredictor.predict`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`predict(self, x: Any) -> np.ndarray`
- **规范定义名**：`ai4e_core.abilities.modeling.models.lightgbm.LightGBMPredictor.predict`

### 用途

按冻结特征次序输入[N,D]，返回冻结目标次序的[N,Q]预测。

### 导入与签名

```python
from ai4e_core.abilities.modeling.models.lightgbm import LightGBMPredictor
```

```text
predict(self, x: Any) -> np.ndarray
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `Any` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`np.ndarray`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FloatingPointError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.models.lightgbm import LightGBMPredictor

print(signature(LightGBMPredictor.predict))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `pcno_cylinder`, `surrogate_modeling/double_cylinder`, `surrogate_modeling/nasa_crm`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.shapenet_car_abupt`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.pod_surrogate_replacement`, `recipe_extensions.sampling`, `recipe_extensions.wdno`, `surrogate_modeling.double_cylinder`, `surrogate_modeling.nasa_crm`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.models.lightgbm`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/models/lightgbm.py:89`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.models.lightgbm')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
