<!-- dojo-help: {"domain": "ai4e_core.abilities.geometry.mesh_sdf", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.geometry.mesh_sdf 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.geometry.mesh_sdf", "topic_id": "module:ai4e_core.abilities.geometry.mesh_sdf"} -->
# `ai4e_core.abilities.geometry.mesh_sdf` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-geometry-mesh-sdf-mesh-signed-distance"></a>
## `ai4e_core.abilities.geometry.mesh_sdf.mesh_signed_distance`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`mesh_signed_distance(query_points: np.ndarray, surface: vtkDataObject, *, epsilon: float=EPSILON) -> tuple[np.ndarray, np.ndarray, np.ndarray]`
- **规范定义名**：`ai4e_core.abilities.geometry.mesh_sdf.mesh_signed_distance`

### 用途

计算查询点到网格表面的有符号距离、面上最近点和方向。

必须先通过表面门禁。符号遵循输入绕序；只有朝外定向的闭合表面才可
解释为外正内负，开放表面或反向绕序不保证物理内外。
方向为 ``(查询点 - 面上最近点) / (|距离| + epsilon)``。不改写输入网格，
也不把失败降级为点到点。

Args:
    query_points: 查询点，形状 ``(N, 3)``。
    surface: 带二维面单元的表面 VTK 对象。
    epsilon: 距离为零时避免除零的偏置。

Returns:
    ``(有符号距离, 面上最近点, 方向)``，首维均为 ``N``。

### 导入与签名

```python
from ai4e_core.abilities.geometry.mesh_sdf import mesh_signed_distance
```

```text
mesh_signed_distance(query_points: np.ndarray, surface: vtkDataObject, *, epsilon: float=EPSILON) -> tuple[np.ndarray, np.ndarray, np.ndarray]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `query_points` | `np.ndarray` | `必填` |
| `surface` | `vtkDataObject` | `必填` |
| `epsilon` | `float` | `EPSILON` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`tuple[np.ndarray, np.ndarray, np.ndarray]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.geometry.mesh_sdf import mesh_signed_distance

print(signature(mesh_signed_distance))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.geometry.mesh_sdf`
- 仓库相对路径：`packages/ai4e-core/abilities/geometry/mesh_sdf.py:18`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.geometry.mesh_sdf')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
