<!-- dojo-help: {"domain": "ai4e_core.applications.aero_cfd.trainprep.pointfields", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.aero_cfd.trainprep.pointfields 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.aero_cfd.trainprep.pointfields", "topic_id": "module:ai4e_core.applications.aero_cfd.trainprep.pointfields"} -->
# `ai4e_core.applications.aero_cfd.trainprep.pointfields` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-pointfields-pointdataset"></a>
## `ai4e_core.applications.aero_cfd.trainprep.pointfields.PointDataset`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`PointDataset(view, normalization, split, *, training=False)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.pointfields.PointDataset`

### 用途

训练一次访问一个样本；验证每个访问对应一个完整分块。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.pointfields import PointDataset
```

```text
PointDataset(view, normalization, split, *, training=False)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `view` | `未标注` | `必填` |
| `normalization` | `未标注` | `必填` |
| `split` | `未标注` | `必填` |
| `training` | `未标注` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`PointDataset`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.pointfields import PointDataset

print(signature(PointDataset))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.pointfields`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/pointfields.py:26`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.pointfields')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-pointfields-collate"></a>
## `ai4e_core.applications.aero_cfd.trainprep.pointfields.collate`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`collate(items)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.pointfields.collate`

### 用途

参考批次严格为一；完整保留计算项身份。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.pointfields import collate
```

```text
collate(items)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `items` | `未标注` | `必填` |

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
from ai4e_core.applications.aero_cfd.trainprep.pointfields import collate

print(signature(collate))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.shapenet_car_abupt`, `recipe_extensions.field_mapping`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.pointfields`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/pointfields.py:72`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.pointfields')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-pointfields-features"></a>
## `ai4e_core.applications.aero_cfd.trainprep.pointfields.features`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`features(raw, normalization)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.pointfields.features`

### 用途

坐标、法向和广播工况按有序输入契约拼接。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.pointfields import features
```

```text
features(raw, normalization)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `raw` | `未标注` | `必填` |
| `normalization` | `未标注` | `必填` |

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
from ai4e_core.applications.aero_cfd.trainprep.pointfields import features

print(signature(features))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.free_wiring`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.pointfields`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/pointfields.py:17`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.pointfields')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-pointfields-open-preparation"></a>
## `ai4e_core.applications.aero_cfd.trainprep.pointfields.open_preparation`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`open_preparation(config, component, reference=None, *, validate=True)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.pointfields.open_preparation`

### 用途

打开数据视图并验证冻结记录；内容变化不能靠旧文件名混过。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.pointfields import open_preparation
```

```text
open_preparation(config, component, reference=None, *, validate=True)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `未标注` | `必填` |
| `component` | `未标注` | `必填` |
| `reference` | `未标注` | `None` |
| `validate` | `未标注` | `True` |

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
from ai4e_core.applications.aero_cfd.trainprep.pointfields import open_preparation

print(signature(open_preparation))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`gencp`
- 案例：`gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `recipe_extensions.gencp`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.pointfields`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/pointfields.py:86`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.pointfields')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
