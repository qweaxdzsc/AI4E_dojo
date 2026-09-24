<!-- dojo-help: {"domain": "ai4e_core.abilities.training.selection", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.training.selection 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.training.selection", "topic_id": "module:ai4e_core.abilities.training.selection"} -->
# `ai4e_core.abilities.training.selection` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-training-selection-bestmetric"></a>
## `ai4e_core.abilities.training.selection.BestMetric`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`BestMetric(*, mode: Literal['min', 'max']='min', tie: Literal['first', 'last']='first')`
- **规范定义名**：`ai4e_core.abilities.training.selection.BestMetric`

### 用途

在同一评价口径内选优；保存成功后显式提交状态。

mode 为 min/max；tie=first 保留先到者，tie=last 接受相等的新候选。
source 是不透明非空字符串，可标识普通、EMA 或其他权重来源。
本对象不复制权重、不写文件，也不验证指标单位或候选模型身份。
调用者须冻结真正受评权重，在 writer 保存成功后 commit，并将最佳快照
与本状态共同纳入恢复检查点。多个线程或进程不能共享一次判断/提交事务。

### 导入与签名

```python
from ai4e_core.abilities.training.selection import BestMetric
```

```text
BestMetric(*, mode: Literal['min', 'max']='min', tie: Literal['first', 'last']='first')
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `mode` | `Literal['min', 'max']` | `'min'` |
| `tie` | `Literal['first', 'last']` | `'first'` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`BestMetric`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.training.selection import BestMetric

print(signature(BestMetric))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.research_state`

### 源码位置

- 模块：`ai4e_core.abilities.training.selection`
- 仓库相对路径：`packages/ai4e-core/abilities/training/selection.py:20`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.selection')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-selection-bestmetric-commit"></a>
## `ai4e_core.abilities.training.selection.BestMetric.commit`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`commit(self, value: float, *, step: int, source: str) -> None`
- **规范定义名**：`ai4e_core.abilities.training.selection.BestMetric.commit`

### 用途

保存成功后提交胜出候选；非法元信息或不胜出的值抛 ValueError。

### 导入与签名

```python
from ai4e_core.abilities.training.selection import BestMetric
```

```text
commit(self, value: float, *, step: int, source: str) -> None
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `value` | `float` | `必填` |
| `step` | `int` | `必填关键字参数` |
| `source` | `str` | `必填关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`None`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.training.selection import BestMetric

print(signature(BestMetric.commit))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.research_state`

### 源码位置

- 模块：`ai4e_core.abilities.training.selection`
- 仓库相对路径：`packages/ai4e-core/abilities/training/selection.py:49`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.selection')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-selection-bestmetric-improves"></a>
## `ai4e_core.abilities.training.selection.BestMetric.improves`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`improves(self, value: float) -> bool`
- **规范定义名**：`ai4e_core.abilities.training.selection.BestMetric.improves`

### 用途

校验并判断候选，不修改状态；NaN/Inf 不作为落选静默忽略。

### 导入与签名

```python
from ai4e_core.abilities.training.selection import BestMetric
```

```text
improves(self, value: float) -> bool
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `value` | `float` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`bool`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.training.selection import BestMetric

print(signature(BestMetric.improves))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.research_state`

### 源码位置

- 模块：`ai4e_core.abilities.training.selection`
- 仓库相对路径：`packages/ai4e-core/abilities/training/selection.py:40`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.selection')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-selection-bestmetric-load-state-dict"></a>
## `ai4e_core.abilities.training.selection.BestMetric.load_state_dict`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`load_state_dict(self, state: dict[str, Any]) -> None`
- **规范定义名**：`ai4e_core.abilities.training.selection.BestMetric.load_state_dict`

### 用途

校验通过后恢复标量状态；失败不改变当前选择。

### 导入与签名

```python
from ai4e_core.abilities.training.selection import BestMetric
```

```text
load_state_dict(self, state: dict[str, Any]) -> None
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `state` | `dict[str, Any]` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`None`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.training.selection import BestMetric

print(signature(BestMetric.load_state_dict))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`
- 案例：`classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `recipe_extensions.pod_surrogate_replacement`, `recipe_extensions.research_state`

### 源码位置

- 模块：`ai4e_core.abilities.training.selection`
- 仓库相对路径：`packages/ai4e-core/abilities/training/selection.py:93`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.selection')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-selection-bestmetric-state-dict"></a>
## `ai4e_core.abilities.training.selection.BestMetric.state_dict`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`state_dict(self) -> dict[str, Any]`
- **规范定义名**：`ai4e_core.abilities.training.selection.BestMetric.state_dict`

### 用途

返回普通标量状态；尚未选优时 best/step/source 均为 None。

### 导入与签名

```python
from ai4e_core.abilities.training.selection import BestMetric
```

```text
state_dict(self) -> dict[str, Any]
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

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
from ai4e_core.abilities.training.selection import BestMetric

print(signature(BestMetric.state_dict))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`
- 案例：`classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `recipe_extensions.pod_surrogate_replacement`, `recipe_extensions.research_state`

### 源码位置

- 模块：`ai4e_core.abilities.training.selection`
- 仓库相对路径：`packages/ai4e-core/abilities/training/selection.py:58`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.selection')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-selection-bestmetric-validate-state-dict"></a>
## `ai4e_core.abilities.training.selection.BestMetric.validate_state_dict`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`validate_state_dict(self, state: dict[str, Any]) -> None`
- **规范定义名**：`ai4e_core.abilities.training.selection.BestMetric.validate_state_dict`

### 用途

核对政策和选择元信息；不读取文件或修改当前选择。

### 导入与签名

```python
from ai4e_core.abilities.training.selection import BestMetric
```

```text
validate_state_dict(self, state: dict[str, Any]) -> None
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `state` | `dict[str, Any]` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`None`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.training.selection import BestMetric

print(signature(BestMetric.validate_state_dict))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.research_state`

### 源码位置

- 模块：`ai4e_core.abilities.training.selection`
- 仓库相对路径：`packages/ai4e-core/abilities/training/selection.py:69`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.selection')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
