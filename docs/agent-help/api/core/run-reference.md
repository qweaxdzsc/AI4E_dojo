<!-- dojo-help: {"domain": "ai4e_core.run.execute", "kind": "api", "layer": "core.run", "summary": "ai4e_core.run.execute 的完整源码参考与公开符号索引。", "title": "ai4e_core.run.execute", "topic_id": "module:ai4e_core.run.execute"} -->
# `ai4e_core.run.execute` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-run-batchexecutionerror"></a>
## `ai4e_core.run.BatchExecutionError`

- **层级**：`core.run`
- **稳定性**：`stable`
- **定义**：`BatchExecutionError(summary)`
- **规范定义名**：`ai4e_core.run.execute.BatchExecutionError`

### 用途

首错停止，并携带已经完成的批量摘要。

### 导入与签名

```python
from ai4e_core.run.execute import BatchExecutionError
```

```text
BatchExecutionError(summary)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `summary` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`BatchExecutionError`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.run.execute import BatchExecutionError

print(signature(BatchExecutionError))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.geotransolver_aero`

### 源码位置

- 模块：`ai4e_core.run.execute`
- 仓库相对路径：`packages/ai4e-core/run/execute.py:8`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.run.execute')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-run-runwriter"></a>
## `ai4e_core.run.RunWriter`

- **层级**：`core.run`
- **稳定性**：`stable`
- **定义**：`RunWriter(run_dir: Path)`
- **规范定义名**：`ai4e_core.run.writer.RunWriter`

### 用途

只写一次运行的配置、日志和摘要，不写训练张量。

### 导入与签名

```python
from ai4e_core.run.writer import RunWriter
```

```text
RunWriter(run_dir: Path)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `run_dir` | `Path` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`RunWriter`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`RuntimeError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.run.writer import RunWriter

print(signature(RunWriter))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.run.writer`
- 仓库相对路径：`packages/ai4e-core/run/writer.py:17`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.run.writer')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-run-trainingrun"></a>
## `ai4e_core.run.TrainingRun`

- **层级**：`core.run`
- **稳定性**：`stable`
- **定义**：`TrainingRun()`
- **规范定义名**：`ai4e_core.run.training.TrainingRun`

### 用途

向业务交付执行意图和报告接口，隐藏会话状态。

### 导入与签名

```python
from ai4e_core.run.training import TrainingRun
```

```text
TrainingRun()
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`TrainingRun`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`RuntimeError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.run.training import TrainingRun

print(signature(TrainingRun))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `gencp`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`, `parametric_pde`, `pcno`, `pcno_cylinder`, `safediffcon`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `extension.pcno`, `extension.pcno_cylinder`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `geothermal.pcno`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `parametric_pde.advection`, `parametric_pde.burgers`, `parametric_pde.convection_diffusion`, `parametric_pde.diffusion_trapezoid`, `parametric_pde.neumann_diffusion`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.free_wiring`, `recipe_extensions.gencp`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.sampling`, `recipe_extensions.wdno`, `safediffcon.burgers`, `safediffcon.tokamak`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_core.run.training`
- 仓库相对路径：`packages/ai4e-core/run/training.py:9`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.run.training')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-run-configuration-adapter"></a>
## `ai4e_core.run.configuration_adapter`

- **层级**：`core.run`
- **稳定性**：`stable`
- **定义**：`configuration_adapter(adapter)`
- **规范定义名**：`ai4e_core.run.session.configuration_adapter`

### 用途

显式注入一次托管运行的加载适配器，退出后恢复；不猜测领域。

### 导入与签名

```python
from ai4e_core.run.session import configuration_adapter
```

```text
configuration_adapter(adapter)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `adapter` | `未标注` | `必填` |

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
from ai4e_core.run.session import configuration_adapter

print(signature(configuration_adapter))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.run.session`
- 仓库相对路径：`packages/ai4e-core/run/session.py:22`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.run.session')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-run-execute"></a>
## `ai4e_core.run.execute`

- **层级**：`core.run`
- **稳定性**：`stable`
- **定义**：`execute(data, *, save, output, settings=None) -> dict`
- **规范定义名**：`ai4e_core.run.dataset.execute`

### 用途

执行数据视图；settings 交给保存策略，workers 只控制并行样本数。

### 导入与签名

```python
from ai4e_core.run.dataset import execute
```

```text
execute(data, *, save, output, settings=None) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `data` | `未标注` | `必填` |
| `save` | `未标注` | `必填关键字参数` |
| `output` | `未标注` | `必填关键字参数` |
| `settings` | `未标注` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`BatchExecutionError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.run.dataset import execute

print(signature(execute))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `gencp`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`, `parametric_pde`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `parametric_pde.advection`, `parametric_pde.burgers`, `parametric_pde.convection_diffusion`, `parametric_pde.diffusion_trapezoid`, `parametric_pde.neumann_diffusion`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.run.dataset`
- 仓库相对路径：`packages/ai4e-core/run/dataset.py:27`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.run.dataset')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-run-execute-many"></a>
## `ai4e_core.run.execute_many`

- **层级**：`core.run`
- **稳定性**：`stable`
- **定义**：`execute_many(items: Sequence, stage: Stage, *, context: dict, continue_on_error: bool=False) -> dict`
- **规范定义名**：`ai4e_core.run.execute.execute_many`

### 用途

逐样本运行并丢弃数组上下文；失败保留样本和原业务步骤。

### 导入与签名

```python
from ai4e_core.run.execute import execute_many
```

```text
execute_many(items: Sequence, stage: Stage, *, context: dict, continue_on_error: bool=False) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `items` | `Sequence` | `必填` |
| `stage` | `Stage` | `必填` |
| `context` | `dict` | `必填关键字参数` |
| `continue_on_error` | `bool` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`BatchExecutionError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.run.execute import execute_many

print(signature(execute_many))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.run.execute`
- 仓库相对路径：`packages/ai4e-core/run/execute.py:16`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.run.execute')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-run-execute-operation"></a>
## `ai4e_core.run.execute_operation`

- **层级**：`core.run`
- **稳定性**：`stable`
- **定义**：`execute_operation(job: dict, operation: Callable[..., dict[str, Any]], *, publish: Callable[[dict], None], canceled: Callable[[], bool]) -> dict[str, Any]`
- **规范定义名**：`ai4e_core.run.operation.execute_operation`

### 用途

建立独立运行后调用领域操作；领域返回状态，运行器负责收尾。

### 导入与签名

```python
from ai4e_core.run.operation import execute_operation
```

```text
execute_operation(job: dict, operation: Callable[..., dict[str, Any]], *, publish: Callable[[dict], None], canceled: Callable[[], bool]) -> dict[str, Any]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `job` | `dict` | `必填` |
| `operation` | `Callable[..., dict[str, Any]]` | `必填` |
| `publish` | `Callable[[dict], None]` | `必填关键字参数` |
| `canceled` | `Callable[[], bool]` | `必填关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, Any]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.run.operation import execute_operation

print(signature(execute_operation))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.run.operation`
- 仓库相对路径：`packages/ai4e-core/run/operation.py:43`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.run.operation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-run-for-each"></a>
## `ai4e_core.run.for_each`

- **层级**：`core.run`
- **稳定性**：`stable`
- **定义**：`for_each(stage: Stage) -> Callable[[dict], dict]`
- **规范定义名**：`ai4e_core.run.execute.for_each`

### 用途

将单样本 Stage 包成作业 Stage 的一步，不引入第二种执行容器。

### 导入与签名

```python
from ai4e_core.run.execute import for_each
```

```text
for_each(stage: Stage) -> Callable[[dict], dict]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `stage` | `Stage` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Callable[[dict], dict]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.run.execute import for_each

print(signature(for_each))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.run.execute`
- 仓库相对路径：`packages/ai4e-core/run/execute.py:59`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.run.execute')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-run-launch"></a>
## `ai4e_core.run.launch`

- **层级**：`core.run`
- **稳定性**：`stable`
- **定义**：`launch(stages, *, script, config_loader, argv=None, only=None, resolver=None) -> int`
- **规范定义名**：`ai4e_core.run.session.launch`

### 用途

通用启动入口；config_loader 接收配置路径和覆盖，返回完整生效配置。

### 导入与签名

```python
from ai4e_core.run.session import launch
```

```text
launch(stages, *, script, config_loader, argv=None, only=None, resolver=None) -> int
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `stages` | `未标注` | `必填` |
| `script` | `未标注` | `必填关键字参数` |
| `config_loader` | `未标注` | `必填关键字参数` |
| `argv` | `未标注` | `None` |
| `only` | `未标注` | `None` |
| `resolver` | `未标注` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`int`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.run.session import launch

print(signature(launch))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `gencp`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`, `parametric_pde`, `pcno`, `pcno_cylinder`, `safediffcon`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `extension.pcno`, `extension.pcno_cylinder`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `geothermal.pcno`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `parametric_pde.advection`, `parametric_pde.burgers`, `parametric_pde.convection_diffusion`, `parametric_pde.diffusion_trapezoid`, `parametric_pde.neumann_diffusion`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.free_wiring`, `recipe_extensions.gencp`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.sampling`, `recipe_extensions.wdno`, `safediffcon.burgers`, `safediffcon.tokamak`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_core.run.session`
- 仓库相对路径：`packages/ai4e-core/run/session.py:48`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.run.session')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-run-load-user-configuration"></a>
## `ai4e_core.run.load_user_configuration`

- **层级**：`core.run`
- **稳定性**：`stable`
- **定义**：`load_user_configuration(config_loader, path, overrides=None)`
- **规范定义名**：`ai4e_core.run.session.load_user_configuration`

### 用途

完整转交调用方的配置加载器；不读取或改写领域参数。

### 导入与签名

```python
from ai4e_core.run.session import load_user_configuration
```

```text
load_user_configuration(config_loader, path, overrides=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config_loader` | `未标注` | `必填` |
| `path` | `未标注` | `必填` |
| `overrides` | `未标注` | `None` |

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
from ai4e_core.run.session import load_user_configuration

print(signature(load_user_configuration))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.run.session`
- 仓库相对路径：`packages/ai4e-core/run/session.py:42`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.run.session')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-run-managed-run"></a>
## `ai4e_core.run.managed_run`

- **层级**：`core.run`
- **稳定性**：`stable`
- **定义**：`managed_run(context: RunContext, *, allow_unmanaged: bool=False)`
- **规范定义名**：`ai4e_core.run.provenance.managed_run`

### 用途

writer 提前落溯源，覆盖配置解析及启动失败；退出必须有真实会话摘要。

### 导入与签名

```python
from ai4e_core.run.provenance import managed_run
```

```text
managed_run(context: RunContext, *, allow_unmanaged: bool=False)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `context` | `RunContext` | `必填` |
| `allow_unmanaged` | `bool` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`RuntimeError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.run.provenance import managed_run

print(signature(managed_run))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.run.provenance`
- 仓库相对路径：`packages/ai4e-core/run/provenance.py:13`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.run.provenance')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-run-run-from-config"></a>
## `ai4e_core.run.run_from_config`

- **层级**：`core.run`
- **稳定性**：`stable`
- **定义**：`run_from_config(config_path: str | Path, *, builders: Mapping[str, Callable[[Mapping[str, Any]], Stage]], overrides: Mapping[str, Any] | Sequence[str] | None=None, run_root: str | Path | None=None, recipe_dir: str | Path | None=None, dry_run: bool=False, overwrite: bool=False, continue_on_error: bool=False) -> dict[str, Any]`
- **规范定义名**：`ai4e_core.run.runner.run_from_config`

### 用途

读配置并执行已选阶段，留下运行记录。

Args:
    config_path: 案例 YAML 路径。
    builders: 阶段名到装配函数。
    overrides: 点号覆盖。
    run_root: 运行根目录；缺省读 ``run.root`` 或当前目录。
    recipe_dir: 案例目录，用于解析相对的随包统计量路径。
    dry_run: 为真时不写训练 ``.pt``。
    overwrite: 将允许覆盖的执行意图传给业务写入步骤。
    continue_on_error: 逐项执行遇错时是否继续。

Returns:
    含运行目录、展开配置、批量计数和业务报告的作业上下文。

### 导入与签名

```python
from ai4e_core.run.runner import run_from_config
```

```text
run_from_config(config_path: str | Path, *, builders: Mapping[str, Callable[[Mapping[str, Any]], Stage]], overrides: Mapping[str, Any] | Sequence[str] | None=None, run_root: str | Path | None=None, recipe_dir: str | Path | None=None, dry_run: bool=False, overwrite: bool=False, continue_on_error: bool=False) -> dict[str, Any]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config_path` | `str | Path` | `必填` |
| `builders` | `Mapping[str, Callable[[Mapping[str, Any]], Stage]]` | `必填关键字参数` |
| `overrides` | `Mapping[str, Any] | Sequence[str] | None` | `None` |
| `run_root` | `str | Path | None` | `None` |
| `recipe_dir` | `str | Path | None` | `None` |
| `dry_run` | `bool` | `False` |
| `overwrite` | `bool` | `False` |
| `continue_on_error` | `bool` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, Any]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.run.runner import run_from_config

print(signature(run_from_config))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.run.runner`
- 仓库相对路径：`packages/ai4e-core/run/runner.py:17`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.run.runner')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-run-run-recipe"></a>
## `ai4e_core.run.run_recipe`

- **层级**：`core.run`
- **稳定性**：`stable`
- **定义**：`run_recipe(cfg, *, stages, script, only=None, flags=None, source_config=None, resolver=None) -> int`
- **规范定义名**：`ai4e_core.run.session.run_recipe`

### 用途

在各自日志阶段中执行已选函数并汇总；恢复阶段上下文，异常返回非零。

### 导入与签名

```python
from ai4e_core.run.session import run_recipe
```

```text
run_recipe(cfg, *, stages, script, only=None, flags=None, source_config=None, resolver=None) -> int
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cfg` | `未标注` | `必填` |
| `stages` | `未标注` | `必填关键字参数` |
| `script` | `未标注` | `必填关键字参数` |
| `only` | `未标注` | `None` |
| `flags` | `未标注` | `None` |
| `source_config` | `未标注` | `None` |
| `resolver` | `未标注` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`int`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

`data_root`, `run_root`

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.run.session import run_recipe

print(signature(run_recipe))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.run.session`
- 仓库相对路径：`packages/ai4e-core/run/session.py:79`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.run.session')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-run-stage"></a>
## `ai4e_core.run.stage`

- **层级**：`core.run`
- **稳定性**：`stable`
- **定义**：`stage(name, function, *args, **kwargs)`
- **规范定义名**：`ai4e_core.run.session.stage`

### 用途

在当前会话执行一个业务阶段，返回交付物并恢复日志上下文。

### 导入与签名

```python
from ai4e_core.run.session import stage
```

```text
stage(name, function, *args, **kwargs)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `name` | `未标注` | `必填` |
| `function` | `未标注` | `必填` |
| `*args` | `未标注` | `可变位置参数` |
| `**kwargs` | `未标注` | `可变关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`RuntimeError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.run.session import stage

print(signature(stage))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `gencp`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`, `parametric_pde`, `pcno`, `pcno_cylinder`, `safediffcon`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `extension.pcno`, `extension.pcno_cylinder`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `geothermal.pcno`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `parametric_pde.advection`, `parametric_pde.burgers`, `parametric_pde.convection_diffusion`, `parametric_pde.diffusion_trapezoid`, `parametric_pde.neumann_diffusion`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.free_wiring`, `recipe_extensions.gencp`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.sampling`, `recipe_extensions.wdno`, `safediffcon.burgers`, `safediffcon.tokamak`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_core.run.session`
- 仓库相对路径：`packages/ai4e-core/run/session.py:197`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.run.session')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
