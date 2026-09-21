<!-- dojo-help: {"domain": "ai4e_core.abilities.geometry.surface", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.geometry.surface 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.geometry.surface", "topic_id": "module:ai4e_core.abilities.geometry.surface"} -->
# `ai4e_core.abilities.geometry.surface` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-geometry-surface-preparedsurface"></a>
## `ai4e_core.abilities.geometry.surface.PreparedSurface`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`class PreparedSurface`
- **规范定义名**：`ai4e_core.abilities.geometry.surface.PreparedSurface`

### 用途

与输入存储独立的表面，以及原点数和面参与标记。

### 导入与签名

```python
from ai4e_core.abilities.geometry.surface import PreparedSurface
```

```text
class PreparedSurface
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`PreparedSurface`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.geometry.surface import PreparedSurface

print(signature(PreparedSurface))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.geometry.surface`
- 仓库相对路径：`packages/ai4e-core/abilities/geometry/surface.py:22`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.geometry.surface')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-geometry-surface-prepare-surface"></a>
## `ai4e_core.abilities.geometry.surface.prepare_surface`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`prepare_surface(data: vtkDataObject) -> PreparedSurface`
- **规范定义名**：`ai4e_core.abilities.geometry.surface.prepare_surface`

### 用途

验证并转换私有表面副本，携带原 point ID，不继承调用方旧法向。

几何计算不需要物理场；工作副本清除属性后仅添加身份数组，避免
VTK 复用已有 Normals 或同名身份字段。原始对象的所有属性不变。

### 导入与签名

```python
from ai4e_core.abilities.geometry.surface import prepare_surface
```

```text
prepare_surface(data: vtkDataObject) -> PreparedSurface
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `data` | `vtkDataObject` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`PreparedSurface`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`RuntimeError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.geometry.surface import prepare_surface

print(signature(prepare_surface))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.geometry.surface`
- 仓库相对路径：`packages/ai4e-core/abilities/geometry/surface.py:52`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.geometry.surface')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-geometry-surface-require-surface-mesh"></a>
## `ai4e_core.abilities.geometry.surface.require_surface_mesh`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`require_surface_mesh(data: vtkDataObject) -> vtkDataSet`
- **规范定义名**：`ai4e_core.abilities.geometry.surface.require_surface_mesh`

### 用途

要求非空 VTK 网格的全部单元均为支持的二维面；不提取体外壳。

允许混合面类型和弯曲、开放表面。首次遇到点、线、体或不支持的
面类型即抛 ValueError，并报告原单元编号与类型。输入不会被修改。

### 导入与签名

```python
from ai4e_core.abilities.geometry.surface import require_surface_mesh
```

```text
require_surface_mesh(data: vtkDataObject) -> vtkDataSet
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `data` | `vtkDataObject` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`vtkDataSet`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.geometry.surface import require_surface_mesh

print(signature(require_surface_mesh))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.geometry.surface`
- 仓库相对路径：`packages/ai4e-core/abilities/geometry/surface.py:30`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.geometry.surface')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
