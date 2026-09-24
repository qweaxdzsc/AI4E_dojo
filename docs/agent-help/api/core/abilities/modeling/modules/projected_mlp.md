<!-- dojo-help: {"domain": "ai4e_core.abilities.modeling.modules.projected_mlp", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.modeling.modules.projected_mlp 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.modeling.modules.projected_mlp", "topic_id": "module:ai4e_core.abilities.modeling.modules.projected_mlp"} -->
# `ai4e_core.abilities.modeling.modules.projected_mlp` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-modeling-modules-projected-mlp-mlp"></a>
## `ai4e_core.abilities.modeling.modules.projected_mlp.Mlp`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`Mlp(in_features: int, hidden_features: int | list[int] | None=None, out_features: int | None=None, act_layer: nn.Module | type[nn.Module] | str=nn.GELU, drop: float=0.0, final_dropout: bool=True, bias: bool=True, use_batchnorm: bool=False, spectral_norm: bool=False, use_te: bool=False)`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.projected_mlp.Mlp`

### 用途

可独立使用的Mlp计算组件。

Multi-layer perceptron with configurable architecture.

Supports arbitrary depth, dropout, batch normalization, spectral
normalization, bias control, and optional Transformer Engine linear
layers.

Parameters
----------
in_features : int
    Number of input features.
hidden_features : int | list[int] | None, optional
    Hidden layer dimension(s). Can be:
    - ``int``: Single hidden layer with this dimension
    - ``list[int]``: Multiple hidden layers with specified dimensions
    - ``None``: Single hidden layer with ``in_features`` dimension
    Default is ``None``.
out_features : int | None, optional
    Number of output features. If ``None``, defaults to ``in_features``.
    Default is ``None``.
act_layer : nn.Module | type[nn.Module] | str, optional
    Activation function. Can be:
    - ``str``: Name of activation (e.g., ``"gelu"``, ``"relu"``, ``"silu"``)
    - ``type``: Activation class to instantiate (e.g., ``nn.GELU``)
    - ``nn.Module``: Pre-instantiated activation module
    Default is ``nn.GELU``.
drop : float, optional
    Dropout rate applied after each hidden layer. Default is ``0.0``.
final_dropout : bool, optional
    Whether to apply dropout after the final linear layer. Default is ``True``.
bias : bool, optional
    Whether to include bias terms in the linear layers. Default is ``True``.
use_batchnorm : bool, optional
    If ``True``, applies ``BatchNorm1d`` after each linear layer
    (including the output layer). Default is ``False``.
spectral_norm : bool, optional
    If ``True``, applies spectral normalization to all linear layer
    weights, constraining the spectral norm to 1. Default is ``False``.
use_te : bool, optional
    Whether to use Transformer Engine linear layers for optimized performance.
    Requires Transformer Engine to be installed. Default is ``False``.

Examples
--------
>>> import torch
>>> mlp = Mlp(in_features=64, hidden_features=128, out_features=32)
>>> x = torch.randn(2, 64)
>>> out = mlp(x)
>>> out.shape
torch.Size([2, 32])

>>> mlp = Mlp(in_features=64, hidden_features=[128, 256, 128], out_features=32)
>>> x = torch.randn(2, 64)
>>> out = mlp(x)
>>> out.shape
torch.Size([2, 32])

>>> # With batch normalization and spectral normalization
>>> mlp = Mlp(
...     in_features=10,
...     hidden_features=[32, 16],
...     out_features=4,
...     use_batchnorm=True,
...     spectral_norm=True,
... )
>>> mlp(torch.randn(8, 10)).shape
torch.Size([8, 4])

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.projected_mlp import Mlp
```

```text
Mlp(in_features: int, hidden_features: int | list[int] | None=None, out_features: int | None=None, act_layer: nn.Module | type[nn.Module] | str=nn.GELU, drop: float=0.0, final_dropout: bool=True, bias: bool=True, use_batchnorm: bool=False, spectral_norm: bool=False, use_te: bool=False)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `in_features` | `int` | `必填` |
| `hidden_features` | `int | list[int] | None` | `None` |
| `out_features` | `int | None` | `None` |
| `act_layer` | `nn.Module | type[nn.Module] | str` | `nn.GELU` |
| `drop` | `float` | `0.0` |
| `final_dropout` | `bool` | `True` |
| `bias` | `bool` | `True` |
| `use_batchnorm` | `bool` | `False` |
| `spectral_norm` | `bool` | `False` |
| `use_te` | `bool` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Mlp`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`NotImplementedError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.projected_mlp import Mlp

print(signature(Mlp))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.projected_mlp`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/projected_mlp.py:33`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.projected_mlp')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-projected-mlp-mlp-forward"></a>
## `ai4e_core.abilities.modeling.modules.projected_mlp.Mlp.forward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x: torch.Tensor) -> torch.Tensor`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.projected_mlp.Mlp.forward`

### 用途

执行forward；张量布局、参数与返回值见下列参考说明。

Forward pass of the MLP.

Parameters
----------
x : torch.Tensor
    Input tensor of shape ``(*, in_features)`` where ``*`` denotes
    any number of batch dimensions.

Returns
-------
torch.Tensor
    Output tensor of shape ``(*, out_features)``.

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.projected_mlp import Mlp
```

```text
forward(self, x: torch.Tensor) -> torch.Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `torch.Tensor` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`torch.Tensor`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.projected_mlp import Mlp

print(signature(Mlp.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.projected_mlp`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/projected_mlp.py:153`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.projected_mlp')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-projected-mlp-get-activation"></a>
## `ai4e_core.abilities.modeling.modules.projected_mlp.get_activation`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`get_activation(name)`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.projected_mlp.get_activation`

### 用途

按显式名称构造激活，不猜测未知名称。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.projected_mlp import get_activation
```

```text
get_activation(name)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `name` | `未标注` | `必填` |

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
from ai4e_core.abilities.modeling.modules.projected_mlp import get_activation

print(signature(get_activation))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.projected_mlp`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/projected_mlp.py:17`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.projected_mlp')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
