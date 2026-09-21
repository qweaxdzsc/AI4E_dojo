<!-- dojo-help: {"domain": "ai4e_contrib.application.coupled_physics.gencp.validation", "kind": "api", "layer": "contrib.application", "summary": "ai4e_contrib.application.coupled_physics.gencp.validation 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.application.coupled_physics.gencp.validation", "topic_id": "module:ai4e_contrib.application.coupled_physics.gencp.validation"} -->
# `ai4e_contrib.application.coupled_physics.gencp.validation` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-application-coupled-physics-gencp-validation-generate-single"></a>
## `ai4e_contrib.application.coupled_physics.gencp.validation.generate_single`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`generate_single(model, batch, *, dataset, field, settings, seed=43)`
- **规范定义名**：`ai4e_contrib.application.coupled_physics.gencp.validation.generate_single`

### 用途

复现原单场生成网格，隔离验证对训练随机流的影响。

### 导入与签名

```python
from ai4e_contrib.application.coupled_physics.gencp.validation import generate_single
```

```text
generate_single(model, batch, *, dataset, field, settings, seed=43)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model` | `未标注` | `必填` |
| `batch` | `未标注` | `必填` |
| `dataset` | `未标注` | `必填关键字参数` |
| `field` | `未标注` | `必填关键字参数` |
| `settings` | `未标注` | `必填关键字参数` |
| `seed` | `未标注` | `43` |

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
from ai4e_contrib.application.coupled_physics.gencp.validation import generate_single

print(signature(generate_single))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`gencp`
- 案例：`gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`

### 源码位置

- 模块：`ai4e_contrib.application.coupled_physics.gencp.validation`
- 仓库相对路径：`packages/ai4e-contrib/application/coupled_physics/gencp/validation.py:22`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.coupled_physics.gencp.validation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-coupled-physics-gencp-validation-selection-metric"></a>
## `ai4e_contrib.application.coupled_physics.gencp.validation.selection_metric`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`selection_metric(prediction, target, field, *, dataset, normalization=None)`
- **规范定义名**：`ai4e_contrib.application.coupled_physics.gencp.validation.selection_metric`

### 用途

原选优口径：物理空间 FSI 的 u/SDF，NT 逐分量平均。

### 导入与签名

```python
from ai4e_contrib.application.coupled_physics.gencp.validation import selection_metric
```

```text
selection_metric(prediction, target, field, *, dataset, normalization=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `prediction` | `未标注` | `必填` |
| `target` | `未标注` | `必填` |
| `field` | `未标注` | `必填` |
| `dataset` | `未标注` | `必填关键字参数` |
| `normalization` | `未标注` | `None` |

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
from ai4e_contrib.application.coupled_physics.gencp.validation import selection_metric

print(signature(selection_metric))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`gencp`
- 案例：`gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`

### 源码位置

- 模块：`ai4e_contrib.application.coupled_physics.gencp.validation`
- 仓库相对路径：`packages/ai4e-contrib/application/coupled_physics/gencp/validation.py:37`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.coupled_physics.gencp.validation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-coupled-physics-gencp-validation-validation-batch"></a>
## `ai4e_contrib.application.coupled_physics.gencp.validation.validation_batch`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`validation_batch(preparation, field, device)`
- **规范定义名**：`ai4e_contrib.application.coupled_physics.gencp.validation.validation_batch`

### 用途

按冻结验证身份读取实际样本。

### 导入与签名

```python
from ai4e_contrib.application.coupled_physics.gencp.validation import validation_batch
```

```text
validation_batch(preparation, field, device)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `preparation` | `未标注` | `必填` |
| `field` | `未标注` | `必填` |
| `device` | `未标注` | `必填` |

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
from ai4e_contrib.application.coupled_physics.gencp.validation import validation_batch

print(signature(validation_batch))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`gencp`
- 案例：`gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`

### 源码位置

- 模块：`ai4e_contrib.application.coupled_physics.gencp.validation`
- 仓库相对路径：`packages/ai4e-contrib/application/coupled_physics/gencp/validation.py:13`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.coupled_physics.gencp.validation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
