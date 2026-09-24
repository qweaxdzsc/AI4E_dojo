<!-- dojo-help: {"domain": "ai4e_core.abilities.training.epoch_stream", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.training.epoch_stream 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.training.epoch_stream", "topic_id": "module:ai4e_core.abilities.training.epoch_stream"} -->
# `ai4e_core.abilities.training.epoch_stream` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-training-epoch-stream-epochbatchstream"></a>
## `ai4e_core.abilities.training.epoch_stream.EpochBatchStream`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`EpochBatchStream(epoch_items: Callable[[np.random.Generator, int], Sequence[Any]], batch_size: int, *, seed: int=42, drop_last: bool=False, source_contract: dict[str, Any])`
- **规范定义名**：`ai4e_core.abilities.training.epoch_stream.EpochBatchStream`

### 用途

保留用户有序记录、PCG64 和轮内游标，支持尾批或显式丢尾。

epoch_items(rng, epoch) 接收独立 NumPy Generator 和从零开始的轮次，
返回有限 list/tuple。它应只使用传入 rng 抽样，来源与语义由调用者通过
source_contract 声明。构造、快照与恢复均不调用它；下一轮首批才生成记录。
不负责读取数据、设备搬运、额外打乱、多 worker 预取或外部函数状态恢复。

### 导入与签名

```python
from ai4e_core.abilities.training.epoch_stream import EpochBatchStream
```

```text
EpochBatchStream(epoch_items: Callable[[np.random.Generator, int], Sequence[Any]], batch_size: int, *, seed: int=42, drop_last: bool=False, source_contract: dict[str, Any])
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `epoch_items` | `Callable[[np.random.Generator, int], Sequence[Any]]` | `必填` |
| `batch_size` | `int` | `必填` |
| `seed` | `int` | `42` |
| `drop_last` | `bool` | `False` |
| `source_contract` | `dict[str, Any]` | `必填关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`EpochBatchStream`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`TypeError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.training.epoch_stream import EpochBatchStream

print(signature(EpochBatchStream))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.research_state`, `recipe_extensions.tail_batch`

### 源码位置

- 模块：`ai4e_core.abilities.training.epoch_stream`
- 仓库相对路径：`packages/ai4e-core/abilities/training/epoch_stream.py:27`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.epoch_stream')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-epoch-stream-epochbatchstream-epoch"></a>
## `ai4e_core.abilities.training.epoch_stream.EpochBatchStream.epoch`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`epoch(self) -> int`
- **规范定义名**：`ai4e_core.abilities.training.epoch_stream.EpochBatchStream.epoch`

### 用途

当前零基轮次；尚未取批时为 -1。

### 导入与签名

```python
from ai4e_core.abilities.training.epoch_stream import EpochBatchStream
```

```text
epoch(self) -> int
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`int`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.training.epoch_stream import EpochBatchStream

print(signature(EpochBatchStream.epoch))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`, `surrogate_modeling/double_cylinder`, `surrogate_modeling/nasa_crm`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.free_wiring`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.inference_fields`, `recipe_extensions.inference_metrics`, `recipe_extensions.model_block`, `recipe_extensions.physical_visualization`, `recipe_extensions.research_state`, `recipe_extensions.sampling`, `recipe_extensions.tail_batch`, `surrogate_modeling.double_cylinder`, `surrogate_modeling.nasa_crm`

### 源码位置

- 模块：`ai4e_core.abilities.training.epoch_stream`
- 仓库相对路径：`packages/ai4e-core/abilities/training/epoch_stream.py:58`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.epoch_stream')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-epoch-stream-epochbatchstream-epoch-end"></a>
## `ai4e_core.abilities.training.epoch_stream.EpochBatchStream.epoch_end`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`epoch_end(self) -> bool`
- **规范定义名**：`ai4e_core.abilities.training.epoch_stream.EpochBatchStream.epoch_end`

### 用途

取批后是否已到轮末，可连接 fit_iterations 的 epoch_end 回调。

### 导入与签名

```python
from ai4e_core.abilities.training.epoch_stream import EpochBatchStream
```

```text
epoch_end(self) -> bool
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`bool`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.training.epoch_stream import EpochBatchStream

print(signature(EpochBatchStream.epoch_end))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.training.epoch_stream`
- 仓库相对路径：`packages/ai4e-core/abilities/training/epoch_stream.py:68`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.epoch_stream')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-epoch-stream-epochbatchstream-load-state-dict"></a>
## `ai4e_core.abilities.training.epoch_stream.EpochBatchStream.load_state_dict`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`load_state_dict(self, state: dict[str, Any]) -> None`
- **规范定义名**：`ai4e_core.abilities.training.epoch_stream.EpochBatchStream.load_state_dict`

### 用途

先验证完整副本再恢复；拒绝时保持当前流不变。

### 导入与签名

```python
from ai4e_core.abilities.training.epoch_stream import EpochBatchStream
```

```text
load_state_dict(self, state: dict[str, Any]) -> None
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `state` | `dict[str, Any]` | `必填` |

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
from ai4e_core.abilities.training.epoch_stream import EpochBatchStream

print(signature(EpochBatchStream.load_state_dict))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`
- 案例：`classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `recipe_extensions.pod_surrogate_replacement`, `recipe_extensions.research_state`

### 源码位置

- 模块：`ai4e_core.abilities.training.epoch_stream`
- 仓库相对路径：`packages/ai4e-core/abilities/training/epoch_stream.py:154`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.epoch_stream')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-epoch-stream-epochbatchstream-next"></a>
## `ai4e_core.abilities.training.epoch_stream.EpochBatchStream.next`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`next(self) -> list[Any]`
- **规范定义名**：`ai4e_core.abilities.training.epoch_stream.EpochBatchStream.next`

### 用途

交付独立的下一批记录；空轮或丢尾后零批即失败，不自动跳过。

### 导入与签名

```python
from ai4e_core.abilities.training.epoch_stream import EpochBatchStream
```

```text
next(self) -> list[Any]
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`list[Any]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.training.epoch_stream import EpochBatchStream

print(signature(EpochBatchStream.next))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.training.epoch_stream`
- 仓库相对路径：`packages/ai4e-core/abilities/training/epoch_stream.py:75`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.epoch_stream')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-epoch-stream-epochbatchstream-offset"></a>
## `ai4e_core.abilities.training.epoch_stream.EpochBatchStream.offset`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`offset(self) -> int`
- **规范定义名**：`ai4e_core.abilities.training.epoch_stream.EpochBatchStream.offset`

### 用途

当前轮已交付的记录数；丢弃尾项不计入。

### 导入与签名

```python
from ai4e_core.abilities.training.epoch_stream import EpochBatchStream
```

```text
offset(self) -> int
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`int`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.training.epoch_stream import EpochBatchStream

print(signature(EpochBatchStream.offset))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.training.epoch_stream`
- 仓库相对路径：`packages/ai4e-core/abilities/training/epoch_stream.py:63`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.epoch_stream')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-epoch-stream-epochbatchstream-state-dict"></a>
## `ai4e_core.abilities.training.epoch_stream.EpochBatchStream.state_dict`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`state_dict(self) -> dict[str, Any]`
- **规范定义名**：`ai4e_core.abilities.training.epoch_stream.EpochBatchStream.state_dict`

### 用途

捕获下一批之前的独立状态，不保存函数或读取下一轮。

### 导入与签名

```python
from ai4e_core.abilities.training.epoch_stream import EpochBatchStream
```

```text
state_dict(self) -> dict[str, Any]
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
from ai4e_core.abilities.training.epoch_stream import EpochBatchStream

print(signature(EpochBatchStream.state_dict))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`
- 案例：`classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `recipe_extensions.pod_surrogate_replacement`, `recipe_extensions.research_state`

### 源码位置

- 模块：`ai4e_core.abilities.training.epoch_stream`
- 仓库相对路径：`packages/ai4e-core/abilities/training/epoch_stream.py:93`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.epoch_stream')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-epoch-stream-epochbatchstream-validate-state-dict"></a>
## `ai4e_core.abilities.training.epoch_stream.EpochBatchStream.validate_state_dict`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`validate_state_dict(self, state: dict[str, Any]) -> None`
- **规范定义名**：`ai4e_core.abilities.training.epoch_stream.EpochBatchStream.validate_state_dict`

### 用途

只校验恢复声明，不修改本流、不取样；非法输入抛 ValueError。

### 导入与签名

```python
from ai4e_core.abilities.training.epoch_stream import EpochBatchStream
```

```text
validate_state_dict(self, state: dict[str, Any]) -> None
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `state` | `dict[str, Any]` | `必填` |

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
from ai4e_core.abilities.training.epoch_stream import EpochBatchStream

print(signature(EpochBatchStream.validate_state_dict))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.research_state`

### 源码位置

- 模块：`ai4e_core.abilities.training.epoch_stream`
- 仓库相对路径：`packages/ai4e-core/abilities/training/epoch_stream.py:150`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.epoch_stream')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
