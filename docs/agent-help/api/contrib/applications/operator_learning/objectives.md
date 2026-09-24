<!-- dojo-help: {"domain": "ai4e_contrib.application.operator_learning.objectives", "kind": "api", "layer": "contrib.application", "summary": "ai4e_contrib.application.operator_learning.objectives 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.application.operator_learning.objectives", "topic_id": "module:ai4e_contrib.application.operator_learning.objectives"} -->
# `ai4e_contrib.application.operator_learning.objectives` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-application-operator-learning-objectives-fieldobjective"></a>
## `ai4e_contrib.application.operator_learning.objectives.FieldObjective`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`FieldObjective(statistics, *, physical_weight=0.0)`
- **规范定义名**：`ai4e_contrib.application.operator_learning.objectives.FieldObjective`

### 用途

普通训练目标对象，调用已有约束并保持梯度，不持有训练会话。

### 导入与签名

```python
from ai4e_contrib.application.operator_learning.objectives import FieldObjective
```

```text
FieldObjective(statistics, *, physical_weight=0.0)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `statistics` | `未标注` | `必填` |
| `physical_weight` | `未标注` | `0.0` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`FieldObjective`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.application.operator_learning.objectives import FieldObjective

print(signature(FieldObjective))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`
- 案例：`operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`

### 源码位置

- 模块：`ai4e_contrib.application.operator_learning.objectives`
- 仓库相对路径：`packages/ai4e-contrib/application/operator_learning/objectives.py:40`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.operator_learning.objectives')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-operator-learning-objectives-physical-terms"></a>
## `ai4e_contrib.application.operator_learning.objectives.physical_terms`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`physical_terms(prediction, target, valid, *, mean, scale)`
- **规范定义名**：`ai4e_contrib.application.operator_learning.objectives.physical_terms`

### 用途

分别返回监督MSE和非负解违约；用于正系数、非负源、零Dirichlet的Darcy。

样本的最外圈可能是离散内部点，不强加边界零值。非负解由椭圆方程
最大值原理给出，不依赖采样点是否恰落在边界。scale统一比较量纲；
这里不宣称评价了完整PDE残差。调用方负责来源方程的准入。

### 导入与签名

```python
from ai4e_contrib.application.operator_learning.objectives import physical_terms
```

```text
physical_terms(prediction, target, valid, *, mean, scale)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `prediction` | `未标注` | `必填` |
| `target` | `未标注` | `必填` |
| `valid` | `未标注` | `必填` |
| `mean` | `未标注` | `必填关键字参数` |
| `scale` | `未标注` | `必填关键字参数` |

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
from ai4e_contrib.application.operator_learning.objectives import physical_terms

print(signature(physical_terms))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.operator_learning.objectives`
- 仓库相对路径：`packages/ai4e-contrib/application/operator_learning/objectives.py:10`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.operator_learning.objectives')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
