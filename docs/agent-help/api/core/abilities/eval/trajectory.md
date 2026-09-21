<!-- dojo-help: {"domain": "ai4e_core.abilities.eval.trajectory", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.eval.trajectory 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.eval.trajectory", "topic_id": "module:ai4e_core.abilities.eval.trajectory"} -->
# `ai4e_core.abilities.eval.trajectory` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-eval-trajectory-horizon-mse"></a>
## `ai4e_core.abilities.eval.trajectory.horizon_mse`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`horizon_mse(prediction: torch.Tensor, target: torch.Tensor, horizons: tuple[int, ...], *, time_dim: int=1, includes_initial: bool=True) -> dict[str, float]`
- **规范定义名**：`ai4e_core.abilities.eval.trajectory.horizon_mse`

### 用途

计算从第一个预测帧到给定 horizon 的累计全元素 MSE。

当输入包含初始帧时排除索引 0，并对 ``1..horizon`` 求均值；否则对
``0..horizon-1`` 求均值。超过已有时间长度的指标不返回。该定义与滚动预测中
常见的 ``mse_H_steps`` 一致，不表示单独第 H 帧误差。

### 导入与签名

```python
from ai4e_core.abilities.eval.trajectory import horizon_mse
```

```text
horizon_mse(prediction: torch.Tensor, target: torch.Tensor, horizons: tuple[int, ...], *, time_dim: int=1, includes_initial: bool=True) -> dict[str, float]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `prediction` | `torch.Tensor` | `必填` |
| `target` | `torch.Tensor` | `必填` |
| `horizons` | `tuple[int, ...]` | `必填` |
| `time_dim` | `int` | `1` |
| `includes_initial` | `bool` | `True` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, float]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.eval.trajectory import horizon_mse

print(signature(horizon_mse))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.eval.trajectory`
- 仓库相对路径：`packages/ai4e-core/abilities/eval/trajectory.py:6`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.eval.trajectory')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-eval-trajectory-named-frame-metrics"></a>
## `ai4e_core.abilities.eval.trajectory.named_frame_metrics`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`named_frame_metrics(prediction, target, *, ids, times, fields, units)`
- **规范定义名**：`ai4e_core.abilities.eval.trajectory.named_frame_metrics`

### 用途

CPU float64 的逐样本/时间/场 MSE 与相对 L2，零范数写 None。

### 导入与签名

```python
from ai4e_core.abilities.eval.trajectory import named_frame_metrics
```

```text
named_frame_metrics(prediction, target, *, ids, times, fields, units)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `prediction` | `未标注` | `必填` |
| `target` | `未标注` | `必填` |
| `ids` | `未标注` | `必填关键字参数` |
| `times` | `未标注` | `必填关键字参数` |
| `fields` | `未标注` | `必填关键字参数` |
| `units` | `未标注` | `必填关键字参数` |

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
from ai4e_core.abilities.eval.trajectory import named_frame_metrics

print(signature(named_frame_metrics))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.eval.trajectory`
- 仓库相对路径：`packages/ai4e-core/abilities/eval/trajectory.py:70`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.eval.trajectory')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-eval-trajectory-trajectory-metrics"></a>
## `ai4e_core.abilities.eval.trajectory.trajectory_metrics`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`trajectory_metrics(prediction, target, *, axes=('B', 'T', 'H', 'W', 'C'))`
- **规范定义名**：`ai4e_core.abilities.eval.trajectory.trajectory_metrics`

### 用途

输入 B,T,H,W,C；返回逐样本/逐分量/逐物理帧相对 L2。

### 导入与签名

```python
from ai4e_core.abilities.eval.trajectory import trajectory_metrics
```

```text
trajectory_metrics(prediction, target, *, axes=('B', 'T', 'H', 'W', 'C'))
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `prediction` | `未标注` | `必填` |
| `target` | `未标注` | `必填` |
| `axes` | `未标注` | `('B', 'T', 'H', 'W', 'C')` |

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
from ai4e_core.abilities.eval.trajectory import trajectory_metrics

print(signature(trajectory_metrics))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.eval.trajectory`
- 仓库相对路径：`packages/ai4e-core/abilities/eval/trajectory.py:35`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.eval.trajectory')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
