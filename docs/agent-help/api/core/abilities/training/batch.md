<!-- dojo-help: {"domain": "ai4e_core.abilities.training.batch", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.training.batch 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.training.batch", "topic_id": "module:ai4e_core.abilities.training.batch"} -->
# `ai4e_core.abilities.training.batch` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-training-batch-concatenate-geometry"></a>
## `ai4e_core.abilities.training.batch.concatenate_geometry`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`concatenate_geometry(positions: list, indices: list) -> dict`
- **规范定义名**：`ai4e_core.abilities.training.batch.concatenate_geometry`

### 用途

根据各样本实际点数偏移局部索引，并生成几何批次身份。

### 导入与签名

```python
from ai4e_core.abilities.training.batch import concatenate_geometry
```

```text
concatenate_geometry(positions: list, indices: list) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `positions` | `list` | `必填` |
| `indices` | `list` | `必填` |

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
from ai4e_core.abilities.training.batch import concatenate_geometry

print(signature(concatenate_geometry))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.training.batch`
- 仓库相对路径：`packages/ai4e-core/abilities/training/batch.py:13`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.batch')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-batch-stack"></a>
## `ai4e_core.abilities.training.batch.stack`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`stack(values: list[torch.Tensor]) -> torch.Tensor`
- **规范定义名**：`ai4e_core.abilities.training.batch.stack`

### 用途

同形状数据堆叠，不自动填充。

### 导入与签名

```python
from ai4e_core.abilities.training.batch import stack
```

```text
stack(values: list[torch.Tensor]) -> torch.Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `values` | `list[torch.Tensor]` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`torch.Tensor`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.training.batch import stack

print(signature(stack))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.training.batch`
- 仓库相对路径：`packages/ai4e-core/abilities/training/batch.py:6`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.batch')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-batch-to-device"></a>
## `ai4e_core.abilities.training.batch.to_device`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`to_device(value, device)`
- **规范定义名**：`ai4e_core.abilities.training.batch.to_device`

### 用途

递归移动嵌套输入，保持浮点、整数和布尔类型，不隐式修正精度。

### 导入与签名

```python
from ai4e_core.abilities.training.batch import to_device
```

```text
to_device(value, device)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `value` | `未标注` | `必填` |
| `device` | `未标注` | `必填` |

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
from ai4e_core.abilities.training.batch import to_device

print(signature(to_device))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.training.batch`
- 仓库相对路径：`packages/ai4e-core/abilities/training/batch.py:33`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.batch')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
