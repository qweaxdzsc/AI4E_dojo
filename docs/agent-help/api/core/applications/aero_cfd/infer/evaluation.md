<!-- dojo-help: {"domain": "ai4e_core.applications.aero_cfd.infer.evaluation", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.aero_cfd.infer.evaluation 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.aero_cfd.infer.evaluation", "topic_id": "module:ai4e_core.applications.aero_cfd.infer.evaluation"} -->
# `ai4e_core.applications.aero_cfd.infer.evaluation` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-aero-cfd-infer-evaluation-evaluate-sample"></a>
## `ai4e_core.applications.aero_cfd.infer.evaluation.evaluate_sample`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`evaluate_sample(item, selections, metrics=None) -> list[dict]`
- **规范定义名**：`ai4e_core.applications.aero_cfd.infer.evaluation.evaluate_sample`

### 用途

使用当前预测数组评价选中分量，结果不依赖是否保存张量。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.infer.evaluation import evaluate_sample
```

```text
evaluate_sample(item, selections, metrics=None) -> list[dict]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `item` | `未标注` | `必填` |
| `selections` | `未标注` | `必填` |
| `metrics` | `未标注` | `None` |

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
from ai4e_core.applications.aero_cfd.infer.evaluation import evaluate_sample

print(signature(evaluate_sample))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.inference_metrics`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.infer.evaluation`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/infer/evaluation.py:10`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.infer.evaluation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-infer-evaluation-record-metric"></a>
## `ai4e_core.applications.aero_cfd.infer.evaluation.record_metric`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`record_metric(row: dict, metric: str)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.infer.evaluation.record_metric`

### 用途

读取固定样本指标；性能值仅由已登记的预测计时取得。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.infer.evaluation import record_metric
```

```text
record_metric(row: dict, metric: str)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `row` | `dict` | `必填` |
| `metric` | `str` | `必填` |

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
from ai4e_core.applications.aero_cfd.infer.evaluation import record_metric

print(signature(record_metric))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `gencp`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`, `pcno`, `surrogate_modeling/double_cylinder`, `surrogate_modeling/nasa_crm`
- 案例：`classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `geothermal.pcno`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `surrogate_modeling.double_cylinder`, `surrogate_modeling.nasa_crm`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.infer.evaluation`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/infer/evaluation.py:127`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.infer.evaluation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-infer-evaluation-result-views"></a>
## `ai4e_core.applications.aero_cfd.infer.evaluation.result_views`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`result_views(records: list[dict]) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.infer.evaluation.result_views`

### 用途

交付可直接展示的样本值和全部分片统计，不加载或预测模型。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.infer.evaluation import result_views
```

```text
result_views(records: list[dict]) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `records` | `list[dict]` | `必填` |

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
from ai4e_core.applications.aero_cfd.infer.evaluation import result_views

print(signature(result_views))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.infer.evaluation`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/infer/evaluation.py:137`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.infer.evaluation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-infer-evaluation-summarize-records"></a>
## `ai4e_core.applications.aero_cfd.infer.evaluation.summarize_records`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`summarize_records(records: list[dict], *, include_all: bool=False) -> list[dict]`
- **规范定义名**：`ai4e_core.applications.aero_cfd.infer.evaluation.summarize_records`

### 用途

按权重、分片和物理量分组；缺失结果不会被当作完整成功。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.infer.evaluation import summarize_records
```

```text
summarize_records(records: list[dict], *, include_all: bool=False) -> list[dict]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `records` | `list[dict]` | `必填` |
| `include_all` | `bool` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`list[dict]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.infer.evaluation import summarize_records

print(signature(summarize_records))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.infer.evaluation`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/infer/evaluation.py:54`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.infer.evaluation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
