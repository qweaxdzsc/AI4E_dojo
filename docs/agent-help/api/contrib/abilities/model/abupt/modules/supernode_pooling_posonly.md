<!-- dojo-help: {"domain": "ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly", "topic_id": "module:ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly"} -->
# `ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-model-abupt-modules-supernode-pooling-posonly-supernodepoolingposonly"></a>
## `ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly.SupernodePoolingPosonly`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`SupernodePoolingPosonly(hidden_dim: int, ndim: int, radius: float | None=None, k: int | None=None, max_degree: int=32, mode: str='relpos')`
- **规范定义名**：`ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly.SupernodePoolingPosonly`

### 用途

Supernode pooling layer.

The permutation of the supernodes is preserved through the message passing (contrary to the (GP-)UPT code).
Additionally, radius is used instead of radius_graph, which is more efficient.

Args:
    radius: Radius around each supernode. From points within this radius, messages are passed to the supernode.
    k: Numer of neighbors for each supernode. From the k-NN points, messages are passed to the supernode.
    hidden_dim: Hidden dimension for positional embeddings, messages and the resulting output vector.
    ndim: Number of positional dimension (e.g., ndim=2 for a 2D position, ndim=3 for a 3D position)
    max_degree: Maximum degree of the radius graph. Defaults to 32.
    mode: Are positions embedded in absolute space ("abspos") or relative space ("relpos").
        "readd_supernode_pos" will always use the absolute position.
    readd_supernode_pos: If true, the absolute positional encoding of the supernode is concated to the
      supernode vector after message passing and linearly projected back to hidden_dim. Defaults to True.

### 导入与签名

```python
from ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly import SupernodePoolingPosonly
```

```text
SupernodePoolingPosonly(hidden_dim: int, ndim: int, radius: float | None=None, k: int | None=None, max_degree: int=32, mode: str='relpos')
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `hidden_dim` | `int` | `必填` |
| `ndim` | `int` | `必填` |
| `radius` | `float | None` | `None` |
| `k` | `int | None` | `None` |
| `max_degree` | `int` | `32` |
| `mode` | `str` | `'relpos'` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`SupernodePoolingPosonly`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`NotImplementedError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly import SupernodePoolingPosonly

print(signature(SupernodePoolingPosonly))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/abupt/modules/supernode_pooling_posonly.py:27`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-abupt-modules-supernode-pooling-posonly-supernodepoolingposonly-accumulate-messages"></a>
## `ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly.SupernodePoolingPosonly.accumulate_messages`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`accumulate_messages(x: torch.Tensor, dst_idx: torch.Tensor, supernode_idx: torch.Tensor, batch_idx: torch.Tensor | None=None) -> tuple[torch.Tensor, int]`
- **规范定义名**：`ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly.SupernodePoolingPosonly.accumulate_messages`

### 用途

Method the accumulate the messages of neighbouring points into the supernodes.

Args:
    x: Tensor containing the message representation of each neighbour representation.
    dst_idx: Index of the destination (i.e., supernode) where each message should go to.
    supernode_idx: Indexes of the supernode in the input point cloud.
    batch_idx: Batch index of the points in the sparse tensor.

Returns:
    Tensor with the aggregated messages for each supernode.

### 导入与签名

```python
from ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly import SupernodePoolingPosonly
```

```text
accumulate_messages(x: torch.Tensor, dst_idx: torch.Tensor, supernode_idx: torch.Tensor, batch_idx: torch.Tensor | None=None) -> tuple[torch.Tensor, int]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `torch.Tensor` | `必填` |
| `dst_idx` | `torch.Tensor` | `必填` |
| `supernode_idx` | `torch.Tensor` | `必填` |
| `batch_idx` | `torch.Tensor | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`tuple[torch.Tensor, int]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly import SupernodePoolingPosonly

print(signature(SupernodePoolingPosonly.accumulate_messages))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/abupt/modules/supernode_pooling_posonly.py:183`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-abupt-modules-supernode-pooling-posonly-supernodepoolingposonly-compute-src-and-dst-indices"></a>
## `ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly.SupernodePoolingPosonly.compute_src_and_dst_indices`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`compute_src_and_dst_indices(self, input_pos: torch.Tensor, supernode_idx: torch.Tensor, batch_idx: torch.Tensor | None=None) -> tuple[torch.Tensor, torch.Tensor]`
- **规范定义名**：`ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly.SupernodePoolingPosonly.compute_src_and_dst_indices`

### 用途

Compute the source and destination indices for the message passing to the supernodes.

Args:
    input_pos: Sparse tensor with shape (batch_size * numner of points, 3), representing the input geometries.
    supernode_idx: Indexes of the supernodes in the sparse tensor input_pos.
    batch_idx: 1D tensor, containing the batch index of each entry in input_pos. Default None.

Returns:
    Tensor with src and destination indexes for the message passing into the supernodes.

### 导入与签名

```python
from ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly import SupernodePoolingPosonly
```

```text
compute_src_and_dst_indices(self, input_pos: torch.Tensor, supernode_idx: torch.Tensor, batch_idx: torch.Tensor | None=None) -> tuple[torch.Tensor, torch.Tensor]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `input_pos` | `torch.Tensor` | `必填` |
| `supernode_idx` | `torch.Tensor` | `必填` |
| `batch_idx` | `torch.Tensor | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`tuple[torch.Tensor, torch.Tensor]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`NotImplementedError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly import SupernodePoolingPosonly

print(signature(SupernodePoolingPosonly.compute_src_and_dst_indices))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/abupt/modules/supernode_pooling_posonly.py:88`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-abupt-modules-supernode-pooling-posonly-supernodepoolingposonly-create-messages"></a>
## `ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly.SupernodePoolingPosonly.create_messages`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`create_messages(self, input_pos: torch.Tensor, src_idx: torch.Tensor, dst_idx: torch.Tensor, supernode_idx: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]`
- **规范定义名**：`ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly.SupernodePoolingPosonly.create_messages`

### 用途

Create messages for the message passing to the supernodes, based on different positional encoding
representations.

Args:
    input_pos: Tensor of shape (batch_size * number_of_points_per_sample, {2,3}), representing the point cloud
        representation of the input geometry.
    src_idx: Index of the source nodes from input_pos.
    dst_idx: Source index of the destination nodes from input_pos tensor. These indexes should be the matching
        supernode indexes.
    supernode_idx: Indexes of the node in input_pos that are considered supernodes.

Raises:
    NotImplementedError: Raised if the mode is not implemented. Either "abspos" or "relpos" are allowed.

Returns:
    Tensor with messages for the message passing into the super nodes and the embedding coordinates of the
        supernodes.

### 导入与签名

```python
from ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly import SupernodePoolingPosonly
```

```text
create_messages(self, input_pos: torch.Tensor, src_idx: torch.Tensor, dst_idx: torch.Tensor, supernode_idx: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `input_pos` | `torch.Tensor` | `必填` |
| `src_idx` | `torch.Tensor` | `必填` |
| `dst_idx` | `torch.Tensor` | `必填` |
| `supernode_idx` | `torch.Tensor` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`tuple[torch.Tensor, torch.Tensor]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`NotImplementedError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly import SupernodePoolingPosonly

print(signature(SupernodePoolingPosonly.create_messages))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/abupt/modules/supernode_pooling_posonly.py:139`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-abupt-modules-supernode-pooling-posonly-supernodepoolingposonly-forward"></a>
## `ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly.SupernodePoolingPosonly.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, input_pos: torch.Tensor, supernode_idx: torch.Tensor, batch_idx: torch.Tensor | None=None) -> torch.Tensor`
- **规范定义名**：`ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly.SupernodePoolingPosonly.forward`

### 用途

Forward pass of the supernode pooling layer.

Args:
    input_pos: Sparse tensor with shape (batch_size * number_of_points_per_sample, 3), representing the point
        cloud representation of the input geometry.
    supernode_idx: indexes of the supernodes in the sparse tensor input_pos.
    batch_idx: 1D tensor, containing the batch index of each entry in input_pos. Default None.

Returns:
    Tensor with the aggregated messages for each supernode.

### 导入与签名

```python
from ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly import SupernodePoolingPosonly
```

```text
forward(self, input_pos: torch.Tensor, supernode_idx: torch.Tensor, batch_idx: torch.Tensor | None=None) -> torch.Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `input_pos` | `torch.Tensor` | `必填` |
| `supernode_idx` | `torch.Tensor` | `必填` |
| `batch_idx` | `torch.Tensor | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`torch.Tensor`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly import SupernodePoolingPosonly

print(signature(SupernodePoolingPosonly.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/abupt/modules/supernode_pooling_posonly.py:218`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.abupt.modules.supernode_pooling_posonly')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
