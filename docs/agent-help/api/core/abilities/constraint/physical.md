<!-- dojo-help: {"domain": "ai4e_core.abilities.constraint.physical", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.constraint.physical 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.constraint.physical", "topic_id": "module:ai4e_core.abilities.constraint.physical"} -->
# `ai4e_core.abilities.constraint.physical` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-constraint-physical-boundary-residual"></a>
## `ai4e_core.abilities.constraint.physical.boundary_residual`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`boundary_residual(*, value, gradient, normals, condition, target=None)`
- **规范定义名**：`ai4e_core.abilities.constraint.physical.boundary_residual`

### 用途

Dirichlet 或物理外法向 Neumann 残差；零梯度不等同于任意零通量。

### 导入与签名

```python
from ai4e_core.abilities.constraint.physical import boundary_residual
```

```text
boundary_residual(*, value, gradient, normals, condition, target=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `value` | `未标注` | `必填关键字参数` |
| `gradient` | `未标注` | `必填关键字参数` |
| `normals` | `未标注` | `必填关键字参数` |
| `condition` | `未标注` | `必填关键字参数` |
| `target` | `未标注` | `None` |

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
from ai4e_core.abilities.constraint.physical import boundary_residual

print(signature(boundary_residual))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.constraint.physical`
- 仓库相对路径：`packages/ai4e-core/abilities/constraint/physical.py:22`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.constraint.physical')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-constraint-physical-residual-loss"></a>
## `ai4e_core.abilities.constraint.physical.residual_loss`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`residual_loss(residual, *, loss='mse', reduction='mean')`
- **规范定义名**：`ai4e_core.abilities.constraint.physical.residual_loss`

### 用途

逐点残差归约；l2 为原 Burgers 使用的非平方全局范数。

### 导入与签名

```python
from ai4e_core.abilities.constraint.physical import residual_loss
```

```text
residual_loss(residual, *, loss='mse', reduction='mean')
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `residual` | `未标注` | `必填` |
| `loss` | `未标注` | `'mse'` |
| `reduction` | `未标注` | `'mean'` |

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
from ai4e_core.abilities.constraint.physical import residual_loss

print(signature(residual_loss))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.constraint.physical`
- 仓库相对路径：`packages/ai4e-core/abilities/constraint/physical.py:8`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.constraint.physical')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
