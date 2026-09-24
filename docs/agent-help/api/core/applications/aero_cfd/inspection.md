<!-- dojo-help: {"domain": "ai4e_core.applications.aero_cfd.inspection", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.aero_cfd.inspection 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.aero_cfd.inspection", "topic_id": "module:ai4e_core.applications.aero_cfd.inspection"} -->
# `ai4e_core.applications.aero_cfd.inspection` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-aero-cfd-inspection-execute"></a>
## `ai4e_core.applications.aero_cfd.inspection.execute`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`execute(request: dict) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.inspection.execute`

### 用途

执行 describe_case/inspect_dataset/validate_configuration/trace_model/compare_fields。trace_model 只取样组网。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.inspection import execute
```

```text
execute(request: dict) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `request` | `dict` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.inspection import execute

print(signature(execute))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `gencp`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`, `parametric_pde`, `safediffcon`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `parametric_pde.advection`, `parametric_pde.burgers`, `parametric_pde.convection_diffusion`, `parametric_pde.diffusion_trapezoid`, `parametric_pde.neumann_diffusion`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.sampling`, `safediffcon.burgers`, `safediffcon.tokamak`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.inspection`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/inspection.py:248`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.inspection')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-inspection-normalize-config"></a>
## `ai4e_core.applications.aero_cfd.inspection.normalize_config`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`normalize_config(config: dict) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.inspection.normalize_config`

### 用途

五段用户输入转换为既有业务树，旧采样单键兼容，双键拒绝。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.inspection import normalize_config
```

```text
normalize_config(config: dict) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `dict` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.inspection import normalize_config

print(signature(normalize_config))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.inspection`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/inspection.py:12`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.inspection')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-inspection-parameter-capabilities"></a>
## `ai4e_core.applications.aero_cfd.inspection.parameter_capabilities`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`parameter_capabilities(config, model)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.inspection.parameter_capabilities`

### 用途

由实际工作流和模型提供者导出可编辑范围，含损失与采样能力，不让前端重写算法限制。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.inspection import parameter_capabilities
```

```text
parameter_capabilities(config, model)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `未标注` | `必填` |
| `model` | `未标注` | `必填` |

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
from ai4e_core.applications.aero_cfd.inspection import parameter_capabilities

print(signature(parameter_capabilities))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.inspection`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/inspection.py:158`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.inspection')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-inspection-public-configuration"></a>
## `ai4e_core.applications.aero_cfd.inspection.public_configuration`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`public_configuration(config: dict) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.inspection.public_configuration`

### 用途

返回可保存的五段输入；不把内部展开树反馈为用户 YAML。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.inspection import public_configuration
```

```text
public_configuration(config: dict) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `dict` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.inspection import public_configuration

print(signature(public_configuration))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.inspection`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/inspection.py:33`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.inspection')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
