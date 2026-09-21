<!-- dojo-help: {"domain": "ai4e_core.applications.aero_cfd.post.field_analysis", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.aero_cfd.post.field_analysis 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.aero_cfd.post.field_analysis", "topic_id": "module:ai4e_core.applications.aero_cfd.post.field_analysis"} -->
# `ai4e_core.applications.aero_cfd.post.field_analysis` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-aero-cfd-post-field-analysis-clip-field"></a>
## `ai4e_core.applications.aero_cfd.post.field_analysis.clip_field`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`clip_field(mesh: Any, *, origin: Any, normal: Any, keep: str='positive', operation: Any=None) -> Any`
- **规范定义名**：`ai4e_core.applications.aero_cfd.post.field_analysis.clip_field`

### 用途

剖切领域网格。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.post.field_analysis import clip_field
```

```text
clip_field(mesh: Any, *, origin: Any, normal: Any, keep: str='positive', operation: Any=None) -> Any
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `mesh` | `Any` | `必填` |
| `origin` | `Any` | `必填关键字参数` |
| `normal` | `Any` | `必填关键字参数` |
| `keep` | `str` | `'positive'` |
| `operation` | `Any` | `None` |

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
from ai4e_core.applications.aero_cfd.post.field_analysis import clip_field

print(signature(clip_field))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.geotransolver_aero`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.post.field_analysis`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/post/field_analysis.py:47`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.post.field_analysis')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-post-field-analysis-contour-field"></a>
## `ai4e_core.applications.aero_cfd.post.field_analysis.contour_field`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`contour_field(mesh: Any, *, field: str, operation: Any=None, **parameters: Any) -> Any`
- **规范定义名**：`ai4e_core.applications.aero_cfd.post.field_analysis.contour_field`

### 用途

提取指定物理场等值。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.post.field_analysis import contour_field
```

```text
contour_field(mesh: Any, *, field: str, operation: Any=None, **parameters: Any) -> Any
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `mesh` | `Any` | `必填` |
| `field` | `str` | `必填关键字参数` |
| `operation` | `Any` | `None` |
| `**parameters` | `Any` | `可变关键字参数` |

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
from ai4e_core.applications.aero_cfd.post.field_analysis import contour_field

print(signature(contour_field))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.geotransolver_aero`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.post.field_analysis`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/post/field_analysis.py:56`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.post.field_analysis')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-post-field-analysis-mesh-field"></a>
## `ai4e_core.applications.aero_cfd.post.field_analysis.mesh_field`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`mesh_field(mesh: Any, field: str) -> str`
- **规范定义名**：`ai4e_core.applications.aero_cfd.post.field_analysis.mesh_field`

### 用途

将领域字段选择映射到网格数组，拒绝跨域错绑。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.post.field_analysis import mesh_field
```

```text
mesh_field(mesh: Any, field: str) -> str
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `mesh` | `Any` | `必填` |
| `field` | `str` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`str`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.post.field_analysis import mesh_field

print(signature(mesh_field))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.post.field_analysis`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/post/field_analysis.py:30`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.post.field_analysis')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-post-field-analysis-probe-field"></a>
## `ai4e_core.applications.aero_cfd.post.field_analysis.probe_field`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`probe_field(mesh: Any, *, fields: Any, operation: Any=None, **parameters: Any) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.post.field_analysis.probe_field`

### 用途

在显式位置采样物理场，域外位置保留无效标记。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.post.field_analysis import probe_field
```

```text
probe_field(mesh: Any, *, fields: Any, operation: Any=None, **parameters: Any) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `mesh` | `Any` | `必填` |
| `fields` | `Any` | `必填关键字参数` |
| `operation` | `Any` | `None` |
| `**parameters` | `Any` | `可变关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.post.field_analysis import probe_field

print(signature(probe_field))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.post.field_analysis`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/post/field_analysis.py:87`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.post.field_analysis')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-post-field-analysis-profile-field"></a>
## `ai4e_core.applications.aero_cfd.post.field_analysis.profile_field`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`profile_field(mesh: Any, *, fields: Any, operation: Any=None, **parameters: Any) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.post.field_analysis.profile_field`

### 用途

沿线采样所选物理场。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.post.field_analysis import profile_field
```

```text
profile_field(mesh: Any, *, fields: Any, operation: Any=None, **parameters: Any) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `mesh` | `Any` | `必填` |
| `fields` | `Any` | `必填关键字参数` |
| `operation` | `Any` | `None` |
| `**parameters` | `Any` | `可变关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.post.field_analysis import profile_field

print(signature(profile_field))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.geotransolver_aero`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.post.field_analysis`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/post/field_analysis.py:80`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.post.field_analysis')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-post-field-analysis-region-statistics"></a>
## `ai4e_core.applications.aero_cfd.post.field_analysis.region_statistics`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`region_statistics(mesh: Any, *, field: str, component: str | int='scalar', association: str='point', operation: Any=None) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.post.field_analysis.region_statistics`

### 用途

计算派生域统计，保留变换与插值口径。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.post.field_analysis import region_statistics
```

```text
region_statistics(mesh: Any, *, field: str, component: str | int='scalar', association: str='point', operation: Any=None) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `mesh` | `Any` | `必填` |
| `field` | `str` | `必填关键字参数` |
| `component` | `str | int` | `'scalar'` |
| `association` | `str` | `'point'` |
| `operation` | `Any` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.post.field_analysis import region_statistics

print(signature(region_statistics))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.geotransolver_aero`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.post.field_analysis`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/post/field_analysis.py:94`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.post.field_analysis')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-post-field-analysis-slice-field"></a>
## `ai4e_core.applications.aero_cfd.post.field_analysis.slice_field`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`slice_field(mesh: Any, *, origin: Any, normal: Any, operation: Any=None) -> Any`
- **规范定义名**：`ai4e_core.applications.aero_cfd.post.field_analysis.slice_field`

### 用途

按物理平面切片，可注入替换计算函数。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.post.field_analysis import slice_field
```

```text
slice_field(mesh: Any, *, origin: Any, normal: Any, operation: Any=None) -> Any
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `mesh` | `Any` | `必填` |
| `origin` | `Any` | `必填关键字参数` |
| `normal` | `Any` | `必填关键字参数` |
| `operation` | `Any` | `None` |

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
from ai4e_core.applications.aero_cfd.post.field_analysis import slice_field

print(signature(slice_field))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.geotransolver_aero`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.post.field_analysis`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/post/field_analysis.py:40`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.post.field_analysis')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-post-field-analysis-streamlines"></a>
## `ai4e_core.applications.aero_cfd.post.field_analysis.streamlines`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`streamlines(mesh: Any, *, field: str, operation: Any=None, **parameters: Any) -> Any`
- **规范定义名**：`ai4e_core.applications.aero_cfd.post.field_analysis.streamlines`

### 用途

从显式种子积分物理流线。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.post.field_analysis import streamlines
```

```text
streamlines(mesh: Any, *, field: str, operation: Any=None, **parameters: Any) -> Any
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `mesh` | `Any` | `必填` |
| `field` | `str` | `必填关键字参数` |
| `operation` | `Any` | `None` |
| `**parameters` | `Any` | `可变关键字参数` |

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
from ai4e_core.applications.aero_cfd.post.field_analysis import streamlines

print(signature(streamlines))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.geotransolver_aero`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.post.field_analysis`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/post/field_analysis.py:72`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.post.field_analysis')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-post-field-analysis-vector-field"></a>
## `ai4e_core.applications.aero_cfd.post.field_analysis.vector_field`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`vector_field(mesh: Any, *, field: str, operation: Any=None, **parameters: Any) -> Any`
- **规范定义名**：`ai4e_core.applications.aero_cfd.post.field_analysis.vector_field`

### 用途

绘制完整三分量物理矢量。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.post.field_analysis import vector_field
```

```text
vector_field(mesh: Any, *, field: str, operation: Any=None, **parameters: Any) -> Any
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `mesh` | `Any` | `必填` |
| `field` | `str` | `必填关键字参数` |
| `operation` | `Any` | `None` |
| `**parameters` | `Any` | `可变关键字参数` |

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
from ai4e_core.applications.aero_cfd.post.field_analysis import vector_field

print(signature(vector_field))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.geotransolver_aero`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.post.field_analysis`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/post/field_analysis.py:64`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.post.field_analysis')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
