<!-- dojo-help: {"domain": "ai4e_core.abilities.training.kriging", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.training.kriging 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.training.kriging", "topic_id": "module:ai4e_core.abilities.training.kriging"} -->
# `ai4e_core.abilities.training.kriging` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-training-kriging-condition-kriging"></a>
## `ai4e_core.abilities.training.kriging.condition_kriging`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`condition_kriging(x: Any, y: Any, *, trend: Any=None, kernel_config: Mapping | None=None, noise_variance: Any=0.0, jitter: float=1e-10, negative_variance_tolerance: float=1e-10) -> tuple[Kriging, dict]`
- **规范定义名**：`ai4e_core.abilities.training.kriging.condition_kriging`

### 用途

按显式固定核参数求条件模型，不做超参数优化；默认未知常数趋势。

### 导入与签名

```python
from ai4e_core.abilities.training.kriging import condition_kriging
```

```text
condition_kriging(x: Any, y: Any, *, trend: Any=None, kernel_config: Mapping | None=None, noise_variance: Any=0.0, jitter: float=1e-10, negative_variance_tolerance: float=1e-10) -> tuple[Kriging, dict]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `Any` | `必填` |
| `y` | `Any` | `必填` |
| `trend` | `Any` | `None` |
| `kernel_config` | `Mapping | None` | `None` |
| `noise_variance` | `Any` | `0.0` |
| `jitter` | `float` | `1e-10` |
| `negative_variance_tolerance` | `float` | `1e-10` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`tuple[Kriging, dict]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.training.kriging import condition_kriging

print(signature(condition_kriging))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.training.kriging`
- 仓库相对路径：`packages/ai4e-core/abilities/training/kriging.py:106`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.kriging')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-kriging-fit-kriging"></a>
## `ai4e_core.abilities.training.kriging.fit_kriging`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`fit_kriging(x: Any, y: Any, *, trend: Any=None, kernel_config: Mapping | None=None, noise_variance: Any=0.0, jitter: float=1e-10, optimization: Mapping | None=None, cancelled: Callable[[], bool] | None=None, deadline: float | None=None) -> tuple[Kriging, dict]`
- **规范定义名**：`ai4e_core.abilities.training.kriging.fit_kriging`

### 用途

单初值L-BFGS-B优化对数长度尺度及过程方差，返回模型与真实终止诊断。

deadline为time.monotonic绝对时刻；在每次目标计算前检查。超时或取消
抛异常，不把不完整优化当成功。maxiter/maxfun限制正常返回诊断，模型
采用优化器最终有效点。预测状态可重载，不声明优化器任意内部步恢复。

### 导入与签名

```python
from ai4e_core.abilities.training.kriging import fit_kriging
```

```text
fit_kriging(x: Any, y: Any, *, trend: Any=None, kernel_config: Mapping | None=None, noise_variance: Any=0.0, jitter: float=1e-10, optimization: Mapping | None=None, cancelled: Callable[[], bool] | None=None, deadline: float | None=None) -> tuple[Kriging, dict]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `Any` | `必填` |
| `y` | `Any` | `必填` |
| `trend` | `Any` | `None` |
| `kernel_config` | `Mapping | None` | `None` |
| `noise_variance` | `Any` | `0.0` |
| `jitter` | `float` | `1e-10` |
| `optimization` | `Mapping | None` | `None` |
| `cancelled` | `Callable[[], bool] | None` | `None` |
| `deadline` | `float | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`tuple[Kriging, dict]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`InterruptedError`, `TimeoutError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.training.kriging import fit_kriging

print(signature(fit_kriging))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.training.kriging`
- 仓库相对路径：`packages/ai4e-core/abilities/training/kriging.py:161`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.kriging')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-kriging-kriging-profile-gradient"></a>
## `ai4e_core.abilities.training.kriging.kriging_profile_gradient`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`kriging_profile_gradient(model: Kriging) -> np.ndarray`
- **规范定义名**：`ai4e_core.abilities.training.kriging.kriging_profile_gradient`

### 用途

固定条件点的profile-ML解析梯度，次序为逐轴log长度尺度、log过程方差。

GLS残差对趋势导数的项由F.T@alpha=0消去；这里不使用REML投影迹项。
用已保存Cholesky解各个dC，不显式构造协方差逆，也不推进优化器。

### 导入与签名

```python
from ai4e_core.abilities.training.kriging import kriging_profile_gradient
```

```text
kriging_profile_gradient(model: Kriging) -> np.ndarray
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model` | `Kriging` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`np.ndarray`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FloatingPointError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.training.kriging import kriging_profile_gradient

print(signature(kriging_profile_gradient))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.training.kriging`
- 仓库相对路径：`packages/ai4e-core/abilities/training/kriging.py:131`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.kriging')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-kriging-solve-kriging-condition"></a>
## `ai4e_core.abilities.training.kriging.solve_kriging_condition`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`solve_kriging_condition(covariance: Any, design: Any, y: Any, *, noise_variance: Any=0.0, jitter: float=1e-10, negative_variance_tolerance: float=1e-10) -> tuple[KrigingCondition, dict]`
- **规范定义名**：`ai4e_core.abilities.training.kriging.solve_kriging_condition`

### 用途

给定[N,N]过程协方差、[N,P]满秩趋势和[N]响应，求固定条件状态。

显式GLS未知趋势，保留趋势估计方差。噪声与jitter分别登记；不自动增大
扰动、不使用伪逆。矩阵不正定或趋势退化抛ValueError，不静默换模型。

### 导入与签名

```python
from ai4e_core.abilities.training.kriging import solve_kriging_condition
```

```text
solve_kriging_condition(covariance: Any, design: Any, y: Any, *, noise_variance: Any=0.0, jitter: float=1e-10, negative_variance_tolerance: float=1e-10) -> tuple[KrigingCondition, dict]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `covariance` | `Any` | `必填` |
| `design` | `Any` | `必填` |
| `y` | `Any` | `必填` |
| `noise_variance` | `Any` | `0.0` |
| `jitter` | `float` | `1e-10` |
| `negative_variance_tolerance` | `float` | `1e-10` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`tuple[KrigingCondition, dict]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FloatingPointError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.training.kriging import solve_kriging_condition

print(signature(solve_kriging_condition))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.training.kriging`
- 仓库相对路径：`packages/ai4e-core/abilities/training/kriging.py:33`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.kriging')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
