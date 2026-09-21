<!-- dojo-help: {"domain": "ai4e_core.applications.aero_cfd.infer.pointfields", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.aero_cfd.infer.pointfields 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.aero_cfd.infer.pointfields", "topic_id": "module:ai4e_core.applications.aero_cfd.infer.pointfields"} -->
# `ai4e_core.applications.aero_cfd.infer.pointfields` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-aero-cfd-infer-pointfields-complete"></a>
## `ai4e_core.applications.aero_cfd.infer.pointfields.complete`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`complete(directory, identity, count, parts, width=4)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.infer.pointfields.complete`

### 用途

验证实际预测内容；同形状但旧权重的文件不可复用。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.infer.pointfields import complete
```

```text
complete(directory, identity, count, parts, width=4)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `directory` | `未标注` | `必填` |
| `identity` | `未标注` | `必填` |
| `count` | `未标注` | `必填` |
| `parts` | `未标注` | `必填` |
| `width` | `未标注` | `4` |

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
from ai4e_core.applications.aero_cfd.infer.pointfields import complete

print(signature(complete))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`wdno`
- 案例：`wdno.burgers_base`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.infer.pointfields`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/infer/pointfields.py:46`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.infer.pointfields')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-infer-pointfields-execute"></a>
## `ai4e_core.applications.aero_cfd.infer.pointfields.execute`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`execute(config, data_component, model_component, run)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.infer.pointfields.execute`

### 用途

独立恢复权重并按声明执行操作，所有失败保留已提交记录。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.infer.pointfields import execute
```

```text
execute(config, data_component, model_component, run)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `未标注` | `必填` |
| `data_component` | `未标注` | `必填` |
| `model_component` | `未标注` | `必填` |
| `run` | `未标注` | `必填` |

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
from ai4e_core.applications.aero_cfd.infer.pointfields import execute

print(signature(execute))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `gencp`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`, `parametric_pde`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `parametric_pde.advection`, `parametric_pde.burgers`, `parametric_pde.convection_diffusion`, `parametric_pde.diffusion_trapezoid`, `parametric_pde.neumann_diffusion`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.infer.pointfields`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/infer/pointfields.py:110`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.infer.pointfields')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-infer-pointfields-metrics-stem"></a>
## `ai4e_core.applications.aero_cfd.infer.pointfields.metrics_stem`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`metrics_stem(selected, all_samples)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.infer.pointfields.metrics_stem`

### 用途

按原选择顺序生成指标文件名，避免不同样本子集相互覆盖。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.infer.pointfields import metrics_stem
```

```text
metrics_stem(selected, all_samples)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `selected` | `未标注` | `必填` |
| `all_samples` | `未标注` | `必填` |

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
from ai4e_core.applications.aero_cfd.infer.pointfields import metrics_stem

print(signature(metrics_stem))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.infer.pointfields`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/infer/pointfields.py:78`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.infer.pointfields')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-infer-pointfields-preflight"></a>
## `ai4e_core.applications.aero_cfd.infer.pointfields.preflight`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`preflight(root, output, inferred, selected, settings)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.infer.pointfields.preflight`

### 用途

干跑与提交共用已有目标检查；恢复模式只授权重新计算合法来源。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.infer.pointfields import preflight
```

```text
preflight(root, output, inferred, selected, settings)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `root` | `未标注` | `必填` |
| `output` | `未标注` | `必填` |
| `inferred` | `未标注` | `必填` |
| `selected` | `未标注` | `必填` |
| `settings` | `未标注` | `必填` |

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
from ai4e_core.applications.aero_cfd.infer.pointfields import preflight

print(signature(preflight))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.infer.pointfields`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/infer/pointfields.py:87`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.infer.pointfields')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-infer-pointfields-select"></a>
## `ai4e_core.applications.aero_cfd.infer.pointfields.select`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`select(available, samples=None, *, all_samples=False)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.infer.pointfields.select`

### 用途

显式全量与指定名单互斥；默认只选择一个随机样本。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.infer.pointfields import select
```

```text
select(available, samples=None, *, all_samples=False)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `available` | `未标注` | `必填` |
| `samples` | `未标注` | `None` |
| `all_samples` | `未标注` | `False` |

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
from ai4e_core.applications.aero_cfd.infer.pointfields import select

print(signature(select))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.infer.pointfields`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/infer/pointfields.py:30`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.infer.pointfields')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
