<!-- dojo-help: {"domain": "ai4e_core.abilities.eval.result_metrics", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.eval.result_metrics 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.eval.result_metrics", "topic_id": "module:ai4e_core.abilities.eval.result_metrics"} -->
# `ai4e_core.abilities.eval.result_metrics` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-eval-result-metrics-evaluate-arrays"></a>
## `ai4e_core.abilities.eval.result_metrics.evaluate_arrays`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`evaluate_arrays(prediction, truth, *, component='scalar', mask=None, metrics=None)`
- **规范定义名**：`ai4e_core.abilities.eval.result_metrics.evaluate_arrays`

### 用途

在物理空间按有效实体计算；零分母返回不可定义而非伪造有限数。

### 导入与签名

```python
from ai4e_core.abilities.eval.result_metrics import evaluate_arrays
```

```text
evaluate_arrays(prediction, truth, *, component='scalar', mask=None, metrics=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `prediction` | `未标注` | `必填` |
| `truth` | `未标注` | `必填` |
| `component` | `未标注` | `'scalar'` |
| `mask` | `未标注` | `None` |
| `metrics` | `未标注` | `None` |

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
from ai4e_core.abilities.eval.result_metrics import evaluate_arrays

print(signature(evaluate_arrays))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.eval.result_metrics`
- 仓库相对路径：`packages/ai4e-core/abilities/eval/result_metrics.py:8`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.eval.result_metrics')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
