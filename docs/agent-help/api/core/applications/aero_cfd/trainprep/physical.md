<!-- dojo-help: {"domain": "ai4e_core.applications.aero_cfd.trainprep.physical", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.aero_cfd.trainprep.physical 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.aero_cfd.trainprep.physical", "topic_id": "module:ai4e_core.applications.aero_cfd.trainprep.physical"} -->
# `ai4e_core.applications.aero_cfd.trainprep.physical` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-physical-physicalpreparation"></a>
## `ai4e_core.applications.aero_cfd.trainprep.physical.PhysicalPreparation`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`class PhysicalPreparation`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.physical.PhysicalPreparation`

### 用途

准备阶段状态；record 可持久化，运行对象仅保留在内存。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.physical import PhysicalPreparation
```

```text
class PhysicalPreparation
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`PhysicalPreparation`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.physical import PhysicalPreparation

print(signature(PhysicalPreparation))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.physical`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/physical.py:22`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.physical')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-physical-bind-fields"></a>
## `ai4e_core.applications.aero_cfd.trainprep.physical.bind_fields`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`bind_fields(data, *, settings=None)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.physical.bind_fields`

### 用途

绑定领域输入和目标；缺失分片不能退回另一份数据。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.physical import bind_fields
```

```text
bind_fields(data, *, settings=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `data` | `未标注` | `必填` |
| `settings` | `未标注` | `None` |

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
from ai4e_core.applications.aero_cfd.trainprep.physical import bind_fields

print(signature(bind_fields))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.physical`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/physical.py:76`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.physical')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-physical-check-report"></a>
## `ai4e_core.applications.aero_cfd.trainprep.physical.check_report`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`check_report(data, *, session)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.physical.check_report`

### 用途

交付检查报告，不发布准备产物。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.physical import check_report
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

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.physical import check_report

print(signature(check_report))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.physical`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/physical.py:216`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.physical')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-physical-configure-batching"></a>
## `ai4e_core.applications.aero_cfd.trainprep.physical.configure_batching`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`configure_batching(data, *, batch_size=None, model_component=None)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.physical.configure_batching`

### 用途

记录现有物理模型单实例批次约定，不额外拼接样本。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.physical import configure_batching
```

```text
configure_batching(data, *, batch_size=None, model_component=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `data` | `未标注` | `必填` |
| `batch_size` | `未标注` | `None` |
| `model_component` | `未标注` | `None` |

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
from ai4e_core.applications.aero_cfd.trainprep.physical import configure_batching

print(signature(configure_batching))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.physical`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/physical.py:141`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.physical')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-physical-configure-sampling"></a>
## `ai4e_core.applications.aero_cfd.trainprep.physical.configure_sampling`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`configure_sampling(data, *, settings=None, operation=None, model_component=None)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.physical.configure_sampling`

### 用途

配置 sample/config/normalization → batch 能力，训练时逐轮调用。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.physical import configure_sampling
```

```text
configure_sampling(data, *, settings=None, operation=None, model_component=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `data` | `未标注` | `必填` |
| `settings` | `未标注` | `None` |
| `operation` | `未标注` | `None` |
| `model_component` | `未标注` | `None` |

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
from ai4e_core.applications.aero_cfd.trainprep.physical import configure_sampling

print(signature(configure_sampling))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.physical`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/physical.py:103`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.physical')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-physical-consume"></a>
## `ai4e_core.applications.aero_cfd.trainprep.physical.consume`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`consume(config, dataset_component, model_component, reference=None)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.physical.consume`

### 用途

导入已有准备记录并按当前平台配置组计算，不拿冻结声明挡现行参数。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.physical import consume
```

```text
consume(config, dataset_component, model_component, reference=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `未标注` | `必填` |
| `dataset_component` | `未标注` | `必填` |
| `model_component` | `未标注` | `必填` |
| `reference` | `未标注` | `None` |

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
from ai4e_core.applications.aero_cfd.trainprep.physical import consume

print(signature(consume))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`, `surrogate_modeling/double_cylinder`, `surrogate_modeling/nasa_crm`
- 案例：`classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `recipe_extensions.geotransolver`, `recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.resunet`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`, `recipe_extensions.operator_physical_loss`, `recipe_extensions.research_state`, `recipe_extensions.tail_batch`, `surrogate_modeling.double_cylinder`, `surrogate_modeling.nasa_crm`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.physical`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/physical.py:243`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.physical')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-physical-freeze-normalization"></a>
## `ai4e_core.applications.aero_cfd.trainprep.physical.freeze_normalization`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`freeze_normalization(data, *, settings=None)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.physical.freeze_normalization`

### 用途

从旧记录恢复或拟合训练变换；不推进模型随机状态。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.physical import freeze_normalization
```

```text
freeze_normalization(data, *, settings=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `data` | `未标注` | `必填` |
| `settings` | `未标注` | `None` |

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
from ai4e_core.applications.aero_cfd.trainprep.physical import freeze_normalization

print(signature(freeze_normalization))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.physical`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/physical.py:91`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.physical')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-physical-normalized-fields"></a>
## `ai4e_core.applications.aero_cfd.trainprep.physical.normalized_fields`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`normalized_fields(sample: dict, normalization: Normalization) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.physical.normalized_fields`

### 用途

点字段保持物理来源，样本条件由模型绑定显式变换。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.physical import normalized_fields
```

```text
normalized_fields(sample: dict, normalization: Normalization) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `sample` | `dict` | `必填` |
| `normalization` | `Normalization` | `必填` |

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
from ai4e_core.applications.aero_cfd.trainprep.physical import normalized_fields

print(signature(normalized_fields))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.physical`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/physical.py:296`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.physical')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-physical-open-dataset"></a>
## `ai4e_core.applications.aero_cfd.trainprep.physical.open_dataset`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`open_dataset(config, dataset_component, model_component, reference=None, dataset=None, *, version=1)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.physical.open_dataset`

### 用途

打开物理清单或已冻结准备引用，不在此拟合变换或进行模型准备。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.physical import open_dataset
```

```text
open_dataset(config, dataset_component, model_component, reference=None, dataset=None, *, version=1)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `未标注` | `必填` |
| `dataset_component` | `未标注` | `必填` |
| `model_component` | `未标注` | `必填` |
| `reference` | `未标注` | `None` |
| `dataset` | `未标注` | `None` |
| `version` | `未标注` | `1` |

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
from ai4e_core.applications.aero_cfd.trainprep.physical import open_dataset

print(signature(open_dataset))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.physical`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/physical.py:39`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.physical')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-physical-open-preparation"></a>
## `ai4e_core.applications.aero_cfd.trainprep.physical.open_preparation`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`open_preparation(config, dataset_component, model_component, reference=None)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.physical.open_preparation`

### 用途

兼容旧三元组入口，并只读导入现行通用 version=2 准备。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.physical import open_preparation
```

```text
open_preparation(config, dataset_component, model_component, reference=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `未标注` | `必填` |
| `dataset_component` | `未标注` | `必填` |
| `model_component` | `未标注` | `必填` |
| `reference` | `未标注` | `None` |

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
from ai4e_core.applications.aero_cfd.trainprep.physical import open_preparation

print(signature(open_preparation))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`gencp`
- 案例：`gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `recipe_extensions.gencp`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.physical`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/physical.py:263`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.physical')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-physical-publish"></a>
## `ai4e_core.applications.aero_cfd.trainprep.physical.publish`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`publish(data, *, session)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.physical.publish`

### 用途

通过唯一 writer 发布已校验的物理准备。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.physical import publish
```

```text
publish(data, *, session)
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
from ai4e_core.applications.aero_cfd.trainprep.physical import publish

print(signature(publish))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.physical`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/physical.py:223`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.physical')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-physical-validate-preparation"></a>
## `ai4e_core.applications.aero_cfd.trainprep.physical.validate_preparation`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`validate_preparation(data)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.physical.validate_preparation`

### 用途

按当前平台配置校验一份可读样本；已导入准备不拿冻结声明挡现行参数。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.physical import validate_preparation
```

```text
validate_preparation(data)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `data` | `未标注` | `必填` |

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
from ai4e_core.applications.aero_cfd.trainprep.physical import validate_preparation

print(signature(validate_preparation))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.physical`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/physical.py:151`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.physical')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
