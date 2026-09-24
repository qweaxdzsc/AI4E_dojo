<!-- dojo-help: {"domain": "ai4e_core.abilities.modeling.modules.position_encoding", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.modeling.modules.position_encoding 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.modeling.modules.position_encoding", "topic_id": "module:ai4e_core.abilities.modeling.modules.position_encoding"} -->
# `ai4e_core.abilities.modeling.modules.position_encoding` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-modeling-modules-position-encoding-continuoussincosembed"></a>
## `ai4e_core.abilities.modeling.modules.position_encoding.ContinuousSincosEmbed`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`ContinuousSincosEmbed(dim: int, ndim: int, max_wavelength: int=10000, assert_positive: bool=True)`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.position_encoding.ContinuousSincosEmbed`

### 用途

Embedding layer for continuous coordinates using sine and cosine functions as used in transformers.
This implementation is able to deal with arbitrary coordinate dimensions (e.g., 2D and 3D coordinate systems).

Args:
    dim: Dimensionality of the embedded input coordinates.
    ndim: Number of dimensions of the input domain.
    max_wavelength: Max length. Defaults to 10000.
    assert_positive: If true, assert if all input coordiantes are positive. Defaults to True.

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.position_encoding import ContinuousSincosEmbed
```

```text
ContinuousSincosEmbed(dim: int, ndim: int, max_wavelength: int=10000, assert_positive: bool=True)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dim` | `int` | `必填` |
| `ndim` | `int` | `必填` |
| `max_wavelength` | `int` | `10000` |
| `assert_positive` | `bool` | `True` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`ContinuousSincosEmbed`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`NotImplementedError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.position_encoding import ContinuousSincosEmbed

print(signature(ContinuousSincosEmbed))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.unet_transformer`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.position_encoding`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/position_encoding.py:8`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.position_encoding')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-position-encoding-continuoussincosembed-forward"></a>
## `ai4e_core.abilities.modeling.modules.position_encoding.ContinuousSincosEmbed.forward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, coords: torch.Tensor) -> torch.Tensor`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.position_encoding.ContinuousSincosEmbed.forward`

### 用途

Forward method of the ContinuousSincosEmbed layer.

Args:
    coords: Tensor of coordinates. The shape of the tensor should be
        (batch size, number of points, coordinate dimension) or (number of points, coordinate dimension).

Returns:
    Tensor with embedded coordinates.

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.position_encoding import ContinuousSincosEmbed
```

```text
forward(self, coords: torch.Tensor) -> torch.Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `coords` | `torch.Tensor` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`torch.Tensor`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`NotImplementedError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.position_encoding import ContinuousSincosEmbed

print(signature(ContinuousSincosEmbed.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.position_encoding`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/position_encoding.py:44`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.position_encoding')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-position-encoding-ropefrequency"></a>
## `ai4e_core.abilities.modeling.modules.position_encoding.RopeFrequency`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`RopeFrequency(dim: int, ndim: int, max_wavelength: int=10000.0, assert_positive: bool=True)`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.position_encoding.RopeFrequency`

### 用途

Creates frequencies for rotary embeddings (RoPE) from https://arxiv.org/abs/2104.09864 for variable positions.

Args:
    dim: Dimensionality of frequencies (in transformers this should be the head dimension).
    ndim: Dimensionality of the coordinates (e.g., 2 for 2D coordinates, 3 for 3D coordinates).
    max_wavelength: Theta parameter for the transformer sine/cosine embedding. Default: 10000.0
    assert_positive: Makes sure that coordinates were rescaled to be positive only. Default: True

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.position_encoding import RopeFrequency
```

```text
RopeFrequency(dim: int, ndim: int, max_wavelength: int=10000.0, assert_positive: bool=True)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dim` | `int` | `必填` |
| `ndim` | `int` | `必填` |
| `max_wavelength` | `int` | `10000.0` |
| `assert_positive` | `bool` | `True` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`RopeFrequency`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.position_encoding import RopeFrequency

print(signature(RopeFrequency))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.position_encoding`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/position_encoding.py:77`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.position_encoding')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-position-encoding-ropefrequency-forward"></a>
## `ai4e_core.abilities.modeling.modules.position_encoding.RopeFrequency.forward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, coords: torch.Tensor) -> torch.Tensor`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.position_encoding.RopeFrequency.forward`

### 用途

生成与坐标同设备的复数旋转频率，不隐式跨设备计算。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.position_encoding import RopeFrequency
```

```text
forward(self, coords: torch.Tensor) -> torch.Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `coords` | `torch.Tensor` | `必填` |

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
from ai4e_core.abilities.modeling.modules.position_encoding import RopeFrequency

print(signature(RopeFrequency.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.position_encoding`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/position_encoding.py:112`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.position_encoding')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
