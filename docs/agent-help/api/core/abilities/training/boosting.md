<!-- dojo-help: {"domain": "ai4e_core.abilities.training.boosting", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.training.boosting 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.training.boosting", "topic_id": "module:ai4e_core.abilities.training.boosting"} -->
# `ai4e_core.abilities.training.boosting` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-training-boosting-fit-boosting"></a>
## `ai4e_core.abilities.training.boosting.fit_boosting`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`fit_boosting(x: Any, y: Any, *, target_names: Sequence[str], feature_names: Sequence[str] | None=None, params: Mapping | None=None, num_boost_round: int=100, initial_model: LightGBMPredictor | None=None, cancelled: Callable[[], bool] | None=None, deadline: float | None=None) -> tuple[LightGBMPredictor, dict]`
- **规范定义名**：`ai4e_core.abilities.training.boosting.fit_boosting`

### 用途

训练[N,D]到[N,Q]独立提升树，返回普通预测对象和实际轮次诊断。

num_boost_round为本次请求的追加轮数。接续须同训练数组/字段/有效参数与
后端版本；原生追加不等于已证明与不中断逐值相同。每轮之前检查停止；
任一目标取消/超时会抛异常，不把部分目标模型冒充完整结果。deadline为
time.monotonic绝对时刻，单次原生树计算无法在内部抢占。

### 导入与签名

```python
from ai4e_core.abilities.training.boosting import fit_boosting
```

```text
fit_boosting(x: Any, y: Any, *, target_names: Sequence[str], feature_names: Sequence[str] | None=None, params: Mapping | None=None, num_boost_round: int=100, initial_model: LightGBMPredictor | None=None, cancelled: Callable[[], bool] | None=None, deadline: float | None=None) -> tuple[LightGBMPredictor, dict]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `Any` | `必填` |
| `y` | `Any` | `必填` |
| `target_names` | `Sequence[str]` | `必填关键字参数` |
| `feature_names` | `Sequence[str] | None` | `None` |
| `params` | `Mapping | None` | `None` |
| `num_boost_round` | `int` | `100` |
| `initial_model` | `LightGBMPredictor | None` | `None` |
| `cancelled` | `Callable[[], bool] | None` | `None` |
| `deadline` | `float | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`tuple[LightGBMPredictor, dict]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`InterruptedError`, `TimeoutError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.training.boosting import fit_boosting

print(signature(fit_boosting))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.training.boosting`
- 仓库相对路径：`packages/ai4e-core/abilities/training/boosting.py:113`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.boosting')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
