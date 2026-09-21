<!-- dojo-help: {"domain": "ai4e_contrib.ability.constraint.equations", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.constraint.equations 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.constraint.equations", "topic_id": "module:ai4e_contrib.ability.constraint.equations"} -->
# `ai4e_contrib.ability.constraint.equations` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-constraint-equations-advection"></a>
## `ai4e_contrib.ability.constraint.equations.advection`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`advection(*, u_t, u_x, velocity)`
- **规范定义名**：`ai4e_contrib.ability.constraint.equations.advection`

### 用途

一维常系数对流残差 u_t + velocity*u_x。

### 导入与签名

```python
from ai4e_contrib.ability.constraint.equations import advection
```

```text
advection(*, u_t, u_x, velocity)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `u_t` | `未标注` | `必填关键字参数` |
| `u_x` | `未标注` | `必填关键字参数` |
| `velocity` | `未标注` | `必填关键字参数` |

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
from ai4e_contrib.ability.constraint.equations import advection

print(signature(advection))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`parametric_pde`
- 案例：`parametric_pde.advection`, `parametric_pde.burgers`, `parametric_pde.convection_diffusion`, `parametric_pde.diffusion_trapezoid`, `parametric_pde.neumann_diffusion`

### 源码位置

- 模块：`ai4e_contrib.ability.constraint.equations`
- 仓库相对路径：`packages/ai4e-contrib/ability/constraint/equations/__init__.py:44`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.constraint.equations')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-constraint-equations-burgers"></a>
## `ai4e_contrib.ability.constraint.equations.burgers`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`burgers(*, u, u_t, u_x, u_xx, convection_coefficient=1.0, viscosity=0.01)`
- **规范定义名**：`ai4e_contrib.ability.constraint.equations.burgers`

### 用途

黏性 Burgers 残差 u_t + mu*u*u_x - nu*u_xx。

### 导入与签名

```python
from ai4e_contrib.ability.constraint.equations import burgers
```

```text
burgers(*, u, u_t, u_x, u_xx, convection_coefficient=1.0, viscosity=0.01)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `u` | `未标注` | `必填关键字参数` |
| `u_t` | `未标注` | `必填关键字参数` |
| `u_x` | `未标注` | `必填关键字参数` |
| `u_xx` | `未标注` | `必填关键字参数` |
| `convection_coefficient` | `未标注` | `1.0` |
| `viscosity` | `未标注` | `0.01` |

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
from ai4e_contrib.ability.constraint.equations import burgers

print(signature(burgers))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`parametric_pde`, `safediffcon`, `wdno`
- 案例：`parametric_pde.advection`, `parametric_pde.burgers`, `parametric_pde.convection_diffusion`, `parametric_pde.diffusion_trapezoid`, `parametric_pde.neumann_diffusion`, `recipe_extensions.safediffcon`, `recipe_extensions.wdno`, `safediffcon.burgers`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.ability.constraint.equations`
- 仓库相对路径：`packages/ai4e-contrib/ability/constraint/equations/__init__.py:69`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.constraint.equations')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-constraint-equations-convection-diffusion"></a>
## `ai4e_contrib.ability.constraint.equations.convection_diffusion`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`convection_diffusion(*, u_t, u_x, u_xx, velocity, diffusivity)`
- **规范定义名**：`ai4e_contrib.ability.constraint.equations.convection_diffusion`

### 用途

一维对流扩散残差 u_t + velocity*u_x - diffusivity*u_xx。

### 导入与签名

```python
from ai4e_contrib.ability.constraint.equations import convection_diffusion
```

```text
convection_diffusion(*, u_t, u_x, u_xx, velocity, diffusivity)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `u_t` | `未标注` | `必填关键字参数` |
| `u_x` | `未标注` | `必填关键字参数` |
| `u_xx` | `未标注` | `必填关键字参数` |
| `velocity` | `未标注` | `必填关键字参数` |
| `diffusivity` | `未标注` | `必填关键字参数` |

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
from ai4e_contrib.ability.constraint.equations import convection_diffusion

print(signature(convection_diffusion))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`parametric_pde`
- 案例：`parametric_pde.advection`, `parametric_pde.burgers`, `parametric_pde.convection_diffusion`, `parametric_pde.diffusion_trapezoid`, `parametric_pde.neumann_diffusion`

### 源码位置

- 模块：`ai4e_contrib.ability.constraint.equations`
- 仓库相对路径：`packages/ai4e-contrib/ability/constraint/equations/__init__.py:60`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.constraint.equations')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-constraint-equations-diffusion"></a>
## `ai4e_contrib.ability.constraint.equations.diffusion`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`diffusion(*, u_t, u_xx, diffusivity, u_yy=None)`
- **规范定义名**：`ai4e_contrib.ability.constraint.equations.diffusion`

### 用途

一维或二维各向同性扩散残差；输入为物理坐标导数。

### 导入与签名

```python
from ai4e_contrib.ability.constraint.equations import diffusion
```

```text
diffusion(*, u_t, u_xx, diffusivity, u_yy=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `u_t` | `未标注` | `必填关键字参数` |
| `u_xx` | `未标注` | `必填关键字参数` |
| `diffusivity` | `未标注` | `必填关键字参数` |
| `u_yy` | `未标注` | `None` |

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
from ai4e_contrib.ability.constraint.equations import diffusion

print(signature(diffusion))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.constraint.equations`
- 仓库相对路径：`packages/ai4e-contrib/ability/constraint/equations/__init__.py:50`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.constraint.equations')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-constraint-equations-navier-stokes-2d"></a>
## `ai4e_contrib.ability.constraint.equations.navier_stokes_2d`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`navier_stokes_2d(*, u, v, u_t, v_t, u_x, u_y, v_x, v_y, p_x, p_y, u_xx, u_yy, v_xx, v_yy, density=1.0, kinematic_viscosity=0.01)`
- **规范定义名**：`ai4e_contrib.ability.constraint.equations.navier_stokes_2d`

### 用途

二维非定常不可压 NS；常密度/常运动黏度、物理压力、无体积力。

返回 continuity/momentum_x/momentum_y 逐点残差。压力基准与初边界条件
属于完整问题装配；本函数不隐式补充这些条件。

### 导入与签名

```python
from ai4e_contrib.ability.constraint.equations import navier_stokes_2d
```

```text
navier_stokes_2d(*, u, v, u_t, v_t, u_x, u_y, v_x, v_y, p_x, p_y, u_xx, u_yy, v_xx, v_yy, density=1.0, kinematic_viscosity=0.01)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `u` | `未标注` | `必填关键字参数` |
| `v` | `未标注` | `必填关键字参数` |
| `u_t` | `未标注` | `必填关键字参数` |
| `v_t` | `未标注` | `必填关键字参数` |
| `u_x` | `未标注` | `必填关键字参数` |
| `u_y` | `未标注` | `必填关键字参数` |
| `v_x` | `未标注` | `必填关键字参数` |
| `v_y` | `未标注` | `必填关键字参数` |
| `p_x` | `未标注` | `必填关键字参数` |
| `p_y` | `未标注` | `必填关键字参数` |
| `u_xx` | `未标注` | `必填关键字参数` |
| `u_yy` | `未标注` | `必填关键字参数` |
| `v_xx` | `未标注` | `必填关键字参数` |
| `v_yy` | `未标注` | `必填关键字参数` |
| `density` | `未标注` | `1.0` |
| `kinematic_viscosity` | `未标注` | `0.01` |

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
from ai4e_contrib.ability.constraint.equations import navier_stokes_2d

print(signature(navier_stokes_2d))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.constraint.equations`
- 仓库相对路径：`packages/ai4e-contrib/ability/constraint/equations/__init__.py:77`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.constraint.equations')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
