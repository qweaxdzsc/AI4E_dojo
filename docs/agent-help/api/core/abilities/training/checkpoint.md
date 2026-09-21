<!-- dojo-help: {"domain": "ai4e_core.abilities.training.checkpoint", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.training.checkpoint 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.training.checkpoint", "topic_id": "module:ai4e_core.abilities.training.checkpoint"} -->
# `ai4e_core.abilities.training.checkpoint` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-training-checkpoint-capture"></a>
## `ai4e_core.abilities.training.checkpoint.capture`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`capture(model, optimizer, *, epoch, updates, best, contract, ema=None, scaler=None, scheduler=None)`
- **规范定义名**：`ai4e_core.abilities.training.checkpoint.capture`

### 用途

冻结模型、优化器和所有已启用随机/数值状态。

### 导入与签名

```python
from ai4e_core.abilities.training.checkpoint import capture
```

```text
capture(model, optimizer, *, epoch, updates, best, contract, ema=None, scaler=None, scheduler=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model` | `未标注` | `必填` |
| `optimizer` | `未标注` | `必填` |
| `epoch` | `未标注` | `必填关键字参数` |
| `updates` | `未标注` | `必填关键字参数` |
| `best` | `未标注` | `必填关键字参数` |
| `contract` | `未标注` | `必填关键字参数` |
| `ema` | `未标注` | `None` |
| `scaler` | `未标注` | `None` |
| `scheduler` | `未标注` | `None` |

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
from ai4e_core.abilities.training.checkpoint import capture

print(signature(capture))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.training.checkpoint`
- 仓库相对路径：`packages/ai4e-core/abilities/training/checkpoint.py:10`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.checkpoint')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-checkpoint-capture-iteration"></a>
## `ai4e_core.abilities.training.checkpoint.capture_iteration`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`capture_iteration(model, optimizer, *, updates, stream, contract, history, ema=None, scheduler=None, scaler=None)`
- **规范定义名**：`ai4e_core.abilities.training.checkpoint.capture_iteration`

### 用途

在既有检查点容器中补充迭代状态，不改变旧轮次恢复语义。

### 导入与签名

```python
from ai4e_core.abilities.training.checkpoint import capture_iteration
```

```text
capture_iteration(model, optimizer, *, updates, stream, contract, history, ema=None, scheduler=None, scaler=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model` | `未标注` | `必填` |
| `optimizer` | `未标注` | `必填` |
| `updates` | `未标注` | `必填关键字参数` |
| `stream` | `未标注` | `必填关键字参数` |
| `contract` | `未标注` | `必填关键字参数` |
| `history` | `未标注` | `必填关键字参数` |
| `ema` | `未标注` | `None` |
| `scheduler` | `未标注` | `None` |
| `scaler` | `未标注` | `None` |

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
from ai4e_core.abilities.training.checkpoint import capture_iteration

print(signature(capture_iteration))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.training.checkpoint`
- 仓库相对路径：`packages/ai4e-core/abilities/training/checkpoint.py:114`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.checkpoint')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-checkpoint-restore"></a>
## `ai4e_core.abilities.training.checkpoint.restore`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`restore(path, model, optimizer, *, contract, ema=None, scaler=None, scheduler=None)`
- **规范定义名**：`ai4e_core.abilities.training.checkpoint.restore`

### 用途

加载用户指定可信本地检查点，语义不一致即拒绝恢复。

### 导入与签名

```python
from ai4e_core.abilities.training.checkpoint import restore
```

```text
restore(path, model, optimizer, *, contract, ema=None, scaler=None, scheduler=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `未标注` | `必填` |
| `model` | `未标注` | `必填` |
| `optimizer` | `未标注` | `必填` |
| `contract` | `未标注` | `必填关键字参数` |
| `ema` | `未标注` | `None` |
| `scaler` | `未标注` | `None` |
| `scheduler` | `未标注` | `None` |

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
from ai4e_core.abilities.training.checkpoint import restore

print(signature(restore))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.training.checkpoint`
- 仓库相对路径：`packages/ai4e-core/abilities/training/checkpoint.py:44`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.checkpoint')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-checkpoint-restore-iteration"></a>
## `ai4e_core.abilities.training.checkpoint.restore_iteration`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`restore_iteration(path, model, optimizer, *, stream, contract, ema=None, scheduler=None, scaler=None)`
- **规范定义名**：`ai4e_core.abilities.training.checkpoint.restore_iteration`

### 用途

先核对合同和游标副本，再恢复模型与真实数据流，拒绝时不消耗输入。

### 导入与签名

```python
from ai4e_core.abilities.training.checkpoint import restore_iteration
```

```text
restore_iteration(path, model, optimizer, *, stream, contract, ema=None, scheduler=None, scaler=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `未标注` | `必填` |
| `model` | `未标注` | `必填` |
| `optimizer` | `未标注` | `必填` |
| `stream` | `未标注` | `必填关键字参数` |
| `contract` | `未标注` | `必填关键字参数` |
| `ema` | `未标注` | `None` |
| `scheduler` | `未标注` | `None` |
| `scaler` | `未标注` | `None` |

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
from ai4e_core.abilities.training.checkpoint import restore_iteration

print(signature(restore_iteration))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.training.checkpoint`
- 仓库相对路径：`packages/ai4e-core/abilities/training/checkpoint.py:133`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.checkpoint')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-checkpoint-restore-selection"></a>
## `ai4e_core.abilities.training.checkpoint.restore_selection`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`restore_selection(state, path, *, best_on_equal=False)`
- **规范定义名**：`ai4e_core.abilities.training.checkpoint.restore_selection`

### 用途

恢复此前选优产物；缺失时拒绝把最新模型伪装成最佳模型。

### 导入与签名

```python
from ai4e_core.abilities.training.checkpoint import restore_selection
```

```text
restore_selection(state, path, *, best_on_equal=False)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `state` | `未标注` | `必填` |
| `path` | `未标注` | `必填` |
| `best_on_equal` | `未标注` | `False` |

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
from ai4e_core.abilities.training.checkpoint import restore_selection

print(signature(restore_selection))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.training.checkpoint`
- 仓库相对路径：`packages/ai4e-core/abilities/training/checkpoint.py:79`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.checkpoint')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
