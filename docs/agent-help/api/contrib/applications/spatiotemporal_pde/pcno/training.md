<!-- dojo-help: {"domain": "ai4e_contrib.application.spatiotemporal_pde.pcno.training", "kind": "api", "layer": "contrib.application", "summary": "ai4e_contrib.application.spatiotemporal_pde.pcno.training 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.application.spatiotemporal_pde.pcno.training", "topic_id": "module:ai4e_contrib.application.spatiotemporal_pde.pcno.training"} -->
# `ai4e_contrib.application.spatiotemporal_pde.pcno.training` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-application-spatiotemporal-pde-pcno-training-construct"></a>
## `ai4e_contrib.application.spatiotemporal_pde.pcno.training.construct`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`construct(cfg, branch)`
- **规范定义名**：`ai4e_contrib.application.spatiotemporal_pde.pcno.training.construct`

### 用途

固定模型随机性，显式使用用户选择的构造器。

### 导入与签名

```python
from ai4e_contrib.application.spatiotemporal_pde.pcno.training import construct
```

```text
construct(cfg, branch)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cfg` | `未标注` | `必填` |
| `branch` | `未标注` | `必填` |

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
from ai4e_contrib.application.spatiotemporal_pde.pcno.training import construct

print(signature(construct))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `gencp`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`, `pcno`, `safediffcon`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.shapenet_car_abupt`, `classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `geothermal.pcno`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.gencp`, `recipe_extensions.model_block`, `recipe_extensions.sampling`, `safediffcon.burgers`, `safediffcon.tokamak`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.application.spatiotemporal_pde.pcno.training`
- 仓库相对路径：`packages/ai4e-contrib/application/spatiotemporal_pde/pcno/training.py:38`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.spatiotemporal_pde.pcno.training')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-spatiotemporal-pde-pcno-training-contract"></a>
## `ai4e_contrib.application.spatiotemporal_pde.pcno.training.contract`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`contract(cfg, preparation, branch, arm)`
- **规范定义名**：`ai4e_contrib.application.spatiotemporal_pde.pcno.training.contract`

### 用途

冻结影响恢复的科学参数及组件源码身份。

### 导入与签名

```python
from ai4e_contrib.application.spatiotemporal_pde.pcno.training import contract
```

```text
contract(cfg, preparation, branch, arm)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cfg` | `未标注` | `必填` |
| `preparation` | `未标注` | `必填` |
| `branch` | `未标注` | `必填` |
| `arm` | `未标注` | `必填` |

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
from ai4e_contrib.application.spatiotemporal_pde.pcno.training import contract

print(signature(contract))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`
- 案例：`classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `recipe_extensions.pod_surrogate_replacement`, `recipe_extensions.research_state`, `recipe_extensions.tail_batch`

### 源码位置

- 模块：`ai4e_contrib.application.spatiotemporal_pde.pcno.training`
- 仓库相对路径：`packages/ai4e-contrib/application/spatiotemporal_pde/pcno/training.py:49`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.spatiotemporal_pde.pcno.training')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-spatiotemporal-pde-pcno-training-fork-warmup"></a>
## `ai4e_contrib.application.spatiotemporal_pde.pcno.training.fork_warmup`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`fork_warmup(cfg, preparation, warmup, arm, session)`
- **规范定义名**：`ai4e_contrib.application.spatiotemporal_pde.pcno.training.fork_warmup`

### 用途

显式从共同预热分叉；仅在物理/梯度权重为零的预热边界允许。

### 导入与签名

```python
from ai4e_contrib.application.spatiotemporal_pde.pcno.training import fork_warmup
```

```text
fork_warmup(cfg, preparation, warmup, arm, session)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cfg` | `未标注` | `必填` |
| `preparation` | `未标注` | `必填` |
| `warmup` | `未标注` | `必填` |
| `arm` | `未标注` | `必填` |
| `session` | `未标注` | `必填` |

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
from ai4e_contrib.application.spatiotemporal_pde.pcno.training import fork_warmup

print(signature(fork_warmup))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`pcno_cylinder`
- 案例：`pcno.double_cylinder`

### 源码位置

- 模块：`ai4e_contrib.application.spatiotemporal_pde.pcno.training`
- 仓库相对路径：`packages/ai4e-contrib/application/spatiotemporal_pde/pcno/training.py:128`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.spatiotemporal_pde.pcno.training')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-spatiotemporal-pde-pcno-training-load-preparation"></a>
## `ai4e_contrib.application.spatiotemporal_pde.pcno.training.load_preparation`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`load_preparation(path)`
- **规范定义名**：`ai4e_contrib.application.spatiotemporal_pde.pcno.training.load_preparation`

### 用途

仅接受已准入双圆柱准备，验证原始来源未改变。

### 导入与签名

```python
from ai4e_contrib.application.spatiotemporal_pde.pcno.training import load_preparation
```

```text
load_preparation(path)
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
from ai4e_contrib.application.spatiotemporal_pde.pcno.training import load_preparation

print(signature(load_preparation))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.spatiotemporal_pde.pcno.training`
- 仓库相对路径：`packages/ai4e-contrib/application/spatiotemporal_pde/pcno/training.py:23`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.spatiotemporal_pde.pcno.training')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-spatiotemporal-pde-pcno-training-publish-checkpoints"></a>
## `ai4e_contrib.application.spatiotemporal_pde.pcno.training.publish_checkpoints`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`publish_checkpoints(cfg, preparation, branches, output)`
- **规范定义名**：`ai4e_contrib.application.spatiotemporal_pde.pcno.training.publish_checkpoints`

### 用途

交付检查点引用和摘要，不复制大权重。

### 导入与签名

```python
from ai4e_contrib.application.spatiotemporal_pde.pcno.training import publish_checkpoints
```

```text
publish_checkpoints(cfg, preparation, branches, output)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cfg` | `未标注` | `必填` |
| `preparation` | `未标注` | `必填` |
| `branches` | `未标注` | `必填` |
| `output` | `未标注` | `必填` |

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
from ai4e_contrib.application.spatiotemporal_pde.pcno.training import publish_checkpoints

print(signature(publish_checkpoints))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`pcno`, `pcno_cylinder`
- 案例：`geothermal.pcno`, `pcno.double_cylinder`

### 源码位置

- 模块：`ai4e_contrib.application.spatiotemporal_pde.pcno.training`
- 仓库相对路径：`packages/ai4e-contrib/application/spatiotemporal_pde/pcno/training.py:144`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.spatiotemporal_pde.pcno.training')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-spatiotemporal-pde-pcno-training-tracked-session"></a>
## `ai4e_contrib.application.spatiotemporal_pde.pcno.training.tracked_session`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`tracked_session(session, preparation, resume=None)`
- **规范定义名**：`ai4e_contrib.application.spatiotemporal_pde.pcno.training.tracked_session`

### 用途

用公开checkpoint接口登记可恢复分支清单，记录仍由writer独占。

### 导入与签名

```python
from ai4e_contrib.application.spatiotemporal_pde.pcno.training import tracked_session
```

```text
tracked_session(session, preparation, resume=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `session` | `未标注` | `必填` |
| `preparation` | `未标注` | `必填` |
| `resume` | `未标注` | `None` |

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
from ai4e_contrib.application.spatiotemporal_pde.pcno.training import tracked_session

print(signature(tracked_session))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`pcno_cylinder`
- 案例：`pcno.double_cylinder`

### 源码位置

- 模块：`ai4e_contrib.application.spatiotemporal_pde.pcno.training`
- 仓库相对路径：`packages/ai4e-contrib/application/spatiotemporal_pde/pcno/training.py:166`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.spatiotemporal_pde.pcno.training')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-spatiotemporal-pde-pcno-training-train-branch"></a>
## `ai4e_contrib.application.spatiotemporal_pde.pcno.training.train_branch`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`train_branch(cfg, preparation, branch, arm, *, session, resume=None, stop_after=None, cancelled=None)`
- **规范定义名**：`ai4e_contrib.application.spatiotemporal_pde.pcno.training.train_branch`

### 用途

执行一个明确分支；stop_after用于测量/中断证据，不修改科学预算。

### 导入与签名

```python
from ai4e_contrib.application.spatiotemporal_pde.pcno.training import train_branch
```

```text
train_branch(cfg, preparation, branch, arm, *, session, resume=None, stop_after=None, cancelled=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cfg` | `未标注` | `必填` |
| `preparation` | `未标注` | `必填` |
| `branch` | `未标注` | `必填` |
| `arm` | `未标注` | `必填` |
| `session` | `未标注` | `必填关键字参数` |
| `resume` | `未标注` | `None` |
| `stop_after` | `未标注` | `None` |
| `cancelled` | `未标注` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FloatingPointError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.application.spatiotemporal_pde.pcno.training import train_branch

print(signature(train_branch))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`pcno`, `pcno_cylinder`
- 案例：`geothermal.pcno`, `pcno.double_cylinder`

### 源码位置

- 模块：`ai4e_contrib.application.spatiotemporal_pde.pcno.training`
- 仓库相对路径：`packages/ai4e-contrib/application/spatiotemporal_pde/pcno/training.py:64`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.spatiotemporal_pde.pcno.training')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
