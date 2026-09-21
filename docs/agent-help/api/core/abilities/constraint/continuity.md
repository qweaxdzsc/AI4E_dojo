<!-- dojo-help: {"domain": "ai4e_core.abilities.constraint.continuity", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.constraint.continuity 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.constraint.continuity", "topic_id": "module:ai4e_core.abilities.constraint.continuity"} -->
# `ai4e_core.abilities.constraint.continuity` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-constraint-continuity-staggered-divergence"></a>
## `ai4e_core.abilities.constraint.continuity.staggered_divergence`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`staggered_divergence(velocity, spacing=(1.0, 1.0))`
- **规范定义名**：`ai4e_core.abilities.constraint.continuity.staggered_divergence`

### 用途

对 (..., X, Y, 2) 面速度求前向通量散度，输出 (..., X-1, Y-1)。

### 导入与签名

```python
from ai4e_core.abilities.constraint.continuity import staggered_divergence
```

```text
staggered_divergence(velocity, spacing=(1.0, 1.0))
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `velocity` | `未标注` | `必填` |
| `spacing` | `未标注` | `(1.0, 1.0)` |

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
from ai4e_core.abilities.constraint.continuity import staggered_divergence

print(signature(staggered_divergence))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.constraint.continuity`
- 仓库相对路径：`packages/ai4e-core/abilities/constraint/continuity.py:9`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.constraint.continuity')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-constraint-continuity-triangle-divergence"></a>
## `ai4e_core.abilities.constraint.continuity.triangle_divergence`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`triangle_divergence(velocity, cells, inverse)`
- **规范定义名**：`ai4e_core.abilities.constraint.continuity.triangle_divergence`

### 用途

二维节点速度的单元散度，不声称等同于来源求解器离散。

### 导入与签名

```python
from ai4e_core.abilities.constraint.continuity import triangle_divergence
```

```text
triangle_divergence(velocity, cells, inverse)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `velocity` | `未标注` | `必填` |
| `cells` | `未标注` | `必填` |
| `inverse` | `未标注` | `必填` |

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
from ai4e_core.abilities.constraint.continuity import triangle_divergence

print(signature(triangle_divergence))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.constraint.continuity`
- 仓库相对路径：`packages/ai4e-core/abilities/constraint/continuity.py:44`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.constraint.continuity')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-constraint-continuity-triangle-geometry"></a>
## `ai4e_core.abilities.constraint.continuity.triangle_geometry`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`triangle_geometry(position, cells)`
- **规范定义名**：`ai4e_core.abilities.constraint.continuity.triangle_geometry`

### 用途

返回三角形梯度变换和面积；拒绝退化或非法连接关系。

### 导入与签名

```python
from ai4e_core.abilities.constraint.continuity import triangle_geometry
```

```text
triangle_geometry(position, cells)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `position` | `未标注` | `必填` |
| `cells` | `未标注` | `必填` |

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
from ai4e_core.abilities.constraint.continuity import triangle_geometry

print(signature(triangle_geometry))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.constraint.continuity`
- 仓库相对路径：`packages/ai4e-core/abilities/constraint/continuity.py:21`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.constraint.continuity')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-constraint-continuity-triangle-gradient"></a>
## `ai4e_core.abilities.constraint.continuity.triangle_gradient`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`triangle_gradient(values, cells, inverse)`
- **规范定义名**：`ai4e_core.abilities.constraint.continuity.triangle_gradient`

### 用途

节点值 (..., N, C) 返回 (..., triangles, C, xy) 的可微梯度。

### 导入与签名

```python
from ai4e_core.abilities.constraint.continuity import triangle_gradient
```

```text
triangle_gradient(values, cells, inverse)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `values` | `未标注` | `必填` |
| `cells` | `未标注` | `必填` |
| `inverse` | `未标注` | `必填` |

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
from ai4e_core.abilities.constraint.continuity import triangle_gradient

print(signature(triangle_gradient))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.constraint.continuity`
- 仓库相对路径：`packages/ai4e-core/abilities/constraint/continuity.py:37`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.constraint.continuity')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-constraint-continuity-weighted-mean-square"></a>
## `ai4e_core.abilities.constraint.continuity.weighted_mean_square`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`weighted_mean_square(values, weights)`
- **规范定义名**：`ai4e_core.abilities.constraint.continuity.weighted_mean_square`

### 用途

有效域加权均方；空域或非法权重明确失败。

### 导入与签名

```python
from ai4e_core.abilities.constraint.continuity import weighted_mean_square
```

```text
weighted_mean_square(values, weights)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `values` | `未标注` | `必填` |
| `weights` | `未标注` | `必填` |

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
from ai4e_core.abilities.constraint.continuity import weighted_mean_square

print(signature(weighted_mean_square))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.constraint.continuity`
- 仓库相对路径：`packages/ai4e-core/abilities/constraint/continuity.py:52`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.constraint.continuity')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
