<!-- dojo-help: {"domain": "ai4e_core.abilities.modeling.modules.context_projection", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.modeling.modules.context_projection 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.modeling.modules.context_projection", "topic_id": "module:ai4e_core.abilities.modeling.modules.context_projection"} -->
# `ai4e_core.abilities.modeling.modules.context_projection` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-modeling-modules-context-projection-contextprojector"></a>
## `ai4e_core.abilities.modeling.modules.context_projection.ContextProjector`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`ContextProjector(dim: int, heads: int=8, dim_head: int=64, dropout: float=0.0, slice_num: int=64, use_te: bool=False, plus: bool=False, concrete_dropout: bool=False)`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.context_projection.ContextProjector`

### 用途

可独立使用的ContextProjector计算组件。

Projects context features onto physical state space.

This context projector is conceptually similar to half of a GALE attention layer.
It projects context values (geometry or global embeddings) onto a learned physical
state space, but unlike a full attention layer, it never projects back to the
original space. The projected features are used as context in all GALE blocks
of the GeoTransolver model.

Parameters
----------
dim : int
    Input dimension of the context features.
heads : int, optional
    Number of projection heads. Default is 8.
dim_head : int, optional
    Dimension of each projection head. Default is 64.
dropout : float, optional
    Dropout rate. Default is 0.0.
slice_num : int, optional
    Number of learned physical state slices. Default is 64.
use_te : bool, optional
    Whether to use Transformer Engine backend when available. Default is ``False``.
plus : bool, optional
    Whether to use Transolver++ features. Default is ``False``.

Forward
-------
x : torch.Tensor
    Input tensor of shape :math:`(B, N, C)` where :math:`B` is batch size,
    :math:`N` is number of tokens, and :math:`C` is number of channels.

Outputs
-------
torch.Tensor
    Slice tokens of shape :math:`(B, H, S, D)` where :math:`H` is number of heads,
    :math:`S` is number of slices, and :math:`D` is head dimension.

Notes
-----
The global features are reused in all blocks of the model, so the learned
projections must capture globally useful features rather than layer-specific ones.

See Also
--------
:class:`~physicsnemo.nn.module.gale.GALE` : Full GALE attention layer that uses these projected context features.
:class:`~physicsnemo.models.geotransolver.GeoTransolver` : Main model that uses ContextProjector for geometry and global embeddings.

Examples
--------
>>> import torch
>>> projector = ContextProjector(dim=64, heads=8, dim_head=32, slice_num=32, use_te=False)
>>> x = torch.randn(2, 100, 64)  # (batch, tokens, features)
>>> slice_tokens = projector(x)
>>> slice_tokens.shape
torch.Size([2, 8, 32, 32])

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.context_projection import ContextProjector
```

```text
ContextProjector(dim: int, heads: int=8, dim_head: int=64, dropout: float=0.0, slice_num: int=64, use_te: bool=False, plus: bool=False, concrete_dropout: bool=False)
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
| `concrete_dropout` | `bool` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`ContextProjector`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`NotImplementedError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.context_projection import ContextProjector

print(signature(ContextProjector))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.context_projection`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/context_projection.py:142`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.context_projection')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-context-projection-contextprojector-forward"></a>
## `ai4e_core.abilities.modeling.modules.context_projection.ContextProjector.forward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x: torch.Tensor) -> torch.Tensor`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.context_projection.ContextProjector.forward`

### 用途

执行forward；张量布局、参数与返回值见下列参考说明。

Project inputs to physical state slices.

This performs a partial physics attention operation: it projects the input onto
learned physical state slices but does not project back to the original space.
The resulting slice tokens serve as context for GALE attention layers.

Parameters
----------
x : torch.Tensor
    Input tensor of shape :math:`(B, N, C)` where :math:`B` is batch size, :math:`N` is
    number of tokens, and :math:`C` is number of channels.

Returns
-------
torch.Tensor
    Slice tokens of shape :math:`(B, H, S, D)` where :math:`H` is number of heads,
    :math:`S` is number of slices, and :math:`D` is head dimension.

Notes
-----
This method implements the encoding portion of the physics attention mechanism.
The slice tokens capture learned physical state representations that are used
as cross-attention context throughout the model.

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.context_projection import ContextProjector
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

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.context_projection import ContextProjector

print(signature(ContextProjector.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.context_projection`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/context_projection.py:257`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.context_projection')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-context-projection-contextprojector-project-input-onto-slices"></a>
## `ai4e_core.abilities.modeling.modules.context_projection.ContextProjector.project_input_onto_slices`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`project_input_onto_slices(self, x: torch.Tensor) -> torch.Tensor | tuple[torch.Tensor, torch.Tensor]`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.context_projection.ContextProjector.project_input_onto_slices`

### 用途

执行project_input_onto_slices；张量布局、参数与返回值见下列参考说明。

Project the input onto the slice space.

Parameters
----------
x : torch.Tensor
    Input tensor of shape :math:`(B, N, C)` where :math:`B` is batch size,
    :math:`N` is number of tokens, and :math:`C` is number of channels.

Returns
-------
torch.Tensor or tuple[torch.Tensor, torch.Tensor]
    If ``plus=True``, returns single tensor of shape :math:`(B, N, H, D)` where
    :math:`H` is number of heads and :math:`D` is head dimension. If ``plus=False``,
    returns tuple of two tensors both of shape :math:`(B, N, H, D)`, representing
    the query and key projections respectively.

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.context_projection import ContextProjector
```

```text
project_input_onto_slices(self, x: torch.Tensor) -> torch.Tensor | tuple[torch.Tensor, torch.Tensor]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `torch.Tensor` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`torch.Tensor | tuple[torch.Tensor, torch.Tensor]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.context_projection import ContextProjector

print(signature(ContextProjector.project_input_onto_slices))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.context_projection`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/context_projection.py:232`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.context_projection')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-context-projection-globalcontextbuilder"></a>
## `ai4e_core.abilities.modeling.modules.context_projection.GlobalContextBuilder`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`GlobalContextBuilder(functional_dims: tuple[int, ...], geometry_dim: int | None=None, global_dim: int | None=None, radii: list[float] | None=None, neighbors_in_radius: list[int] | None=None, n_hidden_local: int=32, n_hidden: int=256, n_head: int=8, dropout: float=0.0, slice_num: int=32, use_te: bool=False, plus: bool=False, include_local_features: bool=False, structured_shape: tuple[int, ...] | None=None, concrete_dropout: bool=False)`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.context_projection.GlobalContextBuilder`

### 用途

可独立使用的GlobalContextBuilder计算组件。

Orchestrates all context construction with a clean, simple interface.

Manages geometry tokenization, global embedding tokenization, and optional
multi-scale local features. This is the main entry point for building context
in the GeoTransolver model.

Parameters
----------
functional_dims : tuple[int, ...]
    Dimensions of each functional input type.
geometry_dim : int | None, optional
    Geometry feature dimension. If ``None``, geometry context is disabled.
    Default is ``None``.
global_dim : int | None, optional
    Global embedding dimension. If ``None``, global context is disabled.
    Default is ``None``.
radii : list[float], optional
    Radii for local features. Default is ``[0.05, 0.25]``.
neighbors_in_radius : list[int], optional
    Neighbors per radius. Default is ``[8, 32]``.
n_hidden_local : int, optional
    Hidden dim for local features. Default is 32.
n_hidden : int, optional
    Model hidden dimension. Default is 256.
n_head : int, optional
    Number of attention heads. Default is 8.
dropout : float, optional
    Dropout rate. Default is 0.0.
slice_num : int, optional
    Number of slices for tokenization. Default is 32.
use_te : bool, optional
    Whether to use Transformer Engine. Default is ``False``.
plus : bool, optional
    Whether to use Transolver++ features. Default is ``False``.
include_local_features : bool, optional
    Enable local feature extraction. Default is ``False``.
structured_shape : tuple[int, ...] | None, optional
    If set, disables ball-query extractors and uses
    :class:`StructuredContextProjector` for geometry when ``geometry_dim``
    is set. Default is ``None``.

Forward
-------
This class does not implement a standard ``forward`` method. Instead, use
:meth:`build_context` to construct context, local features, and the
detached geometry context.

See Also
--------
:class:`ContextProjector` : Used for tokenizing geometry and global embeddings.
:class:`MultiScaleFeatureExtractor` : Used for multi-scale local features.
:class:`~physicsnemo.models.geotransolver.GeoTransolver` : Main model that uses this builder.

Examples
--------
>>> import torch
>>> builder = GlobalContextBuilder(
...     functional_dims=(64,),
...     geometry_dim=3,
...     global_dim=16,
...     n_hidden=256,
...     n_head=8,
...     use_te=False,
... )
>>> local_embeddings = (torch.randn(2, 100, 64),)
>>> geometry = torch.randn(2, 100, 3)
>>> global_embedding = torch.randn(2, 1, 16)
>>> context, local_feats, geo_ctx = builder.build_context(
...     local_embeddings, None, geometry, global_embedding
... )
>>> context.shape
torch.Size([2, 8, 32, 64])

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.context_projection import GlobalContextBuilder
```

```text
GlobalContextBuilder(functional_dims: tuple[int, ...], geometry_dim: int | None=None, global_dim: int | None=None, radii: list[float] | None=None, neighbors_in_radius: list[int] | None=None, n_hidden_local: int=32, n_hidden: int=256, n_head: int=8, dropout: float=0.0, slice_num: int=32, use_te: bool=False, plus: bool=False, include_local_features: bool=False, structured_shape: tuple[int, ...] | None=None, concrete_dropout: bool=False)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `functional_dims` | `tuple[int, ...]` | `必填` |
| `geometry_dim` | `int | None` | `None` |
| `global_dim` | `int | None` | `None` |
| `radii` | `list[float] | None` | `None` |
| `neighbors_in_radius` | `list[int] | None` | `None` |
| `n_hidden_local` | `int` | `32` |
| `n_hidden` | `int` | `256` |
| `n_head` | `int` | `8` |
| `dropout` | `float` | `0.0` |
| `slice_num` | `int` | `32` |
| `use_te` | `bool` | `False` |
| `plus` | `bool` | `False` |
| `include_local_features` | `bool` | `False` |
| `structured_shape` | `tuple[int, ...] | None` | `None` |
| `concrete_dropout` | `bool` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`GlobalContextBuilder`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`NotImplementedError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.context_projection import GlobalContextBuilder

print(signature(GlobalContextBuilder))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.context_projection`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/context_projection.py:388`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.context_projection')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-context-projection-globalcontextbuilder-build-context"></a>
## `ai4e_core.abilities.modeling.modules.context_projection.GlobalContextBuilder.build_context`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`build_context(self, local_embeddings: tuple[torch.Tensor, ...], local_positions: tuple[torch.Tensor, ...] | None, geometry: torch.Tensor | None=None, global_embedding: torch.Tensor | None=None) -> tuple[torch.Tensor | None, list[torch.Tensor] | None, torch.Tensor | None]`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.context_projection.GlobalContextBuilder.build_context`

### 用途

执行build_context；张量布局、参数与返回值见下列参考说明。

Build all context and local features.

Parameters
----------
local_embeddings : tuple[torch.Tensor, ...]
    Input embeddings, each of shape :math:`(B, N, C_i)` where :math:`B` is
    batch size, :math:`N` is number of tokens, and :math:`C_i` is the feature
    dimension for input type :math:`i`.
local_positions : tuple[torch.Tensor, ...] | None
    Local positions, each of shape :math:`(B, N, 3)`. These are used to query
    neighbors for local features. Required if ``include_local_features=True``.
geometry : torch.Tensor | None, optional
    Geometry features of shape :math:`(B, N, C_{geo})`. Default is ``None``.
global_embedding : torch.Tensor | None, optional
    Global embedding of shape :math:`(B, N_g, C_g)`. Default is ``None``.

Returns
-------
tuple[torch.Tensor | None, list[torch.Tensor] | None, torch.Tensor | None]
    - ``context``: Concatenated context tensor of shape :math:`(B, H, S, D_c)`
      where :math:`D_c` is the total context dimension, or ``None`` if no
      context sources are provided.
    - ``local_features``: List of local feature tensors, one per input type,
      each of shape :math:`(B, N, D_l)`, or ``None`` if local features are
      disabled.
    - ``geometry_context_detached``: Detached geometry-tokenizer output of shape
      :math:`(B, H, S, D)`, intended for downstream observers such as the
      embedded OOD guard.  ``None`` when geometry tokenization is disabled
      or no geometry was provided.

Raises
------
ValueError
    If ``local_positions`` is ``None`` but local features are enabled.

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.context_projection import GlobalContextBuilder
```

```text
build_context(self, local_embeddings: tuple[torch.Tensor, ...], local_positions: tuple[torch.Tensor, ...] | None, geometry: torch.Tensor | None=None, global_embedding: torch.Tensor | None=None) -> tuple[torch.Tensor | None, list[torch.Tensor] | None, torch.Tensor | None]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `local_embeddings` | `tuple[torch.Tensor, ...]` | `必填` |
| `local_positions` | `tuple[torch.Tensor, ...] | None` | `必填` |
| `geometry` | `torch.Tensor | None` | `None` |
| `global_embedding` | `torch.Tensor | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`tuple[torch.Tensor | None, list[torch.Tensor] | None, torch.Tensor | None]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.context_projection import GlobalContextBuilder

print(signature(GlobalContextBuilder.build_context))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.context_projection`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/context_projection.py:575`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.context_projection')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-context-projection-globalcontextbuilder-get-context-dim"></a>
## `ai4e_core.abilities.modeling.modules.context_projection.GlobalContextBuilder.get_context_dim`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`get_context_dim(self) -> int`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.context_projection.GlobalContextBuilder.get_context_dim`

### 用途

执行get_context_dim；张量布局、参数与返回值见下列参考说明。

Return total context dimension.

Returns
-------
int
    Total dimension of the concatenated context features.

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.context_projection import GlobalContextBuilder
```

```text
get_context_dim(self) -> int
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`int`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.context_projection import GlobalContextBuilder

print(signature(GlobalContextBuilder.get_context_dim))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.context_projection`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/context_projection.py:564`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.context_projection')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-context-projection-structuredcontextprojector"></a>
## `ai4e_core.abilities.modeling.modules.context_projection.StructuredContextProjector`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`StructuredContextProjector(dim: int, spatial_shape: tuple[int, ...], heads: int=8, dim_head: int=64, dropout: float=0.0, slice_num: int=64, kernel: int=3, use_te: bool=False, plus: bool=False, concrete_dropout: bool=False)`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.context_projection.StructuredContextProjector`

### 用途

可独立使用的StructuredContextProjector计算组件。

Context projector with Conv2d/Conv3d geometry encoding on structured grids.

Same output interface as :class:`ContextProjector`—slice tokens
:math:`(B, H, S, D)`—but projects per-cell geometry via spatial convolutions
aligned with structured GALE attention.

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.context_projection import StructuredContextProjector
```

```text
StructuredContextProjector(dim: int, spatial_shape: tuple[int, ...], heads: int=8, dim_head: int=64, dropout: float=0.0, slice_num: int=64, kernel: int=3, use_te: bool=False, plus: bool=False, concrete_dropout: bool=False)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dim` | `int` | `必填` |
| `spatial_shape` | `tuple[int, ...]` | `必填` |
| `heads` | `int` | `8` |
| `dim_head` | `int` | `64` |
| `dropout` | `float` | `0.0` |
| `slice_num` | `int` | `64` |
| `kernel` | `int` | `3` |
| `use_te` | `bool` | `False` |
| `plus` | `bool` | `False` |
| `concrete_dropout` | `bool` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`StructuredContextProjector`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`NotImplementedError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.context_projection import StructuredContextProjector

print(signature(StructuredContextProjector))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.context_projection`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/context_projection.py:300`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.context_projection')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-context-projection-structuredcontextprojector-forward"></a>
## `ai4e_core.abilities.modeling.modules.context_projection.StructuredContextProjector.forward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x: torch.Tensor) -> torch.Tensor`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.context_projection.StructuredContextProjector.forward`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.context_projection import StructuredContextProjector
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

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.context_projection import StructuredContextProjector

print(signature(StructuredContextProjector.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.context_projection`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/context_projection.py:370`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.context_projection')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
