<!-- dojo-help: {"domain": "ai4e_core.abilities.modeling.modules.physics_attention", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.modeling.modules.physics_attention 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.modeling.modules.physics_attention", "topic_id": "module:ai4e_core.abilities.modeling.modules.physics_attention"} -->
# `ai4e_core.abilities.modeling.modules.physics_attention` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-modeling-modules-physics-attention-physicsattentionbase"></a>
## `ai4e_core.abilities.modeling.modules.physics_attention.PhysicsAttentionBase`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`PhysicsAttentionBase(dim: int, heads: int, dim_head: int, dropout: float, slice_num: int, use_te: bool, plus: bool)`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.physics_attention.PhysicsAttentionBase`

### 用途

可独立使用的PhysicsAttentionBase计算组件。

Base class for physics attention modules.

This class implements the core physics attention mechanism that projects
inputs onto learned physics-informed slices before applying attention.
Subclasses implement domain-specific input projections.

The physics attention mechanism consists of:

1. Project inputs onto learned slice space
2. Compute slice weights via temperature-scaled softmax
3. Aggregate features for each slice
4. Apply attention among slices
5. Project attended features back to original space

Parameters
----------
dim : int
    Input feature dimension.
heads : int
    Number of attention heads.
dim_head : int
    Dimension per attention head.
dropout : float
    Dropout rate.
slice_num : int
    Number of physics slices.
use_te : bool
    Whether to use transformer engine.
plus : bool
    Whether to use Transolver++ variant.

Forward
-------
x : torch.Tensor
    Input tensor of shape :math:`(B, N, C)` where :math:`B` is batch size,
    :math:`N` is number of tokens, and :math:`C` is feature dimension.

Outputs
-------
torch.Tensor
    Output tensor of shape :math:`(B, N, C)`.

See Also
--------
This is an abstract base class. Use one of the concrete implementations:

- :class:`PhysicsAttentionIrregularMesh` for unstructured mesh data
- :class:`PhysicsAttentionStructuredMesh2D` for 2D image-like data
- :class:`PhysicsAttentionStructuredMesh3D` for 3D volumetric data

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.physics_attention import PhysicsAttentionBase
```

```text
PhysicsAttentionBase(dim: int, heads: int, dim_head: int, dropout: float, slice_num: int, use_te: bool, plus: bool)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dim` | `int` | `必填` |
| `heads` | `int` | `必填` |
| `dim_head` | `int` | `必填` |
| `dropout` | `float` | `必填` |
| `slice_num` | `int` | `必填` |
| `use_te` | `bool` | `必填` |
| `plus` | `bool` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`PhysicsAttentionBase`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`NotImplementedError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.physics_attention import PhysicsAttentionBase

print(signature(PhysicsAttentionBase))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.physics_attention`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/physics_attention.py:133`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.physics_attention')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-physics-attention-physicsattentionbase-forward"></a>
## `ai4e_core.abilities.modeling.modules.physics_attention.PhysicsAttentionBase.forward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x: torch.Tensor) -> torch.Tensor`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.physics_attention.PhysicsAttentionBase.forward`

### 用途

执行forward；张量布局、参数与返回值见下列参考说明。

Forward pass of physics attention.

Parameters
----------
x : torch.Tensor
    Input tensor of shape :math:`(B, N, C)`.

Returns
-------
torch.Tensor
    Output tensor of shape :math:`(B, N, C)`.

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.physics_attention import PhysicsAttentionBase
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
from ai4e_core.abilities.modeling.modules.physics_attention import PhysicsAttentionBase

print(signature(PhysicsAttentionBase.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.physics_attention`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/physics_attention.py:375`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.physics_attention')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-physics-attention-physicsattentionbase-project-input-onto-slices"></a>
## `ai4e_core.abilities.modeling.modules.physics_attention.PhysicsAttentionBase.project_input_onto_slices`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`project_input_onto_slices(self, x: torch.Tensor) -> torch.Tensor | tuple[torch.Tensor, torch.Tensor]`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.physics_attention.PhysicsAttentionBase.project_input_onto_slices`

### 用途

执行project_input_onto_slices；张量布局、参数与返回值见下列参考说明。

Project input tensor onto the slice space.

Parameters
----------
x : torch.Tensor
    Input tensor of shape :math:`(B, N, C)`.

Returns
-------
torch.Tensor | tuple[torch.Tensor, torch.Tensor]
    For Transolver++: single projected tensor of shape
    :math:`(B, N, H, D)` where :math:`H` is number of attention heads
    and :math:`D` is dimension per head.
    For standard Transolver: tuple of (x_mid, fx_mid) both of shape
    :math:`(B, N, H, D)`.

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.physics_attention import PhysicsAttentionBase
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
from ai4e_core.abilities.modeling.modules.physics_attention import PhysicsAttentionBase

print(signature(PhysicsAttentionBase.project_input_onto_slices))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.physics_attention`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/physics_attention.py:241`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.physics_attention')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-physics-attention-physicsattentionirregularmesh"></a>
## `ai4e_core.abilities.modeling.modules.physics_attention.PhysicsAttentionIrregularMesh`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`PhysicsAttentionIrregularMesh(dim: int, heads: int=8, dim_head: int=64, dropout: float=0.0, slice_num: int=64, use_te: bool=False, plus: bool=False)`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.physics_attention.PhysicsAttentionIrregularMesh`

### 用途

可独立使用的PhysicsAttentionIrregularMesh计算组件。

Physics attention for irregular/unstructured mesh data.

Uses linear projections to map input tokens to the slice space, suitable
for meshes with arbitrary connectivity.

Parameters
----------
dim : int
    Input feature dimension.
heads : int, optional, default=8
    Number of attention heads.
dim_head : int, optional, default=64
    Dimension per attention head.
dropout : float, optional, default=0.0
    Dropout rate.
slice_num : int, optional, default=64
    Number of physics slices.
use_te : bool, optional, default=True
    Whether to use transformer engine.
plus : bool, optional, default=False
    Whether to use Transolver++ variant.

Forward
-------
x : torch.Tensor
    Input tensor of shape :math:`(B, N, C)` where :math:`B` is batch size,
    :math:`N` is number of tokens, and :math:`C` is feature dimension.

Outputs
-------
torch.Tensor
    Output tensor of shape :math:`(B, N, C)`.

Examples
--------
>>> import torch
>>> attn = PhysicsAttentionIrregularMesh(dim=128, heads=4, dim_head=32, dropout=0.0, slice_num=16, use_te=False)
>>> x = torch.randn(2, 1000, 128)
>>> out = attn(x)
>>> out.shape
torch.Size([2, 1000, 128])

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.physics_attention import PhysicsAttentionIrregularMesh
```

```text
PhysicsAttentionIrregularMesh(dim: int, heads: int=8, dim_head: int=64, dropout: float=0.0, slice_num: int=64, use_te: bool=False, plus: bool=False)
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

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`PhysicsAttentionIrregularMesh`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`NotImplementedError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.physics_attention import PhysicsAttentionIrregularMesh

print(signature(PhysicsAttentionIrregularMesh))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.physics_attention`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/physics_attention.py:414`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.physics_attention')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-physics-attention-physicsattentionirregularmesh-project-input-onto-slices"></a>
## `ai4e_core.abilities.modeling.modules.physics_attention.PhysicsAttentionIrregularMesh.project_input_onto_slices`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`project_input_onto_slices(self, x: torch.Tensor) -> torch.Tensor | tuple[torch.Tensor, torch.Tensor]`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.physics_attention.PhysicsAttentionIrregularMesh.project_input_onto_slices`

### 用途

执行project_input_onto_slices；张量布局、参数与返回值见下列参考说明。

Project input onto slice space using linear layers.

Parameters
----------
x : torch.Tensor
    Input tensor of shape :math:`(B, N, C)`.

Returns
-------
torch.Tensor | tuple[torch.Tensor, torch.Tensor]
    Projected tensors of shape :math:`(B, N, H, D)` where :math:`H` is
    number of attention heads and :math:`D` is dimension per head.

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.physics_attention import PhysicsAttentionIrregularMesh
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
from ai4e_core.abilities.modeling.modules.physics_attention import PhysicsAttentionIrregularMesh

print(signature(PhysicsAttentionIrregularMesh.project_input_onto_slices))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.physics_attention`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/physics_attention.py:482`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.physics_attention')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-physics-attention-physicsattentionstructuredmesh2d"></a>
## `ai4e_core.abilities.modeling.modules.physics_attention.PhysicsAttentionStructuredMesh2D`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`PhysicsAttentionStructuredMesh2D(dim: int, spatial_shape: tuple[int, int], heads: int=8, dim_head: int=64, dropout: float=0.0, slice_num: int=64, kernel: int=3, use_te: bool=False, plus: bool=False)`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.physics_attention.PhysicsAttentionStructuredMesh2D`

### 用途

可独立使用的PhysicsAttentionStructuredMesh2D计算组件。

Physics attention for 2D structured/image-like data.

Uses 2D convolutions to project inputs, leveraging spatial locality in
structured grids.

Parameters
----------
dim : int
    Input feature dimension.
spatial_shape : tuple[int, int]
    Spatial dimensions (height, width) of the input.
heads : int, optional, default=8
    Number of attention heads.
dim_head : int, optional, default=64
    Dimension per attention head.
dropout : float, optional, default=0.0
    Dropout rate.
slice_num : int, optional, default=64
    Number of physics slices.
kernel : int, optional, default=3
    Convolution kernel size.
use_te : bool, optional, default=True
    Whether to use transformer engine.
plus : bool, optional, default=False
    Whether to use Transolver++ variant.

Forward
-------
x : torch.Tensor
    Input tensor of shape :math:`(B, N, C)` where :math:`B` is batch size,
    :math:`N` is number of tokens (flattened spatial: height times width),
    and :math:`C` is feature dimension.

Outputs
-------
torch.Tensor
    Output tensor of shape :math:`(B, N, C)`.

Examples
--------
>>> import torch
>>> attn = PhysicsAttentionStructuredMesh2D(
...     dim=128,
...     spatial_shape=(32, 32),
...     heads=4,
...     dim_head=32,
...     dropout=0.0,
...     slice_num=16,
...     use_te=False,
... )
>>> x = torch.randn(2, 32*32, 128)
>>> out = attn(x)
>>> out.shape
torch.Size([2, 1024, 128])

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.physics_attention import PhysicsAttentionStructuredMesh2D
```

```text
PhysicsAttentionStructuredMesh2D(dim: int, spatial_shape: tuple[int, int], heads: int=8, dim_head: int=64, dropout: float=0.0, slice_num: int=64, kernel: int=3, use_te: bool=False, plus: bool=False)
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

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`PhysicsAttentionStructuredMesh2D`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`NotImplementedError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.physics_attention import PhysicsAttentionStructuredMesh2D

print(signature(PhysicsAttentionStructuredMesh2D))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.physics_attention`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/physics_attention.py:505`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.physics_attention')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-physics-attention-physicsattentionstructuredmesh2d-project-input-onto-slices"></a>
## `ai4e_core.abilities.modeling.modules.physics_attention.PhysicsAttentionStructuredMesh2D.project_input_onto_slices`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`project_input_onto_slices(self, x: torch.Tensor) -> torch.Tensor | tuple[torch.Tensor, torch.Tensor]`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.physics_attention.PhysicsAttentionStructuredMesh2D.project_input_onto_slices`

### 用途

执行project_input_onto_slices；张量布局、参数与返回值见下列参考说明。

Project input onto slice space using 2D convolutions.

Parameters
----------
x : torch.Tensor
    Input tensor of shape :math:`(B, N, C)` where :math:`N` is the
    flattened spatial dimension (height times width).

Returns
-------
torch.Tensor | tuple[torch.Tensor, torch.Tensor]
    Projected tensors of shape :math:`(B, N, H, D)` where :math:`H` is
    number of attention heads and :math:`D` is dimension per head.

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.physics_attention import PhysicsAttentionStructuredMesh2D
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
from ai4e_core.abilities.modeling.modules.physics_attention import PhysicsAttentionStructuredMesh2D

print(signature(PhysicsAttentionStructuredMesh2D.project_input_onto_slices))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.physics_attention`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/physics_attention.py:587`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.physics_attention')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
