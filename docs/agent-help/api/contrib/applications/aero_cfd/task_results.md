<!-- dojo-help: {"domain": "ai4e_contrib.application.aero_cfd.task_results", "kind": "api", "layer": "contrib.application", "summary": "ai4e_contrib.application.aero_cfd.task_results 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.application.aero_cfd.task_results", "topic_id": "module:ai4e_contrib.application.aero_cfd.task_results"} -->
# `ai4e_contrib.application.aero_cfd.task_results` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-application-aero-cfd-task-results-read-json"></a>
## `ai4e_contrib.application.aero_cfd.task_results.read_json`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`read_json(path)`
- **规范定义名**：`ai4e_contrib.application.aero_cfd.task_results.read_json`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.application.aero_cfd.task_results import read_json
```

```text
read_json(path)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `未标注` | `必填` |

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
from ai4e_contrib.application.aero_cfd.task_results import read_json

print(signature(read_json))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.aero_cfd.task_results`
- 仓库相对路径：`packages/ai4e-contrib/application/aero_cfd/task_results.py:23`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.aero_cfd.task_results')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-aero-cfd-task-results-read-results"></a>
## `ai4e_contrib.application.aero_cfd.task_results.read_results`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`read_results(payload)`
- **规范定义名**：`ai4e_contrib.application.aero_cfd.task_results.read_results`

### 用途

读取传入批次的明确子运行，交付结果成员、指标和显示描述。

### 导入与签名

```python
from ai4e_contrib.application.aero_cfd.task_results import read_results
```

```text
read_results(payload)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `payload` | `未标注` | `必填` |

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
from ai4e_contrib.application.aero_cfd.task_results import read_results

print(signature(read_results))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`gencp`, `pcno`
- 案例：`extension.pcno`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `geothermal.pcno`, `recipe_extensions.gencp`

### 源码位置

- 模块：`ai4e_contrib.application.aero_cfd.task_results`
- 仓库相对路径：`packages/ai4e-contrib/application/aero_cfd/task_results.py:31`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.aero_cfd.task_results')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
