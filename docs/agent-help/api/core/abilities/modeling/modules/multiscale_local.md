<!-- dojo-help: {"domain": "ai4e_core.abilities.modeling.modules.multiscale_local", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.modeling.modules.multiscale_local 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.modeling.modules.multiscale_local", "topic_id": "module:ai4e_core.abilities.modeling.modules.multiscale_local"} -->
# `ai4e_core.abilities.modeling.modules.multiscale_local` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-modeling-modules-multiscale-local-geometricfeatureprocessor"></a>
## `ai4e_core.abilities.modeling.modules.multiscale_local.GeometricFeatureProcessor`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`GeometricFeatureProcessor(radius: float, neighbors_in_radius: int, feature_dim: int, hidden_dim: int)`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.multiscale_local.GeometricFeatureProcessor`

### 用途

可独立使用的GeometricFeatureProcessor计算组件。

Processes geometric features at a single spatial scale using BQWarp.

This is a simple, reusable component that handles neighbor querying and
feature processing for one radius scale. It encapsulates the BQWarp +
MLP pattern used throughout the model.

Parameters
----------
radius : float
    Query radius for neighbor search.
neighbors_in_radius : int
    Maximum number of neighbors within the radius.
feature_dim : int
    Dimension of the input features to query.
hidden_dim : int
    Output dimension after MLP processing.

Forward
-------
query_points : torch.Tensor
    Query coordinates of shape :math:`(B, N, 3)` where :math:`B` is batch size
    and :math:`N` is number of query points.
key_features : torch.Tensor
    Features to query from of shape :math:`(B, N, C)` where :math:`C` is
    ``feature_dim``.

Outputs
-------
torch.Tensor
    Processed features of shape :math:`(B, N, D)` where :math:`D` is ``hidden_dim``.

See Also
--------
:class:`MultiScaleFeatureExtractor` : Uses multiple GeometricFeatureProcessor instances.
:class:`~physicsnemo.nn.BQWarp` : The ball query operation used internally.

Examples
--------
>>> import torch
>>> processor = GeometricFeatureProcessor(
...     radius=0.1, neighbors_in_radius=16, feature_dim=3, hidden_dim=64
... )
>>> query_points = torch.randn(2, 100, 3)  # (batch, points, xyz)
>>> key_features = torch.randn(2, 100, 3)  # (batch, points, features)
>>> output = processor(query_points, key_features)
>>> output.shape
torch.Size([2, 100, 64])

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.multiscale_local import GeometricFeatureProcessor
```

```text
GeometricFeatureProcessor(radius: float, neighbors_in_radius: int, feature_dim: int, hidden_dim: int)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `radius` | `float` | `必填` |
| `neighbors_in_radius` | `int` | `必填` |
| `feature_dim` | `int` | `必填` |
| `hidden_dim` | `int` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`GeometricFeatureProcessor`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.multiscale_local import GeometricFeatureProcessor

print(signature(GeometricFeatureProcessor))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.multiscale_local`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/multiscale_local.py:19`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.multiscale_local')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-multiscale-local-geometricfeatureprocessor-forward"></a>
## `ai4e_core.abilities.modeling.modules.multiscale_local.GeometricFeatureProcessor.forward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, query_points: torch.Tensor, key_features: torch.Tensor) -> torch.Tensor`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.multiscale_local.GeometricFeatureProcessor.forward`

### 用途

执行forward；张量布局、参数与返回值见下列参考说明。

Query neighbors and process features.

Parameters
----------
query_points : torch.Tensor
    Query coordinates of shape :math:`(B, N, 3)` where :math:`B` is batch size
    and :math:`N` is number of query points.
key_features : torch.Tensor
    Features to query from of shape :math:`(B, N, C)` where :math:`C` is the
    feature dimension.

Returns
-------
torch.Tensor
    Processed features of shape :math:`(B, N, D)` where :math:`D` is the
    hidden dimension.

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.multiscale_local import GeometricFeatureProcessor
```

```text
forward(self, query_points: torch.Tensor, key_features: torch.Tensor) -> torch.Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `query_points` | `torch.Tensor` | `必填` |
| `key_features` | `torch.Tensor` | `必填` |

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
from ai4e_core.abilities.modeling.modules.multiscale_local import GeometricFeatureProcessor

print(signature(GeometricFeatureProcessor.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.multiscale_local`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/multiscale_local.py:83`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.multiscale_local')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-multiscale-local-multiscalefeatureextractor"></a>
## `ai4e_core.abilities.modeling.modules.multiscale_local.MultiScaleFeatureExtractor`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`MultiScaleFeatureExtractor(geometry_dim: int, radii: list[float], neighbors_in_radius: list[int], hidden_dim: int, n_head: int, dim_head: int, dropout: float=0.0, slice_num: int=64, use_te: bool=False, plus: bool=False, concrete_dropout: bool=False)`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.multiscale_local.MultiScaleFeatureExtractor`

### 用途

可独立使用的MultiScaleFeatureExtractor计算组件。

Multi-scale geometric feature extraction with minimal complexity.

Manages multiple GeometricFeatureProcessor instances for different radii.
Provides both tokenized context and concatenated local features.

Parameters
----------
geometry_dim : int
    Dimension of geometry features.
radii : list[float]
    Radii for multi-scale processing.
neighbors_in_radius : list[int]
    Neighbors per radius (must have same length as ``radii``).
hidden_dim : int
    Hidden dimension for processing.
n_head : int
    Number of attention heads.
dim_head : int
    Dimension per head.
dropout : float, optional
    Dropout rate. Default is 0.0.
slice_num : int, optional
    Number of slices for context tokenization. Default is 64.
use_te : bool, optional
    Whether to use Transformer Engine. Default is ``False``.
plus : bool, optional
    Whether to use Transolver++ features. Default is ``False``.

Forward
-------
This class does not implement a standard ``forward`` method. Instead, use:

- :meth:`extract_context_features`: Get tokenized features for GALE context.
- :meth:`extract_local_features`: Get concatenated features for local pathway.

See Also
--------
:class:`GeometricFeatureProcessor` : Single-scale processor used by this class.
:class:`ContextProjector` : Tokenizer used for context features.
:class:`GlobalContextBuilder` : High-level builder that uses this class.

Examples
--------
>>> import torch
>>> extractor = MultiScaleFeatureExtractor(
...     geometry_dim=3,
...     radii=[0.05, 0.25],
...     neighbors_in_radius=[8, 32],
...     hidden_dim=32,
...     n_head=8,
...     dim_head=32,
...     use_te=False,
... )
>>> spatial_coords = torch.randn(2, 100, 3)
>>> geometry = torch.randn(2, 100, 3)
>>> context_feats = extractor.extract_context_features(spatial_coords, geometry)
>>> len(context_feats)  # One per scale
2
>>> local_feats = extractor.extract_local_features(spatial_coords, geometry)
>>> local_feats.shape  # Concatenated across scales
torch.Size([2, 100, 64])

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.multiscale_local import MultiScaleFeatureExtractor
```

```text
MultiScaleFeatureExtractor(geometry_dim: int, radii: list[float], neighbors_in_radius: list[int], hidden_dim: int, n_head: int, dim_head: int, dropout: float=0.0, slice_num: int=64, use_te: bool=False, plus: bool=False, concrete_dropout: bool=False)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `geometry_dim` | `int` | `必填` |
| `radii` | `list[float]` | `必填` |
| `neighbors_in_radius` | `list[int]` | `必填` |
| `hidden_dim` | `int` | `必填` |
| `n_head` | `int` | `必填` |
| `dim_head` | `int` | `必填` |
| `dropout` | `float` | `0.0` |
| `slice_num` | `int` | `64` |
| `use_te` | `bool` | `False` |
| `plus` | `bool` | `False` |
| `concrete_dropout` | `bool` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`MultiScaleFeatureExtractor`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`NotImplementedError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.multiscale_local import MultiScaleFeatureExtractor

print(signature(MultiScaleFeatureExtractor))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.multiscale_local`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/multiscale_local.py:116`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.multiscale_local')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-multiscale-local-multiscalefeatureextractor-extract-context-features"></a>
## `ai4e_core.abilities.modeling.modules.multiscale_local.MultiScaleFeatureExtractor.extract_context_features`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`extract_context_features(self, spatial_coords: torch.Tensor, geometry: torch.Tensor) -> list[torch.Tensor]`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.multiscale_local.MultiScaleFeatureExtractor.extract_context_features`

### 用途

执行extract_context_features；张量布局、参数与返回值见下列参考说明。

Extract and tokenize features for context.

Parameters
----------
spatial_coords : torch.Tensor
    Spatial coordinates of shape :math:`(B, N, 3)`.
geometry : torch.Tensor
    Geometry features of shape :math:`(B, N, C_{geo})`.

Returns
-------
list[torch.Tensor]
    List of tokenized context features, one per scale, each of shape
    :math:`(B, H, S, D)`.

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.multiscale_local import MultiScaleFeatureExtractor
```

```text
extract_context_features(self, spatial_coords: torch.Tensor, geometry: torch.Tensor) -> list[torch.Tensor]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `spatial_coords` | `torch.Tensor` | `必填` |
| `geometry` | `torch.Tensor` | `必填` |

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
from ai4e_core.abilities.modeling.modules.multiscale_local import MultiScaleFeatureExtractor

print(signature(MultiScaleFeatureExtractor.extract_context_features))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.multiscale_local`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/multiscale_local.py:223`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.multiscale_local')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-multiscale-local-multiscalefeatureextractor-extract-local-features"></a>
## `ai4e_core.abilities.modeling.modules.multiscale_local.MultiScaleFeatureExtractor.extract_local_features`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`extract_local_features(self, spatial_coords: torch.Tensor, geometry: torch.Tensor) -> torch.Tensor`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.multiscale_local.MultiScaleFeatureExtractor.extract_local_features`

### 用途

执行extract_local_features；张量布局、参数与返回值见下列参考说明。

Extract and concatenate features for local pathway.

Parameters
----------
spatial_coords : torch.Tensor
    Spatial coordinates of shape :math:`(B, N, 3)`.
geometry : torch.Tensor
    Geometry features of shape :math:`(B, N, C_{geo})`.

Returns
-------
torch.Tensor
    Concatenated local features of shape :math:`(B, N, D_{total})` where
    :math:`D_{total}` is ``hidden_dim * num_scales``.

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.multiscale_local import MultiScaleFeatureExtractor
```

```text
extract_local_features(self, spatial_coords: torch.Tensor, geometry: torch.Tensor) -> torch.Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `spatial_coords` | `torch.Tensor` | `必填` |
| `geometry` | `torch.Tensor` | `必填` |

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
from ai4e_core.abilities.modeling.modules.multiscale_local import MultiScaleFeatureExtractor

print(signature(MultiScaleFeatureExtractor.extract_local_features))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.multiscale_local`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/multiscale_local.py:247`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.multiscale_local')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
