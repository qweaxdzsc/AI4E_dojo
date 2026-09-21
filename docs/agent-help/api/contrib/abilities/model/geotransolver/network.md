<!-- dojo-help: {"domain": "ai4e_contrib.ability.model.geotransolver.network", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.model.geotransolver.network 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.model.geotransolver.network", "topic_id": "module:ai4e_contrib.ability.model.geotransolver.network"} -->
# `ai4e_contrib.ability.model.geotransolver.network` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-model-geotransolver-network-geotransolver"></a>
## `ai4e_contrib.ability.model.geotransolver.network.GeoTransolver`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`GeoTransolver(functional_dim: int | tuple[int, ...], out_dim: int | tuple[int, ...], geometry_dim: int | None=None, global_dim: int | None=None, n_layers: int=4, n_hidden: int=256, dropout: float=0.0, n_head: int=8, act: str='gelu', mlp_ratio: int=4, slice_num: int=32, use_te: bool=False, time_input: bool=False, plus: bool=False, include_local_features: bool=False, radii: list[float] | None=None, neighbors_in_radius: list[int] | None=None, n_hidden_local: int=32, structured_shape: tuple[int, ...] | None=None, attention_type: Literal['GALE', 'GALE_FA']='GALE', concrete_dropout: bool=False, state_mixing_mode: str='weighted', activation_checkpointing: bool=False, checkpointing_ratio: float=1.0, activation_checkpointing_components: tuple[str, ...] | list[str]=('blocks',))`
- **规范定义名**：`ai4e_contrib.ability.model.geotransolver.network.GeoTransolver`

### 用途

可独立使用的GeoTransolver计算组件。

GeoTransolver: Geometry-Aware Physics Attention Transformer.

GeoTransolver is an adaptation of the Transolver architecture, replacing standard
attention with GALE (Geometry-Aware Latent Embeddings) attention. GALE combines
physics-aware self-attention on learned state slices with cross-attention to
geometry and global context embeddings.

The model projects geometry and global features onto physical state spaces, which
are then used as context in all transformer blocks. This design enables the model
to incorporate geometric structure and global information throughout the forward
pass.

Parameters
----------
functional_dim : int | tuple[int, ...]
    Dimension of the input values (local embeddings), not including global
    embeddings or geometry features. Input will be projected to ``n_hidden``
    before processing. Can be a single int or tuple for multiple input types.
out_dim : int | tuple[int, ...]
    Dimension of the output of the model. Must have same length as
    ``functional_dim`` if both are tuples.
geometry_dim : int | None, optional
    Pointwise dimension of the geometry input features. If provided, geometry
    features will be projected onto physical states and used as context in all
    GALE layers. Default is ``None``.
global_dim : int | None, optional
    Dimension of the global embedding features. If provided, global features
    will be projected onto physical states and used as context in all GALE
    layers. Default is ``None``.
n_layers : int, optional
    Number of GALE layers in the model. Default is 4.
n_hidden : int, optional
    Hidden dimension of the transformer. Default is 256.
dropout : float, optional
    Dropout rate applied across the GALE layers. Default is 0.0.
n_head : int, optional
    Number of attention heads in each GALE layer. Must evenly divide
    ``n_hidden`` to yield an integer head dimension. Default is 8.
act : str, optional
    Activation function name. Default is ``"gelu"``.
mlp_ratio : int, optional
    Ratio of MLP hidden dimension to ``n_hidden``. Default is 4.
slice_num : int, optional
    Number of learned physical state slices in the GALE layers, representing
    the number of learned states each layer should project inputs onto.
    Default is 32.
use_te : bool, optional
    Whether to use Transformer Engine backend when available. Default is ``False``.
time_input : bool, optional
    Whether to include time embeddings. Default is ``False``.
plus : bool, optional
    Whether to use Transolver++ features in the GALE layers. Default is ``False``.
include_local_features : bool, optional
    Whether to include local features in the global context. Default is ``False``.
radii : list[float], optional
    Radii for the local features. Default is ``[0.05, 0.25]``.
neighbors_in_radius : list[int], optional
    Neighbors in radius for the local features. Default is ``[8, 32]``.
n_hidden_local : int, optional
    Hidden dimension for the local features. Default is 32.
structured_shape : tuple[int, ...] | None, optional
    If set to ``(H, W)`` or ``(H, W, D)``, enables structured 2D/3D paths
    (Conv2d/Conv3d GALE; no ball-query local features). Inputs may be
    flattened :math:`(B, N, C)` with :math:`N = H W` or :math:`H W D`, or
    spatial :math:`(B, H, W, C)` / :math:`(B, H, W, D, C)`. Default is ``None``.
attention_type : {"GALE", "GALE_FA"}, optional
    Attention implementation used inside each GALE block: ``"GALE"`` for the
    reference version, ``"GALE_FA"`` for the flash-attention one.  Validated
    in :class:`~physicsnemo.nn.GALEBlock`, which raises on any other value.
    Default is ``"GALE"``.
state_mixing_mode : str, optional
    How to blend self-attention and cross-attention outputs in GALE layers.
    ``"weighted"`` uses a learnable sigmoid-gated weighted sum.
    ``"concat_project"`` concatenates the two along the head dimension and
    projects back with a linear layer. Default is ``"weighted"``.
activation_checkpointing : bool, optional, default=False
    Whether to enable activation checkpointing during training.
checkpointing_ratio : float, optional, default=1.0
    Fraction of GALE blocks to checkpoint when
    ``activation_checkpointing=True``. Selected blocks are distributed
    evenly across the block stack.
activation_checkpointing_components : tuple[str, ...] | list[str], optional
    Components covered when activation checkpointing is enabled. Supported
    values are ``"context"``, ``"preprocess"``, ``"blocks"``, and
    ``"output"``. The default ``("blocks",)`` matches Transolver's
    block-only policy. ``checkpointing_ratio`` applies to the block stack;
    other selected components are either fully checkpointed or disabled.

Forward
-------
local_embedding : torch.Tensor | tuple[torch.Tensor, ...]
    Local embedding: unstructured :math:`(B, N, C)`; structured 2D
    :math:`(B, H, W, C)` or flattened :math:`(B, H W, C)`; structured 3D
    :math:`(B, H, W, D, C)` or flattened. Can be a tuple for multiple input types.
local_positions : torch.Tensor | tuple[torch.Tensor, ...] | None, optional
    Local positions for each input, each of shape :math:`(B, N, 3)`. Required if
    ``include_local_features=True``. Default is ``None``.
global_embedding : torch.Tensor | None, optional
    Global embedding of the input data of shape :math:`(B, N_g, C_g)` where
    :math:`N_g` is number of global tokens and :math:`C_g` is ``global_dim``.
    If ``None``, global context is not used. Default is ``None``.
geometry : torch.Tensor | None, optional
    Geometry features of the input data of shape :math:`(B, N, C_{geo})` where
    :math:`C_{geo}` is ``geometry_dim``. If ``None``, geometry context is not
    used. Default is ``None``.
time : torch.Tensor | None, optional
    Time embedding (currently not implemented). Default is ``None``.

Outputs
-------
torch.Tensor | tuple[torch.Tensor, ...]
    When ``return_embedding_states=False`` (default): output tensor(s) of
    shape :math:`(B, N, C_{out})`. Returns a single tensor if input was
    a single tensor, or a tuple of tensors if input was a tuple
    (multi-stream). For structured grids, output matches the input
    layout—flattened :math:`(B, N, C_{out})` or spatial
    :math:`(B, H, W, C_{out})` / :math:`(B, H, W, D, C_{out})` when
    inputs were 4D/5D.

    When ``return_embedding_states=True``, returns a 2-tuple
    ``(output, embedding_states)`` where ``output`` follows the same
    rules above, and ``embedding_states`` is of shape
    :math:`(B, H, S, D_c)` (geometry/global context), or ``None`` if no
    context sources were provided.

Raises
------
ValueError
    If ``n_hidden`` is not evenly divisible by ``n_head``.
ValueError
    If ``functional_dim`` and ``out_dim`` have different lengths when both
    are tuples.
NotImplementedError
    If ``time`` is provided (not yet implemented).

Notes
-----
Unstructured mesh uses linear GALE projection; structured ``structured_shape``
uses the same Conv2d/Conv3d slice projection as :class:`~physicsnemo.models.transolver.Transolver`.
Ball-query local features are disabled when ``structured_shape`` is set.

For more details on Transolver, see:

- `Transolver paper <https://arxiv.org/pdf/2402.02366>`_
- `Transolver++ paper <https://arxiv.org/pdf/2502.02414>`_

See Also
--------
:class:`~physicsnemo.nn.module.gale.GALE` : The attention mechanism used in GeoTransolver.
:class:`~physicsnemo.nn.module.gale.GALEBlock` : Transformer block using GALE attention.
:class:`~physicsnemo.models.geotransolver.context_projector.ContextProjector` : Projects context features onto physical states.

Examples
--------
Basic usage with local embeddings only:

>>> import torch
>>> from physicsnemo.models.geotransolver import GeoTransolver
>>> model = GeoTransolver(
...     functional_dim=64,
...     out_dim=3,
...     n_hidden=256,
...     n_layers=4,
...     use_te=False,
... )
>>> local_emb = torch.randn(2, 1000, 64)  # (batch, nodes, features)
>>> output = model(local_emb)
>>> output.shape
torch.Size([2, 1000, 3])

Usage with geometry, global context, and embedding states:

>>> model = GeoTransolver(
...     functional_dim=64,
...     out_dim=3,
...     geometry_dim=3,
...     global_dim=16,
...     n_hidden=256,
...     n_layers=4,
...     use_te=False,
... )
>>> local_emb = torch.randn(2, 1000, 64)
>>> geometry = torch.randn(2, 1000, 3)  # (batch, nodes, spatial_dim)
>>> global_emb = torch.randn(2, 1, 16)  # (batch, 1, global_features)
>>> output = model(local_emb, global_embedding=global_emb, geometry=geometry)
>>> output.shape
torch.Size([2, 1000, 3])

To also retrieve the geometry/global context embeddings:

>>> output, emb_states = model(
...     local_emb,
...     global_embedding=global_emb,
...     geometry=geometry,
...     return_embedding_states=True,
... )
>>> emb_states.shape[0] == 2  # batch dimension preserved
True

Structured 2D grid:

>>> model = GeoTransolver(
...     functional_dim=3,
...     out_dim=1,
...     structured_shape=(8, 8),
...     n_hidden=64,
...     n_head=4,
...     n_layers=2,
...     use_te=False,
... )
>>> y = model(torch.randn(2, 8, 8, 3))
>>> y.shape
torch.Size([2, 8, 8, 1])

### 导入与签名

```python
from ai4e_contrib.ability.model.geotransolver.network import GeoTransolver
```

```text
GeoTransolver(functional_dim: int | tuple[int, ...], out_dim: int | tuple[int, ...], geometry_dim: int | None=None, global_dim: int | None=None, n_layers: int=4, n_hidden: int=256, dropout: float=0.0, n_head: int=8, act: str='gelu', mlp_ratio: int=4, slice_num: int=32, use_te: bool=False, time_input: bool=False, plus: bool=False, include_local_features: bool=False, radii: list[float] | None=None, neighbors_in_radius: list[int] | None=None, n_hidden_local: int=32, structured_shape: tuple[int, ...] | None=None, attention_type: Literal['GALE', 'GALE_FA']='GALE', concrete_dropout: bool=False, state_mixing_mode: str='weighted', activation_checkpointing: bool=False, checkpointing_ratio: float=1.0, activation_checkpointing_components: tuple[str, ...] | list[str]=('blocks',))
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `functional_dim` | `int | tuple[int, ...]` | `必填` |
| `out_dim` | `int | tuple[int, ...]` | `必填` |
| `geometry_dim` | `int | None` | `None` |
| `global_dim` | `int | None` | `None` |
| `n_layers` | `int` | `4` |
| `n_hidden` | `int` | `256` |
| `dropout` | `float` | `0.0` |
| `n_head` | `int` | `8` |
| `act` | `str` | `'gelu'` |
| `mlp_ratio` | `int` | `4` |
| `slice_num` | `int` | `32` |
| `use_te` | `bool` | `False` |
| `time_input` | `bool` | `False` |
| `plus` | `bool` | `False` |
| `include_local_features` | `bool` | `False` |
| `radii` | `list[float] | None` | `None` |
| `neighbors_in_radius` | `list[int] | None` | `None` |
| `n_hidden_local` | `int` | `32` |
| `structured_shape` | `tuple[int, ...] | None` | `None` |
| `attention_type` | `Literal['GALE', 'GALE_FA']` | `'GALE'` |
| `concrete_dropout` | `bool` | `False` |
| `state_mixing_mode` | `str` | `'weighted'` |
| `activation_checkpointing` | `bool` | `False` |
| `checkpointing_ratio` | `float` | `1.0` |
| `activation_checkpointing_components` | `tuple[str, ...] | list[str]` | `('blocks',)` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`GeoTransolver`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`NotImplementedError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.geotransolver.network import GeoTransolver

print(signature(GeoTransolver))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`geotransolver/bumper_beam`, `geotransolver/darcy`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_geotransolver`, `aero_cfd.shapenet_car_geotransolver`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `recipe_extensions.geotransolver_aero`

### 源码位置

- 模块：`ai4e_contrib.ability.model.geotransolver.network`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/geotransolver/network.py:105`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.geotransolver.network')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-geotransolver-network-geotransolver-forward"></a>
## `ai4e_contrib.ability.model.geotransolver.network.GeoTransolver.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, local_embedding: torch.Tensor | tuple[torch.Tensor, ...], local_positions: torch.Tensor | tuple[torch.Tensor, ...] | None=None, global_embedding: torch.Tensor | None=None, geometry: torch.Tensor | None=None, time: torch.Tensor | None=None, *, return_embedding_states: bool=False, return_point_features: bool=False) -> torch.Tensor | tuple[torch.Tensor, ...]`
- **规范定义名**：`ai4e_contrib.ability.model.geotransolver.network.GeoTransolver.forward`

### 用途

执行forward；张量布局、参数与返回值见下列参考说明。

Forward pass of the GeoTransolver model.

The model constructs global context embeddings from geometry and global features
by projecting them onto physical state spaces. These context embeddings are then
used in all GALE blocks via cross-attention, allowing geometric and global
information to guide the learned physical state dynamics.

Parameters
----------
local_embedding : torch.Tensor | tuple[torch.Tensor, ...]
    Local embedding of the input data of shape :math:`(B, N, C)` where
    :math:`B` is batch size, :math:`N` is number of nodes/tokens, and
    :math:`C` is ``functional_dim``.
local_positions : torch.Tensor | tuple[torch.Tensor, ...] | None, optional
    Local positions for each input, each of shape :math:`(B, N, 3)`.
    Required if ``include_local_features=True``. Default is ``None``.
global_embedding : torch.Tensor | None, optional
    Global embedding of shape :math:`(B, N_g, C_g)`. Default is ``None``.
geometry : torch.Tensor | None, optional
    Geometry features of shape :math:`(B, N, C_{geo})`. Default is ``None``.
time : torch.Tensor | None, optional
    Time embedding (not yet implemented). Default is ``None``.
return_embedding_states : bool, optional, keyword-only
    If ``True``, return ``(output, embedding_states)`` instead of just
    ``output``.  The ``embedding_states`` tensor contains geometry/global
    context of shape :math:`(B, H, S, D_c)`.  Default is ``False``.
return_point_features : bool, optional, keyword-only
    If ``True``, also return the per-point features computed just before
    the output projection (``ln_mlp_out``), of shape
    :math:`(B, N, D_{eff})` where
    :math:`D_{eff} = n\_hidden + n\_hidden\_local \cdot len(radii)`.
    These per-point latents are intended for attaching pointwise heads
    (e.g. a field GP head for per-point uncertainty).  Returned as the
    last element of the output tuple.  Default is ``False``.

Returns
-------
Float[torch.Tensor, "batch tokens out_dim"] | tuple[Float[torch.Tensor, "batch tokens out_dim"], Float[torch.Tensor, "batch heads slices context_dim"]]
    With neither flag set (default): output tensor of shape
    :math:`(B, N, C_{out})`.

    With one flag set: a 2-tuple, ``(output, embedding_states)`` or
    ``(output, point_features)``.

    With both set: the 3-tuple
    ``(output, embedding_states, point_features)``.  The two flags are
    keyword-only, since they share a return signature and reading a
    bare ``True`` at the call site would not say which was meant.

Raises
------
NotImplementedError
    If ``time`` is provided.
ValueError
    If input tensors have incorrect dimensions.

### 导入与签名

```python
from ai4e_contrib.ability.model.geotransolver.network import GeoTransolver
```

```text
forward(self, local_embedding: torch.Tensor | tuple[torch.Tensor, ...], local_positions: torch.Tensor | tuple[torch.Tensor, ...] | None=None, global_embedding: torch.Tensor | None=None, geometry: torch.Tensor | None=None, time: torch.Tensor | None=None, *, return_embedding_states: bool=False, return_point_features: bool=False) -> torch.Tensor | tuple[torch.Tensor, ...]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `local_embedding` | `torch.Tensor | tuple[torch.Tensor, ...]` | `必填` |
| `local_positions` | `torch.Tensor | tuple[torch.Tensor, ...] | None` | `None` |
| `global_embedding` | `torch.Tensor | None` | `None` |
| `geometry` | `torch.Tensor | None` | `None` |
| `time` | `torch.Tensor | None` | `None` |
| `return_embedding_states` | `bool` | `False` |
| `return_point_features` | `bool` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`torch.Tensor | tuple[torch.Tensor, ...]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`NotImplementedError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.geotransolver.network import GeoTransolver

print(signature(GeoTransolver.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.geotransolver.network`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/geotransolver/network.py:531`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.geotransolver.network')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-geotransolver-network-geotransolver-forward-stream"></a>
## `ai4e_contrib.ability.model.geotransolver.network.GeoTransolver.forward_stream`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward_stream(self, local_embedding: torch.Tensor, *, stream_index: int, geometry: torch.Tensor | None=None, global_embedding: torch.Tensor | None=None) -> torch.Tensor`
- **规范定义名**：`ai4e_contrib.ability.model.geotransolver.network.GeoTransolver.forward_stream`

### 用途

以原权重计算指定非结构点流；仅限不依赖其他流的全局几何分支。

输入 [B,N,C]；输出 [B,N,O]。不新增参数或修改原 forward 的状态键。
局部上下文依赖全部输入流，故该分支明确拒绝局部编码与结构网格。

### 导入与签名

```python
from ai4e_contrib.ability.model.geotransolver.network import GeoTransolver
```

```text
forward_stream(self, local_embedding: torch.Tensor, *, stream_index: int, geometry: torch.Tensor | None=None, global_embedding: torch.Tensor | None=None) -> torch.Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `local_embedding` | `torch.Tensor` | `必填` |
| `stream_index` | `int` | `必填关键字参数` |
| `geometry` | `torch.Tensor | None` | `None` |
| `global_embedding` | `torch.Tensor | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`torch.Tensor`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.geotransolver.network import GeoTransolver

print(signature(GeoTransolver.forward_stream))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.geotransolver.network`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/geotransolver/network.py:506`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.geotransolver.network')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
