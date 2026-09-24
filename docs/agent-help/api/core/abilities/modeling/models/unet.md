<!-- dojo-help: {"domain": "ai4e_core.abilities.modeling.models.unet", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.modeling.models.unet 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.modeling.models.unet", "topic_id": "module:ai4e_core.abilities.modeling.models.unet"} -->
# `ai4e_core.abilities.modeling.models.unet` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-modeling-models-unet-unet"></a>
## `ai4e_core.abilities.modeling.models.unet.UNet`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`UNet(in_channels: int, out_channels: int, *, spatial_dim: int, base_channels: int=8, levels: int=3, encoder: nn.Module | None=None, bottleneck: nn.Module | None=None, decoder: nn.Module | None=None, head: nn.Module | None=None)`
- **规范定义名**：`ai4e_core.abilities.modeling.models.unet.UNet`

### 用途

多尺度场预测，编码器显式交付浅到深跳连及尺寸。

### 导入与签名

```python
from ai4e_core.abilities.modeling.models.unet import UNet
```

```text
UNet(in_channels: int, out_channels: int, *, spatial_dim: int, base_channels: int=8, levels: int=3, encoder: nn.Module | None=None, bottleneck: nn.Module | None=None, decoder: nn.Module | None=None, head: nn.Module | None=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `in_channels` | `int` | `必填` |
| `out_channels` | `int` | `必填` |
| `spatial_dim` | `int` | `必填关键字参数` |
| `base_channels` | `int` | `8` |
| `levels` | `int` | `3` |
| `encoder` | `nn.Module | None` | `None` |
| `bottleneck` | `nn.Module | None` | `None` |
| `decoder` | `nn.Module | None` | `None` |
| `head` | `nn.Module | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`UNet`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.models.unet import UNet

print(signature(UNet))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.models.unet`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/models/unet.py:15`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.models.unet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-models-unet-unet-forward"></a>
## `ai4e_core.abilities.modeling.models.unet.UNet.forward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, value: Tensor) -> Tensor`
- **规范定义名**：`ai4e_core.abilities.modeling.models.unet.UNet.forward`

### 用途

由注入的四部分预测，默认输出保持输入空间尺寸。

### 导入与签名

```python
from ai4e_core.abilities.modeling.models.unet import UNet
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
from ai4e_core.abilities.modeling.models.unet import UNet

print(signature(UNet.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.models.unet`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/models/unet.py:73`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.models.unet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-models-unet-unet-forward-features"></a>
## `ai4e_core.abilities.modeling.models.unet.UNet.forward_features`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward_features(self, value: Tensor) -> tuple[Tensor, list[Tensor], list[tuple[int, ...]]]`
- **规范定义名**：`ai4e_core.abilities.modeling.models.unet.UNet.forward_features`

### 用途

返回解码特征、浅到深跳连及尺寸，方便独立消费。

### 导入与签名

```python
from ai4e_core.abilities.modeling.models.unet import UNet
```

```text
forward_features(self, value: Tensor) -> tuple[Tensor, list[Tensor], list[tuple[int, ...]]]
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
from ai4e_core.abilities.modeling.models.unet import UNet

print(signature(UNet.forward_features))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.models.unet`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/models/unet.py:66`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.models.unet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-models-unet-unet2d"></a>
## `ai4e_core.abilities.modeling.models.unet.UNet2d`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`UNet2d(in_channels: int, out_channels: int, **kwargs)`
- **规范定义名**：`ai4e_core.abilities.modeling.models.unet.UNet2d`

### 用途

二维三级场U-Net。

### 导入与签名

```python
from ai4e_core.abilities.modeling.models.unet import UNet2d
```

```text
UNet2d(in_channels: int, out_channels: int, **kwargs)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `in_channels` | `int` | `必填` |
| `out_channels` | `int` | `必填` |
| `**kwargs` | `未标注` | `可变关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`UNet2d`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.models.unet import UNet2d

print(signature(UNet2d))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.resunet`, `recipe_extensions.network_composition.unet_transformer`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.models.unet`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/models/unet.py:79`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.models.unet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-models-unet-unet3d"></a>
## `ai4e_core.abilities.modeling.models.unet.UNet3d`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`UNet3d(in_channels: int, out_channels: int, **kwargs)`
- **规范定义名**：`ai4e_core.abilities.modeling.models.unet.UNet3d`

### 用途

三维三级场U-Net，三空间轴均下采样。

### 导入与签名

```python
from ai4e_core.abilities.modeling.models.unet import UNet3d
```

```text
UNet3d(in_channels: int, out_channels: int, **kwargs)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `in_channels` | `int` | `必填` |
| `out_channels` | `int` | `必填` |
| `**kwargs` | `未标注` | `可变关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`UNet3d`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.models.unet import UNet3d

print(signature(UNet3d))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.resunet`, `recipe_extensions.network_composition.unet_transformer`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.models.unet`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/models/unet.py:86`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.models.unet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
