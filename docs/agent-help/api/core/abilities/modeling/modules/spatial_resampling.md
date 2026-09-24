<!-- dojo-help: {"domain": "ai4e_core.abilities.modeling.modules.spatial_resampling", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.modeling.modules.spatial_resampling 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.modeling.modules.spatial_resampling", "topic_id": "module:ai4e_core.abilities.modeling.modules.spatial_resampling"} -->
# `ai4e_core.abilities.modeling.modules.spatial_resampling` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-modeling-modules-spatial-resampling-spatialdownsample"></a>
## `ai4e_core.abilities.modeling.modules.spatial_resampling.SpatialDownsample`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`SpatialDownsample(spatial_dim: int, *, projection: nn.Module | None=None)`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.spatial_resampling.SpatialDownsample`

### 用途

最大池化并可接通道投影；轴长不足时拒绝，不静默填充。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.spatial_resampling import SpatialDownsample
```

```text
SpatialDownsample(spatial_dim: int, *, projection: nn.Module | None=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `spatial_dim` | `int` | `必填` |
| `projection` | `nn.Module | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`SpatialDownsample`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.spatial_resampling import SpatialDownsample

print(signature(SpatialDownsample))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.resunet`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.spatial_resampling`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/spatial_resampling.py:23`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.spatial_resampling')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-spatial-resampling-spatialdownsample-forward"></a>
## `ai4e_core.abilities.modeling.modules.spatial_resampling.SpatialDownsample.forward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, value: Tensor) -> Tensor`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.spatial_resampling.SpatialDownsample.forward`

### 用途

各空间轴缩小二倍后应用显式投影。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.spatial_resampling import SpatialDownsample
```

```text
forward(self, value: Tensor) -> Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `value` | `Tensor` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Tensor`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.spatial_resampling import SpatialDownsample

print(signature(SpatialDownsample.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.spatial_resampling`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/spatial_resampling.py:34`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.spatial_resampling')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-spatial-resampling-spatialupsample"></a>
## `ai4e_core.abilities.modeling.modules.spatial_resampling.SpatialUpsample`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`SpatialUpsample(*, projection: nn.Module | None=None)`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.spatial_resampling.SpatialUpsample`

### 用途

插值到声明尺寸后应用可训练投影。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.spatial_resampling import SpatialUpsample
```

```text
SpatialUpsample(*, projection: nn.Module | None=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `projection` | `nn.Module | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`SpatialUpsample`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.spatial_resampling import SpatialUpsample

print(signature(SpatialUpsample))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.spatial_resampling`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/spatial_resampling.py:41`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.spatial_resampling')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-spatial-resampling-spatialupsample-forward"></a>
## `ai4e_core.abilities.modeling.modules.spatial_resampling.SpatialUpsample.forward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, value: Tensor, size: Sequence[int]) -> Tensor`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.spatial_resampling.SpatialUpsample.forward`

### 用途

目标尺寸由对应跳连或调用者显式交付。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.spatial_resampling import SpatialUpsample
```

```text
forward(self, value: Tensor, size: Sequence[int]) -> Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `value` | `Tensor` | `必填` |
| `size` | `Sequence[int]` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Tensor`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.spatial_resampling import SpatialUpsample

print(signature(SpatialUpsample.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.spatial_resampling`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/spatial_resampling.py:48`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.spatial_resampling')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-spatial-resampling-resize-spatial"></a>
## `ai4e_core.abilities.modeling.modules.spatial_resampling.resize_spatial`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`resize_spatial(value: Tensor, size: Sequence[int]) -> Tensor`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.spatial_resampling.resize_spatial`

### 用途

按给定空间尺寸线性插值，不对齐角点；不改变批与通道轴。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.spatial_resampling import resize_spatial
```

```text
resize_spatial(value: Tensor, size: Sequence[int]) -> Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `value` | `Tensor` | `必填` |
| `size` | `Sequence[int]` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Tensor`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.spatial_resampling import resize_spatial

print(signature(resize_spatial))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.spatial_resampling`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/spatial_resampling.py:9`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.spatial_resampling')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
