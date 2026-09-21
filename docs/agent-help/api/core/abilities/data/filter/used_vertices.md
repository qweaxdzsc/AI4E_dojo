<!-- dojo-help: {"domain": "ai4e_core.abilities.data.filter.used_vertices", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.data.filter.used_vertices 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.data.filter.used_vertices", "topic_id": "module:ai4e_core.abilities.data.filter.used_vertices"} -->
# `ai4e_core.abilities.data.filter.used_vertices` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-data-filter-used-vertices-resolve-cell-type"></a>
## `ai4e_core.abilities.data.filter.used_vertices.resolve_cell_type`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`resolve_cell_type(cell_type: str | int) -> int`
- **规范定义名**：`ai4e_core.abilities.data.filter.used_vertices.resolve_cell_type`

### 用途

把约定的单元类型名或 VTK 类型号解析为类型号。

Raises:
    ValueError: 类型名不认识。

### 导入与签名

```python
from ai4e_core.abilities.data.filter.used_vertices import resolve_cell_type
```

```text
resolve_cell_type(cell_type: str | int) -> int
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cell_type` | `str | int` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`int`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.filter.used_vertices import resolve_cell_type

print(signature(resolve_cell_type))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.filter.used_vertices`
- 仓库相对路径：`packages/ai4e-core/abilities/data/filter/used_vertices.py:25`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.filter.used_vertices')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-filter-used-vertices-used-vertex-mask"></a>
## `ai4e_core.abilities.data.filter.used_vertices.used_vertex_mask`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`used_vertex_mask(data: vtkDataObject, *, cell_type: str | int) -> np.ndarray`
- **规范定义名**：`ai4e_core.abilities.data.filter.used_vertices.used_vertex_mask`

### 用途

标出参与指定类型单元的顶点，不修改原对象、不删点。

所有单元必须是约定类型。点表里从未出现在任何单元中的点为无效。

Args:
    data: 已读入的 VTK 内存对象。
    cell_type: 单元类型名（如 ``quad``）或 VTK 类型号。

Returns:
    与点数等长的布尔 mask，``True`` 表示该点参与了网格。

Raises:
    TypeError: 不是带单元的数据集。
    ValueError: 没有点或单元，或存在其他类型的单元。

### 导入与签名

```python
from ai4e_core.abilities.data.filter.used_vertices import used_vertex_mask
```

```text
used_vertex_mask(data: vtkDataObject, *, cell_type: str | int) -> np.ndarray
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `data` | `vtkDataObject` | `必填` |
| `cell_type` | `str | int` | `必填关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`np.ndarray`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`TypeError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.filter.used_vertices import used_vertex_mask

print(signature(used_vertex_mask))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.filter.used_vertices`
- 仓库相对路径：`packages/ai4e-core/abilities/data/filter/used_vertices.py:40`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.filter.used_vertices')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
