<!-- dojo-help: {"domain": "ai4e_contrib.application.spatiotemporal_pde.wdno.handoff", "kind": "api", "layer": "contrib.application", "summary": "ai4e_contrib.application.spatiotemporal_pde.wdno.handoff 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.application.spatiotemporal_pde.wdno.handoff", "topic_id": "module:ai4e_contrib.application.spatiotemporal_pde.wdno.handoff"} -->
# `ai4e_contrib.application.spatiotemporal_pde.wdno.handoff` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-application-spatiotemporal-pde-wdno-handoff-record-arrays"></a>
## `ai4e_contrib.application.spatiotemporal_pde.wdno.handoff.record_arrays`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`record_arrays(session, references: dict, *, stage: str, kind: str) -> None`
- **规范定义名**：`ai4e_contrib.application.spatiotemporal_pde.wdno.handoff.record_arrays`

### 用途

登记已经保存的分片及真实数组依赖，供Task查询和引用。

### 导入与签名

```python
from ai4e_contrib.application.spatiotemporal_pde.wdno.handoff import record_arrays
```

```text
record_arrays(session, references: dict, *, stage: str, kind: str) -> None
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `session` | `未标注` | `必填` |
| `references` | `dict` | `必填` |
| `stage` | `str` | `必填关键字参数` |
| `kind` | `str` | `必填关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`None`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.application.spatiotemporal_pde.wdno.handoff import record_arrays

print(signature(record_arrays))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`wdno`
- 案例：`wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.application.spatiotemporal_pde.wdno.handoff`
- 仓库相对路径：`packages/ai4e-contrib/application/spatiotemporal_pde/wdno/handoff.py:40`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.spatiotemporal_pde.wdno.handoff')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-spatiotemporal-pde-wdno-handoff-record-metrics"></a>
## `ai4e_contrib.application.spatiotemporal_pde.wdno.handoff.record_metrics`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`record_metrics(session, results: dict, summary: dict, metrics) -> None`
- **规范定义名**：`ai4e_contrib.application.spatiotemporal_pde.wdno.handoff.record_metrics`

### 用途

MSE携带目标与样本身份、初帧排除和样本等权口径，拒绝跨定义冒比。

### 导入与签名

```python
from ai4e_contrib.application.spatiotemporal_pde.wdno.handoff import record_metrics
```

```text
record_metrics(session, results: dict, summary: dict, metrics) -> None
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `session` | `未标注` | `必填` |
| `results` | `dict` | `必填` |
| `summary` | `dict` | `必填` |
| `metrics` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`None`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.application.spatiotemporal_pde.wdno.handoff import record_metrics

print(signature(record_metrics))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`wdno`
- 案例：`wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.application.spatiotemporal_pde.wdno.handoff`
- 仓库相对路径：`packages/ai4e-contrib/application/spatiotemporal_pde/wdno/handoff.py:54`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.spatiotemporal_pde.wdno.handoff')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-spatiotemporal-pde-wdno-handoff-split-inputs"></a>
## `ai4e_contrib.application.spatiotemporal_pde.wdno.handoff.split_inputs`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`split_inputs(cfg: dict, stage: str, explicit: dict | None=None) -> dict`
- **规范定义名**：`ai4e_contrib.application.spatiotemporal_pde.wdno.handoff.split_inputs`

### 用途

逐分片选择本次返回值或显式输入，两者不同则报错。

### 导入与签名

```python
from ai4e_contrib.application.spatiotemporal_pde.wdno.handoff import split_inputs
```

```text
split_inputs(cfg: dict, stage: str, explicit: dict | None=None) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cfg` | `dict` | `必填` |
| `stage` | `str` | `必填` |
| `explicit` | `dict | None` | `None` |

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
from ai4e_contrib.application.spatiotemporal_pde.wdno.handoff import split_inputs

print(signature(split_inputs))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`wdno`
- 案例：`wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.application.spatiotemporal_pde.wdno.handoff`
- 仓库相对路径：`packages/ai4e-contrib/application/spatiotemporal_pde/wdno/handoff.py:11`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.spatiotemporal_pde.wdno.handoff')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
