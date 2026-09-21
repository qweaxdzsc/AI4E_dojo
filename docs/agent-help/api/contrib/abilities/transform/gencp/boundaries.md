<!-- dojo-help: {"domain": "ai4e_contrib.ability.transform.gencp.boundaries", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.transform.gencp.boundaries 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.transform.gencp.boundaries", "topic_id": "module:ai4e_contrib.ability.transform.gencp.boundaries"} -->
# `ai4e_contrib.ability.transform.gencp.boundaries` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-transform-gencp-boundaries-clean-condition"></a>
## `ai4e_contrib.ability.transform.gencp.boundaries.clean_condition`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`clean_condition(state, condition, field, *, clean_neutron=True, clean_solid=True)`
- **规范定义名**：`ai4e_contrib.ability.transform.gencp.boundaries.clean_condition`

### 用途

覆盖已声明的条件通道，不修改监督目标速度。

### 导入与签名

```python
from ai4e_contrib.ability.transform.gencp.boundaries import clean_condition
```

```text
clean_condition(state, condition, field, *, clean_neutron=True, clean_solid=True)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `state` | `未标注` | `必填` |
| `condition` | `未标注` | `必填` |
| `field` | `未标注` | `必填` |
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
from ai4e_contrib.ability.transform.gencp.boundaries import clean_condition

print(signature(clean_condition))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.transform.gencp.boundaries`
- 仓库相对路径：`packages/ai4e-contrib/ability/transform/gencp/boundaries.py:8`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.transform.gencp.boundaries')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-transform-gencp-boundaries-neutron-inpainting"></a>
## `ai4e_contrib.ability.transform.gencp.boundaries.neutron_inpainting`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`neutron_inpainting(states, time, *, field, noise, clean)`
- **规范定义名**：`ai4e_contrib.ability.transform.gencp.boundaries.neutron_inpainting`

### 用途

顺序更新中子后，以同一边界噪声的概率路径回填左列。

### 导入与签名

```python
from ai4e_contrib.ability.transform.gencp.boundaries import neutron_inpainting
```

```text
neutron_inpainting(states, time, *, field, noise, clean)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `states` | `未标注` | `必填` |
| `time` | `未标注` | `必填` |
| `field` | `未标注` | `必填关键字参数` |
| `noise` | `未标注` | `必填关键字参数` |
| `clean` | `未标注` | `必填关键字参数` |

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
from ai4e_contrib.ability.transform.gencp.boundaries import neutron_inpainting

print(signature(neutron_inpainting))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`gencp`
- 案例：`gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`

### 源码位置

- 模块：`ai4e_contrib.ability.transform.gencp.boundaries`
- 仓库相对路径：`packages/ai4e-contrib/ability/transform/gencp/boundaries.py:18`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.transform.gencp.boundaries')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
