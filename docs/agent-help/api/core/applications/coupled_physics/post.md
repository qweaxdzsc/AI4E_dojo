<!-- dojo-help: {"domain": "ai4e_core.applications.coupled_physics.post", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.coupled_physics.post 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.coupled_physics.post", "topic_id": "module:ai4e_core.applications.coupled_physics.post"} -->
# `ai4e_core.applications.coupled_physics.post` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-coupled-physics-post-evaluate-fields"></a>
## `ai4e_core.applications.coupled_physics.post.evaluate_fields`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`evaluate_fields(pairs)`
- **规范定义名**：`ai4e_core.applications.coupled_physics.post.evaluate_fields`

### 用途

逐场时空物理量评价，输出可独立 JSON 保存的数值。

### 导入与签名

```python
from ai4e_core.applications.coupled_physics.post import evaluate_fields
```

```text
evaluate_fields(pairs)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `pairs` | `未标注` | `必填` |

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
from ai4e_core.applications.coupled_physics.post import evaluate_fields

print(signature(evaluate_fields))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `gencp`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `recipe_extensions.gencp`, `recipe_extensions.geotransolver_aero`

### 源码位置

- 模块：`ai4e_core.applications.coupled_physics.post`
- 仓库相对路径：`packages/ai4e-core/applications/coupled_physics/post.py:36`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.coupled_physics.post')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-coupled-physics-post-export-analysis"></a>
## `ai4e_core.applications.coupled_physics.post.export_analysis`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`export_analysis(pairs, metrics, output, *, metadata, plots=True, derived=None)`
- **规范定义名**：`ai4e_core.applications.coupled_physics.post.export_analysis`

### 用途

保存派生数组、轻量指标和静态图；所有输入来自固定结果。

### 导入与签名

```python
from ai4e_core.applications.coupled_physics.post import export_analysis
```

```text
export_analysis(pairs, metrics, output, *, metadata, plots=True, derived=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `pairs` | `未标注` | `必填` |
| `metrics` | `未标注` | `必填` |
| `output` | `未标注` | `必填` |
| `metadata` | `未标注` | `必填关键字参数` |
| `plots` | `未标注` | `True` |
| `derived` | `未标注` | `None` |

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
from ai4e_core.applications.coupled_physics.post import export_analysis

print(signature(export_analysis))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`gencp`
- 案例：`gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `recipe_extensions.gencp`

### 源码位置

- 模块：`ai4e_core.applications.coupled_physics.post`
- 仓库相对路径：`packages/ai4e-core/applications/coupled_physics/post.py:44`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.coupled_physics.post')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-coupled-physics-post-read-results"></a>
## `ai4e_core.applications.coupled_physics.post.read_results`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`read_results(path)`
- **规范定义名**：`ai4e_core.applications.coupled_physics.post.read_results`

### 用途

读固定预测和真值；拒绝非数值 pickle 与形状漂移。

### 导入与签名

```python
from ai4e_core.applications.coupled_physics.post import read_results
```

```text
read_results(path)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `未标注` | `必填` |

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
from ai4e_core.applications.coupled_physics.post import read_results

print(signature(read_results))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`gencp`, `pcno`
- 案例：`extension.pcno`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `geothermal.pcno`, `recipe_extensions.gencp`

### 源码位置

- 模块：`ai4e_core.applications.coupled_physics.post`
- 仓库相对路径：`packages/ai4e-core/applications/coupled_physics/post.py:16`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.coupled_physics.post')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
