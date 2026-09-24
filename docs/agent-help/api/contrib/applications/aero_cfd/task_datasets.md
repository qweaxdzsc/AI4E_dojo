<!-- dojo-help: {"domain": "ai4e_contrib.application.aero_cfd.task_datasets", "kind": "api", "layer": "contrib.application", "summary": "ai4e_contrib.application.aero_cfd.task_datasets 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.application.aero_cfd.task_datasets", "topic_id": "module:ai4e_contrib.application.aero_cfd.task_datasets"} -->
# `ai4e_contrib.application.aero_cfd.task_datasets` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-application-aero-cfd-task-datasets-conflict-detail"></a>
## `ai4e_contrib.application.aero_cfd.task_datasets.conflict_detail`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`conflict_detail(existing: dict, incoming: dict) -> str`
- **规范定义名**：`ai4e_contrib.application.aero_cfd.task_datasets.conflict_detail`

### 用途

应用解释处理身份差异；历史缺身份不根据当前配置补写。

### 导入与签名

```python
from ai4e_contrib.application.aero_cfd.task_datasets import conflict_detail
```

```text
conflict_detail(existing: dict, incoming: dict) -> str
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `existing` | `dict` | `必填` |
| `incoming` | `dict` | `必填` |

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
from ai4e_contrib.application.aero_cfd.task_datasets import conflict_detail

print(signature(conflict_detail))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.aero_cfd.task_datasets`
- 仓库相对路径：`packages/ai4e-contrib/application/aero_cfd/task_datasets.py:14`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.aero_cfd.task_datasets')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-aero-cfd-task-datasets-dataset-copy-plan"></a>
## `ai4e_contrib.application.aero_cfd.task_datasets.dataset_copy_plan`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`dataset_copy_plan(manifest: str) -> dict`
- **规范定义名**：`ai4e_contrib.application.aero_cfd.task_datasets.dataset_copy_plan`

### 用途

描述物理数据复制及新副本的引用转换，不写原始清单。

### 导入与签名

```python
from ai4e_contrib.application.aero_cfd.task_datasets import dataset_copy_plan
```

```text
dataset_copy_plan(manifest: str) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `manifest` | `str` | `必填` |

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
from ai4e_contrib.application.aero_cfd.task_datasets import dataset_copy_plan

print(signature(dataset_copy_plan))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.aero_cfd.task_datasets`
- 仓库相对路径：`packages/ai4e-contrib/application/aero_cfd/task_datasets.py:188`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.aero_cfd.task_datasets')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-aero-cfd-task-datasets-describe-dataset"></a>
## `ai4e_contrib.application.aero_cfd.task_datasets.describe_dataset`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`describe_dataset(manifest: str) -> dict`
- **规范定义名**：`ai4e_contrib.application.aero_cfd.task_datasets.describe_dataset`

### 用途

校验科学清单，交付成员与可搬移身份，不承担发布或覆盖许可。

### 导入与签名

```python
from ai4e_contrib.application.aero_cfd.task_datasets import describe_dataset
```

```text
describe_dataset(manifest: str) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `manifest` | `str` | `必填` |

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
from ai4e_contrib.application.aero_cfd.task_datasets import describe_dataset

print(signature(describe_dataset))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.aero_cfd.task_datasets`
- 仓库相对路径：`packages/ai4e-contrib/application/aero_cfd/task_datasets.py:151`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.aero_cfd.task_datasets')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-aero-cfd-task-datasets-migration-candidates"></a>
## `ai4e_contrib.application.aero_cfd.task_datasets.migration_candidates`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`migration_candidates(runs: list[dict]) -> list[dict]`
- **规范定义名**：`ai4e_contrib.application.aero_cfd.task_datasets.migration_candidates`

### 用途

显式旧数据迁移的领域识别；只读历史配置，返回可选择来源。

### 导入与签名

```python
from ai4e_contrib.application.aero_cfd.task_datasets import migration_candidates
```

```text
migration_candidates(runs: list[dict]) -> list[dict]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `runs` | `list[dict]` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`list[dict]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

`inputs.trainprep.dataset`

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.application.aero_cfd.task_datasets import migration_candidates

print(signature(migration_candidates))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.aero_cfd.task_datasets`
- 仓库相对路径：`packages/ai4e-contrib/application/aero_cfd/task_datasets.py:226`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.aero_cfd.task_datasets')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-aero-cfd-task-datasets-processed-claim"></a>
## `ai4e_contrib.application.aero_cfd.task_datasets.processed_claim`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`processed_claim(config: dict) -> dict`
- **规范定义名**：`ai4e_contrib.application.aero_cfd.task_datasets.processed_claim`

### 用途

用源数据与处理产物语义识别同名是否同一意图；并行线程与列表顺序不进入声明。

### 导入与签名

```python
from ai4e_contrib.application.aero_cfd.task_datasets import processed_claim
```

```text
processed_claim(config: dict) -> dict
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
from ai4e_contrib.application.aero_cfd.task_datasets import processed_claim

print(signature(processed_claim))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.aero_cfd.task_datasets`
- 仓库相对路径：`packages/ai4e-contrib/application/aero_cfd/task_datasets.py:8`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.aero_cfd.task_datasets')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-aero-cfd-task-datasets-validate-manifest"></a>
## `ai4e_contrib.application.aero_cfd.task_datasets.validate_manifest`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`validate_manifest(manifest: Path) -> dict`
- **规范定义名**：`ai4e_contrib.application.aero_cfd.task_datasets.validate_manifest`

### 用途

校验完整物理清单和声明成员；张量数值由下游公开读盘能力校验。

### 导入与签名

```python
from ai4e_contrib.application.aero_cfd.task_datasets import validate_manifest
```

```text
validate_manifest(manifest: Path) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `manifest` | `Path` | `必填` |

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
from ai4e_contrib.application.aero_cfd.task_datasets import validate_manifest

print(signature(validate_manifest))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.aero_cfd.task_datasets`
- 仓库相对路径：`packages/ai4e-contrib/application/aero_cfd/task_datasets.py:102`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.aero_cfd.task_datasets')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
