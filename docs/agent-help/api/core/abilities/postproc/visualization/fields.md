<!-- dojo-help: {"domain": "ai4e_core.abilities.postproc.visualization.fields", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.postproc.visualization.fields 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.postproc.visualization.fields", "topic_id": "module:ai4e_core.abilities.postproc.visualization.fields"} -->
# `ai4e_core.abilities.postproc.visualization.fields` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-postproc-visualization-fields-derived-mesh"></a>
## `ai4e_core.abilities.postproc.visualization.fields.derived_mesh`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`derived_mesh(mesh: Any, *, operation: Any, parameters: dict) -> Any`
- **规范定义名**：`ai4e_core.abilities.postproc.visualization.fields.derived_mesh`

### 用途

标明派生实体；插值结果不得继续宣称原始点或单元身份。

### 导入与签名

```python
from ai4e_core.abilities.postproc.visualization.fields import derived_mesh
```

```text
derived_mesh(mesh: Any, *, operation: Any, parameters: dict) -> Any
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `mesh` | `Any` | `必填` |
| `operation` | `Any` | `必填关键字参数` |
| `parameters` | `dict` | `必填关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Any`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.postproc.visualization.fields import derived_mesh

print(signature(derived_mesh))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.visualization.fields`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/visualization/fields.py:77`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.visualization.fields')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-visualization-fields-field-values"></a>
## `ai4e_core.abilities.postproc.visualization.fields.field_values`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`field_values(mesh: Any, field: str, *, association: str='point', component: str | int='scalar', mask: Any=None) -> np.ndarray`
- **规范定义名**：`ai4e_core.abilities.postproc.visualization.fields.field_values`

### 用途

按归属与分量返回独立数组；有效性只过滤声明无效的实体。

### 导入与签名

```python
from ai4e_core.abilities.postproc.visualization.fields import field_values
```

```text
field_values(mesh: Any, field: str, *, association: str='point', component: str | int='scalar', mask: Any=None) -> np.ndarray
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `mesh` | `Any` | `必填` |
| `field` | `str` | `必填` |
| `association` | `str` | `'point'` |
| `component` | `str | int` | `'scalar'` |
| `mask` | `Any` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`np.ndarray`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.postproc.visualization.fields import field_values

print(signature(field_values))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.visualization.fields`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/visualization/fields.py:19`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.visualization.fields')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-visualization-fields-pyvista"></a>
## `ai4e_core.abilities.postproc.visualization.fields.pyvista`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`pyvista() -> Any`
- **规范定义名**：`ai4e_core.abilities.postproc.visualization.fields.pyvista`

### 用途

按需加载绘图库，让纯数组评价不要求安装可视化依赖。

### 导入与签名

```python
from ai4e_core.abilities.postproc.visualization.fields import pyvista
```

```text
pyvista() -> Any
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Any`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ImportError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.postproc.visualization.fields import pyvista

print(signature(pyvista))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.physical_visualization`

### 源码位置

- 模块：`ai4e_core.abilities.postproc.visualization.fields`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/visualization/fields.py:10`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.visualization.fields')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-visualization-fields-scalar-mesh"></a>
## `ai4e_core.abilities.postproc.visualization.fields.scalar_mesh`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`scalar_mesh(mesh: Any, field: str, *, association: str='point', component: str | int='scalar') -> Any`
- **规范定义名**：`ai4e_core.abilities.postproc.visualization.fields.scalar_mesh`

### 用途

返回携带专用着色数组的深拷贝，不改变原场及活动数组。

### 导入与签名

```python
from ai4e_core.abilities.postproc.visualization.fields import scalar_mesh
```

```text
scalar_mesh(mesh: Any, field: str, *, association: str='point', component: str | int='scalar') -> Any
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `mesh` | `Any` | `必填` |
| `field` | `str` | `必填` |
| `association` | `str` | `'point'` |
| `component` | `str | int` | `'scalar'` |

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
from ai4e_core.abilities.postproc.visualization.fields import scalar_mesh

print(signature(scalar_mesh))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.visualization.fields`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/visualization/fields.py:64`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.visualization.fields')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
