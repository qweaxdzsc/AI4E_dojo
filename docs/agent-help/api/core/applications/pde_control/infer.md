<!-- dojo-help: {"domain": "ai4e_core.applications.pde_control.infer", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.pde_control.infer 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.pde_control.infer", "topic_id": "module:ai4e_core.applications.pde_control.infer"} -->
# `ai4e_core.applications.pde_control.infer` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-pde-control-infer-save-results"></a>
## `ai4e_core.applications.pde_control.infer.save_results`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`save_results(output, *, case, ids, target, paper_target, controls, prediction, response, checkpoint, q, metrics, derived=None)`
- **规范定义名**：`ai4e_core.applications.pde_control.infer.save_results`

### 用途

固定物理数组及来源，不把参考状态冒作生成控制的响应。

### 导入与签名

```python
from ai4e_core.applications.pde_control.infer import save_results
```

```text
save_results(output, *, case, ids, target, paper_target, controls, prediction, response, checkpoint, q, metrics, derived=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `output` | `未标注` | `必填` |
| `case` | `未标注` | `必填关键字参数` |
| `ids` | `未标注` | `必填关键字参数` |
| `target` | `未标注` | `必填关键字参数` |
| `paper_target` | `未标注` | `必填关键字参数` |
| `controls` | `未标注` | `必填关键字参数` |
| `prediction` | `未标注` | `必填关键字参数` |
| `response` | `未标注` | `必填关键字参数` |
| `checkpoint` | `未标注` | `必填关键字参数` |
| `q` | `未标注` | `必填关键字参数` |
| `metrics` | `未标注` | `必填关键字参数` |
| `derived` | `未标注` | `None` |

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
from ai4e_core.applications.pde_control.infer import save_results

print(signature(save_results))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`gencp`, `safediffcon`
- 案例：`gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `recipe_extensions.gencp`, `safediffcon.burgers`, `safediffcon.tokamak`

### 源码位置

- 模块：`ai4e_core.applications.pde_control.infer`
- 仓库相对路径：`packages/ai4e-core/applications/pde_control/infer.py:8`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.pde_control.infer')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
