<!-- dojo-help: {"domain": "ai4e_contrib.ability.constraint.safediffcon.pinn_loss", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.constraint.safediffcon.pinn_loss 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.constraint.safediffcon.pinn_loss", "topic_id": "module:ai4e_contrib.ability.constraint.safediffcon.pinn_loss"} -->
# `ai4e_contrib.ability.constraint.safediffcon.pinn_loss` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-constraint-safediffcon-pinn-loss-diff-mat-1d"></a>
## `ai4e_contrib.ability.constraint.safediffcon.pinn_loss.Diff_mat_1D`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`Diff_mat_1D(Nx, device='cpu', partially_observed=None)`
- **规范定义名**：`ai4e_contrib.ability.constraint.safediffcon.pinn_loss.Diff_mat_1D`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.constraint.safediffcon.pinn_loss import Diff_mat_1D
```

```text
Diff_mat_1D(Nx, device='cpu', partially_observed=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `Nx` | `未标注` | `必填` |
| `device` | `未标注` | `'cpu'` |
| `partially_observed` | `未标注` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`NotImplementedError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.constraint.safediffcon.pinn_loss import Diff_mat_1D

print(signature(Diff_mat_1D))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.constraint.safediffcon.pinn_loss`
- 仓库相对路径：`packages/ai4e-contrib/ability/constraint/safediffcon/pinn_loss.py:8`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.constraint.safediffcon.pinn_loss')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-constraint-safediffcon-pinn-loss-get-pinn-loss-2dconv"></a>
## `ai4e_contrib.ability.constraint.safediffcon.pinn_loss.get_pinn_loss_2dconv`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`get_pinn_loss_2dconv(mode='mean', partially_observed=None)`
- **规范定义名**：`ai4e_contrib.ability.constraint.safediffcon.pinn_loss.get_pinn_loss_2dconv`

### 用途

Returns the PINN loss function.

Arguments:
    x: (B, 2, 16, 128)

### 导入与签名

```python
from ai4e_contrib.ability.constraint.safediffcon.pinn_loss import get_pinn_loss_2dconv
```

```text
get_pinn_loss_2dconv(mode='mean', partially_observed=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `mode` | `未标注` | `'mean'` |
| `partially_observed` | `未标注` | `None` |

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
from ai4e_contrib.ability.constraint.safediffcon.pinn_loss import get_pinn_loss_2dconv

print(signature(get_pinn_loss_2dconv))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.constraint.safediffcon.pinn_loss`
- 仓库相对路径：`packages/ai4e-contrib/ability/constraint/safediffcon/pinn_loss.py:118`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.constraint.safediffcon.pinn_loss')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-constraint-safediffcon-pinn-loss-one-step-solver-u"></a>
## `ai4e_contrib.ability.constraint.safediffcon.pinn_loss.one_step_solver_u`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`one_step_solver_u(u, f, dt=0.1, visc=0.01, mode='mean', partially_observed=None)`
- **规范定义名**：`ai4e_contrib.ability.constraint.safediffcon.pinn_loss.one_step_solver_u`

### 用途

Calculates u following the solver using coarse time step, based on which the 
PINN loss will be evaluated.
Note that this is an approximated version -- only 10 time stamps in u.

Arguments:
    u: (B, 11, 128)
    f: (B, 10, 128)

### 导入与签名

```python
from ai4e_contrib.ability.constraint.safediffcon.pinn_loss import one_step_solver_u
```

```text
one_step_solver_u(u, f, dt=0.1, visc=0.01, mode='mean', partially_observed=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `u` | `未标注` | `必填` |
| `f` | `未标注` | `必填` |
| `dt` | `未标注` | `0.1` |
| `visc` | `未标注` | `0.01` |
| `mode` | `未标注` | `'mean'` |
| `partially_observed` | `未标注` | `None` |

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
from ai4e_contrib.ability.constraint.safediffcon.pinn_loss import one_step_solver_u

print(signature(one_step_solver_u))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.constraint.safediffcon.pinn_loss`
- 仓库相对路径：`packages/ai4e-contrib/ability/constraint/safediffcon/pinn_loss.py:47`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.constraint.safediffcon.pinn_loss')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-constraint-safediffcon-pinn-loss-pinn-loss"></a>
## `ai4e_contrib.ability.constraint.safediffcon.pinn_loss.pinn_loss`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`pinn_loss(u, f, mode='mean', partially_observed=None)`
- **规范定义名**：`ai4e_contrib.ability.constraint.safediffcon.pinn_loss.pinn_loss`

### 用途

Calculates the PINN loss given u and f.
Note that this is an approximated version -- only 10 time stamps in u.

Arguments:
    u (B, 11, 128)
    f (B, 10, 128)

### 导入与签名

```python
from ai4e_contrib.ability.constraint.safediffcon.pinn_loss import pinn_loss
```

```text
pinn_loss(u, f, mode='mean', partially_observed=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `u` | `未标注` | `必填` |
| `f` | `未标注` | `必填` |
| `mode` | `未标注` | `'mean'` |
| `partially_observed` | `未标注` | `None` |

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
from ai4e_contrib.ability.constraint.safediffcon.pinn_loss import pinn_loss

print(signature(pinn_loss))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.constraint.safediffcon.pinn_loss`
- 仓库相对路径：`packages/ai4e-contrib/ability/constraint/safediffcon/pinn_loss.py:101`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.constraint.safediffcon.pinn_loss')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-constraint-safediffcon-pinn-loss-residual-gradient"></a>
## `ai4e_contrib.ability.constraint.safediffcon.pinn_loss.residual_gradient`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`residual_gradient(x, mode='mean', partially_observed=None)`
- **规范定义名**：`ai4e_contrib.ability.constraint.safediffcon.pinn_loss.residual_gradient`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.constraint.safediffcon.pinn_loss import residual_gradient
```

```text
residual_gradient(x, mode='mean', partially_observed=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `mode` | `未标注` | `'mean'` |
| `partially_observed` | `未标注` | `None` |

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
from ai4e_contrib.ability.constraint.safediffcon.pinn_loss import residual_gradient

print(signature(residual_gradient))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.constraint.safediffcon.pinn_loss`
- 仓库相对路径：`packages/ai4e-contrib/ability/constraint/safediffcon/pinn_loss.py:130`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.constraint.safediffcon.pinn_loss')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
