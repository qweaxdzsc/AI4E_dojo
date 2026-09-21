<!-- dojo-help: {"domain": "ai4e_core.abilities.modeling.modules.geometry_attention", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.modeling.modules.geometry_attention 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.modeling.modules.geometry_attention", "topic_id": "module:ai4e_core.abilities.modeling.modules.geometry_attention"} -->
# `ai4e_core.abilities.modeling.modules.geometry_attention` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-modeling-modules-geometry-attention-gale"></a>
## `ai4e_core.abilities.modeling.modules.geometry_attention.GALE`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`GALE(dim: int, heads: int=8, dim_head: int=64, dropout: float=0.0, slice_num: int=64, use_te: bool=False, plus: bool=False, context_dim: int=0, concrete_dropout: bool=False, state_mixing_mode: str='weighted')`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.geometry_attention.GALE`

### 用途

可独立使用的GALE计算组件。

Geometry-Aware Latent Embeddings (GALE) attention layer.

This is an extension of the Transolver PhysicsAttention mechanism to support
cross-attention with a context vector, built from geometry and global embeddings.
GALE combines self-attention on learned physical state slices with cross-attention
to geometry-aware context, using a learnable mixing weight to blend the two.

Parameters
----------
dim : int
    Input dimension of the features.
heads : int, optional
    Number of attention heads. Default is 8.
dim_head : int, optional
    Dimension of each attention head. Default is 64.
dropout : float, optional
    Dropout rate. Default is 0.0.
slice_num : int, optional
    Number of learned physical state slices. Default is 64.
use_te : bool, optional
    Whether to use Transformer Engine backend when available. Default is False.
plus : bool, optional
    Whether to use Transolver++ features. Default is False.
context_dim : int, optional
    Dimension of the context vector for cross-attention. Default is 0.
concrete_dropout : bool, optional
    Whether to use ConcreteDropout instead of standard dropout. Default is False.
state_mixing_mode : str, optional
    How to blend self-attention and cross-attention outputs. ``"weighted"`` uses
    a learnable sigmoid-gated weighted sum. ``"concat_project"``
    concatenates the two along the head dimension and projects back with a
    linear layer. Default is ``"weighted"``.

Forward
-------
x : tuple[torch.Tensor, ...]
    Tuple of input tensors, each of shape :math:`(B, N, C)` where :math:`B` is
    batch size, :math:`N` is number of tokens, and :math:`C` is number of channels.
context : tuple[torch.Tensor, ...] | None, optional
    Context tensor for cross-attention of shape :math:`(B, H, S_c, D_c)` where
    :math:`H` is number of heads, :math:`S_c` is number of context slices, and
    :math:`D_c` is context dimension. If ``None``, only self-attention is applied.
    Default is ``None``.

Outputs
-------
list[torch.Tensor]
    List of output tensors, each of shape :math:`(B, N, C)`, same shape as inputs.

Notes
-----
The mixing between self-attention and cross-attention is controlled by a learnable
parameter ``state_mixing`` which is passed through a sigmoid function to ensure
the mixing weight stays in :math:`[0, 1]`.

See Also
--------
:class:`physicsnemo.models.transolver.Physics_Attention.PhysicsAttentionIrregularMesh` : Base physics attention class.
:class:`GALEBlock` : Transformer block using GALE attention.

Examples
--------
>>> import torch
>>> gale = GALE(dim=256, heads=8, dim_head=32, context_dim=32, use_te=False)
>>> x = (torch.randn(2, 100, 256),)  # Single input tensor in tuple
>>> context = torch.randn(2, 8, 64, 32)  # Context for cross-attention
>>> outputs = gale(x, context)
>>> len(outputs)
1
>>> outputs[0].shape
torch.Size([2, 100, 256])

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.geometry_attention import GALE
```

```text
GALE(dim: int, heads: int=8, dim_head: int=64, dropout: float=0.0, slice_num: int=64, use_te: bool=False, plus: bool=False, context_dim: int=0, concrete_dropout: bool=False, state_mixing_mode: str='weighted')
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dim` | `int` | `必填` |
| `heads` | `int` | `8` |
| `dim_head` | `int` | `64` |
| `dropout` | `float` | `0.0` |
| `slice_num` | `int` | `64` |
| `use_te` | `bool` | `False` |
| `plus` | `bool` | `False` |
| `context_dim` | `int` | `0` |
| `concrete_dropout` | `bool` | `False` |
| `state_mixing_mode` | `str` | `'weighted'` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`GALE`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`NotImplementedError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.geometry_attention import GALE

print(signature(GALE))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_geotransolver`, `aero_cfd.shapenet_car_geotransolver`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.geometry_attention`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/geometry_attention.py:194`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.geometry_attention')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-geometry-attention-gale-compute-slice-attention-cross"></a>
## `ai4e_core.abilities.modeling.modules.geometry_attention.GALE.compute_slice_attention_cross`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`compute_slice_attention_cross(self, slice_tokens: list[torch.Tensor], context: torch.Tensor) -> list[torch.Tensor]`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.geometry_attention.GALE.compute_slice_attention_cross`

### 用途

执行compute_slice_attention_cross；张量布局、参数与返回值见下列参考说明。

Compute cross-attention between slice tokens and context.

Parameters
----------
slice_tokens : list[torch.Tensor]
    List of slice token tensors, each of shape :math:`(B, H, S, D)` where
    :math:`B` is batch size, :math:`H` is number of heads, :math:`S` is
    number of slices, and :math:`D` is head dimension.
context : torch.Tensor
    Context tensor of shape :math:`(B, H, S_c, D_c)` where :math:`S_c` is
    number of context slices and :math:`D_c` is context dimension.

Returns
-------
list[torch.Tensor]
    List of cross-attention outputs, each of shape :math:`(B, H, S, D)`.

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.geometry_attention import GALE
```

```text
compute_slice_attention_cross(self, slice_tokens: list[torch.Tensor], context: torch.Tensor) -> list[torch.Tensor]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `slice_tokens` | `list[torch.Tensor]` | `必填` |
| `context` | `torch.Tensor` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`list[torch.Tensor]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.geometry_attention import GALE

print(signature(GALE.compute_slice_attention_cross))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.geometry_attention`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/geometry_attention.py:289`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.geometry_attention')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-geometry-attention-gale-forward"></a>
## `ai4e_core.abilities.modeling.modules.geometry_attention.GALE.forward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x: tuple[torch.Tensor, ...], context: torch.Tensor | None=None) -> list[torch.Tensor]`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.geometry_attention.GALE.forward`

### 用途

执行forward；张量布局、参数与返回值见下列参考说明。

Forward pass of the GALE module.

Applies physics-aware self-attention combined with optional cross-attention
to geometry and global context.

Parameters
----------
x : tuple[torch.Tensor, ...]
    Tuple of input tensors, each of shape :math:`(B, N, C)` where :math:`B`
    is batch size, :math:`N` is number of tokens, and :math:`C` is number
    of channels.
context : torch.Tensor | None, optional
    Context tensor for cross-attention of shape :math:`(B, H, S_c, D_c)`
    where :math:`H` is number of heads, :math:`S_c` is number of context
    slices, and :math:`D_c` is context dimension. If ``None``, only
    self-attention is applied. Default is ``None``.

Returns
-------
list[torch.Tensor]
    List of output tensors, each of shape :math:`(B, N, C)``, same shape
    as inputs.

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.geometry_attention import GALE
```

```text
forward(self, x: tuple[torch.Tensor, ...], context: torch.Tensor | None=None) -> list[torch.Tensor]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `tuple[torch.Tensor, ...]` | `必填` |
| `context` | `torch.Tensor | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`list[torch.Tensor]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.geometry_attention import GALE

print(signature(GALE.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.geometry_attention`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/geometry_attention.py:312`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.geometry_attention')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-geometry-attention-galeblock"></a>
## `ai4e_core.abilities.modeling.modules.geometry_attention.GALEBlock`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`GALEBlock(num_heads: int, hidden_dim: int, dropout: float, act: str='gelu', mlp_ratio: int=4, last_layer: bool=False, out_dim: int=1, slice_num: int=32, use_te: bool=False, plus: bool=False, context_dim: int=0, spatial_shape: tuple[int, ...] | None=None, attention_type: str='GALE', concrete_dropout: bool=False, state_mixing_mode: str='weighted')`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.geometry_attention.GALEBlock`

### 用途

可独立使用的GALEBlock计算组件。

Transformer encoder block using GALE attention.

This block replaces standard self-attention with the GALE (Geometry-Aware Latent
Embeddings) attention mechanism, which combines physics-aware self-attention with
cross-attention to geometry and global context.

Parameters
----------
num_heads : int
    Number of attention heads.
hidden_dim : int
    Hidden dimension of the transformer.
dropout : float
    Dropout rate.
act : str, optional
    Activation function name. Default is ``"gelu"``.
mlp_ratio : int, optional
    Ratio of MLP hidden dimension to ``hidden_dim``. Default is 4.
last_layer : bool, optional
    Whether this is the last layer in the model. Default is ``False``.
out_dim : int, optional
    Output dimension (only used if ``last_layer=True``). Default is 1.
slice_num : int, optional
    Number of learned physical state slices. Default is 32.
use_te : bool, optional
    Whether to use Transformer Engine backend. Default is ``False``.
plus : bool, optional
    Whether to use Transolver++ features. Default is ``False``.
context_dim : int, optional
    Dimension of the context vector for cross-attention. Default is 0.
spatial_shape : tuple[int, ...] | None, optional
    If ``None``, uses irregular-mesh GALE. Length-2 tuple enables 2D Conv2d
    projection; length-3 tuple enables 3D Conv3d projection (flattened
    :math:`N = H \times W` or :math:`H \times W \times D`). Default is ``None``.
attention_type : str, optional
    Attention backend to use. ``"GALE"`` uses the standard physics-aware
    slice attention; ``"GALE_FA"`` uses flash-attention variant.
    Default is ``"GALE"``.
state_mixing_mode : str, optional
    How to blend self-attention and cross-attention outputs. ``"weighted"`` uses
    a learnable sigmoid-gated weighted sum. ``"concat_project"``
    concatenates the two along the head dimension and projects back with a
    linear layer. Default is ``"weighted"``.

Forward
-------
fx : tuple[torch.Tensor, ...]
    Tuple of input tensors, each of shape :math:`(B, N, C)` where :math:`B` is
    batch size, :math:`N` is number of tokens, and :math:`C` is hidden dimension.
global_context : tuple[torch.Tensor, ...]
    Global context tensor for cross-attention of shape :math:`(B, H, S_c, D_c)`
    where :math:`H` is number of heads, :math:`S_c` is number of context slices,
    and :math:`D_c` is context dimension.

Outputs
-------
list[torch.Tensor]
    List of output tensors, each of shape :math:`(B, N, C)`, same shape as inputs.

Notes
-----
The block applies layer normalization before the attention operation and uses
residual connections after both the attention and MLP layers.

See Also
--------
:class:`GALE` : The attention mechanism used in this block.
:class:`physicsnemo.models.geotransolver.GeoTransolver` : Main model using GALEBlock.

Examples
--------
>>> import torch
>>> block = GALEBlock(num_heads=8, hidden_dim=256, dropout=0.1, context_dim=32, use_te=False)
>>> fx = (torch.randn(2, 100, 256),)  # Single input tensor in tuple
>>> context = torch.randn(2, 8, 64, 32)  # Global context
>>> outputs = block(fx, context)
>>> len(outputs)
1
>>> outputs[0].shape
torch.Size([2, 100, 256])

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.geometry_attention import GALEBlock
```

```text
GALEBlock(num_heads: int, hidden_dim: int, dropout: float, act: str='gelu', mlp_ratio: int=4, last_layer: bool=False, out_dim: int=1, slice_num: int=32, use_te: bool=False, plus: bool=False, context_dim: int=0, spatial_shape: tuple[int, ...] | None=None, attention_type: str='GALE', concrete_dropout: bool=False, state_mixing_mode: str='weighted')
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `num_heads` | `int` | `必填` |
| `hidden_dim` | `int` | `必填` |
| `dropout` | `float` | `必填` |
| `act` | `str` | `'gelu'` |
| `mlp_ratio` | `int` | `4` |
| `last_layer` | `bool` | `False` |
| `out_dim` | `int` | `1` |
| `slice_num` | `int` | `32` |
| `use_te` | `bool` | `False` |
| `plus` | `bool` | `False` |
| `context_dim` | `int` | `0` |
| `spatial_shape` | `tuple[int, ...] | None` | `None` |
| `attention_type` | `str` | `'GALE'` |
| `concrete_dropout` | `bool` | `False` |
| `state_mixing_mode` | `str` | `'weighted'` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`GALEBlock`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`NotImplementedError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.geometry_attention import GALEBlock

print(signature(GALEBlock))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.geometry_attention`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/geometry_attention.py:410`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.geometry_attention')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-geometry-attention-galeblock-forward"></a>
## `ai4e_core.abilities.modeling.modules.geometry_attention.GALEBlock.forward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, fx: tuple[torch.Tensor, ...], global_context: torch.Tensor) -> list[torch.Tensor]`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.geometry_attention.GALEBlock.forward`

### 用途

执行forward；张量布局、参数与返回值见下列参考说明。

Forward pass of the GALE block.

Parameters
----------
fx : tuple[torch.Tensor, ...]
    Tuple of input tensors, each of shape :math:`(B, N, C)` where :math:`B`
    is batch size, :math:`N` is number of tokens, and :math:`C` is hidden
    dimension.
global_context : torch.Tensor
    Global context tensor for cross-attention of shape :math:`(B, H, S_c, D_c)`
    where :math:`H` is number of heads, :math:`S_c` is number of context slices,
    and :math:`D_c` is context dimension.

Returns
-------
list[torch.Tensor]
    List of output tensors, each of shape :math:`(B, N, C)`, same shape as inputs.

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.geometry_attention import GALEBlock
```

```text
forward(self, fx: tuple[torch.Tensor, ...], global_context: torch.Tensor) -> list[torch.Tensor]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `fx` | `tuple[torch.Tensor, ...]` | `必填` |
| `global_context` | `torch.Tensor` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`list[torch.Tensor]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.geometry_attention import GALEBlock

print(signature(GALEBlock.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.geometry_attention`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/geometry_attention.py:587`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.geometry_attention')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-geometry-attention-galestructuredmesh2d"></a>
## `ai4e_core.abilities.modeling.modules.geometry_attention.GALEStructuredMesh2D`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`GALEStructuredMesh2D(dim: int, spatial_shape: tuple[int, int], heads: int=8, dim_head: int=64, dropout: float=0.0, slice_num: int=64, kernel: int=3, use_te: bool=False, plus: bool=False, context_dim: int=0, state_mixing_mode: str='weighted')`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.geometry_attention.GALEStructuredMesh2D`

### 用途

可独立使用的GALEStructuredMesh2D计算组件。

GALE with Conv2d slice projection for 2D structured grids (see :class:`GALE`).

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.geometry_attention import GALEStructuredMesh2D
```

```text
GALEStructuredMesh2D(dim: int, spatial_shape: tuple[int, int], heads: int=8, dim_head: int=64, dropout: float=0.0, slice_num: int=64, kernel: int=3, use_te: bool=False, plus: bool=False, context_dim: int=0, state_mixing_mode: str='weighted')
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dim` | `int` | `必填` |
| `spatial_shape` | `tuple[int, int]` | `必填` |
| `heads` | `int` | `8` |
| `dim_head` | `int` | `64` |
| `dropout` | `float` | `0.0` |
| `slice_num` | `int` | `64` |
| `kernel` | `int` | `3` |
| `use_te` | `bool` | `False` |
| `plus` | `bool` | `False` |
| `context_dim` | `int` | `0` |
| `state_mixing_mode` | `str` | `'weighted'` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`GALEStructuredMesh2D`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`NotImplementedError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.geometry_attention import GALEStructuredMesh2D

print(signature(GALEStructuredMesh2D))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.geometry_attention`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/geometry_attention.py:381`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.geometry_attention')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
