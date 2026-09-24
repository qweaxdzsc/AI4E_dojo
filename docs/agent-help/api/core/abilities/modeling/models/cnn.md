<!-- dojo-help: {"domain": "ai4e_core.abilities.modeling.models.cnn", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.modeling.models.cnn 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.modeling.models.cnn", "topic_id": "module:ai4e_core.abilities.modeling.models.cnn"} -->
# `ai4e_core.abilities.modeling.models.cnn` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-modeling-models-cnn-cnn"></a>
## `ai4e_core.abilities.modeling.models.cnn.CNN`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`CNN(in_channels: int, out_channels: int, *, spatial_dim: int, hidden_channels: int=16, hidden_layers: int=4, encoder: nn.Module | None=None, head: nn.Module | None=None)`
- **规范定义名**：`ai4e_core.abilities.modeling.models.cnn.CNN`

### 用途

保持空间尺寸的卷积网络，可替换编码器及输出头。

### 导入与签名

```python
from ai4e_core.abilities.modeling.models.cnn import CNN
```

```text
CNN(in_channels: int, out_channels: int, *, spatial_dim: int, hidden_channels: int=16, hidden_layers: int=4, encoder: nn.Module | None=None, head: nn.Module | None=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `in_channels` | `int` | `必填` |
| `out_channels` | `int` | `必填` |
| `spatial_dim` | `int` | `必填关键字参数` |
| `hidden_channels` | `int` | `16` |
| `hidden_layers` | `int` | `4` |
| `encoder` | `nn.Module | None` | `None` |
| `head` | `nn.Module | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`CNN`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.models.cnn import CNN

print(signature(CNN))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.models.cnn`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/models/cnn.py:9`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.models.cnn')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-models-cnn-cnn-forward"></a>
## `ai4e_core.abilities.modeling.models.cnn.CNN.forward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, value: Tensor) -> Tensor`
- **规范定义名**：`ai4e_core.abilities.modeling.models.cnn.CNN.forward`

### 用途

预测通道在前的场，默认保持输入空间尺寸。

### 导入与签名

```python
from ai4e_core.abilities.modeling.models.cnn import CNN
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

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.models.cnn import CNN

print(signature(CNN.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.models.cnn`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/models/cnn.py:50`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.models.cnn')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-models-cnn-cnn-forward-features"></a>
## `ai4e_core.abilities.modeling.models.cnn.CNN.forward_features`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward_features(self, value: Tensor) -> Tensor`
- **规范定义名**：`ai4e_core.abilities.modeling.models.cnn.CNN.forward_features`

### 用途

直接读取空间特征，保留反向传播。

### 导入与签名

```python
from ai4e_core.abilities.modeling.models.cnn import CNN
```

```text
forward_features(self, value: Tensor) -> Tensor
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
from ai4e_core.abilities.modeling.models.cnn import CNN

print(signature(CNN.forward_features))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.models.cnn`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/models/cnn.py:44`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.models.cnn')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-models-cnn-cnn2d"></a>
## `ai4e_core.abilities.modeling.models.cnn.CNN2d`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`CNN2d(in_channels: int, out_channels: int, **kwargs)`
- **规范定义名**：`ai4e_core.abilities.modeling.models.cnn.CNN2d`

### 用途

二维普通卷积网络。

### 导入与签名

```python
from ai4e_core.abilities.modeling.models.cnn import CNN2d
```

```text
CNN2d(in_channels: int, out_channels: int, **kwargs)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `in_channels` | `int` | `必填` |
| `out_channels` | `int` | `必填` |
| `**kwargs` | `未标注` | `可变关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`CNN2d`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.models.cnn import CNN2d

print(signature(CNN2d))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.models.cnn`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/models/cnn.py:55`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.models.cnn')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-models-cnn-cnn3d"></a>
## `ai4e_core.abilities.modeling.models.cnn.CNN3d`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`CNN3d(in_channels: int, out_channels: int, **kwargs)`
- **规范定义名**：`ai4e_core.abilities.modeling.models.cnn.CNN3d`

### 用途

三维普通卷积网络。

### 导入与签名

```python
from ai4e_core.abilities.modeling.models.cnn import CNN3d
```

```text
CNN3d(in_channels: int, out_channels: int, **kwargs)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `in_channels` | `int` | `必填` |
| `out_channels` | `int` | `必填` |
| `**kwargs` | `未标注` | `可变关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`CNN3d`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.models.cnn import CNN3d

print(signature(CNN3d))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.models.cnn`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/models/cnn.py:62`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.models.cnn')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
