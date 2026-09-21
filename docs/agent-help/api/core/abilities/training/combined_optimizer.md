<!-- dojo-help: {"domain": "ai4e_core.abilities.training.combined_optimizer", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.training.combined_optimizer 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.training.combined_optimizer", "topic_id": "module:ai4e_core.abilities.training.combined_optimizer"} -->
# `ai4e_core.abilities.training.combined_optimizer` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-training-combined-optimizer-combinedoptimizer"></a>
## `ai4e_core.abilities.training.combined_optimizer.CombinedOptimizer`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`CombinedOptimizer(optimizers)`
- **规范定义名**：`ai4e_core.abilities.training.combined_optimizer.CombinedOptimizer`

### 用途

按声明次序更新子优化器，调度器直接使用同一 param_groups。

### 导入与签名

```python
from ai4e_core.abilities.training.combined_optimizer import CombinedOptimizer
```

```text
CombinedOptimizer(optimizers)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `optimizers` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`CombinedOptimizer`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.training.combined_optimizer import CombinedOptimizer

print(signature(CombinedOptimizer))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.training.combined_optimizer`
- 仓库相对路径：`packages/ai4e-core/abilities/training/combined_optimizer.py:6`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.combined_optimizer')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-combined-optimizer-combinedoptimizer-load-state-dict"></a>
## `ai4e_core.abilities.training.combined_optimizer.CombinedOptimizer.load_state_dict`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`load_state_dict(self, state_dict)`
- **规范定义名**：`ai4e_core.abilities.training.combined_optimizer.CombinedOptimizer.load_state_dict`

### 用途

恢复后重新关联参数组，避免调度器修改过期字典。

### 导入与签名

```python
from ai4e_core.abilities.training.combined_optimizer import CombinedOptimizer
```

```text
load_state_dict(self, state_dict)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `state_dict` | `未标注` | `必填` |

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
from ai4e_core.abilities.training.combined_optimizer import CombinedOptimizer

print(signature(CombinedOptimizer.load_state_dict))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.training.combined_optimizer`
- 仓库相对路径：`packages/ai4e-core/abilities/training/combined_optimizer.py:42`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.combined_optimizer')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-combined-optimizer-combinedoptimizer-state-dict"></a>
## `ai4e_core.abilities.training.combined_optimizer.CombinedOptimizer.state_dict`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`state_dict(self)`
- **规范定义名**：`ai4e_core.abilities.training.combined_optimizer.CombinedOptimizer.state_dict`

### 用途

保存子优化器类型与完整状态，拒绝恢复时错换算法。

### 导入与签名

```python
from ai4e_core.abilities.training.combined_optimizer import CombinedOptimizer
```

```text
state_dict(self)
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

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
from ai4e_core.abilities.training.combined_optimizer import CombinedOptimizer

print(signature(CombinedOptimizer.state_dict))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.training.combined_optimizer`
- 仓库相对路径：`packages/ai4e-core/abilities/training/combined_optimizer.py:35`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.combined_optimizer')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-combined-optimizer-combinedoptimizer-step"></a>
## `ai4e_core.abilities.training.combined_optimizer.CombinedOptimizer.step`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`step(self, closure=None)`
- **规范定义名**：`ai4e_core.abilities.training.combined_optimizer.CombinedOptimizer.step`

### 用途

闭包仅求值一次，再按顺序更新互斥参数。

### 导入与签名

```python
from ai4e_core.abilities.training.combined_optimizer import CombinedOptimizer
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

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.training.combined_optimizer import CombinedOptimizer

print(signature(CombinedOptimizer.step))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `gencp`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`, `parametric_pde`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `parametric_pde.advection`, `parametric_pde.burgers`, `parametric_pde.convection_diffusion`, `parametric_pde.diffusion_trapezoid`, `parametric_pde.neumann_diffusion`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.wdno`

### 源码位置

- 模块：`ai4e_core.abilities.training.combined_optimizer`
- 仓库相对路径：`packages/ai4e-core/abilities/training/combined_optimizer.py:20`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.combined_optimizer')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-combined-optimizer-combinedoptimizer-zero-grad"></a>
## `ai4e_core.abilities.training.combined_optimizer.CombinedOptimizer.zero_grad`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`zero_grad(self, set_to_none=True)`
- **规范定义名**：`ai4e_core.abilities.training.combined_optimizer.CombinedOptimizer.zero_grad`

### 用途

清空每个子优化器梯度。

### 导入与签名

```python
from ai4e_core.abilities.training.combined_optimizer import CombinedOptimizer
```

```text
zero_grad(self, set_to_none=True)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `set_to_none` | `未标注` | `True` |

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
from ai4e_core.abilities.training.combined_optimizer import CombinedOptimizer

print(signature(CombinedOptimizer.zero_grad))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.wdno`

### 源码位置

- 模块：`ai4e_core.abilities.training.combined_optimizer`
- 仓库相对路径：`packages/ai4e-core/abilities/training/combined_optimizer.py:30`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.combined_optimizer')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
