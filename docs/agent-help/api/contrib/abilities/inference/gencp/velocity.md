<!-- dojo-help: {"domain": "ai4e_contrib.ability.inference.gencp.velocity", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.inference.gencp.velocity 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.inference.gencp.velocity", "topic_id": "module:ai4e_contrib.ability.inference.gencp.velocity"} -->
# `ai4e_contrib.ability.inference.gencp.velocity` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-inference-gencp-velocity-fsi-synchronous-step"></a>
## `ai4e_contrib.ability.inference.gencp.velocity.fsi_synchronous_step`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`fsi_synchronous_step(states, time, dt, velocities, order, boundary=None)`
- **规范定义名**：`ai4e_contrib.ability.inference.gencp.velocity.fsi_synchronous_step`

### 用途

保留参考每步未使用路径噪声的消耗，再执行同步更新。

### 导入与签名

```python
from ai4e_contrib.ability.inference.gencp.velocity import fsi_synchronous_step
```

```text
fsi_synchronous_step(states, time, dt, velocities, order, boundary=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `states` | `未标注` | `必填` |
| `time` | `未标注` | `必填` |
| `dt` | `未标注` | `必填` |
| `velocities` | `未标注` | `必填` |
| `order` | `未标注` | `必填` |
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
from ai4e_contrib.ability.inference.gencp.velocity import fsi_synchronous_step

print(signature(fsi_synchronous_step))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`gencp`
- 案例：`gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`

### 源码位置

- 模块：`ai4e_contrib.ability.inference.gencp.velocity`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/gencp/velocity.py:58`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.gencp.velocity')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-gencp-velocity-fsi-velocity"></a>
## `ai4e_contrib.ability.inference.gencp.velocity.fsi_velocity`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`fsi_velocity(model, states, time, *, history)`
- **规范定义名**：`ai4e_contrib.ability.inference.gencp.velocity.fsi_velocity`

### 用途

求当前 FSI 联合状态的一个场速度。

### 导入与签名

```python
from ai4e_contrib.ability.inference.gencp.velocity import fsi_velocity
```

```text
fsi_velocity(model, states, time, *, history)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model` | `未标注` | `必填` |
| `states` | `未标注` | `必填` |
| `time` | `未标注` | `必填` |
| `history` | `未标注` | `必填关键字参数` |

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
from ai4e_contrib.ability.inference.gencp.velocity import fsi_velocity

print(signature(fsi_velocity))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.gencp.velocity`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/gencp/velocity.py:10`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.gencp.velocity')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-gencp-velocity-nt-velocity"></a>
## `ai4e_contrib.ability.inference.gencp.velocity.nt_velocity`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`nt_velocity(model, states, time, *, field, condition, boundary)`
- **规范定义名**：`ai4e_contrib.ability.inference.gencp.velocity.nt_velocity`

### 用途

条件映射后仅缩放网络时间；积分时间仍为 [0,1]。

### 导入与签名

```python
from ai4e_contrib.ability.inference.gencp.velocity import nt_velocity
```

```text
nt_velocity(model, states, time, *, field, condition, boundary)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model` | `未标注` | `必填` |
| `states` | `未标注` | `必填` |
| `time` | `未标注` | `必填` |
| `field` | `未标注` | `必填关键字参数` |
| `condition` | `未标注` | `必填关键字参数` |
| `boundary` | `未标注` | `必填关键字参数` |

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
from ai4e_contrib.ability.inference.gencp.velocity import nt_velocity

print(signature(nt_velocity))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.gencp.velocity`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/gencp/velocity.py:17`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.gencp.velocity')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-gencp-velocity-single-field"></a>
## `ai4e_contrib.ability.inference.gencp.velocity.single_field`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`single_field(model, condition, target, *, dataset, field, points=10, clean_neutron=True, clean_solid=True)`
- **规范定义名**：`ai4e_contrib.ability.inference.gencp.velocity.single_field`

### 用途

保留原单场验证 N 个网格点、N-1 步；已知其他场条件允许使用。

### 导入与签名

```python
from ai4e_contrib.ability.inference.gencp.velocity import single_field
```

```text
single_field(model, condition, target, *, dataset, field, points=10, clean_neutron=True, clean_solid=True)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model` | `未标注` | `必填` |
| `condition` | `未标注` | `必填` |
| `target` | `未标注` | `必填` |
| `dataset` | `未标注` | `必填关键字参数` |
| `field` | `未标注` | `必填关键字参数` |
| `points` | `未标注` | `10` |
| `clean_neutron` | `未标注` | `True` |
| `clean_solid` | `未标注` | `True` |

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
from ai4e_contrib.ability.inference.gencp.velocity import single_field

print(signature(single_field))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.gencp.velocity`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/gencp/velocity.py:28`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.gencp.velocity')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
