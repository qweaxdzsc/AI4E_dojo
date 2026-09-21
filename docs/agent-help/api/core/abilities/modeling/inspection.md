<!-- dojo-help: {"domain": "ai4e_core.abilities.modeling.inspection", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.modeling.inspection 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.modeling.inspection", "topic_id": "module:ai4e_core.abilities.modeling.inspection"} -->
# `ai4e_core.abilities.modeling.inspection` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-modeling-inspection-fit-graph-viewport"></a>
## `ai4e_core.abilities.modeling.inspection.fit_graph_viewport`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`fit_graph_viewport(html: str) -> str`
- **规范定义名**：`ai4e_core.abilities.modeling.inspection.fit_graph_viewport`

### 用途

把 TorchVista 默认的整图塞进视口改成按宽度适配，避免深网络缩成看不见的细线。

### 导入与签名

```python
from ai4e_core.abilities.modeling.inspection import fit_graph_viewport
```

```text
fit_graph_viewport(html: str) -> str
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `html` | `str` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`str`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`RuntimeError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.inspection import fit_graph_viewport

print(signature(fit_graph_viewport))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.inspection`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/inspection.py:20`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.inspection')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-inspection-trace"></a>
## `ai4e_core.abilities.modeling.inspection.trace`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`trace(model: torch.nn.Module, inputs, output_dir: Path, *, revision: str, input_source: dict, predict=None) -> dict`
- **规范定义名**：`ai4e_core.abilities.modeling.inspection.trace`

### 用途

保持正式模型参数，以真实输入执行中等体量 TorchVista 模块图并记录来源。

### 导入与签名

```python
from ai4e_core.abilities.modeling.inspection import trace
```

```text
trace(model: torch.nn.Module, inputs, output_dir: Path, *, revision: str, input_source: dict, predict=None) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model` | `torch.nn.Module` | `必填` |
| `inputs` | `未标注` | `必填` |
| `output_dir` | `Path` | `必填` |
| `revision` | `str` | `必填关键字参数` |
| `input_source` | `dict` | `必填关键字参数` |
| `predict` | `未标注` | `None` |

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
from ai4e_core.abilities.modeling.inspection import trace

print(signature(trace))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.inspection`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/inspection.py:27`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.inspection')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
