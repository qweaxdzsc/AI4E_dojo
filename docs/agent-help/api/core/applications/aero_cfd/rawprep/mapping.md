<!-- dojo-help: {"domain": "ai4e_core.applications.aero_cfd.rawprep.mapping", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.aero_cfd.rawprep.mapping 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.aero_cfd.rawprep.mapping", "topic_id": "module:ai4e_core.applications.aero_cfd.rawprep.mapping"} -->
# `ai4e_core.applications.aero_cfd.rawprep.mapping` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-aero-cfd-rawprep-mapping-fieldmapparameters"></a>
## `ai4e_core.applications.aero_cfd.rawprep.mapping.FieldMapParameters`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`class FieldMapParameters`
- **规范定义名**：`ai4e_core.applications.aero_cfd.rawprep.mapping.FieldMapParameters`

### 用途

字段映射配置；输出按 entity_like 保留原始行身份，不允许隐式筛选。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.rawprep.mapping import FieldMapParameters
```

```text
class FieldMapParameters
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`FieldMapParameters`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.rawprep.mapping import FieldMapParameters

print(signature(FieldMapParameters))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.field_mapping`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.rawprep.mapping`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/rawprep/mapping.py:20`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.rawprep.mapping')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-rawprep-mapping-map-fields"></a>
## `ai4e_core.applications.aero_cfd.rawprep.mapping.map_fields`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`map_fields(data, *, name: str, inputs, outputs, operation=None, target=None, parameters=None)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.rawprep.mapping.map_fields`

### 用途

登记普通数组函数；输出继承原实体身份，新逻辑字段可直接选择和保存。

输入是原 VTK 顺序的只读数组。函数必须逐行保序返回具名数组；需要改变实体
集合时使用专门的同步筛选步骤。不能从返回数组数值猜测实体排列。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.rawprep.mapping import map_fields
```

```text
map_fields(data, *, name: str, inputs, outputs, operation=None, target=None, parameters=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `data` | `未标注` | `必填` |
| `name` | `str` | `必填关键字参数` |
| `inputs` | `未标注` | `必填关键字参数` |
| `outputs` | `未标注` | `必填关键字参数` |
| `operation` | `未标注` | `None` |
| `target` | `未标注` | `None` |
| `parameters` | `未标注` | `None` |

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
from ai4e_core.applications.aero_cfd.rawprep.mapping import map_fields

print(signature(map_fields))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.field_mapping`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.rawprep.mapping`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/rawprep/mapping.py:59`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.rawprep.mapping')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
