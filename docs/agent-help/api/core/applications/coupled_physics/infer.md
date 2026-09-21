<!-- dojo-help: {"domain": "ai4e_core.applications.coupled_physics.infer", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.coupled_physics.infer 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.coupled_physics.infer", "topic_id": "module:ai4e_core.applications.coupled_physics.infer"} -->
# `ai4e_core.applications.coupled_physics.infer` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-coupled-physics-infer-coupledprediction"></a>
## `ai4e_core.applications.coupled_physics.infer.CoupledPrediction`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`class CoupledPrediction`
- **规范定义名**：`ai4e_core.applications.coupled_physics.infer.CoupledPrediction`

### 用途

只在耦合业务使用的装配对象；不作为全仓组件协议。

### 导入与签名

```python
from ai4e_core.applications.coupled_physics.infer import CoupledPrediction
```

```text
class CoupledPrediction
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`CoupledPrediction`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.coupled_physics.infer import CoupledPrediction

print(signature(CoupledPrediction))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.coupled_physics.infer`
- 仓库相对路径：`packages/ai4e-core/applications/coupled_physics/infer.py:17`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.coupled_physics.infer')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-coupled-physics-infer-bind-field"></a>
## `ai4e_core.applications.coupled_physics.infer.bind_field`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`bind_field(job, name, *, velocity)`
- **规范定义名**：`ai4e_core.applications.coupled_physics.infer.bind_field`

### 用途

绑定一个场速度能力，返回当前装配对象。

### 导入与签名

```python
from ai4e_core.applications.coupled_physics.infer import bind_field
```

```text
bind_field(job, name, *, velocity)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `job` | `未标注` | `必填` |
| `name` | `未标注` | `必填` |
| `velocity` | `未标注` | `必填关键字参数` |

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
from ai4e_core.applications.coupled_physics.infer import bind_field

print(signature(bind_field))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`gencp`
- 案例：`gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`

### 源码位置

- 模块：`ai4e_core.applications.coupled_physics.infer`
- 仓库相对路径：`packages/ai4e-core/applications/coupled_physics/infer.py:30`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.coupled_physics.infer')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-coupled-physics-infer-configure-integration"></a>
## `ai4e_core.applications.coupled_physics.infer.configure_integration`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`configure_integration(job, *, step, order, boundary=None)`
- **规范定义名**：`ai4e_core.applications.coupled_physics.infer.configure_integration`

### 用途

绑定积分策略与显式场顺序。

### 导入与签名

```python
from ai4e_core.applications.coupled_physics.infer import configure_integration
```

```text
configure_integration(job, *, step, order, boundary=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `job` | `未标注` | `必填` |
| `step` | `未标注` | `必填关键字参数` |
| `order` | `未标注` | `必填关键字参数` |
| `boundary` | `未标注` | `None` |

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
from ai4e_core.applications.coupled_physics.infer import configure_integration

print(signature(configure_integration))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`gencp`
- 案例：`gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`

### 源码位置

- 模块：`ai4e_core.applications.coupled_physics.infer`
- 仓库相对路径：`packages/ai4e-core/applications/coupled_physics/infer.py:38`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.coupled_physics.infer')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-coupled-physics-infer-execute-prediction"></a>
## `ai4e_core.applications.coupled_physics.infer.execute_prediction`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`execute_prediction(job, *, observe=None, cancelled=None)`
- **规范定义名**：`ai4e_core.applications.coupled_physics.infer.execute_prediction`

### 用途

只执行已绑定积分，不从真值猜条件。

### 导入与签名

```python
from ai4e_core.applications.coupled_physics.infer import execute_prediction
```

```text
execute_prediction(job, *, observe=None, cancelled=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `job` | `未标注` | `必填` |
| `observe` | `未标注` | `None` |
| `cancelled` | `未标注` | `None` |

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
from ai4e_core.applications.coupled_physics.infer import execute_prediction

print(signature(execute_prediction))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`gencp`
- 案例：`gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`

### 源码位置

- 模块：`ai4e_core.applications.coupled_physics.infer`
- 仓库相对路径：`packages/ai4e-core/applications/coupled_physics/infer.py:44`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.coupled_physics.infer')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-coupled-physics-infer-save-results"></a>
## `ai4e_core.applications.coupled_physics.infer.save_results`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`save_results(predictions, targets, output, *, metadata)`
- **规范定义名**：`ai4e_core.applications.coupled_physics.infer.save_results`

### 用途

固定分场数组与来源，返回独立 post 所需清单。

### 导入与签名

```python
from ai4e_core.applications.coupled_physics.infer import save_results
```

```text
save_results(predictions, targets, output, *, metadata)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `predictions` | `未标注` | `必填` |
| `targets` | `未标注` | `必填` |
| `output` | `未标注` | `必填` |
| `metadata` | `未标注` | `必填关键字参数` |

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
from ai4e_core.applications.coupled_physics.infer import save_results

print(signature(save_results))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`gencp`, `safediffcon`
- 案例：`gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `recipe_extensions.gencp`, `safediffcon.burgers`, `safediffcon.tokamak`

### 源码位置

- 模块：`ai4e_core.applications.coupled_physics.infer`
- 仓库相对路径：`packages/ai4e-core/applications/coupled_physics/infer.py:71`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.coupled_physics.infer')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
