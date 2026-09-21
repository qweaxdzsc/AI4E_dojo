<!-- dojo-help: {"domain": "ai4e_core.abilities.constraint.spatiotemporal_field", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.constraint.spatiotemporal_field 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.constraint.spatiotemporal_field", "topic_id": "module:ai4e_core.abilities.constraint.spatiotemporal_field"} -->
# `ai4e_core.abilities.constraint.spatiotemporal_field` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-constraint-spatiotemporal-field-compute-enhanced-gradient-loss"></a>
## `ai4e_core.abilities.constraint.spatiotemporal_field.compute_enhanced_gradient_loss`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`compute_enhanced_gradient_loss(pred, target, eps=0.0001, max_rel=80.0)`
- **规范定义名**：`ai4e_core.abilities.constraint.spatiotemporal_field.compute_enhanced_gradient_loss`

### 用途

五轴时空场的相对梯度及井距加权监督；压力和温度为当前权重策略：compute_enhanced_gradient_loss；保留来源算法、参数与权重布局。

### 导入与签名

```python
from ai4e_core.abilities.constraint.spatiotemporal_field import compute_enhanced_gradient_loss
```

```text
compute_enhanced_gradient_loss(pred, target, eps=0.0001, max_rel=80.0)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `pred` | `未标注` | `必填` |
| `target` | `未标注` | `必填` |
| `eps` | `未标注` | `0.0001` |
| `max_rel` | `未标注` | `80.0` |

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
from ai4e_core.abilities.constraint.spatiotemporal_field import compute_enhanced_gradient_loss

print(signature(compute_enhanced_gradient_loss))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.constraint.spatiotemporal_field`
- 仓库相对路径：`packages/ai4e-core/abilities/constraint/spatiotemporal_field.py:9`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.constraint.spatiotemporal_field')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-constraint-spatiotemporal-field-create-smooth-weight-map"></a>
## `ai4e_core.abilities.constraint.spatiotemporal_field.create_smooth_weight_map`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`create_smooth_weight_map(pred, target, dist_inj, dist_prod, sigma=3.0, task='pressure', alpha_base=1.0, epsilon=0.0001)`
- **规范定义名**：`ai4e_core.abilities.constraint.spatiotemporal_field.create_smooth_weight_map`

### 用途

五轴时空场的相对梯度及井距加权监督；压力和温度为当前权重策略：create_smooth_weight_map；保留来源算法、参数与权重布局。

### 导入与签名

```python
from ai4e_core.abilities.constraint.spatiotemporal_field import create_smooth_weight_map
```

```text
create_smooth_weight_map(pred, target, dist_inj, dist_prod, sigma=3.0, task='pressure', alpha_base=1.0, epsilon=0.0001)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `pred` | `未标注` | `必填` |
| `target` | `未标注` | `必填` |
| `dist_inj` | `未标注` | `必填` |
| `dist_prod` | `未标注` | `必填` |
| `sigma` | `未标注` | `3.0` |
| `task` | `未标注` | `'pressure'` |
| `alpha_base` | `未标注` | `1.0` |
| `epsilon` | `未标注` | `0.0001` |

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
from ai4e_core.abilities.constraint.spatiotemporal_field import create_smooth_weight_map

print(signature(create_smooth_weight_map))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.constraint.spatiotemporal_field`
- 仓库相对路径：`packages/ai4e-core/abilities/constraint/spatiotemporal_field.py:41`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.constraint.spatiotemporal_field')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-constraint-spatiotemporal-field-weighted-mse"></a>
## `ai4e_core.abilities.constraint.spatiotemporal_field.weighted_mse`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`weighted_mse(pred, target, weight)`
- **规范定义名**：`ai4e_core.abilities.constraint.spatiotemporal_field.weighted_mse`

### 用途

五轴时空场的相对梯度及井距加权监督；压力和温度为当前权重策略：weighted_mse；保留来源算法、参数与权重布局。

### 导入与签名

```python
from ai4e_core.abilities.constraint.spatiotemporal_field import weighted_mse
```

```text
weighted_mse(pred, target, weight)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `pred` | `未标注` | `必填` |
| `target` | `未标注` | `必填` |
| `weight` | `未标注` | `必填` |

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
from ai4e_core.abilities.constraint.spatiotemporal_field import weighted_mse

print(signature(weighted_mse))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.constraint.spatiotemporal_field`
- 仓库相对路径：`packages/ai4e-core/abilities/constraint/spatiotemporal_field.py:69`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.constraint.spatiotemporal_field')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
