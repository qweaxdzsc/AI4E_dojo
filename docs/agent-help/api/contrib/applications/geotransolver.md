<!-- dojo-help: {"domain": "ai4e_contrib.application.geotransolver", "kind": "api", "layer": "contrib.application", "summary": "ai4e_contrib.application.geotransolver 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.application.geotransolver", "topic_id": "module:ai4e_contrib.application.geotransolver"} -->
# `ai4e_contrib.application.geotransolver` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-application-geotransolver-build-model"></a>
## `ai4e_contrib.application.geotransolver.build_model`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`build_model(options: dict)`
- **规范定义名**：`ai4e_contrib.application.geotransolver.build_model`

### 用途

普通 PyTorch 网络；未知扩展由网络入口明确拒绝。

### 导入与签名

```python
from ai4e_contrib.application.geotransolver import build_model
```

```text
build_model(options: dict)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `options` | `dict` | `必填` |

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
from ai4e_contrib.application.geotransolver import build_model

print(signature(build_model))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`, `pcno`, `pcno_cylinder`, `safediffcon`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `extension.pcno`, `extension.pcno_cylinder`, `geothermal.pcno`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.resunet`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`, `recipe_extensions.research_state`, `recipe_extensions.safediffcon`, `recipe_extensions.sampling`, `recipe_extensions.tail_batch`, `recipe_extensions.task_labels`, `safediffcon.burgers`, `safediffcon.tokamak`

### 源码位置

- 模块：`ai4e_contrib.application.geotransolver`
- 仓库相对路径：`packages/ai4e-contrib/application/geotransolver.py:10`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.geotransolver')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-geotransolver-build-optimizer"></a>
## `ai4e_contrib.application.geotransolver.build_optimizer`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`build_optimizer(model, *, lr, weight_decay)`
- **规范定义名**：`ai4e_contrib.application.geotransolver.build_optimizer`

### 用途

二维参数选择 Muon，其余选择 AdamW；计算/状态实现属于 core。

### 导入与签名

```python
from ai4e_contrib.application.geotransolver import build_optimizer
```

```text
build_optimizer(model, *, lr, weight_decay)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model` | `未标注` | `必填` |
| `lr` | `未标注` | `必填关键字参数` |
| `weight_decay` | `未标注` | `必填关键字参数` |

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
from ai4e_contrib.application.geotransolver import build_optimizer

print(signature(build_optimizer))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`geotransolver/bumper_beam`, `geotransolver/darcy`
- 案例：`geotransolver.bumper_beam`, `geotransolver.darcy`, `recipe_extensions.research_state`, `recipe_extensions.tail_batch`

### 源码位置

- 模块：`ai4e_contrib.application.geotransolver`
- 仓库相对路径：`packages/ai4e-contrib/application/geotransolver.py:17`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.geotransolver')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-geotransolver-build-scheduler"></a>
## `ai4e_contrib.application.geotransolver.build_scheduler`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`build_scheduler(optimizer, *, policy, updates_per_epoch, epochs, end_lr)`
- **规范定义名**：`ai4e_contrib.application.geotransolver.build_scheduler`

### 用途

保留原研究的逐更新预热/余弦或逐轮余弦，不按短训目标压缩日程。

### 导入与签名

```python
from ai4e_contrib.application.geotransolver import build_scheduler
```

```text
build_scheduler(optimizer, *, policy, updates_per_epoch, epochs, end_lr)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `optimizer` | `未标注` | `必填` |
| `policy` | `未标注` | `必填关键字参数` |
| `updates_per_epoch` | `未标注` | `必填关键字参数` |
| `epochs` | `未标注` | `必填关键字参数` |
| `end_lr` | `未标注` | `必填关键字参数` |

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
from ai4e_contrib.application.geotransolver import build_scheduler

print(signature(build_scheduler))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`geotransolver/bumper_beam`, `geotransolver/darcy`
- 案例：`geotransolver.bumper_beam`, `geotransolver.darcy`, `recipe_extensions.research_state`, `recipe_extensions.tail_batch`

### 源码位置

- 模块：`ai4e_contrib.application.geotransolver`
- 仓库相对路径：`packages/ai4e-contrib/application/geotransolver.py:34`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.geotransolver')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-geotransolver-component"></a>
## `ai4e_contrib.application.geotransolver.component`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`component(path)`
- **规范定义名**：`ai4e_contrib.application.geotransolver.component`

### 用途

显式全限定路径或普通函数，不建立注册表。

### 导入与签名

```python
from ai4e_contrib.application.geotransolver import component
```

```text
component(path)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `未标注` | `必填` |

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
from ai4e_contrib.application.geotransolver import component

print(signature(component))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `gencp`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`, `parametric_pde`, `pcno`, `pcno_cylinder`, `safediffcon`, `surrogate_modeling/double_cylinder`, `surrogate_modeling/nasa_crm`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `geothermal.pcno`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `parametric_pde.advection`, `parametric_pde.burgers`, `parametric_pde.convection_diffusion`, `parametric_pde.diffusion_trapezoid`, `parametric_pde.neumann_diffusion`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.gencp`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.model_block`, `recipe_extensions.research_state`, `recipe_extensions.sampling`, `recipe_extensions.tail_batch`, `safediffcon.burgers`, `safediffcon.tokamak`, `surrogate_modeling.double_cylinder`, `surrogate_modeling.nasa_crm`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.application.geotransolver`
- 仓库相对路径：`packages/ai4e-contrib/application/geotransolver.py:56`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.geotransolver')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-geotransolver-load-configuration"></a>
## `ai4e_contrib.application.geotransolver.load_configuration`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`load_configuration(path, overrides=None)`
- **规范定义名**：`ai4e_contrib.application.geotransolver.load_configuration`

### 用途

按配置所在目录解析所有相对路径，支持点号覆盖。

### 导入与签名

```python
from ai4e_contrib.application.geotransolver import load_configuration
```

```text
load_configuration(path, overrides=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `未标注` | `必填` |
| `overrides` | `未标注` | `None` |

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
from ai4e_contrib.application.geotransolver import load_configuration

print(signature(load_configuration))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `gencp`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`, `parametric_pde`, `pcno`, `pcno_cylinder`, `safediffcon`, `surrogate_modeling/double_cylinder`, `surrogate_modeling/nasa_crm`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `extension.pcno`, `extension.pcno_cylinder`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `geothermal.pcno`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `parametric_pde.advection`, `parametric_pde.burgers`, `parametric_pde.convection_diffusion`, `parametric_pde.diffusion_trapezoid`, `parametric_pde.neumann_diffusion`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.free_wiring`, `recipe_extensions.gencp`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.research_state`, `recipe_extensions.sampling`, `recipe_extensions.tail_batch`, `recipe_extensions.wdno`, `safediffcon.burgers`, `safediffcon.tokamak`, `surrogate_modeling.double_cylinder`, `surrogate_modeling.nasa_crm`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.application.geotransolver`
- 仓库相对路径：`packages/ai4e-contrib/application/geotransolver.py:152`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.geotransolver')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-geotransolver-validate"></a>
## `ai4e_contrib.application.geotransolver.validate`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`validate(config)`
- **规范定义名**：`ai4e_contrib.application.geotransolver.validate`

### 用途

文件、覆盖和程序调用共用公共路径及参数检查。

### 导入与签名

```python
from ai4e_contrib.application.geotransolver import validate
```

```text
validate(config)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

`data_root`, `inputs.infer.checkpoint`, `inputs.train.resume`, `run_root`

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.application.geotransolver import validate

print(signature(validate))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `gencp`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`, `parametric_pde`, `pcno`, `pcno_cylinder`, `surrogate_modeling/double_cylinder`, `surrogate_modeling/nasa_crm`, `wdno`
- 案例：`classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `extension.pcno`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `geothermal.pcno`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `parametric_pde.advection`, `parametric_pde.burgers`, `parametric_pde.convection_diffusion`, `parametric_pde.diffusion_trapezoid`, `parametric_pde.neumann_diffusion`, `pcno.double_cylinder`, `recipe_extensions.research_state`, `recipe_extensions.tail_batch`, `recipe_extensions.wdno`, `surrogate_modeling.double_cylinder`, `surrogate_modeling.nasa_crm`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.application.geotransolver`
- 仓库相对路径：`packages/ai4e-contrib/application/geotransolver.py:66`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.geotransolver')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
