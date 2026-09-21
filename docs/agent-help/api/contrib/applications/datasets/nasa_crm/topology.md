<!-- dojo-help: {"domain": "ai4e_contrib.application.datasets.nasa_crm.topology", "kind": "api", "layer": "contrib.application", "summary": "ai4e_contrib.application.datasets.nasa_crm.topology 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.application.datasets.nasa_crm.topology", "topic_id": "module:ai4e_contrib.application.datasets.nasa_crm.topology"} -->
# `ai4e_contrib.application.datasets.nasa_crm.topology` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-application-datasets-nasa-crm-topology-load-adjacency"></a>
## `ai4e_contrib.application.datasets.nasa_crm.topology.load_adjacency`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`load_adjacency(path: Path) -> list[set[int]]`
- **规范定义名**：`ai4e_contrib.application.datasets.nasa_crm.topology.load_adjacency`

### 用途

Load and validate the official symmetric NASA CRM node adjacency.

Args:
    path: ``connectivity_NASA-CRM.h5`` path.

Returns:
    One neighbor set for every surface point.

### 导入与签名

```python
from ai4e_contrib.application.datasets.nasa_crm.topology import load_adjacency
```

```text
load_adjacency(path: Path) -> list[set[int]]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `Path` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`list[set[int]]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FileNotFoundError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.application.datasets.nasa_crm.topology import load_adjacency

print(signature(load_adjacency))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.datasets.nasa_crm.topology`
- 仓库相对路径：`packages/ai4e-contrib/application/datasets/nasa_crm/topology.py:11`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.datasets.nasa_crm.topology')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-datasets-nasa-crm-topology-reconstruct-surface-topology"></a>
## `ai4e_contrib.application.datasets.nasa_crm.topology.reconstruct_surface_topology`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`reconstruct_surface_topology(path: Path) -> SurfaceTopology`
- **规范定义名**：`ai4e_contrib.application.datasets.nasa_crm.topology.reconstruct_surface_topology`

### 用途

Enumerate triangle cliques and chordless quad cycles from adjacency.

The NASA file stores graph neighbors rather than a VTK cell array. A triangle
is a three-node clique. A quad is a chordless four-cycle; excluding both
diagonals avoids treating adjacent cells as larger or triangulated faces.

Args:
    path: Official NASA CRM connectivity HDF5 path.

Returns:
    Deduplicated mixed-cell surface topology.

### 导入与签名

```python
from ai4e_contrib.application.datasets.nasa_crm.topology import reconstruct_surface_topology
```

```text
reconstruct_surface_topology(path: Path) -> SurfaceTopology
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `Path` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`SurfaceTopology`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.application.datasets.nasa_crm.topology import reconstruct_surface_topology

print(signature(reconstruct_surface_topology))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.datasets.nasa_crm.topology`
- 仓库相对路径：`packages/ai4e-contrib/application/datasets/nasa_crm/topology.py:48`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.datasets.nasa_crm.topology')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
