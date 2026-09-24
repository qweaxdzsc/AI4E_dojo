<!-- dojo-help: {"domain": "ai4e_core.abilities.modeling.stages.multiscale", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.modeling.stages.multiscale 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.modeling.stages.multiscale", "topic_id": "module:ai4e_core.abilities.modeling.stages.multiscale"} -->
# `ai4e_core.abilities.modeling.stages.multiscale` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-modeling-stages-multiscale-multiscaleencoder"></a>
## `ai4e_core.abilities.modeling.stages.multiscale.MultiScaleEncoder`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`MultiScaleEncoder(stages: Sequence[nn.Module], downsamplers: Sequence[nn.Module])`
- **规范定义名**：`ai4e_core.abilities.modeling.stages.multiscale.MultiScaleEncoder`

### 用途

各级先提特征、保存跳连，再下采样；返回浅到深的特征列表。

### 导入与签名

```python
from ai4e_core.abilities.modeling.stages.multiscale import MultiScaleEncoder
```

```text
MultiScaleEncoder(stages: Sequence[nn.Module], downsamplers: Sequence[nn.Module])
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `stages` | `Sequence[nn.Module]` | `必填` |
| `downsamplers` | `Sequence[nn.Module]` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`MultiScaleEncoder`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.stages.multiscale import MultiScaleEncoder

print(signature(MultiScaleEncoder))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.resunet`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.stages.multiscale`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/stages/multiscale.py:8`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.stages.multiscale')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-stages-multiscale-multiscaleencoder-forward"></a>
## `ai4e_core.abilities.modeling.stages.multiscale.MultiScaleEncoder.forward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, value: Tensor) -> tuple[Tensor, list[Tensor], list[tuple[int, ...]]]`
- **规范定义名**：`ai4e_core.abilities.modeling.stages.multiscale.MultiScaleEncoder.forward`

### 用途

返回底部输入、浅到深跳连及空间尺寸；不脱离梯度。

### 导入与签名

```python
from ai4e_core.abilities.modeling.stages.multiscale import MultiScaleEncoder
```

```text
forward(self, value: Tensor) -> tuple[Tensor, list[Tensor], list[tuple[int, ...]]]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `value` | `Tensor` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`tuple[Tensor, list[Tensor], list[tuple[int, ...]]]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.stages.multiscale import MultiScaleEncoder

print(signature(MultiScaleEncoder.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.stages.multiscale`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/stages/multiscale.py:18`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.stages.multiscale')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-stages-multiscale-skipdecoder"></a>
## `ai4e_core.abilities.modeling.stages.multiscale.SkipDecoder`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`SkipDecoder(up_fusions: Sequence[nn.Module])`
- **规范定义名**：`ai4e_core.abilities.modeling.stages.multiscale.SkipDecoder`

### 用途

融合模块按深到浅注册，消费编码器浅到深的有序交接。

### 导入与签名

```python
from ai4e_core.abilities.modeling.stages.multiscale import SkipDecoder
```

```text
SkipDecoder(up_fusions: Sequence[nn.Module])
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `up_fusions` | `Sequence[nn.Module]` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`SkipDecoder`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.stages.multiscale import SkipDecoder

print(signature(SkipDecoder))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.stages.multiscale`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/stages/multiscale.py:31`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.stages.multiscale')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-stages-multiscale-skipdecoder-forward"></a>
## `ai4e_core.abilities.modeling.stages.multiscale.SkipDecoder.forward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, value: Tensor, skip_features: Sequence[Tensor], spatial_sizes: Sequence[Sequence[int]]) -> Tensor`
- **规范定义名**：`ai4e_core.abilities.modeling.stages.multiscale.SkipDecoder.forward`

### 用途

逐层验证尺寸和浅深关系，不用列表截断隐藏缺失层。

### 导入与签名

```python
from ai4e_core.abilities.modeling.stages.multiscale import SkipDecoder
```

```text
forward(self, value: Tensor, skip_features: Sequence[Tensor], spatial_sizes: Sequence[Sequence[int]]) -> Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `value` | `Tensor` | `必填` |
| `skip_features` | `Sequence[Tensor]` | `必填` |
| `spatial_sizes` | `Sequence[Sequence[int]]` | `必填` |

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
from ai4e_core.abilities.modeling.stages.multiscale import SkipDecoder

print(signature(SkipDecoder.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.stages.multiscale`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/stages/multiscale.py:40`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.stages.multiscale')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
