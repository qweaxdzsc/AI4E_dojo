<!-- dojo-help: {"domain": "ai4e_core.applications.aero_cfd.infer.anchor", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.aero_cfd.infer.anchor 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.aero_cfd.infer.anchor", "topic_id": "module:ai4e_core.applications.aero_cfd.infer.anchor"} -->
# `ai4e_core.applications.aero_cfd.infer.anchor` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-aero-cfd-infer-anchor-configure-evaluation"></a>
## `ai4e_core.applications.aero_cfd.infer.anchor.configure_evaluation`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`configure_evaluation(job, *, settings=None, operation=None, sample_operation=None)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.infer.anchor.configure_evaluation`

### 用途

原生锚点评价允许普通逐场函数，历史评价入口保持原契约。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.infer.anchor import configure_evaluation
```

```text
configure_evaluation(job, *, settings=None, operation=None, sample_operation=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `job` | `未标注` | `必填` |
| `settings` | `未标注` | `None` |
| `operation` | `未标注` | `None` |
| `sample_operation` | `未标注` | `None` |

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
from ai4e_core.applications.aero_cfd.infer.anchor import configure_evaluation

print(signature(configure_evaluation))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.inference_metrics`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.infer.anchor`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/infer/anchor.py:32`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.infer.anchor')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-infer-anchor-configure-mesh-export"></a>
## `ai4e_core.applications.aero_cfd.infer.anchor.configure_mesh_export`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`configure_mesh_export(job, *, settings=None)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.infer.anchor.configure_mesh_export`

### 用途

网格化导出走完整查询或来源回贴；没有可还原拓扑时不登记网格步骤。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.infer.anchor import configure_mesh_export
```

```text
configure_mesh_export(job, *, settings=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `job` | `未标注` | `必填` |
| `settings` | `未标注` | `None` |

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
from ai4e_core.applications.aero_cfd.infer.anchor import configure_mesh_export

print(signature(configure_mesh_export))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.infer.anchor`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/infer/anchor.py:60`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.infer.anchor')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-infer-anchor-configure-selection"></a>
## `ai4e_core.applications.aero_cfd.infer.anchor.configure_selection`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`configure_selection(job, *, fields=None)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.infer.anchor.configure_selection`

### 用途

锚点模板使用同一字段目录，保存仍保留原始向量分量。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.infer.anchor import configure_selection
```

```text
configure_selection(job, *, fields=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `job` | `未标注` | `必填` |
| `fields` | `未标注` | `None` |

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
from ai4e_core.applications.aero_cfd.infer.anchor import configure_selection

print(signature(configure_selection))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.inference_fields`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.infer.anchor`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/infer/anchor.py:176`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.infer.anchor')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-infer-anchor-execute"></a>
## `ai4e_core.applications.aero_cfd.infer.anchor.execute`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`execute(job)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.infer.anchor.execute`

### 用途

执行原有锚点流并发布统一索引，不把数组写入索引。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.infer.anchor import execute
```

```text
execute(job)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `job` | `未标注` | `必填` |

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
from ai4e_core.applications.aero_cfd.infer.anchor import execute

print(signature(execute))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `gencp`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`, `parametric_pde`, `safediffcon`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `parametric_pde.advection`, `parametric_pde.burgers`, `parametric_pde.convection_diffusion`, `parametric_pde.diffusion_trapezoid`, `parametric_pde.neumann_diffusion`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.sampling`, `safediffcon.burgers`, `safediffcon.tokamak`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.infer.anchor`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/infer/anchor.py:90`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.infer.anchor')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-infer-anchor-open-inference"></a>
## `ai4e_core.applications.aero_cfd.infer.anchor.open_inference`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`open_inference(config, *, model_component, session, dataset_component=None, trained=None)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.infer.anchor.open_inference`

### 用途

登记旧锚点输入的独立推理；原子计算与历史 post 共用。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.infer.anchor import open_inference
```

```text
open_inference(config, *, model_component, session, dataset_component=None, trained=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `未标注` | `必填` |
| `model_component` | `未标注` | `必填关键字参数` |
| `session` | `未标注` | `必填关键字参数` |
| `dataset_component` | `未标注` | `None` |
| `trained` | `未标注` | `None` |

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
from ai4e_core.applications.aero_cfd.infer.anchor import open_inference

print(signature(open_inference))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.infer.anchor`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/infer/anchor.py:17`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.infer.anchor')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-infer-anchor-run-selected-batches"></a>
## `ai4e_core.applications.aero_cfd.infer.anchor.run_selected_batches`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`run_selected_batches(config, restored, batches, *, predict, progress, protocol)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.infer.anchor.run_selected_batches`

### 用途

原生锚点推理一次预测后评价和保存，旧 post 保留原两次遍历。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.infer.anchor import run_selected_batches
```

```text
run_selected_batches(config, restored, batches, *, predict, progress, protocol)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `未标注` | `必填` |
| `restored` | `未标注` | `必填` |
| `batches` | `未标注` | `必填` |
| `predict` | `未标注` | `必填关键字参数` |
| `progress` | `未标注` | `必填关键字参数` |
| `protocol` | `未标注` | `必填关键字参数` |

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
from ai4e_core.applications.aero_cfd.infer.anchor import run_selected_batches

print(signature(run_selected_batches))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.infer.anchor`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/infer/anchor.py:186`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.infer.anchor')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
