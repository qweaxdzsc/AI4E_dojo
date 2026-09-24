<!-- dojo-help: {"domain": "ai4e_core.applications.aero_cfd.trainprep.preparation", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.aero_cfd.trainprep.preparation 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.aero_cfd.trainprep.preparation", "topic_id": "module:ai4e_core.applications.aero_cfd.trainprep.preparation"} -->
# `ai4e_core.applications.aero_cfd.trainprep.preparation` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-preparation-preparation"></a>
## `ai4e_core.applications.aero_cfd.trainprep.preparation.Preparation`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`class Preparation`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.preparation.Preparation`

### 用途

一次准备的业务状态；只持久化 record，不持久化函数或张量。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.preparation import Preparation
```

```text
class Preparation
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Preparation`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.preparation import Preparation

print(signature(Preparation))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.preparation`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/preparation.py:60`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-preparation-bind-fields"></a>
## `ai4e_core.applications.aero_cfd.trainprep.preparation.bind_fields`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`bind_fields(data: Preparation, *, settings=None) -> Preparation`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.preparation.bind_fields`

### 用途

公开字段绑定步骤；用户配置中的归一化和采样另由相应步骤消费。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.preparation import bind_fields
```

```text
bind_fields(data: Preparation, *, settings=None) -> Preparation
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `data` | `Preparation` | `必填` |
| `settings` | `未标注` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Preparation`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.preparation import bind_fields

print(signature(bind_fields))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.preparation`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/preparation.py:100`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-preparation-check-report"></a>
## `ai4e_core.applications.aero_cfd.trainprep.preparation.check_report`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`check_report(data, *, session)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.preparation.check_report`

### 用途

准备检查报告，不发布任何持久化阶段产物。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.preparation import check_report
```

```text
check_report(data, *, session)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `data` | `未标注` | `必填` |
| `session` | `未标注` | `必填关键字参数` |

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
from ai4e_core.applications.aero_cfd.trainprep.preparation import check_report

print(signature(check_report))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.preparation`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/preparation.py:403`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-preparation-component-record"></a>
## `ai4e_core.applications.aero_cfd.trainprep.preparation.component_record`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`component_record(component) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.preparation.component_record`

### 用途

冻结入口名称及其源码内容，安装位置不参与摘要。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.preparation import component_record
```

```text
component_record(component) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `component` | `未标注` | `必填` |

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
from ai4e_core.applications.aero_cfd.trainprep.preparation import component_record

print(signature(component_record))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.preparation`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/preparation.py:29`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-preparation-configure-batching"></a>
## `ai4e_core.applications.aero_cfd.trainprep.preparation.configure_batching`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`configure_batching(data: Preparation, *, collate=None, batch_size=None, model_component=None) -> Preparation`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.preparation.configure_batching`

### 用途

注入模型拼批组件，保留跨样本索引偏移契约。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.preparation import configure_batching
```

```text
configure_batching(data: Preparation, *, collate=None, batch_size=None, model_component=None) -> Preparation
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `data` | `Preparation` | `必填` |
| `collate` | `未标注` | `None` |
| `batch_size` | `未标注` | `None` |
| `model_component` | `未标注` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Preparation`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.preparation import configure_batching

print(signature(configure_batching))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.preparation`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/preparation.py:136`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-preparation-configure-sampling"></a>
## `ai4e_core.applications.aero_cfd.trainprep.preparation.configure_sampling`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`configure_sampling(data: Preparation, *, prepare=None, settings=None, model_component=None, operation=None) -> Preparation`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.preparation.configure_sampling`

### 用途

注入模型样本组织组件；每个 epoch 的采样由训练迭代器调用。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.preparation import configure_sampling
```

```text
configure_sampling(data: Preparation, *, prepare=None, settings=None, model_component=None, operation=None) -> Preparation
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `data` | `Preparation` | `必填` |
| `prepare` | `未标注` | `None` |
| `settings` | `未标注` | `None` |
| `model_component` | `未标注` | `None` |
| `operation` | `未标注` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Preparation`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.preparation import configure_sampling

print(signature(configure_sampling))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.preparation`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/preparation.py:125`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-preparation-consume"></a>
## `ai4e_core.applications.aero_cfd.trainprep.preparation.consume`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`consume(config: dict, reference, *, prepare, collate) -> Preparation`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.preparation.consume`

### 用途

导入可读取的现行准备记录，按当前平台配置组计算，不拿冻结声明挡现行参数。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.preparation import consume
```

```text
consume(config: dict, reference, *, prepare, collate) -> Preparation
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `dict` | `必填` |
| `reference` | `未标注` | `必填` |
| `prepare` | `未标注` | `必填关键字参数` |
| `collate` | `未标注` | `必填关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Preparation`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.preparation import consume

print(signature(consume))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`, `surrogate_modeling/double_cylinder`, `surrogate_modeling/nasa_crm`
- 案例：`classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `recipe_extensions.geotransolver`, `recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.resunet`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`, `recipe_extensions.operator_physical_loss`, `recipe_extensions.research_state`, `recipe_extensions.tail_batch`, `surrogate_modeling.double_cylinder`, `surrogate_modeling.nasa_crm`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.preparation`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/preparation.py:412`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-preparation-contract-conflict-message"></a>
## `ai4e_core.applications.aero_cfd.trainprep.preparation.contract_conflict_message`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`contract_conflict_message(frozen: dict, current: dict) -> str`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.preparation.contract_conflict_message`

### 用途

消费冲突文案列出具体冻结项。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.preparation import contract_conflict_message
```

```text
contract_conflict_message(frozen: dict, current: dict) -> str
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `frozen` | `dict` | `必填` |
| `current` | `dict` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`str`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.preparation import contract_conflict_message

print(signature(contract_conflict_message))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.preparation`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/preparation.py:359`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-preparation-dataset-digest"></a>
## `ai4e_core.applications.aero_cfd.trainprep.preparation.dataset_digest`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`dataset_digest(index: ManifestIndex) -> str`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.preparation.dataset_digest`

### 用途

流式核对清单与实际张量字节，捕获原地替换数据。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.preparation import dataset_digest
```

```text
dataset_digest(index: ManifestIndex) -> str
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `index` | `ManifestIndex` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`str`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.preparation import dataset_digest

print(signature(dataset_digest))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.preparation`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/preparation.py:54`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-preparation-declarations"></a>
## `ai4e_core.applications.aero_cfd.trainprep.preparation.declarations`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`declarations(config: dict) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.preparation.declarations`

### 用途

只写准备真正消费的冻结项，不含模型页采样预算。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.preparation import declarations
```

```text
declarations(config: dict) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `dict` | `必填` |

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
from ai4e_core.applications.aero_cfd.trainprep.preparation import declarations

print(signature(declarations))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.resunet`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`, `recipe_extensions.operator_physical_loss`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.preparation`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/preparation.py:202`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-preparation-describe-contract-diffs"></a>
## `ai4e_core.applications.aero_cfd.trainprep.preparation.describe_contract_diffs`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`describe_contract_diffs(frozen: dict, current: dict, prefix: str='') -> list[str]`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.preparation.describe_contract_diffs`

### 用途

列出冻结语义差异，供检查页写明具体项而不是笼统重跑。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.preparation import describe_contract_diffs
```

```text
describe_contract_diffs(frozen: dict, current: dict, prefix: str='') -> list[str]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `frozen` | `dict` | `必填` |
| `current` | `dict` | `必填` |
| `prefix` | `str` | `''` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`list[str]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.preparation import describe_contract_diffs

print(signature(describe_contract_diffs))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.preparation`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/preparation.py:341`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-preparation-digest"></a>
## `ai4e_core.applications.aero_cfd.trainprep.preparation.digest`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`digest(value: dict) -> str`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.preparation.digest`

### 用途

计算与 JSON 键排列无关的交付摘要。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.preparation import digest
```

```text
digest(value: dict) -> str
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `value` | `dict` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`str`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.preparation import digest

print(signature(digest))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`, `surrogate_modeling/double_cylinder`, `surrogate_modeling/nasa_crm`
- 案例：`classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `extension.pcno`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `surrogate_modeling.double_cylinder`, `surrogate_modeling.nasa_crm`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.preparation`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/preparation.py:24`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-preparation-external-inputs"></a>
## `ai4e_core.applications.aero_cfd.trainprep.preparation.external_inputs`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`external_inputs(config: dict) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.preparation.external_inputs`

### 用途

条件文件按内容冻结，防止同路径替换造成静默输入变化。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.preparation import external_inputs
```

```text
external_inputs(config: dict) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `dict` | `必填` |

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
from ai4e_core.applications.aero_cfd.trainprep.preparation import external_inputs

print(signature(external_inputs))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.preparation`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/preparation.py:42`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-preparation-freeze-normalization"></a>
## `ai4e_core.applications.aero_cfd.trainprep.preparation.freeze_normalization`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`freeze_normalization(data: Preparation, *, settings=None) -> Preparation`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.preparation.freeze_normalization`

### 用途

绑定实际统计值或已有冻结记录；不把归一化数据再次变换。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.preparation import freeze_normalization
```

```text
freeze_normalization(data: Preparation, *, settings=None) -> Preparation
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `data` | `Preparation` | `必填` |
| `settings` | `未标注` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Preparation`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.preparation import freeze_normalization

print(signature(freeze_normalization))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.preparation`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/preparation.py:110`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-preparation-frozen-contract"></a>
## `ai4e_core.applications.aero_cfd.trainprep.preparation.frozen_contract`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`frozen_contract(declared: dict) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.preparation.frozen_contract`

### 用途

准备真正消费的冻结项：字段角色、数据规格和采样方法，不含模型页点数。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.preparation import frozen_contract
```

```text
frozen_contract(declared: dict) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `declared` | `dict` | `必填` |

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
from ai4e_core.applications.aero_cfd.trainprep.preparation import frozen_contract

print(signature(frozen_contract))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.preparation`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/preparation.py:294`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-preparation-open-dataset"></a>
## `ai4e_core.applications.aero_cfd.trainprep.preparation.open_dataset`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`open_dataset(config: dict, dataset=None, overlay=None) -> Preparation`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.preparation.open_dataset`

### 用途

打开 datapre 产物或已有清单，独立入口无需执行原始数据处理。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.preparation import open_dataset
```

```text
open_dataset(config: dict, dataset=None, overlay=None) -> Preparation
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `dict` | `必填` |
| `dataset` | `未标注` | `None` |
| `overlay` | `未标注` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Preparation`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.preparation import open_dataset

print(signature(open_dataset))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.preparation`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/preparation.py:72`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-preparation-prepare-fields"></a>
## `ai4e_core.applications.aero_cfd.trainprep.preparation.prepare_fields`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`prepare_fields(data: Preparation) -> Preparation`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.preparation.prepare_fields`

### 用途

按公开物理字段规则配置准备函数，不预先抽样。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.preparation import prepare_fields
```

```text
prepare_fields(data: Preparation) -> Preparation
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `data` | `Preparation` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Preparation`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.preparation import prepare_fields

print(signature(prepare_fields))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.preparation`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/preparation.py:92`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-preparation-publish"></a>
## `ai4e_core.applications.aero_cfd.trainprep.preparation.publish`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`publish(data: Preparation, run=None, *, session=None) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.preparation.publish`

### 用途

发布可独立消费的准备引用；检查模式不写归一化或阶段产物。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.preparation import publish
```

```text
publish(data: Preparation, run=None, *, session=None) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `data` | `Preparation` | `必填` |
| `run` | `未标注` | `None` |
| `session` | `未标注` | `None` |

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
from ai4e_core.applications.aero_cfd.trainprep.preparation import publish

print(signature(publish))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.preparation`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/preparation.py:367`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-preparation-sampling-methods"></a>
## `ai4e_core.applications.aero_cfd.trainprep.preparation.sampling_methods`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`sampling_methods(sampling) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.preparation.sampling_methods`

### 用途

比较用的采样方法视图；忽略超节点和模型页点数。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.preparation import sampling_methods
```

```text
sampling_methods(sampling) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `sampling` | `未标注` | `必填` |

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
from ai4e_core.applications.aero_cfd.trainprep.preparation import sampling_methods

print(signature(sampling_methods))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.preparation`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/preparation.py:264`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-preparation-validate-preparation"></a>
## `ai4e_core.applications.aero_cfd.trainprep.preparation.validate_preparation`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`validate_preparation(data: Preparation) -> Preparation`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.preparation.validate_preparation`

### 用途

逐样本校验全部已声明分片，不把随机探测结果作为训练数据缓存。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.preparation import validate_preparation
```

```text
validate_preparation(data: Preparation) -> Preparation
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `data` | `Preparation` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Preparation`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.preparation import validate_preparation

print(signature(validate_preparation))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.preparation`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/preparation.py:146`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
