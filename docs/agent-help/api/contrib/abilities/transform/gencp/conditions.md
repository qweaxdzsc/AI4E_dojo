<!-- dojo-help: {"domain": "ai4e_contrib.ability.transform.gencp.conditions", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.transform.gencp.conditions 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.transform.gencp.conditions", "topic_id": "module:ai4e_contrib.ability.transform.gencp.conditions"} -->
# `ai4e_contrib.ability.transform.gencp.conditions` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-transform-gencp-conditions-fluid-condition"></a>
## `ai4e_contrib.ability.transform.gencp.conditions.fluid_condition`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`fluid_condition(states, boundary)`
- **规范定义名**：`ai4e_contrib.ability.transform.gencp.conditions.fluid_condition`

### 用途

重复固体最右两列归一化温度；保留原实现而非解释成热通量。

### 导入与签名

```python
from ai4e_contrib.ability.transform.gencp.conditions import fluid_condition
```

```text
fluid_condition(states, boundary)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `states` | `未标注` | `必填` |
| `boundary` | `未标注` | `必填` |

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
from ai4e_contrib.ability.transform.gencp.conditions import fluid_condition

print(signature(fluid_condition))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`gencp`
- 案例：`gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `recipe_extensions.gencp`

### 源码位置

- 模块：`ai4e_contrib.ability.transform.gencp.conditions`
- 仓库相对路径：`packages/ai4e-contrib/ability/transform/gencp/conditions.py:24`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.transform.gencp.conditions')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-transform-gencp-conditions-neutron-condition"></a>
## `ai4e_contrib.ability.transform.gencp.conditions.neutron_condition`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`neutron_condition(states, boundary)`
- **规范定义名**：`ai4e_contrib.ability.transform.gencp.conditions.neutron_condition`

### 用途

固体/流体温度沿宽度拼接，并广播中子外部边界。

### 导入与签名

```python
from ai4e_contrib.ability.transform.gencp.conditions import neutron_condition
```

```text
neutron_condition(states, boundary)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `states` | `未标注` | `必填` |
| `boundary` | `未标注` | `必填` |

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
from ai4e_contrib.ability.transform.gencp.conditions import neutron_condition

print(signature(neutron_condition))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`gencp`
- 案例：`gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`

### 源码位置

- 模块：`ai4e_contrib.ability.transform.gencp.conditions`
- 仓库相对路径：`packages/ai4e-contrib/ability/transform/gencp/conditions.py:6`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.transform.gencp.conditions')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-transform-gencp-conditions-solid-condition"></a>
## `ai4e_contrib.ability.transform.gencp.conditions.solid_condition`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`solid_condition(states, boundary)`
- **规范定义名**：`ai4e_contrib.ability.transform.gencp.conditions.solid_condition`

### 用途

使用中子左八列、流体第一列温度与外部固体左边界。

### 导入与签名

```python
from ai4e_contrib.ability.transform.gencp.conditions import solid_condition
```

```text
solid_condition(states, boundary)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `states` | `未标注` | `必填` |
| `boundary` | `未标注` | `必填` |

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
from ai4e_contrib.ability.transform.gencp.conditions import solid_condition

print(signature(solid_condition))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`gencp`
- 案例：`gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`

### 源码位置

- 模块：`ai4e_contrib.ability.transform.gencp.conditions`
- 仓库相对路径：`packages/ai4e-contrib/ability/transform/gencp/conditions.py:12`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.transform.gencp.conditions')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
