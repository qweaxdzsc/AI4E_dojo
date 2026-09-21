<!-- dojo-help: {"domain": "ai4e_core.applications.aero_cfd.post.field_binding", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.aero_cfd.post.field_binding 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.aero_cfd.post.field_binding", "topic_id": "module:ai4e_core.applications.aero_cfd.post.field_binding"} -->
# `ai4e_core.applications.aero_cfd.post.field_binding` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-aero-cfd-post-field-binding-bind-mesh"></a>
## `ai4e_core.applications.aero_cfd.post.field_binding.bind_mesh`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`bind_mesh(sample: dict, *, domain: str, source_mesh: Any=None) -> Any`
- **规范定义名**：`ai4e_core.applications.aero_cfd.post.field_binding.bind_mesh`

### 用途

使用已交付网格或显式原拓扑回贴，不构建模型或猜测拓扑。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.post.field_binding import bind_mesh
```

```text
bind_mesh(sample: dict, *, domain: str, source_mesh: Any=None) -> Any
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `sample` | `dict` | `必填` |
| `domain` | `str` | `必填关键字参数` |
| `source_mesh` | `Any` | `None` |

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
from ai4e_core.applications.aero_cfd.post.field_binding import bind_mesh

print(signature(bind_mesh))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.physical_visualization`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.post.field_binding`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/post/field_binding.py:106`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.post.field_binding')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-post-field-binding-read-fields"></a>
## `ai4e_core.applications.aero_cfd.post.field_binding.read_fields`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`read_fields(reference: Any) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.post.field_binding.read_fields`

### 用途

读回一个固定样本或拷贝内存快照，验证身份、形状及有效性。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.post.field_binding import read_fields
```

```text
read_fields(reference: Any) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `reference` | `Any` | `必填` |

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
from ai4e_core.applications.aero_cfd.post.field_binding import read_fields

print(signature(read_fields))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.physical_visualization`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.post.field_binding`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/post/field_binding.py:21`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.post.field_binding')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-post-field-binding-select-field"></a>
## `ai4e_core.applications.aero_cfd.post.field_binding.select_field`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`select_field(sample: dict, selection: Any) -> tuple`
- **规范定义名**：`ai4e_core.applications.aero_cfd.post.field_binding.select_field`

### 用途

解析领域、字段和显示类型；返回已绑定的实际数组名。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.post.field_binding import select_field
```

```text
select_field(sample: dict, selection: Any) -> tuple
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `sample` | `dict` | `必填` |
| `selection` | `Any` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`tuple`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.post.field_binding import select_field

print(signature(select_field))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.post.field_binding`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/post/field_binding.py:95`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.post.field_binding')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-post-field-binding-verify-source"></a>
## `ai4e_core.applications.aero_cfd.post.field_binding.verify_source`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`verify_source(sample: dict) -> None`
- **规范定义名**：`ai4e_core.applications.aero_cfd.post.field_binding.verify_source`

### 用途

写出前再次验证固定来源，防止读写期间来源发生变化。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.post.field_binding import verify_source
```

```text
verify_source(sample: dict) -> None
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `sample` | `dict` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`None`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.post.field_binding import verify_source

print(signature(verify_source))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.post.field_binding`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/post/field_binding.py:88`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.post.field_binding')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
