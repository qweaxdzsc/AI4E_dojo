<!-- dojo-help: {"domain": "ai4e_core.abilities.sampling.physical", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.sampling.physical 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.sampling.physical", "topic_id": "module:ai4e_core.abilities.sampling.physical"} -->
# `ai4e_core.abilities.sampling.physical` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-sampling-physical-grid-points"></a>
## `ai4e_core.abilities.sampling.physical.grid_points`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`grid_points(sample)`
- **规范定义名**：`ai4e_core.abilities.sampling.physical.grid_points`

### 用途

按声明轴顺序生成网格点，与展平真值一一对应。

### 导入与签名

```python
from ai4e_core.abilities.sampling.physical import grid_points
```

```text
grid_points(sample)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `sample` | `未标注` | `必填` |

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
from ai4e_core.abilities.sampling.physical import grid_points

print(signature(grid_points))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.sampling.physical`
- 仓库相对路径：`packages/ai4e-core/abilities/sampling/physical.py:16`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.sampling.physical')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-sampling-physical-periodic-points"></a>
## `ai4e_core.abilities.sampling.physical.periodic_points`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`periodic_points(sample, declaration, *, seed, name, boundaries)`
- **规范定义名**：`ai4e_core.abilities.sampling.physical.periodic_points`

### 用途

生成共享时间/切向坐标的平移周期点对，每行保留同一配对身份。

### 导入与签名

```python
from ai4e_core.abilities.sampling.physical import periodic_points
```

```text
periodic_points(sample, declaration, *, seed, name, boundaries)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `sample` | `未标注` | `必填` |
| `declaration` | `未标注` | `必填` |
| `seed` | `未标注` | `必填关键字参数` |
| `name` | `未标注` | `必填关键字参数` |
| `boundaries` | `未标注` | `必填关键字参数` |

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
from ai4e_core.abilities.sampling.physical import periodic_points

print(signature(periodic_points))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.sampling.physical`
- 仓库相对路径：`packages/ai4e-core/abilities/sampling/physical.py:124`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.sampling.physical')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-sampling-physical-sample-points"></a>
## `ai4e_core.abilities.sampling.physical.sample_points`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`sample_points(sample, declaration, *, seed, name, boundary=None, initial=False, supervised=False)`
- **规范定义名**：`ai4e_core.abilities.sampling.physical.sample_points`

### 用途

准备单个具名点集；预算不足、未知键、无标签监督点直接失败。

### 导入与签名

```python
from ai4e_core.abilities.sampling.physical import sample_points
```

```text
sample_points(sample, declaration, *, seed, name, boundary=None, initial=False, supervised=False)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `sample` | `未标注` | `必填` |
| `declaration` | `未标注` | `必填` |
| `seed` | `未标注` | `必填关键字参数` |
| `name` | `未标注` | `必填关键字参数` |
| `boundary` | `未标注` | `None` |
| `initial` | `未标注` | `False` |
| `supervised` | `未标注` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`TypeError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.sampling.physical import sample_points

print(signature(sample_points))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`
- 案例：`classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.resunet`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`, `recipe_extensions.operator_physical_loss`

### 源码位置

- 模块：`ai4e_core.abilities.sampling.physical`
- 仓库相对路径：`packages/ai4e-core/abilities/sampling/physical.py:21`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.sampling.physical')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
