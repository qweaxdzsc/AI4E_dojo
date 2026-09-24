<!-- dojo-help: {"domain": "ai4e_core.applications.parametric_pde.rawprep", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.parametric_pde.rawprep 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.parametric_pde.rawprep", "topic_id": "module:ai4e_core.applications.parametric_pde.rawprep"} -->
# `ai4e_core.applications.parametric_pde.rawprep` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-parametric-pde-rawprep-prepare-named-fields"></a>
## `ai4e_core.applications.parametric_pde.rawprep.prepare_named_fields`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`prepare_named_fields(samples, reader, output, *, session, metadata: dict)`
- **规范定义名**：`ai4e_core.applications.parametric_pde.rawprep.prepare_named_fields`

### 用途

按来源样本名单交付原网格、逐场 PT 和清单；任何失败不发布完整清单。

### 导入与签名

```python
from ai4e_core.applications.parametric_pde.rawprep import prepare_named_fields
```

```text
prepare_named_fields(samples, reader, output, *, session, metadata: dict)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `samples` | `未标注` | `必填` |
| `reader` | `未标注` | `必填` |
| `output` | `未标注` | `必填` |
| `session` | `未标注` | `必填关键字参数` |
| `metadata` | `dict` | `必填关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FileExistsError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.parametric_pde.rawprep import prepare_named_fields

print(signature(prepare_named_fields))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`geotransolver/darcy`
- 案例：`geotransolver.darcy`, `recipe_extensions.research_state`

### 源码位置

- 模块：`ai4e_core.applications.parametric_pde.rawprep`
- 仓库相对路径：`packages/ai4e-core/applications/parametric_pde/rawprep.py:22`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.parametric_pde.rawprep')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-parametric-pde-rawprep-rawprep"></a>
## `ai4e_core.applications.parametric_pde.rawprep.rawprep`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`rawprep(cfg, *, dataset_component, session, **components)`
- **规范定义名**：`ai4e_core.applications.parametric_pde.rawprep.rawprep`

### 用途

逐个核验清单中的完整物理数据，报告来源而不改配置。

### 导入与签名

```python
from ai4e_core.applications.parametric_pde.rawprep import rawprep
```

```text
rawprep(cfg, *, dataset_component, session, **components)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cfg` | `未标注` | `必填` |
| `dataset_component` | `未标注` | `必填关键字参数` |
| `session` | `未标注` | `必填关键字参数` |
| `**components` | `未标注` | `可变关键字参数` |

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
from ai4e_core.applications.parametric_pde.rawprep import rawprep

print(signature(rawprep))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `gencp`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`, `parametric_pde`, `pcno`, `pcno_cylinder`, `safediffcon`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `extension.pcno`, `extension.pcno_cylinder`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `geothermal.pcno`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `parametric_pde.advection`, `parametric_pde.burgers`, `parametric_pde.convection_diffusion`, `parametric_pde.diffusion_trapezoid`, `parametric_pde.neumann_diffusion`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.resunet`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`, `recipe_extensions.operator_physical_loss`, `recipe_extensions.research_state`, `recipe_extensions.sampling`, `recipe_extensions.tail_batch`, `recipe_extensions.task_labels`, `recipe_extensions.wdno`, `safediffcon.burgers`, `safediffcon.tokamak`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_core.applications.parametric_pde.rawprep`
- 仓库相对路径：`packages/ai4e-core/applications/parametric_pde/rawprep.py:4`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.parametric_pde.rawprep')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
