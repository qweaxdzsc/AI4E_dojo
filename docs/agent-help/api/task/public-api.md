<!-- dojo-help: {"domain": "ai4e_task.templates.resources", "kind": "api", "layer": "task", "summary": "ai4e_task.templates.resources 的完整源码参考与公开符号索引。", "title": "ai4e_task.templates.resources", "topic_id": "module:ai4e_task.templates.resources"} -->
# `ai4e_task.templates.resources` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-task-helpindexerror"></a>
## `ai4e_task.HelpIndexError`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`class HelpIndexError`
- **规范定义名**：`ai4e_task.templates.resources.HelpIndexError`

### 用途

帮助中心清单或索引损坏。

### 导入与签名

```python
from ai4e_task.templates.resources import HelpIndexError
```

```text
class HelpIndexError
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`HelpIndexError`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.templates.resources import HelpIndexError

print(signature(HelpIndexError))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.templates.resources`
- 仓库相对路径：`packages/ai4e-task/templates/resources.py:23`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.templates.resources')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-helpsymbolnotfounderror"></a>
## `ai4e_task.HelpSymbolNotFoundError`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`class HelpSymbolNotFoundError`
- **规范定义名**：`ai4e_task.templates.resources.HelpSymbolNotFoundError`

### 用途

请求的 API 符号不存在。

### 导入与签名

```python
from ai4e_task.templates.resources import HelpSymbolNotFoundError
```

```text
class HelpSymbolNotFoundError
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`HelpSymbolNotFoundError`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.templates.resources import HelpSymbolNotFoundError

print(signature(HelpSymbolNotFoundError))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.templates.resources`
- 仓库相对路径：`packages/ai4e-task/templates/resources.py:31`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.templates.resources')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-helptopicnotfounderror"></a>
## `ai4e_task.HelpTopicNotFoundError`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`class HelpTopicNotFoundError`
- **规范定义名**：`ai4e_task.templates.resources.HelpTopicNotFoundError`

### 用途

请求的帮助主题不存在。

### 导入与签名

```python
from ai4e_task.templates.resources import HelpTopicNotFoundError
```

```text
class HelpTopicNotFoundError
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`HelpTopicNotFoundError`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.templates.resources import HelpTopicNotFoundError

print(signature(HelpTopicNotFoundError))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.templates.resources`
- 仓库相对路径：`packages/ai4e-task/templates/resources.py:27`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.templates.resources')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-bind-shared-dataset"></a>
## `ai4e_task.bind_shared_dataset`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`bind_shared_dataset(project: str | Path, task_id: str, name: str, *, revision: str, binding: str | None=None) -> dict`
- **规范定义名**：`ai4e_task.projects.datasets.bind_shared_dataset`

### 用途

将当前共享清单绑定到入口声明的消费键，配置与资产在同一事务保存。

### 导入与签名

```python
from ai4e_task.projects.datasets import bind_shared_dataset
```

```text
bind_shared_dataset(project: str | Path, task_id: str, name: str, *, revision: str, binding: str | None=None) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `task_id` | `str` | `必填` |
| `name` | `str` | `必填` |
| `revision` | `str` | `必填关键字参数` |
| `binding` | `str | None` | `None` |

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
from ai4e_task.projects.datasets import bind_shared_dataset

print(signature(bind_shared_dataset))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.projects.datasets`
- 仓库相对路径：`packages/ai4e-task/projects/datasets.py:43`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.projects.datasets')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-cancel-inference"></a>
## `ai4e_task.cancel_inference`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`cancel_inference(project: str | Path, task_id: str, identity: str) -> dict`
- **规范定义名**：`ai4e_task.tasks.inference.cancel_inference`

### 用途

写入取消意图，由协调器停止自身子运行；不向训练进程发送信号。

### 导入与签名

```python
from ai4e_task.tasks.inference import cancel_inference
```

```text
cancel_inference(project: str | Path, task_id: str, identity: str) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `task_id` | `str` | `必填` |
| `identity` | `str` | `必填` |

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
from ai4e_task.tasks.inference import cancel_inference

print(signature(cancel_inference))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.inference`
- 仓库相对路径：`packages/ai4e-task/tasks/inference.py:292`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.inference')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-cancel-post-metrics"></a>
## `ai4e_task.cancel_post_metrics`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`cancel_post_metrics(project, task_id, identity)`
- **规范定义名**：`ai4e_task.tasks.post_metrics.cancel_post_metrics`

### 用途

请求在样本边界停止，不终止训练或推理进程。

### 导入与签名

```python
from ai4e_task.tasks.post_metrics import cancel_post_metrics
```

```text
cancel_post_metrics(project, task_id, identity)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `未标注` | `必填` |
| `task_id` | `未标注` | `必填` |
| `identity` | `未标注` | `必填` |

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
from ai4e_task.tasks.post_metrics import cancel_post_metrics

print(signature(cancel_post_metrics))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.post_metrics`
- 仓库相对路径：`packages/ai4e-task/tasks/post_metrics.py:221`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.post_metrics')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-check-example"></a>
## `ai4e_task.check_example`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`check_example(case_id: str) -> dict[str, Any]`
- **规范定义名**：`ai4e_task.templates.resources.check_example`

### 用途

检查案例文件、路径污染和 extension 引用，不执行或导入案例。

### 导入与签名

```python
from ai4e_task.templates.resources import check_example
```

```text
check_example(case_id: str) -> dict[str, Any]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `case_id` | `str` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, Any]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.templates.resources import check_example

print(signature(check_example))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.templates.resources`
- 仓库相对路径：`packages/ai4e-task/templates/resources.py:359`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.templates.resources')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-check-inference"></a>
## `ai4e_task.check_inference`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`check_inference(project: str | Path, task_id: str, request: dict) -> dict`
- **规范定义名**：`ai4e_task.tasks.inference.check_inference`

### 用途

预检完整批次并解析设备；不创建训练、推理运行或正式版本。

### 导入与签名

```python
from ai4e_task.tasks.inference import check_inference
```

```text
check_inference(project: str | Path, task_id: str, request: dict) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `task_id` | `str` | `必填` |
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
from ai4e_task.tasks.inference import check_inference

print(signature(check_inference))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.inference`
- 仓库相对路径：`packages/ai4e-task/tasks/inference.py:57`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.inference')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-check-processed-name"></a>
## `ai4e_task.check_processed_name`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`check_processed_name(workspace: str | Path, name: str, *, claim: dict | None=None, context: dict | None=None, overwrite: bool=False) -> dict`
- **规范定义名**：`ai4e_task.storage.processed_datasets.check_processed_name`

### 用途

执行前核对名称；未确认覆盖时同名不同声明拒绝。

### 导入与签名

```python
from ai4e_task.storage.processed_datasets import check_processed_name
```

```text
check_processed_name(workspace: str | Path, name: str, *, claim: dict | None=None, context: dict | None=None, overwrite: bool=False) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `workspace` | `str | Path` | `必填` |
| `name` | `str` | `必填` |
| `claim` | `dict | None` | `None` |
| `context` | `dict | None` | `None` |
| `overwrite` | `bool` | `False` |

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
from ai4e_task.storage.processed_datasets import check_processed_name

print(signature(check_processed_name))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.storage.processed_datasets`
- 仓库相对路径：`packages/ai4e-task/storage/processed_datasets.py:103`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.storage.processed_datasets')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-compare-runs"></a>
## `ai4e_task.compare_runs`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`compare_runs(project: str | Path, left: str, right: str, *, save: bool=False) -> dict`
- **规范定义名**：`ai4e_task.versions.compare.compare_runs`

### 用途

比较固定运行的已有指标；身份与统计定义不匹配时标不可比。

### 导入与签名

```python
from ai4e_task.versions.compare import compare_runs
```

```text
compare_runs(project: str | Path, left: str, right: str, *, save: bool=False) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `left` | `str` | `必填` |
| `right` | `str` | `必填` |
| `save` | `bool` | `False` |

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
from ai4e_task.versions.compare import compare_runs

print(signature(compare_runs))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.versions.compare`
- 仓库相对路径：`packages/ai4e-task/versions/compare.py:116`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.versions.compare')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-compare-versions"></a>
## `ai4e_task.compare_versions`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`compare_versions(project: str | Path, left: str, right: str, *, save: bool=False) -> dict`
- **规范定义名**：`ai4e_task.versions.compare.compare_versions`

### 用途

比较两个正式版本的创建记录，默认不持久化查询。

### 导入与签名

```python
from ai4e_task.versions.compare import compare_versions
```

```text
compare_versions(project: str | Path, left: str, right: str, *, save: bool=False) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `left` | `str` | `必填` |
| `right` | `str` | `必填` |
| `save` | `bool` | `False` |

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
from ai4e_task.versions.compare import compare_versions

print(signature(compare_versions))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.versions.compare`
- 仓库相对路径：`packages/ai4e-task/versions/compare.py:48`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.versions.compare')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-compare-worktree"></a>
## `ai4e_task.compare_worktree`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`compare_worktree(project: str | Path, task_id: str) -> dict`
- **规范定义名**：`ai4e_task.versions.compare.compare_worktree`

### 用途

查询工作目录相对创建记录的变化，不创建正式版本。

### 导入与签名

```python
from ai4e_task.versions.compare import compare_worktree
```

```text
compare_worktree(project: str | Path, task_id: str) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `task_id` | `str` | `必填` |

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
from ai4e_task.versions.compare import compare_worktree

print(signature(compare_worktree))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.versions.compare`
- 仓库相对路径：`packages/ai4e-task/versions/compare.py:69`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.versions.compare')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-configuration-context"></a>
## `ai4e_task.configuration_context`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`configuration_context(config: dict, config_dir: str | Path, *, name='inspect') -> dict`
- **规范定义名**：`ai4e_task.tasks.operation_sources.configuration_context`

### 用途

未属于任务的显式配置上下文；必须声明应用及配置来源目录。

### 导入与签名

```python
from ai4e_task.tasks.operation_sources import configuration_context
```

```text
configuration_context(config: dict, config_dir: str | Path, *, name='inspect') -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `dict` | `必填` |
| `config_dir` | `str | Path` | `必填` |
| `name` | `未标注` | `'inspect'` |

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
from ai4e_task.tasks.operation_sources import configuration_context

print(signature(configuration_context))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.operation_sources`
- 仓库相对路径：`packages/ai4e-task/tasks/operation_sources.py:142`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.operation_sources')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-copy-example"></a>
## `ai4e_task.copy_example`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`copy_example(case_id: str, target: str | Path) -> dict[str, Any]`
- **规范定义名**：`ai4e_task.templates.resources.copy_example`

### 用途

物化完整案例并交付来源可追溯的说明副本，保留原脚本和README字节。

### 导入与签名

```python
from ai4e_task.templates.resources import copy_example
```

```text
copy_example(case_id: str, target: str | Path) -> dict[str, Any]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `case_id` | `str` | `必填` |
| `target` | `str | Path` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, Any]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FileExistsError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.templates.resources import copy_example

print(signature(copy_example))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`
- 案例：`extension.pcno`, `extension.pcno_cylinder`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.free_wiring`, `recipe_extensions.gencp`, `recipe_extensions.geotransolver`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.inference_fields`, `recipe_extensions.inference_metrics`, `recipe_extensions.model_block`, `recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.resunet`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`, `recipe_extensions.operator_physical_loss`, `recipe_extensions.physical_visualization`, `recipe_extensions.pod_surrogate_replacement`, `recipe_extensions.research_state`, `recipe_extensions.safediffcon`, `recipe_extensions.sampling`, `recipe_extensions.tail_batch`, `recipe_extensions.task_labels`, `recipe_extensions.wdno`

### 源码位置

- 模块：`ai4e_task.templates.resources`
- 仓库相对路径：`packages/ai4e-task/templates/resources.py:413`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.templates.resources')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-create-project"></a>
## `ai4e_task.create_project`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`create_project(path: str | Path, *, name: str | None=None) -> Project`
- **规范定义名**：`ai4e_task.projects.project.create_project`

### 用途

原子创建新项目；拒绝覆盖任何已有目录。

### 导入与签名

```python
from ai4e_task.projects.project import create_project
```

```text
create_project(path: str | Path, *, name: str | None=None) -> Project
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `str | Path` | `必填` |
| `name` | `str | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Project`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.projects.project import create_project

print(signature(create_project))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.projects.project`
- 仓库相对路径：`packages/ai4e-task/projects/project.py:14`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.projects.project')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-create-smoke-data"></a>
## `ai4e_task.create_smoke_data`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`create_smoke_data(target: str | Path, *, case_id: str | None=None) -> dict[str, Any]`
- **规范定义名**：`ai4e_task.templates.resources.create_smoke_data`

### 用途

通过案例资源声明在隔离进程生成数据；管理进程不加载领域模块。

### 导入与签名

```python
from ai4e_task.templates.resources import create_smoke_data
```

```text
create_smoke_data(target: str | Path, *, case_id: str | None=None) -> dict[str, Any]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `target` | `str | Path` | `必填` |
| `case_id` | `str | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, Any]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.templates.resources import create_smoke_data

print(signature(create_smoke_data))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.templates.resources`
- 仓库相对路径：`packages/ai4e-task/templates/resources.py:531`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.templates.resources')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-describe-help-symbol"></a>
## `ai4e_task.describe_help_symbol`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`describe_help_symbol(symbol: str) -> dict[str, Any]`
- **规范定义名**：`ai4e_task.templates.resources.describe_help_symbol`

### 用途

按全限定名返回签名、稳定性、正文锚点和源码位置。

### 导入与签名

```python
from ai4e_task.templates.resources import describe_help_symbol
```

```text
describe_help_symbol(symbol: str) -> dict[str, Any]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `symbol` | `str` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, Any]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`HelpSymbolNotFoundError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.templates.resources import describe_help_symbol

print(signature(describe_help_symbol))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.templates.resources`
- 仓库相对路径：`packages/ai4e-task/templates/resources.py:252`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.templates.resources')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-describe-processed-dataset"></a>
## `ai4e_task.describe_processed_dataset`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`describe_processed_dataset(workspace: str | Path, name: str) -> dict`
- **规范定义名**：`ai4e_task.storage.processed_datasets.describe_processed_dataset`

### 用途

读取一条登记并核验清单是否仍可用。

### 导入与签名

```python
from ai4e_task.storage.processed_datasets import describe_processed_dataset
```

```text
describe_processed_dataset(workspace: str | Path, name: str) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `workspace` | `str | Path` | `必填` |
| `name` | `str` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`KeyError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.storage.processed_datasets import describe_processed_dataset

print(signature(describe_processed_dataset))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.storage.processed_datasets`
- 仓库相对路径：`packages/ai4e-task/storage/processed_datasets.py:39`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.storage.processed_datasets')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-describe-processed-name"></a>
## `ai4e_task.describe_processed_name`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`describe_processed_name(workspace: str | Path, name: str, *, claim: dict | None=None, context: dict | None=None) -> dict`
- **规范定义名**：`ai4e_task.storage.processed_datasets.describe_processed_name`

### 用途

给页面回传名称状态；不抛冲突，未确认覆盖的正式提交仍走 check_processed_name。

### 导入与签名

```python
from ai4e_task.storage.processed_datasets import describe_processed_name
```

```text
describe_processed_name(workspace: str | Path, name: str, *, claim: dict | None=None, context: dict | None=None) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `workspace` | `str | Path` | `必填` |
| `name` | `str` | `必填` |
| `claim` | `dict | None` | `None` |
| `context` | `dict | None` | `None` |

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
from ai4e_task.storage.processed_datasets import describe_processed_name

print(signature(describe_processed_name))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.storage.processed_datasets`
- 仓库相对路径：`packages/ai4e-task/storage/processed_datasets.py:80`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.storage.processed_datasets')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-describe-rawprep"></a>
## `ai4e_task.describe_rawprep`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`describe_rawprep(project, task_id)`
- **规范定义名**：`ai4e_task.tasks.rawprep.describe_rawprep`

### 用途

固定当前修订后返回默认配置和处理描述，不修改任务。

### 导入与签名

```python
from ai4e_task.tasks.rawprep import describe_rawprep
```

```text
describe_rawprep(project, task_id)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `未标注` | `必填` |
| `task_id` | `未标注` | `必填` |

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
from ai4e_task.tasks.rawprep import describe_rawprep

print(signature(describe_rawprep))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.rawprep`
- 仓库相对路径：`packages/ai4e-task/tasks/rawprep.py:12`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.rawprep')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-describe-recipe"></a>
## `ai4e_task.describe_recipe`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`describe_recipe(recipe: str | Path, *, config: dict | None=None, cache_dir: Path | None=None) -> dict`
- **规范定义名**：`ai4e_task.tasks.descriptions.describe_recipe`

### 用途

缺少应用声明返回空描述；已声明入口出错不伪装成无描述。

### 导入与签名

```python
from ai4e_task.tasks.descriptions import describe_recipe
```

```text
describe_recipe(recipe: str | Path, *, config: dict | None=None, cache_dir: Path | None=None) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `recipe` | `str | Path` | `必填` |
| `config` | `dict | None` | `None` |
| `cache_dir` | `Path | None` | `None` |

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
from ai4e_task.tasks.descriptions import describe_recipe

print(signature(describe_recipe))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.descriptions`
- 仓库相对路径：`packages/ai4e-task/tasks/descriptions.py:12`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.descriptions')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-describe-shared-name"></a>
## `ai4e_task.describe_shared_name`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`describe_shared_name(project: str | Path, name: str) -> dict`
- **规范定义名**：`ai4e_task.projects.datasets.describe_shared_name`

### 用途

名称门禁只检查本项目，同名无论配置是否相同均要求显式覆盖。

### 导入与签名

```python
from ai4e_task.projects.datasets import describe_shared_name
```

```text
describe_shared_name(project: str | Path, name: str) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `name` | `str` | `必填` |

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
from ai4e_task.projects.datasets import describe_shared_name

print(signature(describe_shared_name))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.projects.datasets`
- 仓库相对路径：`packages/ai4e-task/projects/datasets.py:33`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.projects.datasets')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-export-guide"></a>
## `ai4e_task.export_guide`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`export_guide(target: str | Path) -> dict[str, str]`
- **规范定义名**：`ai4e_task.templates.resources.export_guide`

### 用途

导出 guide 和唯一 skill 源的构建副本，不创建 AGENTS.md。

### 导入与签名

```python
from ai4e_task.templates.resources import export_guide
```

```text
export_guide(target: str | Path) -> dict[str, str]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `target` | `str | Path` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, str]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FileNotFoundError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.templates.resources import export_guide

print(signature(export_guide))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.templates.resources`
- 仓库相对路径：`packages/ai4e-task/templates/resources.py:472`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.templates.resources')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-export-help"></a>
## `ai4e_task.export_help`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`export_help(target: str | Path) -> dict[str, str]`
- **规范定义名**：`ai4e_task.templates.resources.export_help`

### 用途

把完整 Agent 帮助中心导出到目标目录的 docs/agent-help。

### 导入与签名

```python
from ai4e_task.templates.resources import export_help
```

```text
export_help(target: str | Path) -> dict[str, str]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `target` | `str | Path` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, str]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.templates.resources import export_help

print(signature(export_help))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.templates.resources`
- 仓库相对路径：`packages/ai4e-task/templates/resources.py:279`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.templates.resources')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-export-inference"></a>
## `ai4e_task.export_inference`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`export_inference(project, task_id, batch_id, request)`
- **规范定义名**：`ai4e_task.tasks.inference_exports.export_inference`

### 用途

固定批次导出，不接受客户端路径，不改变原运行和任务版本。

### 导入与签名

```python
from ai4e_task.tasks.inference_exports import export_inference
```

```text
export_inference(project, task_id, batch_id, request)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `未标注` | `必填` |
| `task_id` | `未标注` | `必填` |
| `batch_id` | `未标注` | `必填` |
| `request` | `未标注` | `必填` |

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
from ai4e_task.tasks.inference_exports import export_inference

print(signature(export_inference))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.inference_exports`
- 仓库相对路径：`packages/ai4e-task/tasks/inference_exports.py:14`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.inference_exports')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-export-post-metrics"></a>
## `ai4e_task.export_post_metrics`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`export_post_metrics(project, task_id, identity, request)`
- **规范定义名**：`ai4e_task.tasks.post_metrics.export_post_metrics`

### 用途

只向任务评价目录导出固定结果，拒绝任意输出路径。

### 导入与签名

```python
from ai4e_task.tasks.post_metrics import export_post_metrics
```

```text
export_post_metrics(project, task_id, identity, request)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `未标注` | `必填` |
| `task_id` | `未标注` | `必填` |
| `identity` | `未标注` | `必填` |
| `request` | `未标注` | `必填` |

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
from ai4e_task.tasks.post_metrics import export_post_metrics

print(signature(export_post_metrics))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.post_metrics`
- 仓库相对路径：`packages/ai4e-task/tasks/post_metrics.py:230`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.post_metrics')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-fork-task"></a>
## `ai4e_task.fork_task`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`fork_task(project: str | Path, task_id: str, *, name: str | None=None, source: str='worktree', run_id: str | None=None, baseline_version_id: str | None=None, copy_datasets: bool=False, copy_preparation: bool=False, copy_checkpoints: bool=False, idempotency_key: str | None=None) -> dict`
- **规范定义名**：`ai4e_task.tasks.create.fork_task`

### 用途

从当前代码、创建快照或固定运行派生；三种资产复制默认关闭。

### 导入与签名

```python
from ai4e_task.tasks.create import fork_task
```

```text
fork_task(project: str | Path, task_id: str, *, name: str | None=None, source: str='worktree', run_id: str | None=None, baseline_version_id: str | None=None, copy_datasets: bool=False, copy_preparation: bool=False, copy_checkpoints: bool=False, idempotency_key: str | None=None) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `task_id` | `str` | `必填` |
| `name` | `str | None` | `None` |
| `source` | `str` | `'worktree'` |
| `run_id` | `str | None` | `None` |
| `baseline_version_id` | `str | None` | `None` |
| `copy_datasets` | `bool` | `False` |
| `copy_preparation` | `bool` | `False` |
| `copy_checkpoints` | `bool` | `False` |
| `idempotency_key` | `str | None` | `None` |

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
from ai4e_task.tasks.create import fork_task

print(signature(fork_task))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.create`
- 仓库相对路径：`packages/ai4e-task/tasks/create.py:37`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.create')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-freeze-checkpoint"></a>
## `ai4e_task.freeze_checkpoint`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`freeze_checkpoint(project: str | Path, task_id: str, identity: str, revision: str) -> dict`
- **规范定义名**：`ai4e_task.tasks.checkpoints.freeze_checkpoint`

### 用途

固定选择时的完整字节；原权重更新不改变已经固定的副本。

### 导入与签名

```python
from ai4e_task.tasks.checkpoints import freeze_checkpoint
```

```text
freeze_checkpoint(project: str | Path, task_id: str, identity: str, revision: str) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `task_id` | `str` | `必填` |
| `identity` | `str` | `必填` |
| `revision` | `str` | `必填` |

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
from ai4e_task.tasks.checkpoints import freeze_checkpoint

print(signature(freeze_checkpoint))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.checkpoints`
- 仓库相对路径：`packages/ai4e-task/tasks/checkpoints.py:153`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.checkpoints')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-freeze-result-item"></a>
## `ai4e_task.freeze_result_item`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`freeze_result_item(item)`
- **规范定义名**：`ai4e_task.tasks.post_results.freeze_result_item`

### 用途

提交评价时才固定成员内容修订。

### 导入与签名

```python
from ai4e_task.tasks.post_results import freeze_result_item
```

```text
freeze_result_item(item)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `item` | `未标注` | `必填` |

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
from ai4e_task.tasks.post_results import freeze_result_item

print(signature(freeze_result_item))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.post_results`
- 仓库相对路径：`packages/ai4e-task/tasks/post_results.py:105`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.post_results')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-get-lineage"></a>
## `ai4e_task.get_lineage`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`get_lineage(project: str | Path, version_id: str | None=None) -> list[dict]`
- **规范定义名**：`ai4e_task.versions.tree.get_lineage`

### 用途

返回有序版本记录；指定版本时返回其后代子树。

### 导入与签名

```python
from ai4e_task.versions.tree import get_lineage
```

```text
get_lineage(project: str | Path, version_id: str | None=None) -> list[dict]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `version_id` | `str | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`list[dict]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`KeyError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.versions.tree import get_lineage

print(signature(get_lineage))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.versions.tree`
- 仓库相对路径：`packages/ai4e-task/versions/tree.py:8`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.versions.tree')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-get-run"></a>
## `ai4e_task.get_run`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`get_run(project: str | Path, run_id: str) -> dict`
- **规范定义名**：`ai4e_task.tasks.records.get_run`

### 用途

核对持久化收据与 core 产物；未知状态不会自动重新启动。

### 导入与签名

```python
from ai4e_task.tasks.records import get_run
```

```text
get_run(project: str | Path, run_id: str) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `run_id` | `str` | `必填` |

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
from ai4e_task.tasks.records import get_run

print(signature(get_run))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.records`
- 仓库相对路径：`packages/ai4e-task/tasks/records.py:23`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.records')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-get-shared"></a>
## `ai4e_task.get_shared`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`get_shared(project: str | Path, asset_id: str, *, validate: bool=True) -> dict`
- **规范定义名**：`ai4e_task.projects.shared.get_shared`

### 用途

查询资产，默认核验内容与依赖。

### 导入与签名

```python
from ai4e_task.projects.shared import get_shared
```

```text
get_shared(project: str | Path, asset_id: str, *, validate: bool=True) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `asset_id` | `str` | `必填` |
| `validate` | `bool` | `True` |

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
from ai4e_task.projects.shared import get_shared

print(signature(get_shared))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.projects.shared`
- 仓库相对路径：`packages/ai4e-task/projects/shared.py:88`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.projects.shared')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-get-shared-dataset"></a>
## `ai4e_task.get_shared_dataset`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`get_shared_dataset(project: str | Path, name: str) -> dict`
- **规范定义名**：`ai4e_task.projects.datasets.get_shared_dataset`

### 用途

取得同名当前资源；不可用状态返回给调用方，不自动重做。

### 导入与签名

```python
from ai4e_task.projects.datasets import get_shared_dataset
```

```text
get_shared_dataset(project: str | Path, name: str) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `name` | `str` | `必填` |

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
from ai4e_task.projects.datasets import get_shared_dataset

print(signature(get_shared_dataset))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.projects.datasets`
- 仓库相对路径：`packages/ai4e-task/projects/datasets.py:28`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.projects.datasets')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-get-stage-summary"></a>
## `ai4e_task.get_stage_summary`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`get_stage_summary(project: str | Path, task_id: str) -> dict`
- **规范定义名**：`ai4e_task.tasks.query.get_stage_summary`

### 用途

按正式运行事实汇总阶段；已成功不被后来的 unknown 读盘盖成未运行。

### 导入与签名

```python
from ai4e_task.tasks.query import get_stage_summary
```

```text
get_stage_summary(project: str | Path, task_id: str) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `task_id` | `str` | `必填` |

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
from ai4e_task.tasks.query import get_stage_summary

print(signature(get_stage_summary))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.query`
- 仓库相对路径：`packages/ai4e-task/tasks/query.py:70`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.query')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-get-task"></a>
## `ai4e_task.get_task`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`get_task(project: str | Path, task_id: str) -> dict`
- **规范定义名**：`ai4e_task.tasks.records.get_task`

### 用途

读取任务身份及当前代码目录。

### 导入与签名

```python
from ai4e_task.tasks.records import get_task
```

```text
get_task(project: str | Path, task_id: str) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `task_id` | `str` | `必填` |

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
from ai4e_task.tasks.records import get_task

print(signature(get_task))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.records`
- 仓库相对路径：`packages/ai4e-task/tasks/records.py:12`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.records')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-guide-info"></a>
## `ai4e_task.guide_info`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`guide_info() -> dict[str, Any]`
- **规范定义名**：`ai4e_task.templates.resources.guide_info`

### 用途

返回当前解释器、版本和实际安装资源位置，不加载训练栈。

### 导入与签名

```python
from ai4e_task.templates.resources import guide_info
```

```text
guide_info() -> dict[str, Any]
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, Any]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.templates.resources import guide_info

print(signature(guide_info))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.templates.resources`
- 仓库相对路径：`packages/ai4e-task/templates/resources.py:493`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.templates.resources')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-help-info"></a>
## `ai4e_task.help_info`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`help_info() -> dict[str, Any]`
- **规范定义名**：`ai4e_task.templates.resources.help_info`

### 用途

返回帮助中心版本、入口、索引和覆盖数量。

### 导入与签名

```python
from ai4e_task.templates.resources import help_info
```

```text
help_info() -> dict[str, Any]
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, Any]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.templates.resources import help_info

print(signature(help_info))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.templates.resources`
- 仓库相对路径：`packages/ai4e-task/templates/resources.py:105`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.templates.resources')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-help-root"></a>
## `ai4e_task.help_root`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`help_root() -> Path`
- **规范定义名**：`ai4e_task.templates.resources.help_root`

### 用途

返回当前安装或源码树中的 Agent 帮助中心根目录。

### 导入与签名

```python
from ai4e_task.templates.resources import help_root
```

```text
help_root() -> Path
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Path`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FileNotFoundError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.templates.resources import help_root

print(signature(help_root))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.templates.resources`
- 仓库相对路径：`packages/ai4e-task/templates/resources.py:56`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.templates.resources')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-import-run"></a>
## `ai4e_task.import_run`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`import_run(project: str | Path, directory, *, task_id: str | None=None) -> dict`
- **规范定义名**：`ai4e_task.tasks.query.import_run`

### 用途

只读导入；相同 ID 内容冲突拒绝覆盖，旧产物不猜测版本。

### 导入与签名

```python
from ai4e_task.tasks.query import import_run
```

```text
import_run(project: str | Path, directory, *, task_id: str | None=None) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `directory` | `未标注` | `必填` |
| `task_id` | `str | None` | `None` |

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
from ai4e_task.tasks.query import import_run

print(signature(import_run))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.query`
- 仓库相对路径：`packages/ai4e-task/tasks/query.py:18`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.query')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-inference-devices"></a>
## `ai4e_task.inference_devices`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`inference_devices(project: str | Path) -> list[dict]`
- **规范定义名**：`ai4e_task.tasks.inference.inference_devices`

### 用途

列出实际可用设备及已知 Dojo 运行占用，不保证识别外部进程。

### 导入与签名

```python
from ai4e_task.tasks.inference import inference_devices
```

```text
inference_devices(project: str | Path) -> list[dict]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |

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
from ai4e_task.tasks.inference import inference_devices

print(signature(inference_devices))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.inference`
- 仓库相对路径：`packages/ai4e-task/tasks/inference.py:29`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.inference')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-inference-results"></a>
## `ai4e_task.inference_results`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`inference_results(project: str | Path, task_id: str, identity: str) -> dict`
- **规范定义名**：`ai4e_task.tasks.inference_results.inference_results`

### 用途

应用解释固定结果；Task 只核对运行归属和返回文件引用。

### 导入与签名

```python
from ai4e_task.tasks.inference_results import inference_results
```

```text
inference_results(project: str | Path, task_id: str, identity: str) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `task_id` | `str` | `必填` |
| `identity` | `str` | `必填` |

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
from ai4e_task.tasks.inference_results import inference_results

print(signature(inference_results))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.inference_results`
- 仓库相对路径：`packages/ai4e-task/tasks/inference_results.py:27`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.inference_results')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-inference-samples"></a>
## `ai4e_task.inference_samples`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`inference_samples(project: str | Path, task_id: str, checkpoint_id: str) -> dict`
- **规范定义名**：`ai4e_task.tasks.checkpoints.inference_samples`

### 用途

按检查点关联的冻结准备读取真实分片，兼容检查由业务层负责。

### 导入与签名

```python
from ai4e_task.tasks.checkpoints import inference_samples
```

```text
inference_samples(project: str | Path, task_id: str, checkpoint_id: str) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `task_id` | `str` | `必填` |
| `checkpoint_id` | `str` | `必填` |

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
from ai4e_task.tasks.checkpoints import inference_samples

print(signature(inference_samples))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.checkpoints`
- 仓库相对路径：`packages/ai4e-task/tasks/checkpoints.py:116`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.checkpoints')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-initialize-rawprep"></a>
## `ai4e_task.initialize_rawprep`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`initialize_rawprep(project, task_id)`
- **规范定义名**：`ai4e_task.tasks.rawprep.initialize_rawprep`

### 用途

新建平台任务时将实际默认值保存一次；普通读取不产生修订。

### 导入与签名

```python
from ai4e_task.tasks.rawprep import initialize_rawprep
```

```text
initialize_rawprep(project, task_id)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `未标注` | `必填` |
| `task_id` | `未标注` | `必填` |

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
from ai4e_task.tasks.rawprep import initialize_rawprep

print(signature(initialize_rawprep))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.rawprep`
- 仓库相对路径：`packages/ai4e-task/tasks/rawprep.py:48`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.rawprep')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-inspect-task"></a>
## `ai4e_task.inspect_task`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`inspect_task(project, task_id: str, operation: str, *, revision: str, output_dir: str, selection: dict | None=None, configuration: dict | None=None, on_process_started=None) -> dict`
- **规范定义名**：`ai4e_task.tasks.inspections.inspect_task`

### 用途

检查固定修订；describe_case 可描述调用者提供的候选配置而不保存任务。

### 导入与签名

```python
from ai4e_task.tasks.inspections import inspect_task
```

```text
inspect_task(project, task_id: str, operation: str, *, revision: str, output_dir: str, selection: dict | None=None, configuration: dict | None=None, on_process_started=None) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `未标注` | `必填` |
| `task_id` | `str` | `必填` |
| `operation` | `str` | `必填` |
| `revision` | `str` | `必填关键字参数` |
| `output_dir` | `str` | `必填关键字参数` |
| `selection` | `dict | None` | `None` |
| `configuration` | `dict | None` | `None` |
| `on_process_started` | `未标注` | `None` |

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
from ai4e_task.tasks.inspections import inspect_task

print(signature(inspect_task))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.inspections`
- 仓库相对路径：`packages/ai4e-task/tasks/inspections.py:12`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.inspections')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-list-examples"></a>
## `ai4e_task.list_examples`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`list_examples(*, case_type: str | None=None, query: str | None=None, data_form: str | None=None, training_pattern: str | None=None) -> list[dict[str, Any]]`
- **规范定义名**：`ai4e_task.templates.resources.list_examples`

### 用途

按说明子串与标签筛选案例，不导入代码；多项过滤取交集。

query大小写无关，空白视为未指定；标签精确匹配并保留清单顺序。
旧清单无research仍可按原用途检索，不猜测缺失标签。

### 导入与签名

```python
from ai4e_task.templates.resources import list_examples
```

```text
list_examples(*, case_type: str | None=None, query: str | None=None, data_form: str | None=None, training_pattern: str | None=None) -> list[dict[str, Any]]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `case_type` | `str | None` | `None` |
| `query` | `str | None` | `None` |
| `data_form` | `str | None` | `None` |
| `training_pattern` | `str | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`list[dict[str, Any]]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`TypeError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.templates.resources import list_examples

print(signature(list_examples))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.templates.resources`
- 仓库相对路径：`packages/ai4e-task/templates/resources.py:313`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.templates.resources')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-list-help-topics"></a>
## `ai4e_task.list_help_topics`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`list_help_topics(*, kind: str | None=None, layer: str | None=None, domain: str | None=None, case_id: str | None=None) -> list[dict[str, Any]]`
- **规范定义名**：`ai4e_task.templates.resources.list_help_topics`

### 用途

按类型、层级、领域或案例列出 Agent 帮助主题。

### 导入与签名

```python
from ai4e_task.templates.resources import list_help_topics
```

```text
list_help_topics(*, kind: str | None=None, layer: str | None=None, domain: str | None=None, case_id: str | None=None) -> list[dict[str, Any]]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `kind` | `str | None` | `None` |
| `layer` | `str | None` | `None` |
| `domain` | `str | None` | `None` |
| `case_id` | `str | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`list[dict[str, Any]]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.templates.resources import list_help_topics

print(signature(list_help_topics))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.templates.resources`
- 仓库相对路径：`packages/ai4e-task/templates/resources.py:122`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.templates.resources')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-list-inference-batches"></a>
## `ai4e_task.list_inference_batches`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`list_inference_batches(project: str | Path, task_id: str) -> list[dict]`
- **规范定义名**：`ai4e_task.tasks.inference.list_inference_batches`

### 用途

按任务列出批次，不依赖浏览器内存。

### 导入与签名

```python
from ai4e_task.tasks.inference import list_inference_batches
```

```text
list_inference_batches(project: str | Path, task_id: str) -> list[dict]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `task_id` | `str` | `必填` |

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
from ai4e_task.tasks.inference import list_inference_batches

print(signature(list_inference_batches))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.inference`
- 仓库相对路径：`packages/ai4e-task/tasks/inference.py:276`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.inference')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-list-inference-checkpoints"></a>
## `ai4e_task.list_inference_checkpoints`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`list_inference_checkpoints(project: str | Path, task_id: str) -> list[dict]`
- **规范定义名**：`ai4e_task.tasks.checkpoints.list_inference_checkpoints`

### 用途

应用提供候选和科学结论，管理层核验路径、内容修订及缓存来源。

### 导入与签名

```python
from ai4e_task.tasks.checkpoints import list_inference_checkpoints
```

```text
list_inference_checkpoints(project: str | Path, task_id: str) -> list[dict]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `task_id` | `str` | `必填` |

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
from ai4e_task.tasks.checkpoints import list_inference_checkpoints

print(signature(list_inference_checkpoints))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.checkpoints`
- 仓库相对路径：`packages/ai4e-task/tasks/checkpoints.py:44`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.checkpoints')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-list-post-metrics"></a>
## `ai4e_task.list_post_metrics`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`list_post_metrics(project, task_id)`
- **规范定义名**：`ai4e_task.tasks.post_metrics.list_post_metrics`

### 用途

列出当前任务的评价记录。

### 导入与签名

```python
from ai4e_task.tasks.post_metrics import list_post_metrics
```

```text
list_post_metrics(project, task_id)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `未标注` | `必填` |
| `task_id` | `未标注` | `必填` |

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
from ai4e_task.tasks.post_metrics import list_post_metrics

print(signature(list_post_metrics))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.post_metrics`
- 仓库相对路径：`packages/ai4e-task/tasks/post_metrics.py:211`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.post_metrics')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-list-post-result-files"></a>
## `ai4e_task.list_post_result_files`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`list_post_result_files(project, task_id, *, directory='', query='', batch=None, run_id=None, sample=None, split=None, status=None)`
- **规范定义名**：`ai4e_task.tasks.post_results.list_post_result_files`

### 用途

按层列出训练运行、平台数据集与推理结果；无写出的训练 run 仍保留文件夹。

### 导入与签名

```python
from ai4e_task.tasks.post_results import list_post_result_files
```

```text
list_post_result_files(project, task_id, *, directory='', query='', batch=None, run_id=None, sample=None, split=None, status=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `未标注` | `必填` |
| `task_id` | `未标注` | `必填` |
| `directory` | `未标注` | `''` |
| `query` | `未标注` | `''` |
| `batch` | `未标注` | `None` |
| `run_id` | `未标注` | `None` |
| `sample` | `未标注` | `None` |
| `split` | `未标注` | `None` |
| `status` | `未标注` | `None` |

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
from ai4e_task.tasks.post_results import list_post_result_files

print(signature(list_post_result_files))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.post_results`
- 仓库相对路径：`packages/ai4e-task/tasks/post_results.py:633`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.post_results')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-list-processed-datasets"></a>
## `ai4e_task.list_processed_datasets`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`list_processed_datasets(workspace: str | Path) -> list[dict]`
- **规范定义名**：`ai4e_task.storage.processed_datasets.list_processed_datasets`

### 用途

列出工作区全部已处理数据集，含可用性；按登记时间倒序。

### 导入与签名

```python
from ai4e_task.storage.processed_datasets import list_processed_datasets
```

```text
list_processed_datasets(workspace: str | Path) -> list[dict]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `workspace` | `str | Path` | `必填` |

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
from ai4e_task.storage.processed_datasets import list_processed_datasets

print(signature(list_processed_datasets))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.storage.processed_datasets`
- 仓库相对路径：`packages/ai4e-task/storage/processed_datasets.py:60`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.storage.processed_datasets')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-list-runs"></a>
## `ai4e_task.list_runs`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`list_runs(project: str | Path, task_id: str | None=None) -> list[dict]`
- **规范定义名**：`ai4e_task.tasks.records.list_runs`

### 用途

列出某任务或项目的全部运行。

### 导入与签名

```python
from ai4e_task.tasks.records import list_runs
```

```text
list_runs(project: str | Path, task_id: str | None=None) -> list[dict]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `task_id` | `str | None` | `None` |

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
from ai4e_task.tasks.records import list_runs

print(signature(list_runs))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.records`
- 仓库相对路径：`packages/ai4e-task/tasks/records.py:95`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.records')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-list-shared"></a>
## `ai4e_task.list_shared`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`list_shared(project: str | Path) -> list[dict]`
- **规范定义名**：`ai4e_task.projects.shared.list_shared`

### 用途

列出共享资产登记。

### 导入与签名

```python
from ai4e_task.projects.shared import list_shared
```

```text
list_shared(project: str | Path) -> list[dict]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |

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
from ai4e_task.projects.shared import list_shared

print(signature(list_shared))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.projects.shared`
- 仓库相对路径：`packages/ai4e-task/projects/shared.py:83`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.projects.shared')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-list-shared-datasets"></a>
## `ai4e_task.list_shared_datasets`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`list_shared_datasets(project: str | Path) -> list[dict]`
- **规范定义名**：`ai4e_task.projects.datasets.list_shared_datasets`

### 用途

按最近发布时间列出项目共享数据及不可用原因，不扫描张量。

### 导入与签名

```python
from ai4e_task.projects.datasets import list_shared_datasets
```

```text
list_shared_datasets(project: str | Path) -> list[dict]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |

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
from ai4e_task.projects.datasets import list_shared_datasets

print(signature(list_shared_datasets))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.projects.datasets`
- 仓库相对路径：`packages/ai4e-task/projects/datasets.py:8`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.projects.datasets')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-list-stage-artifacts"></a>
## `ai4e_task.list_stage_artifacts`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`list_stage_artifacts(project, task_id: str, roots: dict | None=None, *, include_unmatched: bool=False) -> list[dict]`
- **规范定义名**：`ai4e_task.tasks.artifacts.list_stage_artifacts`

### 用途

列出成功正式产物及终止运行已提交的恢复权重，不整文件核验。

切步名单只回答还有没有、能不能列。字节是否仍是当初那份留给恢复训练、
提交推理和读取准备；列举时再打检查点会把切步卡在半分钟。

### 导入与签名

```python
from ai4e_task.tasks.artifacts import list_stage_artifacts
```

```text
list_stage_artifacts(project, task_id: str, roots: dict | None=None, *, include_unmatched: bool=False) -> list[dict]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `未标注` | `必填` |
| `task_id` | `str` | `必填` |
| `roots` | `dict | None` | `None` |
| `include_unmatched` | `bool` | `False` |

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
from ai4e_task.tasks.artifacts import list_stage_artifacts

print(signature(list_stage_artifacts))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.task_labels`

### 源码位置

- 模块：`ai4e_task.tasks.artifacts`
- 仓库相对路径：`packages/ai4e-task/tasks/artifacts.py:8`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.artifacts')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-list-tasks"></a>
## `ai4e_task.list_tasks`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`list_tasks(project: str | Path) -> list[dict]`
- **规范定义名**：`ai4e_task.tasks.records.list_tasks`

### 用途

按创建顺序列出任务。

### 导入与签名

```python
from ai4e_task.tasks.records import list_tasks
```

```text
list_tasks(project: str | Path) -> list[dict]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |

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
from ai4e_task.tasks.records import list_tasks

print(signature(list_tasks))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.records`
- 仓库相对路径：`packages/ai4e-task/tasks/records.py:18`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.records')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-list-templates"></a>
## `ai4e_task.list_templates`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`list_templates(project: str | Path) -> list[dict]`
- **规范定义名**：`ai4e_task.templates.catalog.list_templates`

### 用途

列出已登记模板。

### 导入与签名

```python
from ai4e_task.templates.catalog import list_templates
```

```text
list_templates(project: str | Path) -> list[dict]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |

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
from ai4e_task.templates.catalog import list_templates

print(signature(list_templates))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.templates.catalog`
- 仓库相对路径：`packages/ai4e-task/templates/catalog.py:23`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.templates.catalog')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-manifest-digest"></a>
## `ai4e_task.manifest_digest`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`manifest_digest(path: str | Path) -> str`
- **规范定义名**：`ai4e_task.storage.processed_datasets.manifest_digest`

### 用途

清单文件内容摘要；路径丢失时由调用方先判断存在。

### 导入与签名

```python
from ai4e_task.storage.processed_datasets import manifest_digest
```

```text
manifest_digest(path: str | Path) -> str
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `str | Path` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`str`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.storage.processed_datasets import manifest_digest

print(signature(manifest_digest))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.storage.processed_datasets`
- 仓库相对路径：`packages/ai4e-task/storage/processed_datasets.py:30`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.storage.processed_datasets')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-match-asset"></a>
## `ai4e_task.match_asset`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`match_asset(asset: dict, requirement: dict, *, status: str) -> dict`
- **规范定义名**：`ai4e_task.tasks.asset_matching.match_asset`

### 用途

返回全部缺失和冲突条件；可选择不等于科学内容已适用。

### 导入与签名

```python
from ai4e_task.tasks.asset_matching import match_asset
```

```text
match_asset(asset: dict, requirement: dict, *, status: str) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `asset` | `dict` | `必填` |
| `requirement` | `dict` | `必填` |
| `status` | `str` | `必填关键字参数` |

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
from ai4e_task.tasks.asset_matching import match_asset

print(signature(match_asset))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.asset_matching`
- 仓库相对路径：`packages/ai4e-task/tasks/asset_matching.py:6`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.asset_matching')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-metric-catalog"></a>
## `ai4e_task.metric_catalog`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`metric_catalog()`
- **规范定义名**：`ai4e_task.tasks.post_metrics.metric_catalog`

### 用途

在检查子进程查询core指标目录，管理进程不加载算法栈。

### 导入与签名

```python
from ai4e_task.tasks.post_metrics import metric_catalog
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
from ai4e_task.tasks.post_metrics import metric_catalog

print(signature(metric_catalog))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.post_metrics`
- 仓库相对路径：`packages/ai4e-task/tasks/post_metrics.py:28`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.post_metrics')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-migrate-shared-datasets"></a>
## `ai4e_task.migrate_shared_datasets`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`migrate_shared_datasets(project: str | Path, *, context: dict, dry_run: bool=True, overwrite: bool=False, sources: dict[str, str] | None=None) -> list[dict]`
- **规范定义名**：`ai4e_task.projects.dataset_migration.migrate_shared_datasets`

### 用途

预览或复制历史物理产物，返回逐项迁移结果，原文件保持不变。

sources 可显式指定 {共享名称: 正式运行ID}，用于旧登记名与冻结配置名不同的情形。
未提供时按配置名称选择最新正式成功运行；空映射不迁移任何内容。
指定来源非正式成功物理运行时抛 ValueError，同名冲突抛 FileExistsError。

### 导入与签名

```python
from ai4e_task.projects.dataset_migration import migrate_shared_datasets
```

```text
migrate_shared_datasets(project: str | Path, *, context: dict, dry_run: bool=True, overwrite: bool=False, sources: dict[str, str] | None=None) -> list[dict]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `context` | `dict` | `必填关键字参数` |
| `dry_run` | `bool` | `True` |
| `overwrite` | `bool` | `False` |
| `sources` | `dict[str, str] | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`list[dict]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FileExistsError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.projects.dataset_migration import migrate_shared_datasets

print(signature(migrate_shared_datasets))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.projects.dataset_migration`
- 仓库相对路径：`packages/ai4e-task/projects/dataset_migration.py:12`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.projects.dataset_migration')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-new-task"></a>
## `ai4e_task.new_task`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`new_task(project, name: str, *, source: str | Path | None=None, idempotency_key: str | None=None, configuration: dict | None=None) -> dict`
- **规范定义名**：`ai4e_task.tasks.create.new_task`

### 用途

从模板、目录或空目录创建新的根版本。

### 导入与签名

```python
from ai4e_task.tasks.create import new_task
```

```text
new_task(project, name: str, *, source: str | Path | None=None, idempotency_key: str | None=None, configuration: dict | None=None) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `未标注` | `必填` |
| `name` | `str` | `必填` |
| `source` | `str | Path | None` | `None` |
| `idempotency_key` | `str | None` | `None` |
| `configuration` | `dict | None` | `None` |

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
from ai4e_task.tasks.create import new_task

print(signature(new_task))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`pcno_cylinder`, `wdno`
- 案例：`pcno.double_cylinder`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_task.tasks.create`
- 仓库相对路径：`packages/ai4e-task/tasks/create.py:20`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.create')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-open-project"></a>
## `ai4e_task.open_project`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`open_project(path: str | Path) -> Project`
- **规范定义名**：`ai4e_task.projects.project.open_project`

### 用途

校验项目描述与数据库存在，不隐式新建丢失的索引。

### 导入与签名

```python
from ai4e_task.projects.project import open_project
```

```text
open_project(path: str | Path) -> Project
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `str | Path` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Project`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FileNotFoundError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.projects.project import open_project

print(signature(open_project))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.projects.project`
- 仓库相对路径：`packages/ai4e-task/projects/project.py:41`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.projects.project')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-operation-context"></a>
## `ai4e_task.operation_context`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`operation_context(project, task_id, *, name='infer', run=None, batch_id=None) -> dict`
- **规范定义名**：`ai4e_task.tasks.operation_sources.operation_context`

### 用途

解析明确当前任务或固定运行/批次；历史缺来源时不回填当前入口。

### 导入与签名

```python
from ai4e_task.tasks.operation_sources import operation_context
```

```text
operation_context(project, task_id, *, name='infer', run=None, batch_id=None) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `未标注` | `必填` |
| `task_id` | `未标注` | `必填` |
| `name` | `未标注` | `'infer'` |
| `run` | `未标注` | `None` |
| `batch_id` | `未标注` | `None` |

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
from ai4e_task.tasks.operation_sources import operation_context

print(signature(operation_context))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.operation_sources`
- 仓库相对路径：`packages/ai4e-task/tasks/operation_sources.py:196`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.operation_sources')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-operation-target"></a>
## `ai4e_task.operation_target`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`operation_target(recipe: str | Path, name: str) -> str`
- **规范定义名**：`ai4e_task.tasks.operations.operation_target`

### 用途

由公共配置指定领域连接；缺少连接只使该项管理操作不可用。

### 导入与签名

```python
from ai4e_task.tasks.operations import operation_target
```

```text
operation_target(recipe: str | Path, name: str) -> str
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `recipe` | `str | Path` | `必填` |
| `name` | `str` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`str`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.tasks.operations import operation_target

print(signature(operation_target))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.operations`
- 仓库相对路径：`packages/ai4e-task/tasks/operations.py:11`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.operations')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-post-results"></a>
## `ai4e_task.post_results`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`post_results(project, task_id)`
- **规范定义名**：`ai4e_task.tasks.post_results.post_results`

### 用途

统一批次、独立推理与历史运行的评价目录；训练无清单时不进入评价项。

### 导入与签名

```python
from ai4e_task.tasks.post_results import post_results
```

```text
post_results(project, task_id)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `未标注` | `必填` |
| `task_id` | `未标注` | `必填` |

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
from ai4e_task.tasks.post_results import post_results

print(signature(post_results))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.post_results`
- 仓库相对路径：`packages/ai4e-task/tasks/post_results.py:415`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.post_results')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-processed-claim"></a>
## `ai4e_task.processed_claim`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`processed_claim(config: dict, *, context: dict) -> dict`
- **规范定义名**：`ai4e_task.storage.processed_datasets.processed_claim`

### 用途

通过明确应用上下文生成处理身份；Task 不解释科学配置。

### 导入与签名

```python
from ai4e_task.storage.processed_datasets import processed_claim
```

```text
processed_claim(config: dict, *, context: dict) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `dict` | `必填` |
| `context` | `dict` | `必填关键字参数` |

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
from ai4e_task.storage.processed_datasets import processed_claim

print(signature(processed_claim))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.storage.processed_datasets`
- 仓库相对路径：`packages/ai4e-task/storage/processed_datasets.py:256`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.storage.processed_datasets')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-publish-processed-from-run"></a>
## `ai4e_task.publish_processed_from_run`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`publish_processed_from_run(workspace: str | Path, project: str | Path, task_id: str, run: dict, *, context: dict | None=None, overwrite: bool=False) -> dict | None`
- **规范定义名**：`ai4e_task.storage.processed_datasets.publish_processed_from_run`

### 用途

登记捕获计划中的唯一成功共享输出；多输出报选择歧义。

### 导入与签名

```python
from ai4e_task.storage.processed_datasets import publish_processed_from_run
```

```text
publish_processed_from_run(workspace: str | Path, project: str | Path, task_id: str, run: dict, *, context: dict | None=None, overwrite: bool=False) -> dict | None
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `workspace` | `str | Path` | `必填` |
| `project` | `str | Path` | `必填` |
| `task_id` | `str` | `必填` |
| `run` | `dict` | `必填` |
| `context` | `dict | None` | `None` |
| `overwrite` | `bool` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict | None`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.storage.processed_datasets import publish_processed_from_run

print(signature(publish_processed_from_run))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.storage.processed_datasets`
- 仓库相对路径：`packages/ai4e-task/storage/processed_datasets.py:216`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.storage.processed_datasets')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-read-case-manifest"></a>
## `ai4e_task.read_case_manifest`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`read_case_manifest() -> dict[str, Any]`
- **规范定义名**：`ai4e_task.templates.resources.read_case_manifest`

### 用途

读取并校验清单顶层契约。

### 导入与签名

```python
from ai4e_task.templates.resources import read_case_manifest
```

```text
read_case_manifest() -> dict[str, Any]
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, Any]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.templates.resources import read_case_manifest

print(signature(read_case_manifest))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.templates.resources`
- 仓库相对路径：`packages/ai4e-task/templates/resources.py:293`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.templates.resources')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-read-configuration"></a>
## `ai4e_task.read_configuration`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`read_configuration(project: str | Path, task_id: str) -> dict`
- **规范定义名**：`ai4e_task.tasks.configuration.read_configuration`

### 用途

读取配置和文件摘要；未知插值保持原样。

### 导入与签名

```python
from ai4e_task.tasks.configuration import read_configuration
```

```text
read_configuration(project: str | Path, task_id: str) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `task_id` | `str` | `必填` |

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
from ai4e_task.tasks.configuration import read_configuration

print(signature(read_configuration))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.configuration`
- 仓库相对路径：`packages/ai4e-task/tasks/configuration.py:25`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.configuration')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-read-help-topic"></a>
## `ai4e_task.read_help_topic`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`read_help_topic(topic_id: str) -> dict[str, Any]`
- **规范定义名**：`ai4e_task.templates.resources.read_help_topic`

### 用途

读取一个主题的结构化元数据和 Markdown 正文。

### 导入与签名

```python
from ai4e_task.templates.resources import read_help_topic
```

```text
read_help_topic(topic_id: str) -> dict[str, Any]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `topic_id` | `str` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, Any]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`HelpIndexError`, `HelpTopicNotFoundError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.templates.resources import read_help_topic

print(signature(read_help_topic))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `gencp`, `parametric_pde`, `safediffcon`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `parametric_pde.advection`, `parametric_pde.burgers`, `parametric_pde.convection_diffusion`, `parametric_pde.diffusion_trapezoid`, `parametric_pde.neumann_diffusion`, `recipe_extensions.field_mapping`, `recipe_extensions.free_wiring`, `recipe_extensions.gencp`, `recipe_extensions.inference_fields`, `recipe_extensions.inference_metrics`, `recipe_extensions.model_block`, `recipe_extensions.physical_visualization`, `recipe_extensions.safediffcon`, `recipe_extensions.sampling`, `recipe_extensions.wdno`, `safediffcon.burgers`, `safediffcon.tokamak`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_task.templates.resources`
- 仓库相对路径：`packages/ai4e-task/templates/resources.py:227`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.templates.resources')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-read-inference-batch"></a>
## `ai4e_task.read_inference_batch`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`read_inference_batch(project: str | Path, task_id: str, identity: str) -> dict`
- **规范定义名**：`ai4e_task.tasks.inference.read_inference_batch`

### 用途

读取持久化批次；协调器失联只报告中断，不自动重复执行。

### 导入与签名

```python
from ai4e_task.tasks.inference import read_inference_batch
```

```text
read_inference_batch(project: str | Path, task_id: str, identity: str) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `task_id` | `str` | `必填` |
| `identity` | `str` | `必填` |

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
from ai4e_task.tasks.inference import read_inference_batch

print(signature(read_inference_batch))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.inference`
- 仓库相对路径：`packages/ai4e-task/tasks/inference.py:260`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.inference')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-read-log"></a>
## `ai4e_task.read_log`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`read_log(project: str | Path, run_id: str) -> str`
- **规范定义名**：`ai4e_task.tasks.query.read_log`

### 用途

读取 core 日志，尚未创建时返回空文本。

### 导入与签名

```python
from ai4e_task.tasks.query import read_log
```

```text
read_log(project: str | Path, run_id: str) -> str
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `run_id` | `str` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`str`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.tasks.query import read_log

print(signature(read_log))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.query`
- 仓库相对路径：`packages/ai4e-task/tasks/query.py:11`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.query')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-read-post-metrics"></a>
## `ai4e_task.read_post_metrics`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`read_post_metrics(project, task_id, identity)`
- **规范定义名**：`ai4e_task.tasks.post_metrics.read_post_metrics`

### 用途

读取已提交行，并核对意外结束进程；不自动重新运行未知计算。

### 导入与签名

```python
from ai4e_task.tasks.post_metrics import read_post_metrics
```

```text
read_post_metrics(project, task_id, identity)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `未标注` | `必填` |
| `task_id` | `未标注` | `必填` |
| `identity` | `未标注` | `必填` |

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
from ai4e_task.tasks.post_metrics import read_post_metrics

print(signature(read_post_metrics))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.post_metrics`
- 仓库相对路径：`packages/ai4e-task/tasks/post_metrics.py:180`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.post_metrics')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-read-run-metrics"></a>
## `ai4e_task.read_run_metrics`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`read_run_metrics(project, run_id: str) -> dict`
- **规范定义名**：`ai4e_task.tasks.artifacts.read_run_metrics`

### 用途

读取现有训练和后处理记录，不从日志推测不存在的指标。

### 导入与签名

```python
from ai4e_task.tasks.artifacts import read_run_metrics
```

```text
read_run_metrics(project, run_id: str) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `未标注` | `必填` |
| `run_id` | `str` | `必填` |

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
from ai4e_task.tasks.artifacts import read_run_metrics

print(signature(read_run_metrics))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.artifacts`
- 仓库相对路径：`packages/ai4e-task/tasks/artifacts.py:87`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.artifacts')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-read-version-details"></a>
## `ai4e_task.read_version_details`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`read_version_details(project, version_id: str) -> dict`
- **规范定义名**：`ai4e_task.versions.details.read_version_details`

### 用途

校验创建快照，返回固定配置和带身份的各阶段实际运行。

### 导入与签名

```python
from ai4e_task.versions.details import read_version_details
```

```text
read_version_details(project, version_id: str) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `未标注` | `必填` |
| `version_id` | `str` | `必填` |

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
from ai4e_task.versions.details import read_version_details

print(signature(read_version_details))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.versions.details`
- 仓库相对路径：`packages/ai4e-task/versions/details.py:12`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.versions.details')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-recipe-entry"></a>
## `ai4e_task.recipe_entry`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`recipe_entry(project: str | Path, task_id: str) -> dict`
- **规范定义名**：`ai4e_task.templates.materialize.recipe_entry`

### 用途

读取任务当前 recipe 投影的入口；不使用创建时冻结的旧键快照。

### 导入与签名

```python
from ai4e_task.templates.materialize import recipe_entry
```

```text
recipe_entry(project: str | Path, task_id: str) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `task_id` | `str` | `必填` |

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
from ai4e_task.templates.materialize import recipe_entry

print(signature(recipe_entry))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.templates.materialize`
- 仓库相对路径：`packages/ai4e-task/templates/materialize.py:8`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.templates.materialize')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-recover-inference"></a>
## `ai4e_task.recover_inference`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`recover_inference(project: str | Path, task_id: str, identity: str) -> dict`
- **规范定义名**：`ai4e_task.tasks.inference.recover_inference`

### 用途

显式恢复协调，子运行按已有收据核对，不重新捕获变化的输入。

### 导入与签名

```python
from ai4e_task.tasks.inference import recover_inference
```

```text
recover_inference(project: str | Path, task_id: str, identity: str) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `task_id` | `str` | `必填` |
| `identity` | `str` | `必填` |

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
from ai4e_task.tasks.inference import recover_inference

print(signature(recover_inference))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.inference`
- 仓库相对路径：`packages/ai4e-task/tasks/inference.py:312`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.inference')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-recover-project"></a>
## `ai4e_task.recover_project`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`recover_project(path: str | Path) -> dict`
- **规范定义名**：`ai4e_task.projects.project.recover_project`

### 用途

持有项目写锁清理中断的创建操作；保留已登记运行和用户目录。

### 导入与签名

```python
from ai4e_task.projects.project import recover_project
```

```text
recover_project(path: str | Path) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `str | Path` | `必填` |

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
from ai4e_task.projects.project import recover_project

print(signature(recover_project))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.projects.project`
- 仓库相对路径：`packages/ai4e-task/projects/project.py:52`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.projects.project')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-register-processed-dataset"></a>
## `ai4e_task.register_processed_dataset`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`register_processed_dataset(workspace: str | Path, name: str, *, manifest_path: str | Path, digest: str, provenance: dict | None=None, claim: dict | None=None, semantics: dict | None=None, stage: str | None=None, overwrite: bool=False) -> dict`
- **规范定义名**：`ai4e_task.storage.processed_datasets.register_processed_dataset`

### 用途

登记或复用资源，原样保留显式 semantics/stage；缺标签不推断。

同名不同声明未确认覆盖时拒绝；同摘要不同标签须明确覆盖。

### 导入与签名

```python
from ai4e_task.storage.processed_datasets import register_processed_dataset
```

```text
register_processed_dataset(workspace: str | Path, name: str, *, manifest_path: str | Path, digest: str, provenance: dict | None=None, claim: dict | None=None, semantics: dict | None=None, stage: str | None=None, overwrite: bool=False) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `workspace` | `str | Path` | `必填` |
| `name` | `str` | `必填` |
| `manifest_path` | `str | Path` | `必填关键字参数` |
| `digest` | `str` | `必填关键字参数` |
| `provenance` | `dict | None` | `None` |
| `claim` | `dict | None` | `None` |
| `semantics` | `dict | None` | `None` |
| `stage` | `str | None` | `None` |
| `overwrite` | `bool` | `False` |

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
from ai4e_task.storage.processed_datasets import register_processed_dataset

print(signature(register_processed_dataset))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.storage.processed_datasets`
- 仓库相对路径：`packages/ai4e-task/storage/processed_datasets.py:138`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.storage.processed_datasets')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-register-shared"></a>
## `ai4e_task.register_shared`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`register_shared(project, name: str, source, *, kind: str='other', copy: bool=False, provenance: dict | None=None, dependencies: list[dict] | None=None, bundle: dict | None=None, semantics: dict | None=None, stage: str | None=None, asset_name: str | None=None) -> dict`
- **规范定义名**：`ai4e_task.projects.shared.register_shared`

### 用途

按资产名登记或复制共享内容；目标存在时拒绝覆盖。

### 导入与签名

```python
from ai4e_task.projects.shared import register_shared
```

```text
register_shared(project, name: str, source, *, kind: str='other', copy: bool=False, provenance: dict | None=None, dependencies: list[dict] | None=None, bundle: dict | None=None, semantics: dict | None=None, stage: str | None=None, asset_name: str | None=None) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `未标注` | `必填` |
| `name` | `str` | `必填` |
| `source` | `未标注` | `必填` |
| `kind` | `str` | `'other'` |
| `copy` | `bool` | `False` |
| `provenance` | `dict | None` | `None` |
| `dependencies` | `list[dict] | None` | `None` |
| `bundle` | `dict | None` | `None` |
| `semantics` | `dict | None` | `None` |
| `stage` | `str | None` | `None` |
| `asset_name` | `str | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FileExistsError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.projects.shared import register_shared

print(signature(register_shared))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.projects.shared`
- 仓库相对路径：`packages/ai4e-task/projects/shared.py:16`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.projects.shared')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-register-template"></a>
## `ai4e_task.register_template`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`register_template(project: str | Path, name: str, source: str | Path) -> dict`
- **规范定义名**：`ai4e_task.templates.catalog.register_template`

### 用途

登记本地模板及当前摘要；展开时使用并记录当前来源。

### 导入与签名

```python
from ai4e_task.templates.catalog import register_template
```

```text
register_template(project: str | Path, name: str, source: str | Path) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `name` | `str` | `必填` |
| `source` | `str | Path` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`NotADirectoryError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.templates.catalog import register_template

print(signature(register_template))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.templates.catalog`
- 仓库相对路径：`packages/ai4e-task/templates/catalog.py:11`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.templates.catalog')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-replace-configuration"></a>
## `ai4e_task.replace_configuration`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`replace_configuration(project: str | Path, task_id: str, config: dict, *, revision: str, script_replacements: dict | None=None) -> dict`
- **规范定义名**：`ai4e_task.tasks.configuration.replace_configuration`

### 用途

按修订原子保存完整配置，不合并旧值或解释业务参数；返回配置和新修订。

### 导入与签名

```python
from ai4e_task.tasks.configuration import replace_configuration
```

```text
replace_configuration(project: str | Path, task_id: str, config: dict, *, revision: str, script_replacements: dict | None=None) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `task_id` | `str` | `必填` |
| `config` | `dict` | `必填` |
| `revision` | `str` | `必填关键字参数` |
| `script_replacements` | `dict | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`TypeError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.tasks.configuration import replace_configuration

print(signature(replace_configuration))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.configuration`
- 仓库相对路径：`packages/ai4e-task/tasks/configuration.py:46`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.configuration')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-replace-scripts"></a>
## `ai4e_task.replace_scripts`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`replace_scripts(project: str | Path, task_id: str, files: dict[str, dict]) -> dict`
- **规范定义名**：`ai4e_task.storage.script_replacement.replace_scripts`

### 用途

按明确文件清单与原件修订执行有备份的替换；失败恢复本次改动。

### 导入与签名

```python
from ai4e_task.storage.script_replacement import replace_scripts
```

```text
replace_scripts(project: str | Path, task_id: str, files: dict[str, dict]) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `task_id` | `str` | `必填` |
| `files` | `dict[str, dict]` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FileNotFoundError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.storage.script_replacement import replace_scripts

print(signature(replace_scripts))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.storage.script_replacement`
- 仓库相对路径：`packages/ai4e-task/storage/script_replacement.py:17`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.storage.script_replacement')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-resource-root"></a>
## `ai4e_task.resource_root`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`resource_root() -> Path`
- **规范定义名**：`ai4e_task.templates.resources.resource_root`

### 用途

定位 wheel 内资源或源码树中的 examples。

### 导入与签名

```python
from ai4e_task.templates.resources import resource_root
```

```text
resource_root() -> Path
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Path`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FileNotFoundError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.templates.resources import resource_root

print(signature(resource_root))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.templates.resources`
- 仓库相对路径：`packages/ai4e-task/templates/resources.py:40`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.templates.resources')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-resume-run"></a>
## `ai4e_task.resume_run`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`resume_run(project, run_id: str, *, checkpoint: str='latest.pt', idempotency_key: str | None=None) -> dict`
- **规范定义名**：`ai4e_task.tasks.execution.resume_run`

### 用途

恢复固定运行的配置及代码，单独注入检查点；不增加正式版本。

### 导入与签名

```python
from ai4e_task.tasks.execution import resume_run
```

```text
resume_run(project, run_id: str, *, checkpoint: str='latest.pt', idempotency_key: str | None=None) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `未标注` | `必填` |
| `run_id` | `str` | `必填` |
| `checkpoint` | `str` | `'latest.pt'` |
| `idempotency_key` | `str | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FileNotFoundError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.tasks.execution import resume_run

print(signature(resume_run))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.execution`
- 仓库相对路径：`packages/ai4e-task/tasks/execution.py:356`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.execution')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-retry-inference"></a>
## `ai4e_task.retry_inference`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`retry_inference(project: str | Path, task_id: str, identity: str, *, idempotency_key: str | None=None) -> dict`
- **规范定义名**：`ai4e_task.tasks.inference.retry_inference`

### 用途

重试失败检查点，沿用固定输入；同一请求键不会生成第二个批次。

### 导入与签名

```python
from ai4e_task.tasks.inference import retry_inference
```

```text
retry_inference(project: str | Path, task_id: str, identity: str, *, idempotency_key: str | None=None) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `task_id` | `str` | `必填` |
| `identity` | `str` | `必填` |
| `idempotency_key` | `str | None` | `None` |

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
from ai4e_task.tasks.inference import retry_inference

print(signature(retry_inference))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.inference`
- 仓库相对路径：`packages/ai4e-task/tasks/inference.py:323`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.inference')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-run-physical-manifest"></a>
## `ai4e_task.run_physical_manifest`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`run_physical_manifest(project: str | Path, run: dict) -> Path | None`
- **规范定义名**：`ai4e_task.projects.datasets.run_physical_manifest`

### 用途

解析运行当时的物理输出；共享已覆盖时不冒充旧运行结果。

### 导入与签名

```python
from ai4e_task.projects.datasets import run_physical_manifest
```

```text
run_physical_manifest(project: str | Path, run: dict) -> Path | None
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `run` | `dict` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Path | None`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.projects.datasets import run_physical_manifest

print(signature(run_physical_manifest))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.projects.datasets`
- 仓库相对路径：`packages/ai4e-task/projects/datasets.py:76`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.projects.datasets')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-save-configuration"></a>
## `ai4e_task.save_configuration`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`save_configuration(project: str | Path, task_id: str, patch: dict, *, revision: str, replace_sections: tuple[str, ...]=()) -> dict`
- **规范定义名**：`ai4e_task.tasks.configuration.save_configuration`

### 用途

在项目锁内核对修订；普通编辑合并，受控 replace_sections 先移除旧段再保存。

### 导入与签名

```python
from ai4e_task.tasks.configuration import save_configuration
```

```text
save_configuration(project: str | Path, task_id: str, patch: dict, *, revision: str, replace_sections: tuple[str, ...]=()) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `task_id` | `str` | `必填` |
| `patch` | `dict` | `必填` |
| `revision` | `str` | `必填关键字参数` |
| `replace_sections` | `tuple[str, ...]` | `()` |

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
from ai4e_task.tasks.configuration import save_configuration

print(signature(save_configuration))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.configuration`
- 仓库相对路径：`packages/ai4e-task/tasks/configuration.py:34`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.configuration')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-search-help"></a>
## `ai4e_task.search_help`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`search_help(query: str, *, kind: str | None=None, layer: str | None=None, limit: int=20) -> list[dict[str, Any]]`
- **规范定义名**：`ai4e_task.templates.resources.search_help`

### 用途

按符号、任务、配置、产物、错误或案例搜索帮助主题。

### 导入与签名

```python
from ai4e_task.templates.resources import search_help
```

```text
search_help(query: str, *, kind: str | None=None, layer: str | None=None, limit: int=20) -> list[dict[str, Any]]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `query` | `str` | `必填` |
| `kind` | `str | None` | `None` |
| `layer` | `str | None` | `None` |
| `limit` | `int` | `20` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`list[dict[str, Any]]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.templates.resources import search_help

print(signature(search_help))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.templates.resources`
- 仓库相对路径：`packages/ai4e-task/templates/resources.py:183`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.templates.resources')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-share-run-asset"></a>
## `ai4e_task.share_run_asset`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`share_run_asset(project, run_id: str, name: str, path, *, kind: str='other', copy: bool=True) -> dict`
- **规范定义名**：`ai4e_task.projects.shared.share_run_asset`

### 用途

显式共享某次运行的产物，仅接受归属该运行的数据或记录区域。

### 导入与签名

```python
from ai4e_task.projects.shared import share_run_asset
```

```text
share_run_asset(project, run_id: str, name: str, path, *, kind: str='other', copy: bool=True) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `未标注` | `必填` |
| `run_id` | `str` | `必填` |
| `name` | `str` | `必填` |
| `path` | `未标注` | `必填` |
| `kind` | `str` | `'other'` |
| `copy` | `bool` | `True` |

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
from ai4e_task.projects.shared import share_run_asset

print(signature(share_run_asset))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.projects.shared`
- 仓库相对路径：`packages/ai4e-task/projects/shared.py:96`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.projects.shared')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-source-location"></a>
## `ai4e_task.source_location`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`source_location(module: str) -> dict[str, str]`
- **规范定义名**：`ai4e_task.templates.resources.source_location`

### 用途

定位当前解释器实际可见的模块源码，不导入模块。

### 导入与签名

```python
from ai4e_task.templates.resources import source_location
```

```text
source_location(module: str) -> dict[str, str]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `module` | `str` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, str]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ModuleNotFoundError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.templates.resources import source_location

print(signature(source_location))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.templates.resources`
- 仓库相对路径：`packages/ai4e-task/templates/resources.py:515`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.templates.resources')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-start-captured-run"></a>
## `ai4e_task.start_captured_run`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`start_captured_run(project: str | Path, run_id: str) -> dict`
- **规范定义名**：`ai4e_task.tasks.execution.start_captured_run`

### 用途

启动已冻结的排队运行；事务内改变启动意图，重复调用不重启进程。

### 导入与签名

```python
from ai4e_task.tasks.execution import start_captured_run
```

```text
start_captured_run(project: str | Path, run_id: str) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `run_id` | `str` | `必填` |

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
from ai4e_task.tasks.execution import start_captured_run

print(signature(start_captured_run))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.execution`
- 仓库相对路径：`packages/ai4e-task/tasks/execution.py:271`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.execution')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-stop-run"></a>
## `ai4e_task.stop_run`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`stop_run(project: str | Path, run_id: str, *, timeout: float=10) -> dict`
- **规范定义名**：`ai4e_task.tasks.execution.stop_run`

### 用途

请求停止并等待确认；未确认保留 stopping 或 unknown。

### 导入与签名

```python
from ai4e_task.tasks.execution import stop_run
```

```text
stop_run(project: str | Path, run_id: str, *, timeout: float=10) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `run_id` | `str` | `必填` |
| `timeout` | `float` | `10` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`RuntimeError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.tasks.execution import stop_run

print(signature(stop_run))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.execution`
- 仓库相对路径：`packages/ai4e-task/tasks/execution.py:312`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.execution')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-submit-inference"></a>
## `ai4e_task.submit_inference`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`submit_inference(project: str | Path, task_id: str, request: dict) -> dict`
- **规范定义名**：`ai4e_task.tasks.inference.submit_inference`

### 用途

固定批次意图和代码后启动独立协调进程；请求重试不创建第二批。

### 导入与签名

```python
from ai4e_task.tasks.inference import submit_inference
```

```text
submit_inference(project: str | Path, task_id: str, request: dict) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `task_id` | `str` | `必填` |
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
from ai4e_task.tasks.inference import submit_inference

print(signature(submit_inference))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.inference`
- 仓库相对路径：`packages/ai4e-task/tasks/inference.py:159`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.inference')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-submit-post-metrics"></a>
## `ai4e_task.submit_post_metrics`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`submit_post_metrics(project, task_id, request)`
- **规范定义名**：`ai4e_task.tasks.post_metrics.submit_post_metrics`

### 用途

固定结果、指标选择与修订，提交幂等后台评价。

### 导入与签名

```python
from ai4e_task.tasks.post_metrics import submit_post_metrics
```

```text
submit_post_metrics(project, task_id, request)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `未标注` | `必填` |
| `task_id` | `未标注` | `必填` |
| `request` | `未标注` | `必填` |

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
from ai4e_task.tasks.post_metrics import submit_post_metrics

print(signature(submit_post_metrics))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.post_metrics`
- 仓库相对路径：`packages/ai4e-task/tasks/post_metrics.py:42`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.post_metrics')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-submit-run"></a>
## `ai4e_task.submit_run`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`submit_run(project, task_id: str, *, overrides: list[str] | None=None, idempotency_key: str | None=None, resumed_from: str | None=None, _code: Path | None=None, _application_source: dict | None=None, expected_revision: str | None=None, operation_mode: str='execute', input_keys: list[str] | None=None, start: bool=True, metadata: dict | None=None, overwrite: bool=False) -> dict`
- **规范定义名**：`ai4e_task.tasks.execution.submit_run`

### 用途

捕获当前工作目录并提交；返回运行记录，不创建正式版本。

### 导入与签名

```python
from ai4e_task.tasks.execution import submit_run
```

```text
submit_run(project, task_id: str, *, overrides: list[str] | None=None, idempotency_key: str | None=None, resumed_from: str | None=None, _code: Path | None=None, _application_source: dict | None=None, expected_revision: str | None=None, operation_mode: str='execute', input_keys: list[str] | None=None, start: bool=True, metadata: dict | None=None, overwrite: bool=False) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `未标注` | `必填` |
| `task_id` | `str` | `必填` |
| `overrides` | `list[str] | None` | `None` |
| `idempotency_key` | `str | None` | `None` |
| `resumed_from` | `str | None` | `None` |
| `_code` | `Path | None` | `None` |
| `_application_source` | `dict | None` | `None` |
| `expected_revision` | `str | None` | `None` |
| `operation_mode` | `str` | `'execute'` |
| `input_keys` | `list[str] | None` | `None` |
| `start` | `bool` | `True` |
| `metadata` | `dict | None` | `None` |
| `overwrite` | `bool` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FileNotFoundError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.tasks.execution import submit_run

print(signature(submit_run))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.execution`
- 仓库相对路径：`packages/ai4e-task/tasks/execution.py:20`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.execution')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-update-project"></a>
## `ai4e_task.update_project`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`update_project(path: str | Path, *, name: str | None=None, description: str | None=None, archived: bool | None=None) -> Project`
- **规范定义名**：`ai4e_task.projects.project.update_project`

### 用途

原子更新项目描述；旧项目缺少新字段时继续兼容。

### 导入与签名

```python
from ai4e_task.projects.project import update_project
```

```text
update_project(path: str | Path, *, name: str | None=None, description: str | None=None, archived: bool | None=None) -> Project
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `str | Path` | `必填` |
| `name` | `str | None` | `None` |
| `description` | `str | None` | `None` |
| `archived` | `bool | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Project`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.projects.project import update_project

print(signature(update_project))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.projects.project`
- 仓库相对路径：`packages/ai4e-task/projects/project.py:76`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.projects.project')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-update-task"></a>
## `ai4e_task.update_task`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`update_task(project: str | Path, task_id: str, *, name: str | None=None, description: str | None=None, archived: bool | None=None) -> dict`
- **规范定义名**：`ai4e_task.tasks.management.update_task`

### 用途

更新任务的管理记录；归档可恢复，不删除资产。

### 导入与签名

```python
from ai4e_task.tasks.management import update_task
```

```text
update_task(project: str | Path, task_id: str, *, name: str | None=None, description: str | None=None, archived: bool | None=None) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `task_id` | `str` | `必填` |
| `name` | `str | None` | `None` |
| `description` | `str | None` | `None` |
| `archived` | `bool | None` | `None` |

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
from ai4e_task.tasks.management import update_task

print(signature(update_task))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.management`
- 仓库相对路径：`packages/ai4e-task/tasks/management.py:12`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.management')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-validate-processed-name"></a>
## `ai4e_task.validate_processed_name`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`validate_processed_name(name: str) -> str`
- **规范定义名**：`ai4e_task.storage.processed_datasets.validate_processed_name`

### 用途

校验平台数据集名称；空值与非法字符都拒绝。

### 导入与签名

```python
from ai4e_task.storage.processed_datasets import validate_processed_name
```

```text
validate_processed_name(name: str) -> str
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `name` | `str` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`str`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_task.storage.processed_datasets import validate_processed_name

print(signature(validate_processed_name))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.storage.processed_datasets`
- 仓库相对路径：`packages/ai4e-task/storage/processed_datasets.py:20`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.storage.processed_datasets')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-validate-rawprep-configuration"></a>
## `ai4e_task.validate_rawprep_configuration`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`validate_rawprep_configuration(project, task_id, rawprep, *, revision)`
- **规范定义名**：`ai4e_task.tasks.rawprep.validate_rawprep_configuration`

### 用途

由相同数据组件校验待保存配置，不在服务中重写算法规则。

### 导入与签名

```python
from ai4e_task.tasks.rawprep import validate_rawprep_configuration
```

```text
validate_rawprep_configuration(project, task_id, rawprep, *, revision)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `未标注` | `必填` |
| `task_id` | `未标注` | `必填` |
| `rawprep` | `未标注` | `必填` |
| `revision` | `未标注` | `必填关键字参数` |

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
from ai4e_task.tasks.rawprep import validate_rawprep_configuration

print(signature(validate_rawprep_configuration))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.rawprep`
- 仓库相对路径：`packages/ai4e-task/tasks/rawprep.py:58`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.rawprep')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-visualization-storage"></a>
## `ai4e_task.visualization_storage`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`visualization_storage(project: str | Path, task_id: str, *, write: bool=False) -> dict`
- **规范定义名**：`ai4e_task.tasks.visualizations.visualization_storage`

### 用途

返回经过身份、归档和路径核验的任务区域，写入时才创建目录。

### 导入与签名

```python
from ai4e_task.tasks.visualizations import visualization_storage
```

```text
visualization_storage(project: str | Path, task_id: str, *, write: bool=False) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `task_id` | `str` | `必填` |
| `write` | `bool` | `False` |

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
from ai4e_task.tasks.visualizations import visualization_storage

print(signature(visualization_storage))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.visualizations`
- 仓库相对路径：`packages/ai4e-task/tasks/visualizations.py:10`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.visualizations')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-task-wait-run"></a>
## `ai4e_task.wait_run`

- **层级**：`task`
- **稳定性**：`stable`
- **定义**：`wait_run(project: str | Path, run_id: str, *, timeout: float=60, interval: float=0.1) -> dict`
- **规范定义名**：`ai4e_task.tasks.execution.wait_run`

### 用途

等待真实完成状态；超时返回当前状态，不把超时当失败。

### 导入与签名

```python
from ai4e_task.tasks.execution import wait_run
```

```text
wait_run(project: str | Path, run_id: str, *, timeout: float=60, interval: float=0.1) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `project` | `str | Path` | `必填` |
| `run_id` | `str` | `必填` |
| `timeout` | `float` | `60` |
| `interval` | `float` | `0.1` |

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
from ai4e_task.tasks.execution import wait_run

print(signature(wait_run))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_task.tasks.execution`
- 仓库相对路径：`packages/ai4e-task/tasks/execution.py:295`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_task')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_task.tasks.execution')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
