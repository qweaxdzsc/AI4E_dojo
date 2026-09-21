<!-- dojo-help: {"domain": "ai4e_contrib.ability.constraint.safediffcon.objective", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.constraint.safediffcon.objective 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.constraint.safediffcon.objective", "topic_id": "module:ai4e_contrib.ability.constraint.safediffcon.objective"} -->
# `ai4e_contrib.ability.constraint.safediffcon.objective` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-constraint-safediffcon-objective-cost"></a>
## `ai4e_contrib.ability.constraint.safediffcon.objective.cost`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`cost(values: torch.Tensor, target, *, case: str, q: float=0.0, weight: float=1.0) -> torch.Tensor`
- **规范定义名**：`ai4e_contrib.ability.constraint.safediffcon.objective.cost`

### 用途

原 guidance/reweight 物理代价；目标使用显式提供的源码目标。

### 导入与签名

```python
from ai4e_contrib.ability.constraint.safediffcon.objective import cost
```

```text
cost(values: torch.Tensor, target, *, case: str, q: float=0.0, weight: float=1.0) -> torch.Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `values` | `torch.Tensor` | `必填` |
| `target` | `未标注` | `必填` |
| `case` | `str` | `必填关键字参数` |
| `q` | `float` | `0.0` |
| `weight` | `float` | `1.0` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`torch.Tensor`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.constraint.safediffcon.objective import cost

print(signature(cost))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.safediffcon`

### 源码位置

- 模块：`ai4e_contrib.ability.constraint.safediffcon.objective`
- 仓库相对路径：`packages/ai4e-contrib/ability/constraint/safediffcon/objective.py:19`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.constraint.safediffcon.objective')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-constraint-safediffcon-objective-diffusion-loss"></a>
## `ai4e_contrib.ability.constraint.safediffcon.objective.diffusion_loss`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`diffusion_loss(model: torch.nn.Module, values) -> torch.Tensor`
- **规范定义名**：`ai4e_contrib.ability.constraint.safediffcon.objective.diffusion_loss`

### 用途

调用原噪声损失，普通训练批次不改变模型内部损失归约。

### 导入与签名

```python
from ai4e_contrib.ability.constraint.safediffcon.objective import diffusion_loss
```

```text
diffusion_loss(model: torch.nn.Module, values) -> torch.Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model` | `torch.nn.Module` | `必填` |
| `values` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`torch.Tensor`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.constraint.safediffcon.objective import diffusion_loss

print(signature(diffusion_loss))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`safediffcon`
- 案例：`safediffcon.burgers`, `safediffcon.tokamak`

### 源码位置

- 模块：`ai4e_contrib.ability.constraint.safediffcon.objective`
- 仓库相对路径：`packages/ai4e-contrib/ability/constraint/safediffcon/objective.py:39`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.constraint.safediffcon.objective')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-constraint-safediffcon-objective-reweights"></a>
## `ai4e_contrib.ability.constraint.safediffcon.objective.reweights`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`reweights(values: torch.Tensor, target, *, case: str, q: float=0.0, weight: float=1.0) -> torch.Tensor`
- **规范定义名**：`ai4e_contrib.ability.constraint.safediffcon.objective.reweights`

### 用途

原指数重加权及全局样本归一化，全部下溢时保持原均匀回退。

### 导入与签名

```python
from ai4e_contrib.ability.constraint.safediffcon.objective import reweights
```

```text
reweights(values: torch.Tensor, target, *, case: str, q: float=0.0, weight: float=1.0) -> torch.Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `values` | `torch.Tensor` | `必填` |
| `target` | `未标注` | `必填` |
| `case` | `str` | `必填关键字参数` |
| `q` | `float` | `0.0` |
| `weight` | `float` | `1.0` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`torch.Tensor`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.constraint.safediffcon.objective import reweights

print(signature(reweights))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.constraint.safediffcon.objective`
- 仓库相对路径：`packages/ai4e-contrib/ability/constraint/safediffcon/objective.py:31`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.constraint.safediffcon.objective')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-constraint-safediffcon-objective-safety"></a>
## `ai4e_contrib.ability.constraint.safediffcon.objective.safety`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`safety(values: torch.Tensor, *, case: str, calibration: bool=False) -> torch.Tensor`
- **规范定义名**：`ai4e_contrib.ability.constraint.safediffcon.objective.safety`

### 用途

以原版统计量返回安全值：Burgers 平方最大值通道，Tokamak 最低q95。

### 导入与签名

```python
from ai4e_contrib.ability.constraint.safediffcon.objective import safety
```

```text
safety(values: torch.Tensor, *, case: str, calibration: bool=False) -> torch.Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `values` | `torch.Tensor` | `必填` |
| `case` | `str` | `必填关键字参数` |
| `calibration` | `bool` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`torch.Tensor`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.constraint.safediffcon.objective import safety

print(signature(safety))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.constraint.safediffcon.objective`
- 仓库相对路径：`packages/ai4e-contrib/ability/constraint/safediffcon/objective.py:8`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.constraint.safediffcon.objective')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
