<!-- dojo-help: {"domain": "ai4e_core.abilities.modeling.modules.covariance", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.modeling.modules.covariance 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.modeling.modules.covariance", "topic_id": "module:ai4e_core.abilities.modeling.modules.covariance"} -->
# `ai4e_core.abilities.modeling.modules.covariance` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-modeling-modules-covariance-krigingcondition"></a>
## `ai4e_core.abilities.modeling.modules.covariance.KrigingCondition`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`KrigingCondition(state: dict)`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.covariance.KrigingCondition`

### 用途

消费已求解条件状态，独立计算未知趋势克里金均值和方差。

构造与读取只校验状态，不做GLS、矩阵分解或超参数优化。预测使用已存
Cholesky因子作三角求解。条件方差不含超参数估计的不确定性。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.covariance import KrigingCondition
```

```text
KrigingCondition(state: dict)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `state` | `dict` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`KrigingCondition`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FloatingPointError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.covariance import KrigingCondition

print(signature(KrigingCondition))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.covariance`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/covariance.py:73`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.covariance')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-covariance-krigingcondition-from-state"></a>
## `ai4e_core.abilities.modeling.modules.covariance.KrigingCondition.from_state`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`from_state(cls, state: dict) -> KrigingCondition`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.covariance.KrigingCondition.from_state`

### 用途

校验并读取固定条件状态，不触发重新拟合。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.covariance import KrigingCondition
```

```text
from_state(cls, state: dict) -> KrigingCondition
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `state` | `dict` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`KrigingCondition`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.covariance import KrigingCondition

print(signature(KrigingCondition.from_state))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.covariance`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/covariance.py:195`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.covariance')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-covariance-krigingcondition-get-state"></a>
## `ai4e_core.abilities.modeling.modules.covariance.KrigingCondition.get_state`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`get_state(self) -> dict`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.covariance.KrigingCondition.get_state`

### 用途

返回独立数组副本；外部修改不影响已有预测状态。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.covariance import KrigingCondition
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
from ai4e_core.abilities.modeling.modules.covariance import KrigingCondition

print(signature(KrigingCondition.get_state))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.covariance`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/covariance.py:190`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.covariance')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-covariance-krigingcondition-predict"></a>
## `ai4e_core.abilities.modeling.modules.covariance.KrigingCondition.predict`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`predict(self, cross_covariance: Any, query_diagonal: Any, query_trend: Any, *, return_variance: bool=False, query_noise: Any=0.0) -> np.ndarray | tuple[np.ndarray, np.ndarray]`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.covariance.KrigingCondition.predict`

### 用途

给定[M,N]交叉协方差、[M]自身方差和[M,P]趋势返回[M]预测。

默认方差为潜在响应；显式query_noise为[M]或标量观测噪声方差。
jitter仅影响训练分解，绝不自动添加到查询方差。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.covariance import KrigingCondition
```

```text
predict(self, cross_covariance: Any, query_diagonal: Any, query_trend: Any, *, return_variance: bool=False, query_noise: Any=0.0) -> np.ndarray | tuple[np.ndarray, np.ndarray]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cross_covariance` | `Any` | `必填` |
| `query_diagonal` | `Any` | `必填` |
| `query_trend` | `Any` | `必填` |
| `return_variance` | `bool` | `False` |
| `query_noise` | `Any` | `0.0` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`np.ndarray | tuple[np.ndarray, np.ndarray]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FloatingPointError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.covariance import KrigingCondition

print(signature(KrigingCondition.predict))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `pcno_cylinder`, `surrogate_modeling/double_cylinder`, `surrogate_modeling/nasa_crm`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.shapenet_car_abupt`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.pod_surrogate_replacement`, `recipe_extensions.sampling`, `recipe_extensions.wdno`, `surrogate_modeling.double_cylinder`, `surrogate_modeling.nasa_crm`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.covariance`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/covariance.py:140`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.covariance')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-covariance-squaredexponential"></a>
## `ai4e_core.abilities.modeling.modules.covariance.SquaredExponential`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`SquaredExponential(length_scale: Any=1.0, variance: float=1.0)`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.covariance.SquaredExponential`

### 用途

各向异性平方指数协方差：variance*exp(-0.5*sum((dx/length_scale)^2))。

variance为过程方差；不添加观测噪声、扰动或隐式特征缩放。
length_scale接受正标量或每个特征的正尺度；普通数组输入输出。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.covariance import SquaredExponential
```

```text
SquaredExponential(length_scale: Any=1.0, variance: float=1.0)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `length_scale` | `Any` | `1.0` |
| `variance` | `float` | `1.0` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`SquaredExponential`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.covariance import SquaredExponential

print(signature(SquaredExponential))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.covariance`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/covariance.py:21`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.covariance')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-covariance-squaredexponential-diagonal"></a>
## `ai4e_core.abilities.modeling.modules.covariance.SquaredExponential.diagonal`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`diagonal(self, x: Any) -> np.ndarray`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.covariance.SquaredExponential.diagonal`

### 用途

返回每个查询点的自身过程方差，不包含任何噪声或扰动。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.covariance import SquaredExponential
```

```text
diagonal(self, x: Any) -> np.ndarray
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `Any` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`np.ndarray`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.covariance import SquaredExponential

print(signature(SquaredExponential.diagonal))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.covariance`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/covariance.py:45`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.covariance')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-covariance-squaredexponential-from-state"></a>
## `ai4e_core.abilities.modeling.modules.covariance.SquaredExponential.from_state`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`from_state(cls, state: dict) -> SquaredExponential`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.covariance.SquaredExponential.from_state`

### 用途

读取显式版本和参数；不拟合也不恢复任意可执行对象。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.covariance import SquaredExponential
```

```text
from_state(cls, state: dict) -> SquaredExponential
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `state` | `dict` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`SquaredExponential`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.covariance import SquaredExponential

print(signature(SquaredExponential.from_state))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.covariance`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/covariance.py:62`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.covariance')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-covariance-squaredexponential-get-state"></a>
## `ai4e_core.abilities.modeling.modules.covariance.SquaredExponential.get_state`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`get_state(self) -> dict`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.covariance.SquaredExponential.get_state`

### 用途

返回可由外部保存的独立数值状态；本对象不写文件。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.covariance import SquaredExponential
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
from ai4e_core.abilities.modeling.modules.covariance import SquaredExponential

print(signature(SquaredExponential.get_state))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.covariance`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/covariance.py:52`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.covariance')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
