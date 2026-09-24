<!-- dojo-help: {"domain": "ai4e_core.abilities.training.iteration_stream", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.training.iteration_stream 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.training.iteration_stream", "topic_id": "module:ai4e_core.abilities.training.iteration_stream"} -->
# `ai4e_core.abilities.training.iteration_stream` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-training-iteration-stream-countediterationstream"></a>
## `ai4e_core.abilities.training.iteration_stream.CountedIterationStream`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`CountedIterationStream(count, batch_size, *, seed=42)`
- **规范定义名**：`ai4e_core.abilities.training.iteration_stream.CountedIterationStream`

### 用途

额外保存已取批次数，供局部目标函数恢复阶段调度。

### 导入与签名

```python
from ai4e_core.abilities.training.iteration_stream import CountedIterationStream
```

```text
CountedIterationStream(count, batch_size, *, seed=42)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `count` | `未标注` | `必填` |
| `batch_size` | `未标注` | `必填` |
| `seed` | `未标注` | `42` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`CountedIterationStream`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.training.iteration_stream import CountedIterationStream

print(signature(CountedIterationStream))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.training.iteration_stream`
- 仓库相对路径：`packages/ai4e-core/abilities/training/iteration_stream.py:48`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.iteration_stream')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-iteration-stream-countediterationstream-load-state-dict"></a>
## `ai4e_core.abilities.training.iteration_stream.CountedIterationStream.load_state_dict`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`load_state_dict(self, state)`
- **规范定义名**：`ai4e_core.abilities.training.iteration_stream.CountedIterationStream.load_state_dict`

### 用途

恢复时拒绝缺少调度游标的状态。

### 导入与签名

```python
from ai4e_core.abilities.training.iteration_stream import CountedIterationStream
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
from ai4e_core.abilities.training.iteration_stream import CountedIterationStream

print(signature(CountedIterationStream.load_state_dict))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`
- 案例：`classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `recipe_extensions.pod_surrogate_replacement`, `recipe_extensions.research_state`

### 源码位置

- 模块：`ai4e_core.abilities.training.iteration_stream`
- 仓库相对路径：`packages/ai4e-core/abilities/training/iteration_stream.py:65`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.iteration_stream')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-iteration-stream-countediterationstream-next"></a>
## `ai4e_core.abilities.training.iteration_stream.CountedIterationStream.next`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`next(self)`
- **规范定义名**：`ai4e_core.abilities.training.iteration_stream.CountedIterationStream.next`

### 用途

返回批次并推进明确的调度游标。

### 导入与签名

```python
from ai4e_core.abilities.training.iteration_stream import CountedIterationStream
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
from ai4e_core.abilities.training.iteration_stream import CountedIterationStream

print(signature(CountedIterationStream.next))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.training.iteration_stream`
- 仓库相对路径：`packages/ai4e-core/abilities/training/iteration_stream.py:55`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.iteration_stream')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-iteration-stream-countediterationstream-state-dict"></a>
## `ai4e_core.abilities.training.iteration_stream.CountedIterationStream.state_dict`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`state_dict(self)`
- **规范定义名**：`ai4e_core.abilities.training.iteration_stream.CountedIterationStream.state_dict`

### 用途

保存随机排列和调度游标。

### 导入与签名

```python
from ai4e_core.abilities.training.iteration_stream import CountedIterationStream
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
from ai4e_core.abilities.training.iteration_stream import CountedIterationStream

print(signature(CountedIterationStream.state_dict))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`
- 案例：`classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `recipe_extensions.pod_surrogate_replacement`, `recipe_extensions.research_state`

### 源码位置

- 模块：`ai4e_core.abilities.training.iteration_stream`
- 仓库相对路径：`packages/ai4e-core/abilities/training/iteration_stream.py:61`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.iteration_stream')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-iteration-stream-iterationstream"></a>
## `ai4e_core.abilities.training.iteration_stream.IterationStream`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`IterationStream(count, batch_size, *, seed=42)`
- **规范定义名**：`ai4e_core.abilities.training.iteration_stream.IterationStream`

### 用途

保存排列、批次游标和发生器状态，恢复时不重复或跳过样本。

### 导入与签名

```python
from ai4e_core.abilities.training.iteration_stream import IterationStream
```

```text
IterationStream(count, batch_size, *, seed=42)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `count` | `未标注` | `必填` |
| `batch_size` | `未标注` | `必填` |
| `seed` | `未标注` | `42` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`IterationStream`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.training.iteration_stream import IterationStream

print(signature(IterationStream))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`
- 案例：`classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `recipe_extensions.pod_surrogate_replacement`

### 源码位置

- 模块：`ai4e_core.abilities.training.iteration_stream`
- 仓库相对路径：`packages/ai4e-core/abilities/training/iteration_stream.py:6`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.iteration_stream')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-iteration-stream-iterationstream-load-state-dict"></a>
## `ai4e_core.abilities.training.iteration_stream.IterationStream.load_state_dict`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`load_state_dict(self, state)`
- **规范定义名**：`ai4e_core.abilities.training.iteration_stream.IterationStream.load_state_dict`

### 用途

恢复同一批次契约，拒绝非法排列与游标。

### 导入与签名

```python
from ai4e_core.abilities.training.iteration_stream import IterationStream
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
from ai4e_core.abilities.training.iteration_stream import IterationStream

print(signature(IterationStream.load_state_dict))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`
- 案例：`classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `recipe_extensions.pod_surrogate_replacement`, `recipe_extensions.research_state`

### 源码位置

- 模块：`ai4e_core.abilities.training.iteration_stream`
- 仓库相对路径：`packages/ai4e-core/abilities/training/iteration_stream.py:35`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.iteration_stream')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-iteration-stream-iterationstream-next"></a>
## `ai4e_core.abilities.training.iteration_stream.IterationStream.next`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`next(self)`
- **规范定义名**：`ai4e_core.abilities.training.iteration_stream.IterationStream.next`

### 用途

返回下一个完整批次索引。

### 导入与签名

```python
from ai4e_core.abilities.training.iteration_stream import IterationStream
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
from ai4e_core.abilities.training.iteration_stream import IterationStream

print(signature(IterationStream.next))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.training.iteration_stream`
- 仓库相对路径：`packages/ai4e-core/abilities/training/iteration_stream.py:16`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.iteration_stream')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-iteration-stream-iterationstream-state-dict"></a>
## `ai4e_core.abilities.training.iteration_stream.IterationStream.state_dict`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`state_dict(self)`
- **规范定义名**：`ai4e_core.abilities.training.iteration_stream.IterationStream.state_dict`

### 用途

捕获下一批之前的状态。

### 导入与签名

```python
from ai4e_core.abilities.training.iteration_stream import IterationStream
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
from ai4e_core.abilities.training.iteration_stream import IterationStream

print(signature(IterationStream.state_dict))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`
- 案例：`classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `recipe_extensions.pod_surrogate_replacement`, `recipe_extensions.research_state`

### 源码位置

- 模块：`ai4e_core.abilities.training.iteration_stream`
- 仓库相对路径：`packages/ai4e-core/abilities/training/iteration_stream.py:25`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.iteration_stream')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
