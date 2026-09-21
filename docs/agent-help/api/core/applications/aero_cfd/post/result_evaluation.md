<!-- dojo-help: {"domain": "ai4e_core.applications.aero_cfd.post.result_evaluation", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.aero_cfd.post.result_evaluation 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.aero_cfd.post.result_evaluation", "topic_id": "module:ai4e_core.applications.aero_cfd.post.result_evaluation"} -->
# `ai4e_core.applications.aero_cfd.post.result_evaluation` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-aero-cfd-post-result-evaluation-describe-result-fields"></a>
## `ai4e_core.applications.aero_cfd.post.result_evaluation.describe_result_fields`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`describe_result_fields(manifests)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.post.result_evaluation.describe_result_fields`

### 用途

只读张量头部获取分量，FakeTensorMode不载入场数组或模型权重。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.post.result_evaluation import describe_result_fields
```

```text
describe_result_fields(manifests)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `manifests` | `未标注` | `必填` |

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
from ai4e_core.applications.aero_cfd.post.result_evaluation import describe_result_fields

print(signature(describe_result_fields))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.post.result_evaluation`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/post/result_evaluation.py:97`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.post.result_evaluation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-post-result-evaluation-evaluate-fields"></a>
## `ai4e_core.applications.aero_cfd.post.result_evaluation.evaluate_fields`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`evaluate_fields(sample: dict, *, selections: list[str] | None, metrics: list[str] | None=None, operation: Callable | None=None) -> list[dict]`
- **规范定义名**：`ai4e_core.applications.aero_cfd.post.result_evaluation.evaluate_fields`

### 用途

评价已经绑定的内存字段；与文件评价复用同一数值能力。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.post.result_evaluation import evaluate_fields
```

```text
evaluate_fields(sample: dict, *, selections: list[str] | None, metrics: list[str] | None=None, operation: Callable | None=None) -> list[dict]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `sample` | `dict` | `必填` |
| `selections` | `list[str] | None` | `必填关键字参数` |
| `metrics` | `list[str] | None` | `None` |
| `operation` | `Callable | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`list[dict]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.post.result_evaluation import evaluate_fields

print(signature(evaluate_fields))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `gencp`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `recipe_extensions.gencp`, `recipe_extensions.geotransolver_aero`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.post.result_evaluation`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/post/result_evaluation.py:24`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.post.result_evaluation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-post-result-evaluation-evaluate-result"></a>
## `ai4e_core.applications.aero_cfd.post.result_evaluation.evaluate_result`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`evaluate_result(item, selections, metrics)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.post.result_evaluation.evaluate_result`

### 用途

逐样本读回，核对固定成员、域和实体；每个字段返回独立状态。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.post.result_evaluation import evaluate_result
```

```text
evaluate_result(item, selections, metrics)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `item` | `未标注` | `必填` |
| `selections` | `未标注` | `必填` |
| `metrics` | `未标注` | `必填` |

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
from ai4e_core.applications.aero_cfd.post.result_evaluation import evaluate_result

print(signature(evaluate_result))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.post.result_evaluation`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/post/result_evaluation.py:140`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.post.result_evaluation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-post-result-evaluation-export-evaluation"></a>
## `ai4e_core.applications.aero_cfd.post.result_evaluation.export_evaluation`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`export_evaluation(record, path, *, format, row_ids=None)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.post.result_evaluation.export_evaluation`

### 用途

显式导出固定评价行，完整保留数值、来源、单位和失败状态。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.post.result_evaluation import export_evaluation
```

```text
export_evaluation(record, path, *, format, row_ids=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `record` | `未标注` | `必填` |
| `path` | `未标注` | `必填` |
| `format` | `未标注` | `必填关键字参数` |
| `row_ids` | `未标注` | `None` |

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
from ai4e_core.applications.aero_cfd.post.result_evaluation import export_evaluation

print(signature(export_evaluation))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.post.result_evaluation`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/post/result_evaluation.py:259`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.post.result_evaluation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-post-result-evaluation-metric-catalog"></a>
## `ai4e_core.applications.aero_cfd.post.result_evaluation.metric_catalog`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`metric_catalog()`
- **规范定义名**：`ai4e_core.applications.aero_cfd.post.result_evaluation.metric_catalog`

### 用途

返回固定结果可重算的评价指标。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.post.result_evaluation import metric_catalog
```

```text
metric_catalog()
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
from ai4e_core.applications.aero_cfd.post.result_evaluation import metric_catalog

print(signature(metric_catalog))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.post.result_evaluation`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/post/result_evaluation.py:17`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.post.result_evaluation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-post-result-evaluation-run-evaluation"></a>
## `ai4e_core.applications.aero_cfd.post.result_evaluation.run_evaluation`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`run_evaluation(job, *, runtime)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.post.result_evaluation.run_evaluation`

### 用途

计算固定结果；运行外围由调用方注入，数据逐样本追加以保留部分交付。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.post.result_evaluation import run_evaluation
```

```text
run_evaluation(job, *, runtime)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `job` | `未标注` | `必填` |
| `runtime` | `未标注` | `必填关键字参数` |

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
from ai4e_core.applications.aero_cfd.post.result_evaluation import run_evaluation

print(signature(run_evaluation))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.post.result_evaluation`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/post/result_evaluation.py:193`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.post.result_evaluation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
