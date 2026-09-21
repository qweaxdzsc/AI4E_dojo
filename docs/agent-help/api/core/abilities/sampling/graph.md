<!-- dojo-help: {"domain": "ai4e_core.abilities.sampling.graph", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.sampling.graph 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.sampling.graph", "topic_id": "module:ai4e_core.abilities.sampling.graph"} -->
# `ai4e_core.abilities.sampling.graph` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-sampling-graph-core-partitions"></a>
## `ai4e_core.abilities.sampling.graph.core_partitions`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`core_partitions(edge_index: torch.Tensor, node_count: int, max_nodes: int) -> list[torch.Tensor]`
- **规范定义名**：`ai4e_core.abilities.sampling.graph.core_partitions`

### 用途

按稳定 BFS 顺序划分互斥核心块，并完整覆盖全部节点。

### 导入与签名

```python
from ai4e_core.abilities.sampling.graph import core_partitions
```

```text
core_partitions(edge_index: torch.Tensor, node_count: int, max_nodes: int) -> list[torch.Tensor]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `edge_index` | `torch.Tensor` | `必填` |
| `node_count` | `int` | `必填` |
| `max_nodes` | `int` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`list[torch.Tensor]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.sampling.graph import core_partitions

print(signature(core_partitions))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.sampling.graph`
- 仓库相对路径：`packages/ai4e-core/abilities/sampling/graph.py:10`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.sampling.graph')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-sampling-graph-expand-halo"></a>
## `ai4e_core.abilities.sampling.graph.expand_halo`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`expand_halo(edge_index: torch.Tensor, core: torch.Tensor, node_count: int, hops: int) -> tuple[torch.Tensor, torch.Tensor]`
- **规范定义名**：`ai4e_core.abilities.sampling.graph.expand_halo`

### 用途

扩展指定跳数的 halo，返回子图节点和其中核心节点的布尔 mask。

### 导入与签名

```python
from ai4e_core.abilities.sampling.graph import expand_halo
```

```text
expand_halo(edge_index: torch.Tensor, core: torch.Tensor, node_count: int, hops: int) -> tuple[torch.Tensor, torch.Tensor]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `edge_index` | `torch.Tensor` | `必填` |
| `core` | `torch.Tensor` | `必填` |
| `node_count` | `int` | `必填` |
| `hops` | `int` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`tuple[torch.Tensor, torch.Tensor]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.sampling.graph import expand_halo

print(signature(expand_halo))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.sampling.graph`
- 仓库相对路径：`packages/ai4e-core/abilities/sampling/graph.py:50`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.sampling.graph')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-sampling-graph-partition-with-halo"></a>
## `ai4e_core.abilities.sampling.graph.partition_with_halo`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`partition_with_halo(edge_index: torch.Tensor, node_count: int, max_nodes: int, hops: int) -> list[dict[str, torch.Tensor]]`
- **规范定义名**：`ai4e_core.abilities.sampling.graph.partition_with_halo`

### 用途

生成核心互斥、halo 可重叠的完整图分区声明；邻接表只构造一次。

### 导入与签名

```python
from ai4e_core.abilities.sampling.graph import partition_with_halo
```

```text
partition_with_halo(edge_index: torch.Tensor, node_count: int, max_nodes: int, hops: int) -> list[dict[str, torch.Tensor]]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `edge_index` | `torch.Tensor` | `必填` |
| `node_count` | `int` | `必填` |
| `max_nodes` | `int` | `必填` |
| `hops` | `int` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`list[dict[str, torch.Tensor]]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.sampling.graph import partition_with_halo

print(signature(partition_with_halo))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.sampling.graph`
- 仓库相对路径：`packages/ai4e-core/abilities/sampling/graph.py:78`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.sampling.graph')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
