<!-- dojo-help: {"domain": "ai4e_core.applications.coupled_physics.trainprep", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.coupled_physics.trainprep 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.coupled_physics.trainprep", "topic_id": "module:ai4e_core.applications.coupled_physics.trainprep"} -->
# `ai4e_core.applications.coupled_physics.trainprep` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-coupled-physics-trainprep-fieldsamples"></a>
## `ai4e_core.applications.coupled_physics.trainprep.FieldSamples`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`FieldSamples(description, reader)`
- **规范定义名**：`ai4e_core.applications.coupled_physics.trainprep.FieldSamples`

### 用途

按需缓存已选窗口；模型训练只消费批次，不处理文件循环。

### 导入与签名

```python
from ai4e_core.applications.coupled_physics.trainprep import FieldSamples
```

```text
FieldSamples(description, reader)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `description` | `未标注` | `必填` |
| `reader` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`FieldSamples`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.coupled_physics.trainprep import FieldSamples

print(signature(FieldSamples))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.coupled_physics.trainprep`
- 仓库相对路径：`packages/ai4e-core/applications/coupled_physics/trainprep.py:73`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.coupled_physics.trainprep')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-coupled-physics-trainprep-fieldsamples-batch"></a>
## `ai4e_core.applications.coupled_physics.trainprep.FieldSamples.batch`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`batch(self, indices, device='cpu')`
- **规范定义名**：`ai4e_core.applications.coupled_physics.trainprep.FieldSamples.batch`

### 用途

收集同场样本为 B,T,H,W,C，不跨场补齐网格。

### 导入与签名

```python
from ai4e_core.applications.coupled_physics.trainprep import FieldSamples
```

```text
batch(self, indices, device='cpu')
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `indices` | `未标注` | `必填` |
| `device` | `未标注` | `'cpu'` |

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
from ai4e_core.applications.coupled_physics.trainprep import FieldSamples

print(signature(FieldSamples.batch))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `gencp`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`
- 案例：`classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.pod_surrogate_replacement`, `recipe_extensions.research_state`, `recipe_extensions.tail_batch`

### 源码位置

- 模块：`ai4e_core.applications.coupled_physics.trainprep`
- 仓库相对路径：`packages/ai4e-core/applications/coupled_physics/trainprep.py:90`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.coupled_physics.trainprep')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-coupled-physics-trainprep-fieldsamples-sample"></a>
## `ai4e_core.applications.coupled_physics.trainprep.FieldSamples.sample`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`sample(self, index)`
- **规范定义名**：`ai4e_core.applications.coupled_physics.trainprep.FieldSamples.sample`

### 用途

读取一个冻结身份的样本。

### 导入与签名

```python
from ai4e_core.applications.coupled_physics.trainprep import FieldSamples
```

```text
sample(self, index)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `index` | `未标注` | `必填` |

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
from ai4e_core.applications.coupled_physics.trainprep import FieldSamples

print(signature(FieldSamples.sample))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `extension.pcno`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `recipe_extensions.geotransolver`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.physical_visualization`, `recipe_extensions.research_state`, `recipe_extensions.wdno`

### 源码位置

- 模块：`ai4e_core.applications.coupled_physics.trainprep`
- 仓库相对路径：`packages/ai4e-core/applications/coupled_physics/trainprep.py:83`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.coupled_physics.trainprep')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-coupled-physics-trainprep-open-preparation"></a>
## `ai4e_core.applications.coupled_physics.trainprep.open_preparation`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`open_preparation(path)`
- **规范定义名**：`ai4e_core.applications.coupled_physics.trainprep.open_preparation`

### 用途

核对来源当前身份；元信息变化时校验内容，不静默重做准备。

### 导入与签名

```python
from ai4e_core.applications.coupled_physics.trainprep import open_preparation
```

```text
open_preparation(path)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `未标注` | `必填` |

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
from ai4e_core.applications.coupled_physics.trainprep import open_preparation

print(signature(open_preparation))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`gencp`
- 案例：`gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `recipe_extensions.gencp`

### 源码位置

- 模块：`ai4e_core.applications.coupled_physics.trainprep`
- 仓库相对路径：`packages/ai4e-core/applications/coupled_physics/trainprep.py:61`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.coupled_physics.trainprep')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-coupled-physics-trainprep-prepare"></a>
## `ai4e_core.applications.coupled_physics.trainprep.prepare`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`prepare(descriptions, path, *, dataset, profile='scaled')`
- **规范定义名**：`ai4e_core.applications.coupled_physics.trainprep.prepare`

### 用途

冻结已解析来源、字段与选择；不复制物理数组。

### 导入与签名

```python
from ai4e_core.applications.coupled_physics.trainprep import prepare
```

```text
prepare(descriptions, path, *, dataset, profile='scaled')
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `descriptions` | `未标注` | `必填` |
| `path` | `未标注` | `必填` |
| `dataset` | `未标注` | `必填关键字参数` |
| `profile` | `未标注` | `'scaled'` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FileExistsError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.coupled_physics.trainprep import prepare

print(signature(prepare))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `gencp`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`, `pcno_cylinder`, `safediffcon`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.shapenet_car_abupt`, `classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.sampling`, `recipe_extensions.wdno`, `safediffcon.burgers`, `safediffcon.tokamak`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_core.applications.coupled_physics.trainprep`
- 仓库相对路径：`packages/ai4e-core/applications/coupled_physics/trainprep.py:13`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.coupled_physics.trainprep')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
