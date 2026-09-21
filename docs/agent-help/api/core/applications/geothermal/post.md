<!-- dojo-help: {"domain": "ai4e_core.applications.geothermal.post", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.geothermal.post 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.geothermal.post", "topic_id": "module:ai4e_core.applications.geothermal.post"} -->
# `ai4e_core.applications.geothermal.post` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-geothermal-post-evaluate-results"></a>
## `ai4e_core.applications.geothermal.post.evaluate_results`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`evaluate_results(record, arrays)`
- **规范定义名**：`ai4e_core.applications.geothermal.post.evaluate_results`

### 用途

第1—20年逐例评价后按例等权；无独立真值不输出精度。

### 导入与签名

```python
from ai4e_core.applications.geothermal.post import evaluate_results
```

```text
evaluate_results(record, arrays)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `record` | `未标注` | `必填` |
| `arrays` | `未标注` | `必填` |

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
from ai4e_core.applications.geothermal.post import evaluate_results

print(signature(evaluate_results))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`pcno`
- 案例：`geothermal.pcno`

### 源码位置

- 模块：`ai4e_core.applications.geothermal.post`
- 仓库相对路径：`packages/ai4e-core/applications/geothermal/post.py:42`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.geothermal.post')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-geothermal-post-read-results"></a>
## `ai4e_core.applications.geothermal.post.read_results`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`read_results(path)`
- **规范定义名**：`ai4e_core.applications.geothermal.post.read_results`

### 用途

核对清单和每个结果内容；扩展数组也按声明读回。

### 导入与签名

```python
from ai4e_core.applications.geothermal.post import read_results
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
from ai4e_core.applications.geothermal.post import read_results

print(signature(read_results))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`gencp`, `pcno`
- 案例：`extension.pcno`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `geothermal.pcno`, `recipe_extensions.gencp`

### 源码位置

- 模块：`ai4e_core.applications.geothermal.post`
- 仓库相对路径：`packages/ai4e-core/applications/geothermal/post.py:13`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.geothermal.post')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
