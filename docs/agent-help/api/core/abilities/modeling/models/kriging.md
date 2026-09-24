<!-- dojo-help: {"domain": "ai4e_core.abilities.modeling.models.kriging", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.modeling.models.kriging 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.modeling.models.kriging", "topic_id": "module:ai4e_core.abilities.modeling.models.kriging"} -->
# `ai4e_core.abilities.modeling.models.kriging` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-modeling-models-kriging-kriging"></a>
## `ai4e_core.abilities.modeling.models.kriging.Kriging`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`Kriging(training_x: Any, *, trend: PolynomialBasis, covariance: SquaredExponential, condition: KrigingCondition)`
- **规范定义名**：`ai4e_core.abilities.modeling.models.kriging.Kriging`

### 用途

单响应ordinary/universal克里金；不拟合、不存盘、不隐式标准化。

多输出由调用方有序组合独立模型，本对象不声明输出间协方差。
普通趋势对象可注入，但持久化首批只接受共享PolynomialBasis的0/1阶。

### 导入与签名

```python
from ai4e_core.abilities.modeling.models.kriging import Kriging
```

```text
Kriging(training_x: Any, *, trend: PolynomialBasis, covariance: SquaredExponential, condition: KrigingCondition)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `training_x` | `Any` | `必填` |
| `trend` | `PolynomialBasis` | `必填关键字参数` |
| `covariance` | `SquaredExponential` | `必填关键字参数` |
| `condition` | `KrigingCondition` | `必填关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Kriging`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`TypeError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.models.kriging import Kriging

print(signature(Kriging))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`surrogate_modeling/double_cylinder`, `surrogate_modeling/nasa_crm`
- 案例：`surrogate_modeling.double_cylinder`, `surrogate_modeling.nasa_crm`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.models.kriging`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/models/kriging.py:14`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.models.kriging')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-models-kriging-kriging-from-state"></a>
## `ai4e_core.abilities.modeling.models.kriging.Kriging.from_state`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`from_state(cls, state: dict) -> Kriging`
- **规范定义名**：`ai4e_core.abilities.modeling.models.kriging.Kriging.from_state`

### 用途

从普通状态重组同一公共组件；不读取旧数据目录或重新估计参数。

### 导入与签名

```python
from ai4e_core.abilities.modeling.models.kriging import Kriging
```

```text
from_state(cls, state: dict) -> Kriging
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `state` | `dict` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Kriging`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.models.kriging import Kriging

print(signature(Kriging.from_state))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.models.kriging`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/models/kriging.py:77`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.models.kriging')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-models-kriging-kriging-get-state"></a>
## `ai4e_core.abilities.modeling.models.kriging.Kriging.get_state`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`get_state(self) -> dict`
- **规范定义名**：`ai4e_core.abilities.modeling.models.kriging.Kriging.get_state`

### 用途

交付完整数值预测状态，不包含优化器的任意步恢复声明。

### 导入与签名

```python
from ai4e_core.abilities.modeling.models.kriging import Kriging
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

`TypeError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.models.kriging import Kriging

print(signature(Kriging.get_state))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.models.kriging`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/models/kriging.py:63`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.models.kriging')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-models-kriging-kriging-predict"></a>
## `ai4e_core.abilities.modeling.models.kriging.Kriging.predict`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`predict(self, x: Any, *, return_variance: bool=False, query_noise: Any=0.0) -> np.ndarray | tuple[np.ndarray, np.ndarray]`
- **规范定义名**：`ai4e_core.abilities.modeling.models.kriging.Kriging.predict`

### 用途

查询[N,D]特征，返回[N]均值及可选方差；噪声按当前输出单位平方声明。

### 导入与签名

```python
from ai4e_core.abilities.modeling.models.kriging import Kriging
```

```text
predict(self, x: Any, *, return_variance: bool=False, query_noise: Any=0.0) -> np.ndarray | tuple[np.ndarray, np.ndarray]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `Any` | `必填` |
| `return_variance` | `bool` | `False` |
| `query_noise` | `Any` | `0.0` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`np.ndarray | tuple[np.ndarray, np.ndarray]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.models.kriging import Kriging

print(signature(Kriging.predict))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `pcno_cylinder`, `surrogate_modeling/double_cylinder`, `surrogate_modeling/nasa_crm`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.shapenet_car_abupt`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.pod_surrogate_replacement`, `recipe_extensions.sampling`, `recipe_extensions.wdno`, `surrogate_modeling.double_cylinder`, `surrogate_modeling.nasa_crm`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.models.kriging`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/models/kriging.py:47`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.models.kriging')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
