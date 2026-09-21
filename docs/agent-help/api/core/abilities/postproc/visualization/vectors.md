<!-- dojo-help: {"domain": "ai4e_core.abilities.postproc.visualization.vectors", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.postproc.visualization.vectors 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.postproc.visualization.vectors", "topic_id": "module:ai4e_core.abilities.postproc.visualization.vectors"} -->
# `ai4e_core.abilities.postproc.visualization.vectors` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-postproc-visualization-vectors-glyph-mesh"></a>
## `ai4e_core.abilities.postproc.visualization.vectors.glyph_mesh`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`glyph_mesh(mesh: Any, *, field: str, association: str='point', stride: int=1, scale: float=0.1, cell_to_point: bool=False) -> Any`
- **规范定义名**：`ai4e_core.abilities.postproc.visualization.vectors.glyph_mesh`

### 用途

按固定间隔绘制箭头，保留完整矢量和独立着色数组。

### 导入与签名

```python
from ai4e_core.abilities.postproc.visualization.vectors import glyph_mesh
```

```text
glyph_mesh(mesh: Any, *, field: str, association: str='point', stride: int=1, scale: float=0.1, cell_to_point: bool=False) -> Any
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `mesh` | `Any` | `必填` |
| `field` | `str` | `必填关键字参数` |
| `association` | `str` | `'point'` |
| `stride` | `int` | `1` |
| `scale` | `float` | `0.1` |
| `cell_to_point` | `bool` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Any`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.postproc.visualization.vectors import glyph_mesh

print(signature(glyph_mesh))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.visualization.vectors`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/visualization/vectors.py:77`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.visualization.vectors')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-visualization-vectors-seed-points"></a>
## `ai4e_core.abilities.postproc.visualization.vectors.seed_points`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`seed_points(*, kind: str='line', count: int=20, start: Any=None, end: Any=None, center: Any=None, radius: float=1.0, normal: Any=(1, 0, 0), width: float=1.0, height: float=1.0, points: Any=None) -> Any`
- **规范定义名**：`ai4e_core.abilities.postproc.visualization.vectors.seed_points`

### 用途

生成确定性点、线、平面或球体种子，不消耗调用者随机流。

### 导入与签名

```python
from ai4e_core.abilities.postproc.visualization.vectors import seed_points
```

```text
seed_points(*, kind: str='line', count: int=20, start: Any=None, end: Any=None, center: Any=None, radius: float=1.0, normal: Any=(1, 0, 0), width: float=1.0, height: float=1.0, points: Any=None) -> Any
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `kind` | `str` | `'line'` |
| `count` | `int` | `20` |
| `start` | `Any` | `None` |
| `end` | `Any` | `None` |
| `center` | `Any` | `None` |
| `radius` | `float` | `1.0` |
| `normal` | `Any` | `(1, 0, 0)` |
| `width` | `float` | `1.0` |
| `height` | `float` | `1.0` |
| `points` | `Any` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Any`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.postproc.visualization.vectors import seed_points

print(signature(seed_points))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.visualization.vectors`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/visualization/vectors.py:14`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.visualization.vectors')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-visualization-vectors-streamline-mesh"></a>
## `ai4e_core.abilities.postproc.visualization.vectors.streamline_mesh`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`streamline_mesh(mesh: Any, *, field: str, seeds: Any, association: str='point', direction: str='both', length: float=1.0, step: float=0.01, max_steps: int=4000, surface: bool=False, cell_to_point: bool=False) -> Any`
- **规范定义名**：`ai4e_core.abilities.postproc.visualization.vectors.streamline_mesh`

### 用途

积分真实拓扑上的矢量场；表面模式显式投影到切平面。

### 导入与签名

```python
from ai4e_core.abilities.postproc.visualization.vectors import streamline_mesh
```

```text
streamline_mesh(mesh: Any, *, field: str, seeds: Any, association: str='point', direction: str='both', length: float=1.0, step: float=0.01, max_steps: int=4000, surface: bool=False, cell_to_point: bool=False) -> Any
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `mesh` | `Any` | `必填` |
| `field` | `str` | `必填关键字参数` |
| `seeds` | `Any` | `必填关键字参数` |
| `association` | `str` | `'point'` |
| `direction` | `str` | `'both'` |
| `length` | `float` | `1.0` |
| `step` | `float` | `0.01` |
| `max_steps` | `int` | `4000` |
| `surface` | `bool` | `False` |
| `cell_to_point` | `bool` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Any`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.postproc.visualization.vectors import streamline_mesh

print(signature(streamline_mesh))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.visualization.vectors`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/visualization/vectors.py:116`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.visualization.vectors')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
