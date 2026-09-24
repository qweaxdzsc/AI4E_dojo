<!-- dojo-help: {"domain": "ai4e_core.abilities.modeling.modules.polynomial", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.modeling.modules.polynomial 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.modeling.modules.polynomial", "topic_id": "module:ai4e_core.abilities.modeling.modules.polynomial"} -->
# `ai4e_core.abilities.modeling.modules.polynomial` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-modeling-modules-polynomial-polynomialbasis"></a>
## `ai4e_core.abilities.modeling.modules.polynomial.PolynomialBasis`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`PolynomialBasis(input_dim: int, degree: int, include_bias: bool=True)`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.polynomial.PolynomialBasis`

### 用途

无需拟合的参数基；常数、一次、二次按组合索引排序。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.polynomial import PolynomialBasis
```

```text
PolynomialBasis(input_dim: int, degree: int, include_bias: bool=True)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `input_dim` | `int` | `必填` |
| `degree` | `int` | `必填` |
| `include_bias` | `bool` | `True` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`PolynomialBasis`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FloatingPointError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.polynomial import PolynomialBasis

print(signature(PolynomialBasis))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.polynomial`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/polynomial.py:8`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.polynomial')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-polynomial-polynomialbasis-from-state"></a>
## `ai4e_core.abilities.modeling.modules.polynomial.PolynomialBasis.from_state`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`from_state(cls, state: dict) -> 'PolynomialBasis'`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.polynomial.PolynomialBasis.from_state`

### 用途

严格校验项序后重建；旧系数不能配合重排的基。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.polynomial import PolynomialBasis
```

```text
from_state(cls, state: dict) -> 'PolynomialBasis'
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `state` | `dict` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`'PolynomialBasis'`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.polynomial import PolynomialBasis

print(signature(PolynomialBasis.from_state))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.polynomial`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/polynomial.py:59`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.polynomial')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-polynomial-polynomialbasis-powers"></a>
## `ai4e_core.abilities.modeling.modules.polynomial.PolynomialBasis.powers`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`powers(self) -> np.ndarray`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.polynomial.PolynomialBasis.powers`

### 用途

返回独立的各列指数副本，禁止调用方改变基列定义。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.polynomial import PolynomialBasis
```

```text
powers(self) -> np.ndarray
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`np.ndarray`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.polynomial import PolynomialBasis

print(signature(PolynomialBasis.powers))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.polynomial`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/polynomial.py:26`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.polynomial')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-polynomial-polynomialbasis-to-state"></a>
## `ai4e_core.abilities.modeling.modules.polynomial.PolynomialBasis.to_state`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`to_state(self) -> dict`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.polynomial.PolynomialBasis.to_state`

### 用途

返回可保存的局部配置及项序，不携带数据字段语义。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.polynomial import PolynomialBasis
```

```text
to_state(self) -> dict
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
from ai4e_core.abilities.modeling.modules.polynomial import PolynomialBasis

print(signature(PolynomialBasis.to_state))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.polynomial`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/polynomial.py:48`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.polynomial')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-polynomial-polynomialbasis-transform"></a>
## `ai4e_core.abilities.modeling.modules.polynomial.PolynomialBasis.transform`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`transform(self, inputs: np.ndarray) -> np.ndarray`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.polynomial.PolynomialBasis.transform`

### 用途

将有限实数 [N,d] 映射为 [N,P]，保留原输入列次序。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.polynomial import PolynomialBasis
```

```text
transform(self, inputs: np.ndarray) -> np.ndarray
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `inputs` | `np.ndarray` | `必填` |

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
from ai4e_core.abilities.modeling.modules.polynomial import PolynomialBasis

print(signature(PolynomialBasis.transform))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`gencp`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `safediffcon`, `wdno`
- 案例：`gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `recipe_extensions.gencp`, `recipe_extensions.task_labels`, `recipe_extensions.wdno`, `safediffcon.burgers`, `safediffcon.tokamak`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.polynomial`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/polynomial.py:30`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.polynomial')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
