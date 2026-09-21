<!-- dojo-help: {"domain": "ai4e_core.abilities.postproc.comparison", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.postproc.comparison 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.postproc.comparison", "topic_id": "module:ai4e_core.abilities.postproc.comparison"} -->
# `ai4e_core.abilities.postproc.comparison` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-postproc-comparison-attach-valid-mesh"></a>
## `ai4e_core.abilities.postproc.comparison.attach_valid_mesh`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`attach_valid_mesh(mesh, points, arrays, *, source_ids=None)`
- **规范定义名**：`ai4e_core.abilities.postproc.comparison.attach_valid_mesh`

### 用途

仅保留所有顶点均有真实预测的单元，过滤区不补零。

### 导入与签名

```python
from ai4e_core.abilities.postproc.comparison import attach_valid_mesh
```

```text
attach_valid_mesh(mesh, points, arrays, *, source_ids=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `mesh` | `未标注` | `必填` |
| `points` | `未标注` | `必填` |
| `arrays` | `未标注` | `必填` |
| `source_ids` | `未标注` | `None` |

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
from ai4e_core.abilities.postproc.comparison import attach_valid_mesh

print(signature(attach_valid_mesh))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.comparison`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/comparison.py:28`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.comparison')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-comparison-cut-plane"></a>
## `ai4e_core.abilities.postproc.comparison.cut_plane`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`cut_plane(mesh, *, axis, fraction)`
- **规范定义名**：`ai4e_core.abilities.postproc.comparison.cut_plane`

### 用途

物理包围盒内定位，VTK 对同一拓扑同时插值真值和全部预测。

### 导入与签名

```python
from ai4e_core.abilities.postproc.comparison import cut_plane
```

```text
cut_plane(mesh, *, axis, fraction)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `mesh` | `未标注` | `必填` |
| `axis` | `未标注` | `必填关键字参数` |
| `fraction` | `未标注` | `必填关键字参数` |

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
from ai4e_core.abilities.postproc.comparison import cut_plane

print(signature(cut_plane))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.comparison`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/comparison.py:76`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.comparison')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-comparison-match-points"></a>
## `ai4e_core.abilities.postproc.comparison.match_points`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`match_points(points, source_points)`
- **规范定义名**：`ai4e_core.abilities.postproc.comparison.match_points`

### 用途

在 PT 保存精度下精确匹配原点；歧义、遗漏或重复均拒绝。

### 导入与签名

```python
from ai4e_core.abilities.postproc.comparison import match_points
```

```text
match_points(points, source_points)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `points` | `未标注` | `必填` |
| `source_points` | `未标注` | `必填` |

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
from ai4e_core.abilities.postproc.comparison import match_points

print(signature(match_points))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.comparison`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/comparison.py:8`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.comparison')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-comparison-surface"></a>
## `ai4e_core.abilities.postproc.comparison.surface`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`surface(mesh)`
- **规范定义名**：`ai4e_core.abilities.postproc.comparison.surface`

### 用途

保留已装配场量并提取可渲染表面。

### 导入与签名

```python
from ai4e_core.abilities.postproc.comparison import surface
```

```text
surface(mesh)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `mesh` | `未标注` | `必填` |

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
from ai4e_core.abilities.postproc.comparison import surface

print(signature(surface))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.inference_fields`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.abilities.postproc.comparison`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/comparison.py:106`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.comparison')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-comparison-write-polydata"></a>
## `ai4e_core.abilities.postproc.comparison.write_polydata`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`write_polydata(path, mesh)`
- **规范定义名**：`ai4e_core.abilities.postproc.comparison.write_polydata`

### 用途

通过数据保存事务输出稳定 VTP，供独立 viz 读取。

### 导入与签名

```python
from ai4e_core.abilities.postproc.comparison import write_polydata
```

```text
write_polydata(path, mesh)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `未标注` | `必填` |
| `mesh` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`OSError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.postproc.comparison import write_polydata

print(signature(write_polydata))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.comparison`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/comparison.py:116`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.comparison')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
