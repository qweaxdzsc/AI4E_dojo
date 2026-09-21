<!-- dojo-help: {"domain": "ai4e_core.abilities.postproc.surface_geometry", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.postproc.surface_geometry 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.postproc.surface_geometry", "topic_id": "module:ai4e_core.abilities.postproc.surface_geometry"} -->
# `ai4e_core.abilities.postproc.surface_geometry` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-postproc-surface-geometry-surfacetopology"></a>
## `ai4e_core.abilities.postproc.surface_geometry.SurfaceTopology`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`class SurfaceTopology`
- **规范定义名**：`ai4e_core.abilities.postproc.surface_geometry.SurfaceTopology`

### 用途

Mixed triangle/quad topology reconstructed from node adjacency.

### 导入与签名

```python
from ai4e_core.abilities.postproc.surface_geometry import SurfaceTopology
```

```text
class SurfaceTopology
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

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
from ai4e_core.abilities.postproc.surface_geometry import SurfaceTopology

print(signature(SurfaceTopology))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.surface_geometry`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/surface_geometry.py:9`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.surface_geometry')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-surface-geometry-surfacetopology-euler-characteristic"></a>
## `ai4e_core.abilities.postproc.surface_geometry.SurfaceTopology.euler_characteristic`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`euler_characteristic(self) -> int`
- **规范定义名**：`ai4e_core.abilities.postproc.surface_geometry.SurfaceTopology.euler_characteristic`

### 用途

Return ``V - E + F`` for topology diagnostics.

### 导入与签名

```python
from ai4e_core.abilities.postproc.surface_geometry import SurfaceTopology
```

```text
euler_characteristic(self) -> int
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
from ai4e_core.abilities.postproc.surface_geometry import SurfaceTopology

print(signature(SurfaceTopology.euler_characteristic))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.surface_geometry`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/surface_geometry.py:23`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.surface_geometry')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-surface-geometry-surfacetopology-face-count"></a>
## `ai4e_core.abilities.postproc.surface_geometry.SurfaceTopology.face_count`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`face_count(self) -> int`
- **规范定义名**：`ai4e_core.abilities.postproc.surface_geometry.SurfaceTopology.face_count`

### 用途

Return the number of reconstructed surface cells.

### 导入与签名

```python
from ai4e_core.abilities.postproc.surface_geometry import SurfaceTopology
```

```text
face_count(self) -> int
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
from ai4e_core.abilities.postproc.surface_geometry import SurfaceTopology

print(signature(SurfaceTopology.face_count))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.surface_geometry`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/surface_geometry.py:18`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.surface_geometry')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-surface-geometry-orient-topology"></a>
## `ai4e_core.abilities.postproc.surface_geometry.orient_topology`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`orient_topology(topology: SurfaceTopology, points: np.ndarray, normals: np.ndarray) -> SurfaceTopology`
- **规范定义名**：`ai4e_core.abilities.postproc.surface_geometry.orient_topology`

### 用途

Orient every face to agree with the supplied NASA nodal normals.

### 导入与签名

```python
from ai4e_core.abilities.postproc.surface_geometry import orient_topology
```

```text
orient_topology(topology: SurfaceTopology, points: np.ndarray, normals: np.ndarray) -> SurfaceTopology
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `topology` | `SurfaceTopology` | `必填` |
| `points` | `np.ndarray` | `必填` |
| `normals` | `np.ndarray` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`SurfaceTopology`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.postproc.surface_geometry import orient_topology

print(signature(orient_topology))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.surface_geometry`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/surface_geometry.py:64`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.surface_geometry')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-surface-geometry-surface-area-ratio"></a>
## `ai4e_core.abilities.postproc.surface_geometry.surface_area_ratio`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`surface_area_ratio(topology: SurfaceTopology, points: np.ndarray, nodal_area: np.ndarray) -> float`
- **规范定义名**：`ai4e_core.abilities.postproc.surface_geometry.surface_area_ratio`

### 用途

Compare reconstructed polygon area with the provided NASA nodal-area sum.

### 导入与签名

```python
from ai4e_core.abilities.postproc.surface_geometry import surface_area_ratio
```

```text
surface_area_ratio(topology: SurfaceTopology, points: np.ndarray, nodal_area: np.ndarray) -> float
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `topology` | `SurfaceTopology` | `必填` |
| `points` | `np.ndarray` | `必填` |
| `nodal_area` | `np.ndarray` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`float`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.postproc.surface_geometry import surface_area_ratio

print(signature(surface_area_ratio))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.surface_geometry`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/surface_geometry.py:28`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.surface_geometry')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
