<!-- dojo-help: {"domain": "ai4e_core.applications.parametric_pde.trainprep", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.parametric_pde.trainprep 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.parametric_pde.trainprep", "topic_id": "module:ai4e_core.applications.parametric_pde.trainprep"} -->
# `ai4e_core.applications.parametric_pde.trainprep` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-parametric-pde-trainprep-prepare-field-inputs"></a>
## `ai4e_core.applications.parametric_pde.trainprep.prepare_field_inputs`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`prepare_field_inputs(physical, output, *, extract, statistics, transform, declaration: dict, caches=None)`
- **规范定义名**：`ai4e_core.applications.parametric_pde.trainprep.prepare_field_inputs`

### 用途

读取物理样本后按显式抽取/统计/变换准备模型数组；统计只看训练分片。

### 导入与签名

```python
from ai4e_core.applications.parametric_pde.trainprep import prepare_field_inputs
```

```text
prepare_field_inputs(physical, output, *, extract, statistics, transform, declaration: dict, caches=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `physical` | `未标注` | `必填` |
| `output` | `未标注` | `必填` |
| `extract` | `未标注` | `必填关键字参数` |
| `statistics` | `未标注` | `必填关键字参数` |
| `transform` | `未标注` | `必填关键字参数` |
| `declaration` | `dict` | `必填关键字参数` |
| `caches` | `未标注` | `None` |

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
from ai4e_core.applications.parametric_pde.trainprep import prepare_field_inputs

print(signature(prepare_field_inputs))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`geotransolver/darcy`
- 案例：`geotransolver.darcy`

### 源码位置

- 模块：`ai4e_core.applications.parametric_pde.trainprep`
- 仓库相对路径：`packages/ai4e-core/applications/parametric_pde/trainprep.py:58`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.parametric_pde.trainprep')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-parametric-pde-trainprep-read-field-inputs"></a>
## `ai4e_core.applications.parametric_pde.trainprep.read_field_inputs`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`read_field_inputs(path, split)`
- **规范定义名**：`ai4e_core.applications.parametric_pde.trainprep.read_field_inputs`

### 用途

读回可搬移模型准备分片，不依赖原始数据目录。

### 导入与签名

```python
from ai4e_core.applications.parametric_pde.trainprep import read_field_inputs
```

```text
read_field_inputs(path, split)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `未标注` | `必填` |
| `split` | `未标注` | `必填` |

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
from ai4e_core.applications.parametric_pde.trainprep import read_field_inputs

print(signature(read_field_inputs))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`geotransolver/bumper_beam`, `geotransolver/darcy`
- 案例：`geotransolver.bumper_beam`, `geotransolver.darcy`

### 源码位置

- 模块：`ai4e_core.applications.parametric_pde.trainprep`
- 仓库相对路径：`packages/ai4e-core/applications/parametric_pde/trainprep.py:112`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.parametric_pde.trainprep')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-parametric-pde-trainprep-trainprep"></a>
## `ai4e_core.applications.parametric_pde.trainprep.trainprep`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`trainprep(cfg, *, dataset_component, model_component, session)`
- **规范定义名**：`ai4e_core.applications.parametric_pde.trainprep.trainprep`

### 用途

显式执行准备；新目录逐样本提交，失败不发布完整准备清单。

### 导入与签名

```python
from ai4e_core.applications.parametric_pde.trainprep import trainprep
```

```text
trainprep(cfg, *, dataset_component, model_component, session)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cfg` | `未标注` | `必填` |
| `dataset_component` | `未标注` | `必填关键字参数` |
| `model_component` | `未标注` | `必填关键字参数` |
| `session` | `未标注` | `必填关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FileExistsError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.parametric_pde.trainprep import trainprep

print(signature(trainprep))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `gencp`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`, `parametric_pde`, `pcno`, `pcno_cylinder`, `safediffcon`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `extension.pcno`, `extension.pcno_cylinder`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `geothermal.pcno`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `parametric_pde.advection`, `parametric_pde.burgers`, `parametric_pde.convection_diffusion`, `parametric_pde.diffusion_trapezoid`, `parametric_pde.neumann_diffusion`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.gencp`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.sampling`, `recipe_extensions.wdno`, `safediffcon.burgers`, `safediffcon.tokamak`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_core.applications.parametric_pde.trainprep`
- 仓库相对路径：`packages/ai4e-core/applications/parametric_pde/trainprep.py:11`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.parametric_pde.trainprep')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
