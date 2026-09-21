<!-- dojo-help: {"domain": "ai4e_core.abilities.training.rotating_chunks", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.training.rotating_chunks 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.training.rotating_chunks", "topic_id": "module:ai4e_core.abilities.training.rotating_chunks"} -->
# `ai4e_core.abilities.training.rotating_chunks` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-training-rotating-chunks-rotatingchunkstream"></a>
## `ai4e_core.abilities.training.rotating_chunks.RotatingChunkStream`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`RotatingChunkStream(chunks, samples_per_chunk)`
- **规范定义名**：`ai4e_core.abilities.training.rotating_chunks.RotatingChunkStream`

### 用途

块内顺序不变，每轮对上一轮块顺序洗牌并留出最后一块。

### 导入与签名

```python
from ai4e_core.abilities.training.rotating_chunks import RotatingChunkStream
```

```text
RotatingChunkStream(chunks, samples_per_chunk)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `chunks` | `未标注` | `必填` |
| `samples_per_chunk` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`RotatingChunkStream`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.training.rotating_chunks import RotatingChunkStream

print(signature(RotatingChunkStream))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.training.rotating_chunks`
- 仓库相对路径：`packages/ai4e-core/abilities/training/rotating_chunks.py:6`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.rotating_chunks')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-rotating-chunks-rotatingchunkstream-load-state-dict"></a>
## `ai4e_core.abilities.training.rotating_chunks.RotatingChunkStream.load_state_dict`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`load_state_dict(self, state)`
- **规范定义名**：`ai4e_core.abilities.training.rotating_chunks.RotatingChunkStream.load_state_dict`

### 用途

拒绝来源或轮次游标不相容的状态。

### 导入与签名

```python
from ai4e_core.abilities.training.rotating_chunks import RotatingChunkStream
```

```text
load_state_dict(self, state)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `state` | `未标注` | `必填` |

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
from ai4e_core.abilities.training.rotating_chunks import RotatingChunkStream

print(signature(RotatingChunkStream.load_state_dict))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.training.rotating_chunks`
- 仓库相对路径：`packages/ai4e-core/abilities/training/rotating_chunks.py:38`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.rotating_chunks')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-rotating-chunks-rotatingchunkstream-next"></a>
## `ai4e_core.abilities.training.rotating_chunks.RotatingChunkStream.next`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`next(self)`
- **规范定义名**：`ai4e_core.abilities.training.rotating_chunks.RotatingChunkStream.next`

### 用途

返回块身份、块内样本位置和从1起算的轮次。

### 导入与签名

```python
from ai4e_core.abilities.training.rotating_chunks import RotatingChunkStream
```

```text
next(self)
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
from ai4e_core.abilities.training.rotating_chunks import RotatingChunkStream

print(signature(RotatingChunkStream.next))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.training.rotating_chunks`
- 仓库相对路径：`packages/ai4e-core/abilities/training/rotating_chunks.py:18`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.rotating_chunks')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-rotating-chunks-rotatingchunkstream-state-dict"></a>
## `ai4e_core.abilities.training.rotating_chunks.RotatingChunkStream.state_dict`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`state_dict(self)`
- **规范定义名**：`ai4e_core.abilities.training.rotating_chunks.RotatingChunkStream.state_dict`

### 用途

记录已有排列和下一样本游标，RNG由共享检查点保存。

### 导入与签名

```python
from ai4e_core.abilities.training.rotating_chunks import RotatingChunkStream
```

```text
state_dict(self)
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
from ai4e_core.abilities.training.rotating_chunks import RotatingChunkStream

print(signature(RotatingChunkStream.state_dict))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.training.rotating_chunks`
- 仓库相对路径：`packages/ai4e-core/abilities/training/rotating_chunks.py:29`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.rotating_chunks')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
