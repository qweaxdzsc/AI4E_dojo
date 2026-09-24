<!-- dojo-help: {"domain": "ai4e_core.applications.base.stage", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.base.stage 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.base.stage", "topic_id": "module:ai4e_core.applications.base.stage"} -->
# `ai4e_core.applications.base.stage` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-base-stage-stage"></a>
## `ai4e_core.applications.base.stage.Stage`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`Stage(name: str, steps: Sequence[Callable[[Any], Any]])`
- **规范定义名**：`ai4e_core.applications.base.stage.Stage`

### 用途

一条业务阶段的盒子，执行时只做 ``ctx = step(ctx)``。

### 导入与签名

```python
from ai4e_core.applications.base.stage import Stage
```

```text
Stage(name: str, steps: Sequence[Callable[[Any], Any]])
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `name` | `str` | `必填` |
| `steps` | `Sequence[Callable[[Any], Any]]` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Stage`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`, `error`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.base.stage import Stage

print(signature(Stage))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.base.stage`
- 仓库相对路径：`packages/ai4e-core/applications/base/stage.py:21`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.base.stage')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-base-stage-stage-run"></a>
## `ai4e_core.applications.base.stage.Stage.run`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`run(self, ctx: Any) -> Any`
- **规范定义名**：`ai4e_core.applications.base.stage.Stage.run`

### 用途

按顺序调用步骤；一步失败则停止。

Args:
    ctx: 作业上下文，通常是映射。

Returns:
    最后一步返回的上下文。

Raises:
    StageError: 某一步抛错。

### 导入与签名

```python
from ai4e_core.applications.base.stage import Stage
```

```text
run(self, ctx: Any) -> Any
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `ctx` | `Any` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Any`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`error`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.base.stage import Stage

print(signature(Stage.run))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `gencp`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`, `parametric_pde`, `pcno`, `pcno_cylinder`, `safediffcon`, `surrogate_modeling/double_cylinder`, `surrogate_modeling/nasa_crm`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `extension.pcno`, `extension.pcno_cylinder`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `geothermal.pcno`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `parametric_pde.advection`, `parametric_pde.burgers`, `parametric_pde.convection_diffusion`, `parametric_pde.diffusion_trapezoid`, `parametric_pde.neumann_diffusion`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.free_wiring`, `recipe_extensions.gencp`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.resunet`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`, `recipe_extensions.operator_physical_loss`, `recipe_extensions.physical_visualization`, `recipe_extensions.pod_surrogate_replacement`, `recipe_extensions.research_state`, `recipe_extensions.sampling`, `recipe_extensions.tail_batch`, `recipe_extensions.wdno`, `safediffcon.burgers`, `safediffcon.tokamak`, `surrogate_modeling.double_cylinder`, `surrogate_modeling.nasa_crm`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_core.applications.base.stage`
- 仓库相对路径：`packages/ai4e-core/applications/base/stage.py:30`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.base.stage')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-base-stage-stageerror"></a>
## `ai4e_core.applications.base.stage.StageError`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`StageError(stage: str, step_name: str, index: int, cause: BaseException)`
- **规范定义名**：`ai4e_core.applications.base.stage.StageError`

### 用途

阶段内某一步失败。

### 导入与签名

```python
from ai4e_core.applications.base.stage import StageError
```

```text
StageError(stage: str, step_name: str, index: int, cause: BaseException)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `stage` | `str` | `必填` |
| `step_name` | `str` | `必填` |
| `index` | `int` | `必填` |
| `cause` | `BaseException` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`StageError`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.base.stage import StageError

print(signature(StageError))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.base.stage`
- 仓库相对路径：`packages/ai4e-core/applications/base/stage.py:10`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.base.stage')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
