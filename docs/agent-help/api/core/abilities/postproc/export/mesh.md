<!-- dojo-help: {"domain": "ai4e_core.abilities.postproc.export.mesh", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.postproc.export.mesh 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.postproc.export.mesh", "topic_id": "module:ai4e_core.abilities.postproc.export.mesh"} -->
# `ai4e_core.abilities.postproc.export.mesh` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-postproc-export-mesh-extract-point-field"></a>
## `ai4e_core.abilities.postproc.export.mesh.extract_point_field`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`extract_point_field(data, *, kind: str, names: tuple[str, ...]=())`
- **规范定义名**：`ai4e_core.abilities.postproc.export.mesh.extract_point_field`

### 用途

从点数据取出第一个匹配场；没有则返回 ``None``，不猜单元场。

### 导入与签名

```python
from ai4e_core.abilities.postproc.export.mesh import extract_point_field
```

```text
extract_point_field(data, *, kind: str, names: tuple[str, ...]=())
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `data` | `未标注` | `必填` |
| `kind` | `str` | `必填关键字参数` |
| `names` | `tuple[str, ...]` | `()` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`TypeError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.postproc.export.mesh import extract_point_field

print(signature(extract_point_field))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.export.mesh`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/export/mesh.py:49`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.export.mesh')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-export-mesh-mesh-topology-kind"></a>
## `ai4e_core.abilities.postproc.export.mesh.mesh_topology_kind`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`mesh_topology_kind(mesh) -> str`
- **规范定义名**：`ai4e_core.abilities.postproc.export.mesh.mesh_topology_kind`

### 用途

判断网格是结构化、非结构、表面还是只有点，不猜测文件名。

结构化含图像/矩形/结构网格；有面或体单元的 PolyData 算表面；
只有独立顶点时算点云。调用方据此选择写出器，不能把点云冒充网格。

### 导入与签名

```python
from ai4e_core.abilities.postproc.export.mesh import mesh_topology_kind
```

```text
mesh_topology_kind(mesh) -> str
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `mesh` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`str`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.postproc.export.mesh import mesh_topology_kind

print(signature(mesh_topology_kind))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.export.mesh`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/export/mesh.py:28`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.export.mesh')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-export-mesh-surface-mesh-point-count"></a>
## `ai4e_core.abilities.postproc.export.mesh.surface_mesh_point_count`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`surface_mesh_point_count(source) -> int`
- **规范定义名**：`ai4e_core.abilities.postproc.export.mesh.surface_mesh_point_count`

### 用途

返回面提取后的点数；原始网格未被单元引用的点不会进入表面交付。

### 导入与签名

```python
from ai4e_core.abilities.postproc.export.mesh import surface_mesh_point_count
```

```text
surface_mesh_point_count(source) -> int
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `source` | `未标注` | `必填` |

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
from ai4e_core.abilities.postproc.export.mesh import surface_mesh_point_count

print(signature(surface_mesh_point_count))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.export.mesh`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/export/mesh.py:88`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.export.mesh')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-export-mesh-verify-mesh-outputs"></a>
## `ai4e_core.abilities.postproc.export.mesh.verify_mesh_outputs`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`verify_mesh_outputs(surface_path, volume_path, *, n_surface: int | None=None, n_volume: int | None=None, min_points: int | None=None) -> None`
- **规范定义名**：`ai4e_core.abilities.postproc.export.mesh.verify_mesh_outputs`

### 用途

验收已写网格：必须有预测场和单元；夹具对齐原点数，正式样本大于锚点数。

### 导入与签名

```python
from ai4e_core.abilities.postproc.export.mesh import verify_mesh_outputs
```

```text
verify_mesh_outputs(surface_path, volume_path, *, n_surface: int | None=None, n_volume: int | None=None, min_points: int | None=None) -> None
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `surface_path` | `未标注` | `必填` |
| `volume_path` | `未标注` | `必填` |
| `n_surface` | `int | None` | `None` |
| `n_volume` | `int | None` | `None` |
| `min_points` | `int | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`None`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`RuntimeError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.postproc.export.mesh import verify_mesh_outputs

print(signature(verify_mesh_outputs))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.export.mesh`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/export/mesh.py:107`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.export.mesh')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-export-mesh-write-surface-mesh"></a>
## `ai4e_core.abilities.postproc.export.mesh.write_surface_mesh`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`write_surface_mesh(source, pred_pressure, path, *, gt=None, overwrite: bool=False) -> Path`
- **规范定义名**：`ai4e_core.abilities.postproc.export.mesh.write_surface_mesh`

### 用途

把压力写回原始网格，抽成面网格后存为 ``.vtp``。

### 导入与签名

```python
from ai4e_core.abilities.postproc.export.mesh import write_surface_mesh
```

```text
write_surface_mesh(source, pred_pressure, path, *, gt=None, overwrite: bool=False) -> Path
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `source` | `未标注` | `必填` |
| `pred_pressure` | `未标注` | `必填` |
| `path` | `未标注` | `必填` |
| `gt` | `未标注` | `None` |
| `overwrite` | `bool` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Path`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.postproc.export.mesh import write_surface_mesh

print(signature(write_surface_mesh))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.export.mesh`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/export/mesh.py:76`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.export.mesh')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-export-mesh-write-volume-mesh"></a>
## `ai4e_core.abilities.postproc.export.mesh.write_volume_mesh`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`write_volume_mesh(source, pred_velocity, path, *, gt=None, overwrite: bool=False) -> Path`
- **规范定义名**：`ai4e_core.abilities.postproc.export.mesh.write_volume_mesh`

### 用途

把速度写回原始体积网格，保留体单元后存为 ``.vtu``。

### 导入与签名

```python
from ai4e_core.abilities.postproc.export.mesh import write_volume_mesh
```

```text
write_volume_mesh(source, pred_velocity, path, *, gt=None, overwrite: bool=False) -> Path
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `source` | `未标注` | `必填` |
| `pred_velocity` | `未标注` | `必填` |
| `path` | `未标注` | `必填` |
| `gt` | `未标注` | `None` |
| `overwrite` | `bool` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Path`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`TypeError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.postproc.export.mesh import write_volume_mesh

print(signature(write_volume_mesh))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.export.mesh`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/export/mesh.py:93`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.export.mesh')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
