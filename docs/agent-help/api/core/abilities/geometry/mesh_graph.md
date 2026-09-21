<!-- dojo-help: {"domain": "ai4e_core.abilities.geometry.mesh_graph", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.geometry.mesh_graph 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.geometry.mesh_graph", "topic_id": "module:ai4e_core.abilities.geometry.mesh_graph"} -->
# `ai4e_core.abilities.geometry.mesh_graph` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-geometry-mesh-graph-cells-to-edges"></a>
## `ai4e_core.abilities.geometry.mesh_graph.cells_to_edges`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`cells_to_edges(cells: torch.Tensor | list[torch.Tensor], *, bidirectional: bool=True) -> torch.Tensor`
- **规范定义名**：`ai4e_core.abilities.geometry.mesh_graph.cells_to_edges`

### 用途

从等宽或混合 VTK 单元提取单元真实边。

三角形、四边形按闭合边界取边；四面体、六面体、楔体和金字塔按
VTK 标准局部边表取边。这里不会把一个单元的所有节点两两相连，因此
六面体不会被错误变成完全图。

### 导入与签名

```python
from ai4e_core.abilities.geometry.mesh_graph import cells_to_edges
```

```text
cells_to_edges(cells: torch.Tensor | list[torch.Tensor], *, bidirectional: bool=True) -> torch.Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cells` | `torch.Tensor | list[torch.Tensor]` | `必填` |
| `bidirectional` | `bool` | `True` |

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
from ai4e_core.abilities.geometry.mesh_graph import cells_to_edges

print(signature(cells_to_edges))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.geometry.mesh_graph`
- 仓库相对路径：`packages/ai4e-core/abilities/geometry/mesh_graph.py:37`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.geometry.mesh_graph')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-geometry-mesh-graph-edge-features"></a>
## `ai4e_core.abilities.geometry.mesh_graph.edge_features`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`edge_features(positions: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor`
- **规范定义名**：`ai4e_core.abilities.geometry.mesh_graph.edge_features`

### 用途

根据节点坐标计算有向边的相对位置和欧氏距离。

### 导入与签名

```python
from ai4e_core.abilities.geometry.mesh_graph import edge_features
```

```text
edge_features(positions: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `positions` | `torch.Tensor` | `必填` |
| `edge_index` | `torch.Tensor` | `必填` |

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
from ai4e_core.abilities.geometry.mesh_graph import edge_features

print(signature(edge_features))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.geometry.mesh_graph`
- 仓库相对路径：`packages/ai4e-core/abilities/geometry/mesh_graph.py:108`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.geometry.mesh_graph')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-geometry-mesh-graph-induced-subgraph"></a>
## `ai4e_core.abilities.geometry.mesh_graph.induced_subgraph`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`induced_subgraph(edge_index: torch.Tensor, node_ids: torch.Tensor, *, node_count: int | None=None) -> tuple[torch.Tensor, torch.Tensor]`
- **规范定义名**：`ai4e_core.abilities.geometry.mesh_graph.induced_subgraph`

### 用途

按保留节点构造诱导子图，返回局部边和局部到原节点的映射。

### 导入与签名

```python
from ai4e_core.abilities.geometry.mesh_graph import induced_subgraph
```

```text
induced_subgraph(edge_index: torch.Tensor, node_ids: torch.Tensor, *, node_count: int | None=None) -> tuple[torch.Tensor, torch.Tensor]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `edge_index` | `torch.Tensor` | `必填` |
| `node_ids` | `torch.Tensor` | `必填` |
| `node_count` | `int | None` | `None` |

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
from ai4e_core.abilities.geometry.mesh_graph import induced_subgraph

print(signature(induced_subgraph))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.geometry.mesh_graph`
- 仓库相对路径：`packages/ai4e-core/abilities/geometry/mesh_graph.py:89`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.geometry.mesh_graph')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-geometry-mesh-graph-triangles-to-edges"></a>
## `ai4e_core.abilities.geometry.mesh_graph.triangles_to_edges`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`triangles_to_edges(triangles: torch.Tensor, *, bidirectional: bool=True) -> torch.Tensor`
- **规范定义名**：`ai4e_core.abilities.geometry.mesh_graph.triangles_to_edges`

### 用途

把 ``(n, 3)`` 三角形连接转换为 ``(2, e)`` 的边索引。

返回的边按字典序稳定排序，并删除同一无向边的重复项。输入只接受整型
三角形索引，不会根据点坐标猜测拓扑。

### 导入与签名

```python
from ai4e_core.abilities.geometry.mesh_graph import triangles_to_edges
```

```text
triangles_to_edges(triangles: torch.Tensor, *, bidirectional: bool=True) -> torch.Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `triangles` | `torch.Tensor` | `必填` |
| `bidirectional` | `bool` | `True` |

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
from ai4e_core.abilities.geometry.mesh_graph import triangles_to_edges

print(signature(triangles_to_edges))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.geometry.mesh_graph`
- 仓库相对路径：`packages/ai4e-core/abilities/geometry/mesh_graph.py:12`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.geometry.mesh_graph')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-geometry-mesh-graph-vtk-cell-edges"></a>
## `ai4e_core.abilities.geometry.mesh_graph.vtk_cell_edges`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`vtk_cell_edges(mesh) -> torch.Tensor`
- **规范定义名**：`ai4e_core.abilities.geometry.mesh_graph.vtk_cell_edges`

### 用途

从 VTK 数据对象的真实单元边生成稳定双向边索引。

体单元优先使用 VTK 自身的局部边定义；没有显式边的线和二维多边形按点序闭合。
本函数不解释物理域、数据集或模型名称。

### 导入与签名

```python
from ai4e_core.abilities.geometry.mesh_graph import vtk_cell_edges
```

```text
vtk_cell_edges(mesh) -> torch.Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `mesh` | `未标注` | `必填` |

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
from ai4e_core.abilities.geometry.mesh_graph import vtk_cell_edges

print(signature(vtk_cell_edges))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.geometry.mesh_graph`
- 仓库相对路径：`packages/ai4e-core/abilities/geometry/mesh_graph.py:121`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.geometry.mesh_graph')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
