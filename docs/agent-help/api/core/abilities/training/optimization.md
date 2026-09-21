<!-- dojo-help: {"domain": "ai4e_core.abilities.training.optimization", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.training.optimization 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.training.optimization", "topic_id": "module:ai4e_core.abilities.training.optimization"} -->
# `ai4e_core.abilities.training.optimization` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-training-optimization-lion"></a>
## `ai4e_core.abilities.training.optimization.Lion`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`Lion(params, lr=0.0001, betas=(0.9, 0.99), weight_decay=0.0)`
- **规范定义名**：`ai4e_core.abilities.training.optimization.Lion`

### 用途

符号动量优化器；本仓实现，不引入第三方优化器包。

### 导入与签名

```python
from ai4e_core.abilities.training.optimization import Lion
```

```text
Lion(params, lr=0.0001, betas=(0.9, 0.99), weight_decay=0.0)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `params` | `未标注` | `必填` |
| `lr` | `未标注` | `0.0001` |
| `betas` | `未标注` | `(0.9, 0.99)` |
| `weight_decay` | `未标注` | `0.0` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Lion`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`RuntimeError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.training.optimization import Lion

print(signature(Lion))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.training.optimization`
- 仓库相对路径：`packages/ai4e-core/abilities/training/optimization.py:10`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.optimization')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-optimization-lion-step"></a>
## `ai4e_core.abilities.training.optimization.Lion.step`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`step(self, closure=None)`
- **规范定义名**：`ai4e_core.abilities.training.optimization.Lion.step`

### 用途

按 Lion 规则更新参数。

### 导入与签名

```python
from ai4e_core.abilities.training.optimization import Lion
```

```text
step(self, closure=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `closure` | `未标注` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`RuntimeError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.training.optimization import Lion

print(signature(Lion.step))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `gencp`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`, `parametric_pde`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `parametric_pde.advection`, `parametric_pde.burgers`, `parametric_pde.convection_diffusion`, `parametric_pde.diffusion_trapezoid`, `parametric_pde.neumann_diffusion`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.wdno`

### 源码位置

- 模块：`ai4e_core.abilities.training.optimization`
- 仓库相对路径：`packages/ai4e-core/abilities/training/optimization.py:23`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.optimization')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-optimization-build-optimizer"></a>
## `ai4e_core.abilities.training.optimization.build_optimizer`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`build_optimizer(name, parameters, *, lr, weight_decay=0.0, betas=None)`
- **规范定义名**：`ai4e_core.abilities.training.optimization.build_optimizer`

### 用途

按名构造 Adam、AdamW 或 Lion；非法种类失败。

### 导入与签名

```python
from ai4e_core.abilities.training.optimization import build_optimizer
```

```text
build_optimizer(name, parameters, *, lr, weight_decay=0.0, betas=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `name` | `未标注` | `必填` |
| `parameters` | `未标注` | `必填` |
| `lr` | `未标注` | `必填关键字参数` |
| `weight_decay` | `未标注` | `0.0` |
| `betas` | `未标注` | `None` |

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
from ai4e_core.abilities.training.optimization import build_optimizer

print(signature(build_optimizer))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`geotransolver/bumper_beam`, `geotransolver/darcy`
- 案例：`geotransolver.bumper_beam`, `geotransolver.darcy`

### 源码位置

- 模块：`ai4e_core.abilities.training.optimization`
- 仓库相对路径：`packages/ai4e-core/abilities/training/optimization.py:82`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.optimization')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-optimization-parameter-groups"></a>
## `ai4e_core.abilities.training.optimization.parameter_groups`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`parameter_groups(model, *, weight_decay: float, policy: str='exclude_bias_norm')`
- **规范定义名**：`ai4e_core.abilities.training.optimization.parameter_groups`

### 用途

偏置和一维参数不衰减；与官方默认优化器分组规则一致。

### 导入与签名

```python
from ai4e_core.abilities.training.optimization import parameter_groups
```

```text
parameter_groups(model, *, weight_decay: float, policy: str='exclude_bias_norm')
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model` | `未标注` | `必填` |
| `weight_decay` | `float` | `必填关键字参数` |
| `policy` | `str` | `'exclude_bias_norm'` |

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
from ai4e_core.abilities.training.optimization import parameter_groups

print(signature(parameter_groups))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.training.optimization`
- 仓库相对路径：`packages/ai4e-core/abilities/training/optimization.py:95`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.optimization')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-optimization-resolve-device"></a>
## `ai4e_core.abilities.training.optimization.resolve_device`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`resolve_device(name: str) -> torch.device`
- **规范定义名**：`ai4e_core.abilities.training.optimization.resolve_device`

### 用途

解析设备名。

``auto`` 按 CUDA、MPS、CPU 选择；找不到加速器时警告并回退 CPU，训练继续。
``gpu`` 映射为 ``cuda``。点名设备不可用时报错，不静默回退。

### 导入与签名

```python
from ai4e_core.abilities.training.optimization import resolve_device
```

```text
resolve_device(name: str) -> torch.device
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `name` | `str` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`torch.device`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.training.optimization import resolve_device

print(signature(resolve_device))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`geotransolver/bumper_beam`, `geotransolver/darcy`
- 案例：`geotransolver.bumper_beam`, `geotransolver.darcy`

### 源码位置

- 模块：`ai4e_core.abilities.training.optimization`
- 仓库相对路径：`packages/ai4e-core/abilities/training/optimization.py:56`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.optimization')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-optimization-update"></a>
## `ai4e_core.abilities.training.optimization.update`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`update(model, optimizer, step, batch, *, clip: float | None=1.0, scaler=None, scheduler=None, accumulate: int=1, accumulation_reduction: str='mean', accum_index: int=0, stability: bool=False) -> tuple`
- **规范定义名**：`ai4e_core.abilities.training.optimization.update`

### 用途

循环独占清梯度、反向、解除缩放、裁剪与更新，返回有效更新标记。

累积未满不 step；跳步不推进调度。mean 按累积步均分，sum 保留梯度和。

### 导入与签名

```python
from ai4e_core.abilities.training.optimization import update
```

```text
update(model, optimizer, step, batch, *, clip: float | None=1.0, scaler=None, scheduler=None, accumulate: int=1, accumulation_reduction: str='mean', accum_index: int=0, stability: bool=False) -> tuple
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model` | `未标注` | `必填` |
| `optimizer` | `未标注` | `必填` |
| `step` | `未标注` | `必填` |
| `batch` | `未标注` | `必填` |
| `clip` | `float | None` | `1.0` |
| `scaler` | `未标注` | `None` |
| `scheduler` | `未标注` | `None` |
| `accumulate` | `int` | `1` |
| `accumulation_reduction` | `str` | `'mean'` |
| `accum_index` | `int` | `0` |
| `stability` | `bool` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`tuple`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.training.optimization import update

print(signature(update))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`gencp`
- 案例：`gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `recipe_extensions.wdno`

### 源码位置

- 模块：`ai4e_core.abilities.training.optimization`
- 仓库相对路径：`packages/ai4e-core/abilities/training/optimization.py:111`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.optimization')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
