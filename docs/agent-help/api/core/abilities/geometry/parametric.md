<!-- dojo-help: {"domain": "ai4e_core.abilities.geometry.parametric", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.geometry.parametric 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.geometry.parametric", "topic_id": "module:ai4e_core.abilities.geometry.parametric"} -->
# `ai4e_core.abilities.geometry.parametric` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-geometry-parametric-boundary-axis"></a>
## `ai4e_core.abilities.geometry.parametric.boundary_axis`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`boundary_axis(name, dimensions)`
- **规范定义名**：`ai4e_core.abilities.geometry.parametric.boundary_axis`

### 用途

命名边界到参考轴与方向；不猜测未知边界。

### 导入与签名

```python
from ai4e_core.abilities.geometry.parametric import boundary_axis
```

```text
boundary_axis(name, dimensions)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `name` | `未标注` | `必填` |
| `dimensions` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.geometry.parametric import boundary_axis

print(signature(boundary_axis))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.geometry.parametric`
- 仓库相对路径：`packages/ai4e-core/abilities/geometry/parametric.py:16`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.geometry.parametric')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-geometry-parametric-outward-normals"></a>
## `ai4e_core.abilities.geometry.parametric.outward_normals`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`outward_normals(points, boundary, mapping)`
- **规范定义名**：`ai4e_core.abilities.geometry.parametric.outward_normals`

### 用途

返回物理空间法向，列顺序为 x 或 x,y。

### 导入与签名

```python
from ai4e_core.abilities.geometry.parametric import outward_normals
```

```text
outward_normals(points, boundary, mapping)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `points` | `未标注` | `必填` |
| `boundary` | `未标注` | `必填` |
| `mapping` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.geometry.parametric import outward_normals

print(signature(outward_normals))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.geometry.parametric`
- 仓库相对路径：`packages/ai4e-core/abilities/geometry/parametric.py:26`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.geometry.parametric')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-geometry-parametric-physical-coordinates"></a>
## `ai4e_core.abilities.geometry.parametric.physical_coordinates`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`physical_coordinates(points, mapping)`
- **规范定义名**：`ai4e_core.abilities.geometry.parametric.physical_coordinates`

### 用途

输入列为 t,x 或 t,eta,xi；返回 t,X 或 t,Y,X。

### 导入与签名

```python
from ai4e_core.abilities.geometry.parametric import physical_coordinates
```

```text
physical_coordinates(points, mapping)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `points` | `未标注` | `必填` |
| `mapping` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.geometry.parametric import physical_coordinates

print(signature(physical_coordinates))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.geometry.parametric`
- 仓库相对路径：`packages/ai4e-core/abilities/geometry/parametric.py:6`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.geometry.parametric')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-geometry-parametric-validate-points"></a>
## `ai4e_core.abilities.geometry.parametric.validate_points`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`validate_points(points, bounds, names)`
- **规范定义名**：`ai4e_core.abilities.geometry.parametric.validate_points`

### 用途

校验参考域点，物理映射独立进行。

### 导入与签名

```python
from ai4e_core.abilities.geometry.parametric import validate_points
```

```text
validate_points(points, bounds, names)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `points` | `未标注` | `必填` |
| `bounds` | `未标注` | `必填` |
| `names` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.geometry.parametric import validate_points

print(signature(validate_points))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.geometry.parametric`
- 仓库相对路径：`packages/ai4e-core/abilities/geometry/parametric.py:43`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.geometry.parametric')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
