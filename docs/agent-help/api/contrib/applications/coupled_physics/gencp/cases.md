<!-- dojo-help: {"domain": "ai4e_contrib.application.coupled_physics.gencp.cases", "kind": "api", "layer": "contrib.application", "summary": "ai4e_contrib.application.coupled_physics.gencp.cases 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.application.coupled_physics.gencp.cases", "topic_id": "module:ai4e_contrib.application.coupled_physics.gencp.cases"} -->
# `ai4e_contrib.application.coupled_physics.gencp.cases` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-application-coupled-physics-gencp-cases-bind-velocity"></a>
## `ai4e_contrib.application.coupled_physics.gencp.cases.bind_velocity`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`bind_velocity(model, *, dataset, field, context, condition=None)`
- **规范定义名**：`ai4e_contrib.application.coupled_physics.gencp.cases.bind_velocity`

### 用途

连接当前场模型与条件函数，返回普通速度回调。

### 导入与签名

```python
from ai4e_contrib.application.coupled_physics.gencp.cases import bind_velocity
```

```text
bind_velocity(model, *, dataset, field, context, condition=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model` | `未标注` | `必填` |
| `dataset` | `未标注` | `必填关键字参数` |
| `field` | `未标注` | `必填关键字参数` |
| `context` | `未标注` | `必填关键字参数` |
| `condition` | `未标注` | `None` |

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
from ai4e_contrib.application.coupled_physics.gencp.cases import bind_velocity

print(signature(bind_velocity))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`gencp`
- 案例：`gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`

### 源码位置

- 模块：`ai4e_contrib.application.coupled_physics.gencp.cases`
- 仓库相对路径：`packages/ai4e-contrib/application/coupled_physics/gencp/cases.py:118`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.coupled_physics.gencp.cases')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-coupled-physics-gencp-cases-dataset-adapter"></a>
## `ai4e_contrib.application.coupled_physics.gencp.cases.dataset_adapter`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`dataset_adapter(dataset)`
- **规范定义名**：`ai4e_contrib.application.coupled_physics.gencp.cases.dataset_adapter`

### 用途

返回原生读取与来源描述模块，不在 core 判断数据集名称。

### 导入与签名

```python
from ai4e_contrib.application.coupled_physics.gencp.cases import dataset_adapter
```

```text
dataset_adapter(dataset)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dataset` | `未标注` | `必填` |

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
from ai4e_contrib.application.coupled_physics.gencp.cases import dataset_adapter

print(signature(dataset_adapter))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`gencp`
- 案例：`gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`

### 源码位置

- 模块：`ai4e_contrib.application.coupled_physics.gencp.cases`
- 仓库相对路径：`packages/ai4e-contrib/application/coupled_physics/gencp/cases.py:15`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.coupled_physics.gencp.cases')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-coupled-physics-gencp-cases-descriptions"></a>
## `ai4e_contrib.application.coupled_physics.gencp.cases.descriptions`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`descriptions(cfg, root)`
- **规范定义名**：`ai4e_contrib.application.coupled_physics.gencp.cases.descriptions`

### 用途

准备分场训练/验证和耦合评价来源。

### 导入与签名

```python
from ai4e_contrib.application.coupled_physics.gencp.cases import descriptions
```

```text
descriptions(cfg, root)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cfg` | `未标注` | `必填` |
| `root` | `未标注` | `必填` |

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
from ai4e_contrib.application.coupled_physics.gencp.cases import descriptions

print(signature(descriptions))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`gencp`
- 案例：`gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `recipe_extensions.geotransolver`

### 源码位置

- 模块：`ai4e_contrib.application.coupled_physics.gencp.cases`
- 仓库相对路径：`packages/ai4e-contrib/application/coupled_physics/gencp/cases.py:20`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.coupled_physics.gencp.cases')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-coupled-physics-gencp-cases-inference-inputs"></a>
## `ai4e_contrib.application.coupled_physics.gencp.cases.inference_inputs`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`inference_inputs(preparation, models, *, device, flow_steps)`
- **规范定义名**：`ai4e_contrib.application.coupled_physics.gencp.cases.inference_inputs`

### 用途

提取配对样本与明确外部边界，再初始化各场生成噪声。

### 导入与签名

```python
from ai4e_contrib.application.coupled_physics.gencp.cases import inference_inputs
```

```text
inference_inputs(preparation, models, *, device, flow_steps)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `preparation` | `未标注` | `必填` |
| `models` | `未标注` | `必填` |
| `device` | `未标注` | `必填关键字参数` |
| `flow_steps` | `未标注` | `必填关键字参数` |

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
from ai4e_contrib.application.coupled_physics.gencp.cases import inference_inputs

print(signature(inference_inputs))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`gencp`
- 案例：`gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`

### 源码位置

- 模块：`ai4e_contrib.application.coupled_physics.gencp.cases`
- 仓库相对路径：`packages/ai4e-contrib/application/coupled_physics/gencp/cases.py:45`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.coupled_physics.gencp.cases')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-coupled-physics-gencp-cases-physical-predictions"></a>
## `ai4e_contrib.application.coupled_physics.gencp.cases.physical_predictions`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`physical_predictions(states, preparation)`
- **规范定义名**：`ai4e_contrib.application.coupled_physics.gencp.cases.physical_predictions`

### 用途

按各场冻结变换恢复物理空间，保留不同空间形状。

### 导入与签名

```python
from ai4e_contrib.application.coupled_physics.gencp.cases import physical_predictions
```

```text
physical_predictions(states, preparation)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `states` | `未标注` | `必填` |
| `preparation` | `未标注` | `必填` |

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
from ai4e_contrib.application.coupled_physics.gencp.cases import physical_predictions

print(signature(physical_predictions))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`gencp`
- 案例：`gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`

### 源码位置

- 模块：`ai4e_contrib.application.coupled_physics.gencp.cases`
- 仓库相对路径：`packages/ai4e-contrib/application/coupled_physics/gencp/cases.py:127`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.coupled_physics.gencp.cases')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
