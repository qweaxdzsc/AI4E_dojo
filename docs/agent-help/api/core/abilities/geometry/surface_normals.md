<!-- dojo-help: {"domain": "ai4e_core.abilities.geometry.surface_normals", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.geometry.surface_normals 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.geometry.surface_normals", "topic_id": "module:ai4e_core.abilities.geometry.surface_normals"} -->
# `ai4e_core.abilities.geometry.surface_normals` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-geometry-surface-normals-surface-point-normals"></a>
## `ai4e_core.abilities.geometry.surface_normals.surface_point_normals`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`surface_point_normals(surface: vtkDataObject, *, epsilon: float=EPSILON) -> np.ndarray`
- **规范定义名**：`ai4e_core.abilities.geometry.surface_normals.surface_point_normals`

### 用途

兼容数组返回接口；完整门禁与有效性语义见 surface_point_normals_with_mask。

返回原点序 (N, 3)，孤立点为零；需要区分孤立点时使用带 mask 的入口。

### 导入与签名

```python
from ai4e_core.abilities.geometry.surface_normals import surface_point_normals
```

```text
surface_point_normals(surface: vtkDataObject, *, epsilon: float=EPSILON) -> np.ndarray
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `surface` | `vtkDataObject` | `必填` |
| `epsilon` | `float` | `EPSILON` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`np.ndarray`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.geometry.surface_normals import surface_point_normals

print(signature(surface_point_normals))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.geometry.surface_normals`
- 仓库相对路径：`packages/ai4e-core/abilities/geometry/surface_normals.py:75`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.geometry.surface_normals')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-geometry-surface-normals-surface-point-normals-with-mask"></a>
## `ai4e_core.abilities.geometry.surface_normals.surface_point_normals_with_mask`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`surface_point_normals_with_mask(surface: vtkDataObject, *, epsilon: float=EPSILON) -> tuple[np.ndarray, np.ndarray]`
- **规范定义名**：`ai4e_core.abilities.geometry.surface_normals.surface_point_normals_with_mask`

### 用途

返回原点序法向 (N, 3) 和 normals_valid_mask (N,)。

全部单元须为支持的二维面。只在私有表面上计算 cell normals 并转为
point normals，再按原 point ID 回贴；不以数量推断顺序。沿用 VTK
一致化和自动定向；开放表面不保证物理外向。孤立点为零且 mask=False。
面或参与面的点出现非有限/零长度法向时抛 RuntimeError；输入不变。
epsilon 必须为正有限数，保留已有两步归一化公式。

### 导入与签名

```python
from ai4e_core.abilities.geometry.surface_normals import surface_point_normals_with_mask
```

```text
surface_point_normals_with_mask(surface: vtkDataObject, *, epsilon: float=EPSILON) -> tuple[np.ndarray, np.ndarray]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `surface` | `vtkDataObject` | `必填` |
| `epsilon` | `float` | `EPSILON` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`tuple[np.ndarray, np.ndarray]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`RuntimeError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.geometry.surface_normals import surface_point_normals_with_mask

print(signature(surface_point_normals_with_mask))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.geometry.surface_normals`
- 仓库相对路径：`packages/ai4e-core/abilities/geometry/surface_normals.py:16`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.geometry.surface_normals')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
