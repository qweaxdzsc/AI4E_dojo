<!-- dojo-help: {"domain": "ai4e_core.applications.geothermal.data", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.geothermal.data 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.geothermal.data", "topic_id": "module:ai4e_core.applications.geothermal.data"} -->
# `ai4e_core.applications.geothermal.data` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-geothermal-data-prepare-inputs"></a>
## `ai4e_core.applications.geothermal.data.prepare_inputs`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`prepare_inputs(dataset, output)`
- **规范定义名**：`ai4e_core.applications.geothermal.data.prepare_inputs`

### 用途

保持作者冻结统计量与张量不变，将准备产物交付为自包含副本。

### 导入与签名

```python
from ai4e_core.applications.geothermal.data import prepare_inputs
```

```text
prepare_inputs(dataset, output)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dataset` | `未标注` | `必填` |
| `output` | `未标注` | `必填` |

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
from ai4e_core.applications.geothermal.data import prepare_inputs

print(signature(prepare_inputs))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `pcno`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.shapenet_car_abupt`, `geothermal.pcno`, `recipe_extensions.field_mapping`, `recipe_extensions.sampling`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_core.applications.geothermal.data`
- 仓库相对路径：`packages/ai4e-core/applications/geothermal/data.py:48`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.geothermal.data')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-geothermal-data-publish-dataset"></a>
## `ai4e_core.applications.geothermal.data.publish_dataset`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`publish_dataset(source, output, *, inspect, kind='dataset')`
- **规范定义名**：`ai4e_core.applications.geothermal.data.publish_dataset`

### 用途

检查来源并复制已核验文件；仅完整发布才写出入口清单。

### 导入与签名

```python
from ai4e_core.applications.geothermal.data import publish_dataset
```

```text
publish_dataset(source, output, *, inspect, kind='dataset')
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `source` | `未标注` | `必填` |
| `output` | `未标注` | `必填` |
| `inspect` | `未标注` | `必填关键字参数` |
| `kind` | `未标注` | `'dataset'` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FileExistsError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.geothermal.data import publish_dataset

print(signature(publish_dataset))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/shapenet_car`, `pcno`
- 案例：`aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `geothermal.pcno`, `recipe_extensions.field_mapping`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.applications.geothermal.data`
- 仓库相对路径：`packages/ai4e-core/applications/geothermal/data.py:11`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.geothermal.data')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-geothermal-data-read-bundle"></a>
## `ai4e_core.applications.geothermal.data.read_bundle`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`read_bundle(path, *, kind=None, verify=True)`
- **规范定义名**：`ai4e_core.applications.geothermal.data.read_bundle`

### 用途

读回冻结记录并验证所有实际依赖；禁止出界或静默接受已变更输入。

### 导入与签名

```python
from ai4e_core.applications.geothermal.data import read_bundle
```

```text
read_bundle(path, *, kind=None, verify=True)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `未标注` | `必填` |
| `kind` | `未标注` | `None` |
| `verify` | `未标注` | `True` |

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
from ai4e_core.applications.geothermal.data import read_bundle

print(signature(read_bundle))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.geothermal.data`
- 仓库相对路径：`packages/ai4e-core/applications/geothermal/data.py:33`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.geothermal.data')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-geothermal-data-record-bundle"></a>
## `ai4e_core.applications.geothermal.data.record_bundle`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`record_bundle(session, path, *, kind, stage)`
- **规范定义名**：`ai4e_core.applications.geothermal.data.record_bundle`

### 用途

把清单及全部数据依赖交付给公开资产入口。

### 导入与签名

```python
from ai4e_core.applications.geothermal.data import record_bundle
```

```text
record_bundle(session, path, *, kind, stage)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `session` | `未标注` | `必填` |
| `path` | `未标注` | `必填` |
| `kind` | `未标注` | `必填关键字参数` |
| `stage` | `未标注` | `必填关键字参数` |

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
from ai4e_core.applications.geothermal.data import record_bundle

print(signature(record_bundle))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`, `pcno`, `surrogate_modeling/double_cylinder`, `surrogate_modeling/nasa_crm`
- 案例：`classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `geothermal.pcno`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `recipe_extensions.research_state`, `surrogate_modeling.double_cylinder`, `surrogate_modeling.nasa_crm`

### 源码位置

- 模块：`ai4e_core.applications.geothermal.data`
- 仓库相对路径：`packages/ai4e-core/applications/geothermal/data.py:56`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.geothermal.data')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
