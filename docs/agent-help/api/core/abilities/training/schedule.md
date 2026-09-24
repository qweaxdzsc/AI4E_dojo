<!-- dojo-help: {"domain": "ai4e_core.abilities.training.schedule", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.training.schedule 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.training.schedule", "topic_id": "module:ai4e_core.abilities.training.schedule"} -->
# `ai4e_core.abilities.training.schedule` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-training-schedule-epochboundaryscheduler"></a>
## `ai4e_core.abilities.training.schedule.EpochBoundaryScheduler`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`EpochBoundaryScheduler(scheduler, updates_per_epoch: int)`
- **规范定义名**：`ai4e_core.abilities.training.schedule.EpochBoundaryScheduler`

### 用途

将每更新调用转换为真实轮次末尾推进，包含恢复游标。

### 导入与签名

```python
from ai4e_core.abilities.training.schedule import EpochBoundaryScheduler
```

```text
EpochBoundaryScheduler(scheduler, updates_per_epoch: int)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `scheduler` | `未标注` | `必填` |
| `updates_per_epoch` | `int` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`EpochBoundaryScheduler`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.training.schedule import EpochBoundaryScheduler

print(signature(EpochBoundaryScheduler))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.training.schedule`
- 仓库相对路径：`packages/ai4e-core/abilities/training/schedule.py:53`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.schedule')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-schedule-epochboundaryscheduler-load-state-dict"></a>
## `ai4e_core.abilities.training.schedule.EpochBoundaryScheduler.load_state_dict`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`load_state_dict(self, state)`
- **规范定义名**：`ai4e_core.abilities.training.schedule.EpochBoundaryScheduler.load_state_dict`

### 用途

轮次定义改变时拒绝恢复。

### 导入与签名

```python
from ai4e_core.abilities.training.schedule import EpochBoundaryScheduler
```

```text
load_state_dict(self, state)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `state` | `未标注` | `必填` |

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
from ai4e_core.abilities.training.schedule import EpochBoundaryScheduler

print(signature(EpochBoundaryScheduler.load_state_dict))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`
- 案例：`classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `recipe_extensions.pod_surrogate_replacement`, `recipe_extensions.research_state`

### 源码位置

- 模块：`ai4e_core.abilities.training.schedule`
- 仓库相对路径：`packages/ai4e-core/abilities/training/schedule.py:75`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.schedule')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-schedule-epochboundaryscheduler-state-dict"></a>
## `ai4e_core.abilities.training.schedule.EpochBoundaryScheduler.state_dict`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`state_dict(self)`
- **规范定义名**：`ai4e_core.abilities.training.schedule.EpochBoundaryScheduler.state_dict`

### 用途

保存底层状态和更新游标。

### 导入与签名

```python
from ai4e_core.abilities.training.schedule import EpochBoundaryScheduler
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
from ai4e_core.abilities.training.schedule import EpochBoundaryScheduler

print(signature(EpochBoundaryScheduler.state_dict))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`
- 案例：`classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `recipe_extensions.pod_surrogate_replacement`, `recipe_extensions.research_state`

### 源码位置

- 模块：`ai4e_core.abilities.training.schedule`
- 仓库相对路径：`packages/ai4e-core/abilities/training/schedule.py:67`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.schedule')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-schedule-epochboundaryscheduler-step"></a>
## `ai4e_core.abilities.training.schedule.EpochBoundaryScheduler.step`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`step(self)`
- **规范定义名**：`ai4e_core.abilities.training.schedule.EpochBoundaryScheduler.step`

### 用途

只在完整轮次结束时推进底层调度器。

### 导入与签名

```python
from ai4e_core.abilities.training.schedule import EpochBoundaryScheduler
```

```text
step(self)
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
from ai4e_core.abilities.training.schedule import EpochBoundaryScheduler

print(signature(EpochBoundaryScheduler.step))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `gencp`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`, `parametric_pde`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `parametric_pde.advection`, `parametric_pde.burgers`, `parametric_pde.convection_diffusion`, `parametric_pde.diffusion_trapezoid`, `parametric_pde.neumann_diffusion`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.research_state`, `recipe_extensions.wdno`

### 源码位置

- 模块：`ai4e_core.abilities.training.schedule`
- 仓库相对路径：`packages/ai4e-core/abilities/training/schedule.py:61`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.schedule')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-schedule-build-scheduler"></a>
## `ai4e_core.abilities.training.schedule.build_scheduler`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`build_scheduler(name, optimizer, *, total_updates: int, warmup_ratio: float=0.05, min_lr: float=1e-06, last_epoch: int=-1)`
- **规范定义名**：`ai4e_core.abilities.training.schedule.build_scheduler`

### 用途

按名构造调度。缺总步数或非法种类失败，不包一层空的 ``step``。

### 导入与签名

```python
from ai4e_core.abilities.training.schedule import build_scheduler
```

```text
build_scheduler(name, optimizer, *, total_updates: int, warmup_ratio: float=0.05, min_lr: float=1e-06, last_epoch: int=-1)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `name` | `未标注` | `必填` |
| `optimizer` | `未标注` | `必填` |
| `total_updates` | `int` | `必填关键字参数` |
| `warmup_ratio` | `float` | `0.05` |
| `min_lr` | `float` | `1e-06` |
| `last_epoch` | `int` | `-1` |

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
from ai4e_core.abilities.training.schedule import build_scheduler

print(signature(build_scheduler))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`geotransolver/bumper_beam`, `geotransolver/darcy`
- 案例：`geotransolver.bumper_beam`, `geotransolver.darcy`, `recipe_extensions.research_state`, `recipe_extensions.tail_batch`

### 源码位置

- 模块：`ai4e_core.abilities.training.schedule`
- 仓库相对路径：`packages/ai4e-core/abilities/training/schedule.py:15`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.schedule')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-schedule-total-updates"></a>
## `ai4e_core.abilities.training.schedule.total_updates`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`total_updates(epochs: int, samples: int, accumulate: int=1) -> int`
- **规范定义名**：`ai4e_core.abilities.training.schedule.total_updates`

### 用途

按轮数、样本数和累积步计算有效更新次数。

### 导入与签名

```python
from ai4e_core.abilities.training.schedule import total_updates
```

```text
total_updates(epochs: int, samples: int, accumulate: int=1) -> int
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `epochs` | `int` | `必填` |
| `samples` | `int` | `必填` |
| `accumulate` | `int` | `1` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`int`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.training.schedule import total_updates

print(signature(total_updates))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.training.schedule`
- 仓库相对路径：`packages/ai4e-core/abilities/training/schedule.py:8`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.schedule')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
