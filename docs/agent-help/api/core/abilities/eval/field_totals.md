<!-- dojo-help: {"domain": "ai4e_core.abilities.eval.field_totals", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.eval.field_totals 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.eval.field_totals", "topic_id": "module:ai4e_core.abilities.eval.field_totals"} -->
# `ai4e_core.abilities.eval.field_totals` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-eval-field-totals-fieldtotals"></a>
## `ai4e_core.abilities.eval.field_totals.FieldTotals`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`FieldTotals(names, *, vector_name='cf', vector_indices=(1, 2, 3))`
- **规范定义名**：`ai4e_core.abilities.eval.field_totals.FieldTotals`

### 用途

保留完整样本的 float64 累计次序，支持点数不相等的样本。

### 导入与签名

```python
from ai4e_core.abilities.eval.field_totals import FieldTotals
```

```text
FieldTotals(names, *, vector_name='cf', vector_indices=(1, 2, 3))
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `names` | `未标注` | `必填` |
| `vector_name` | `未标注` | `'cf'` |
| `vector_indices` | `未标注` | `(1, 2, 3)` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`FieldTotals`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.eval.field_totals import FieldTotals

print(signature(FieldTotals))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.eval.field_totals`
- 仓库相对路径：`packages/ai4e-core/abilities/eval/field_totals.py:6`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.eval.field_totals')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-eval-field-totals-fieldtotals-finalize"></a>
## `ai4e_core.abilities.eval.field_totals.FieldTotals.finalize`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`finalize(self)`
- **规范定义名**：`ai4e_core.abilities.eval.field_totals.FieldTotals.finalize`

### 用途

返回按点加权指标；零真值分母沿用最小正浮点门禁。

### 导入与签名

```python
from ai4e_core.abilities.eval.field_totals import FieldTotals
```

```text
finalize(self)
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

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
from ai4e_core.abilities.eval.field_totals import FieldTotals

print(signature(FieldTotals.finalize))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.eval.field_totals`
- 仓库相对路径：`packages/ai4e-core/abilities/eval/field_totals.py:40`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.eval.field_totals')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-eval-field-totals-fieldtotals-update"></a>
## `ai4e_core.abilities.eval.field_totals.FieldTotals.update`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`update(self, prediction, truth)`
- **规范定义名**：`ai4e_core.abilities.eval.field_totals.FieldTotals.update`

### 用途

累计真实点数；形状与有限值门禁不允许广播掩盖错位。

### 导入与签名

```python
from ai4e_core.abilities.eval.field_totals import FieldTotals
```

```text
update(self, prediction, truth)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `prediction` | `未标注` | `必填` |
| `truth` | `未标注` | `必填` |

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
from ai4e_core.abilities.eval.field_totals import FieldTotals

print(signature(FieldTotals.update))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`gencp`
- 案例：`gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `recipe_extensions.research_state`, `recipe_extensions.wdno`

### 源码位置

- 模块：`ai4e_core.abilities.eval.field_totals`
- 仓库相对路径：`packages/ai4e-core/abilities/eval/field_totals.py:18`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.eval.field_totals')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
