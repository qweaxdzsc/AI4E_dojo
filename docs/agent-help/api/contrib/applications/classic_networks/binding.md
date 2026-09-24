<!-- dojo-help: {"domain": "ai4e_contrib.application.classic_networks.binding", "kind": "api", "layer": "contrib.application", "summary": "ai4e_contrib.application.classic_networks.binding 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.application.classic_networks.binding", "topic_id": "module:ai4e_contrib.application.classic_networks.binding"} -->
# `ai4e_contrib.application.classic_networks.binding` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-application-classic-networks-binding-fieldmodel"></a>
## `ai4e_contrib.application.classic_networks.binding.FieldModel`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`FieldModel(network, family, spatial_dims)`
- **规范定义名**：`ai4e_contrib.application.classic_networks.binding.FieldModel`

### 用途

局部适配规则场、图与真实序列；所有学习参数注册到network。

### 导入与签名

```python
from ai4e_contrib.application.classic_networks.binding import FieldModel
```

```text
FieldModel(network, family, spatial_dims)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `network` | `未标注` | `必填` |
| `family` | `未标注` | `必填` |
| `spatial_dims` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`FieldModel`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.application.classic_networks.binding import FieldModel

print(signature(FieldModel))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.classic_networks.binding`
- 仓库相对路径：`packages/ai4e-contrib/application/classic_networks/binding.py:36`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.classic_networks.binding')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-classic-networks-binding-fieldmodel-forward"></a>
## `ai4e_contrib.application.classic_networks.binding.FieldModel.forward`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`forward(self, input, valid=None, coordinates=None)`
- **规范定义名**：`ai4e_contrib.application.classic_networks.binding.FieldModel.forward`

### 用途

返回末轴场或点批序列末时刻，mask语义由此局部连接转换。

### 导入与签名

```python
from ai4e_contrib.application.classic_networks.binding import FieldModel
```

```text
forward(self, input, valid=None, coordinates=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `input` | `未标注` | `必填` |
| `valid` | `未标注` | `None` |
| `coordinates` | `未标注` | `None` |

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
from ai4e_contrib.application.classic_networks.binding import FieldModel

print(signature(FieldModel.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_contrib.application.classic_networks.binding`
- 仓库相对路径：`packages/ai4e-contrib/application/classic_networks/binding.py:43`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.classic_networks.binding')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-classic-networks-binding-batch"></a>
## `ai4e_contrib.application.classic_networks.binding.batch`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`batch(arrays, ids, *, device, case, sample_points=None, point_sequence=True)`
- **规范定义名**：`ai4e_contrib.application.classic_networks.binding.batch`

### 用途

同索引取特征/目标/mask；循环输入按真实时间轴组织为Q×T×C。

### 导入与签名

```python
from ai4e_contrib.application.classic_networks.binding import batch
```

```text
batch(arrays, ids, *, device, case, sample_points=None, point_sequence=True)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `arrays` | `未标注` | `必填` |
| `ids` | `未标注` | `必填` |
| `device` | `未标注` | `必填关键字参数` |
| `case` | `未标注` | `必填关键字参数` |
| `sample_points` | `未标注` | `None` |
| `point_sequence` | `未标注` | `True` |

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
from ai4e_contrib.application.classic_networks.binding import batch

print(signature(batch))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `gencp`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`
- 案例：`classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.pod_surrogate_replacement`, `recipe_extensions.research_state`, `recipe_extensions.tail_batch`

### 源码位置

- 模块：`ai4e_contrib.application.classic_networks.binding`
- 仓库相对路径：`packages/ai4e-contrib/application/classic_networks/binding.py:81`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.classic_networks.binding')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-classic-networks-binding-build-network"></a>
## `ai4e_contrib.application.classic_networks.binding.build_network`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`build_network(model)`
- **规范定义名**：`ai4e_contrib.application.classic_networks.binding.build_network`

### 用途

创建中立网络，参数通过局部配置显式传递，不改变核心协议。

### 导入与签名

```python
from ai4e_contrib.application.classic_networks.binding import build_network
```

```text
build_network(model)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model` | `未标注` | `必填` |

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
from ai4e_contrib.application.classic_networks.binding import build_network

print(signature(build_network))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`
- 案例：`classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `recipe_extensions.operator_physical_loss`

### 源码位置

- 模块：`ai4e_contrib.application.classic_networks.binding`
- 仓库相对路径：`packages/ai4e-contrib/application/classic_networks/binding.py:10`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.classic_networks.binding')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-classic-networks-binding-construct"></a>
## `ai4e_contrib.application.classic_networks.binding.construct`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`construct(cfg)`
- **规范定义名**：`ai4e_contrib.application.classic_networks.binding.construct`

### 用途

按普通构造器接入完整网络；布局适配不进入网络能力。

### 导入与签名

```python
from ai4e_contrib.application.classic_networks.binding import construct
```

```text
construct(cfg)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cfg` | `未标注` | `必填` |

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
from ai4e_contrib.application.classic_networks.binding import construct

print(signature(construct))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `gencp`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`, `pcno`, `safediffcon`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.shapenet_car_abupt`, `classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `geothermal.pcno`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.gencp`, `recipe_extensions.model_block`, `recipe_extensions.sampling`, `safediffcon.burgers`, `safediffcon.tokamak`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.application.classic_networks.binding`
- 仓库相对路径：`packages/ai4e-contrib/application/classic_networks/binding.py:75`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.classic_networks.binding')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-classic-networks-binding-objective"></a>
## `ai4e_contrib.application.classic_networks.binding.objective`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`objective(model, item)`
- **规范定义名**：`ai4e_contrib.application.classic_networks.binding.objective`

### 用途

有效域归一化MSE；失效占位永不参与损失或梯度。

### 导入与签名

```python
from ai4e_contrib.application.classic_networks.binding import objective
```

```text
objective(model, item)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model` | `未标注` | `必填` |
| `item` | `未标注` | `必填` |

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
from ai4e_contrib.application.classic_networks.binding import objective

print(signature(objective))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `gencp`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `pcno`, `safediffcon`, `wdno`
- 案例：`classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `geothermal.pcno`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `recipe_extensions.geotransolver`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.pod_surrogate_replacement`, `recipe_extensions.research_state`, `recipe_extensions.safediffcon`, `recipe_extensions.tail_batch`, `recipe_extensions.task_labels`, `recipe_extensions.wdno`, `safediffcon.burgers`, `safediffcon.tokamak`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.application.classic_networks.binding`
- 仓库相对路径：`packages/ai4e-contrib/application/classic_networks/binding.py:107`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.classic_networks.binding')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
