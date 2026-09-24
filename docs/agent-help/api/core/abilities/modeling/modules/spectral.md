<!-- dojo-help: {"domain": "ai4e_core.abilities.modeling.modules.spectral", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.modeling.modules.spectral 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.modeling.modules.spectral", "topic_id": "module:ai4e_core.abilities.modeling.modules.spectral"} -->
# `ai4e_core.abilities.modeling.modules.spectral` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-modeling-modules-spectral-fourierblock"></a>
## `ai4e_core.abilities.modeling.modules.spectral.FourierBlock`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`FourierBlock(in_channels: int, out_channels: int, modes: tuple[int, ...], *, activation: str='gelu', fft_norm: str='forward', dtype: torch.dtype=torch.float32, spectral: nn.Module | None=None, local: nn.Module | None=None)`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.spectral.FourierBlock`

### 用途

谱卷积与逐点局部分支相加，再施加显式激活。

两支可替换为普通模块，必须输出相同布局；默认局部支复用 ConvBlock。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.spectral import FourierBlock
```

```text
FourierBlock(in_channels: int, out_channels: int, modes: tuple[int, ...], *, activation: str='gelu', fft_norm: str='forward', dtype: torch.dtype=torch.float32, spectral: nn.Module | None=None, local: nn.Module | None=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `in_channels` | `int` | `必填` |
| `out_channels` | `int` | `必填` |
| `modes` | `tuple[int, ...]` | `必填` |
| `activation` | `str` | `'gelu'` |
| `fft_norm` | `str` | `'forward'` |
| `dtype` | `torch.dtype` | `torch.float32` |
| `spectral` | `nn.Module | None` | `None` |
| `local` | `nn.Module | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`FourierBlock`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`TypeError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.spectral import FourierBlock

print(signature(FourierBlock))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.spectral`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/spectral.py:82`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.spectral')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-spectral-fourierblock-forward"></a>
## `ai4e_core.abilities.modeling.modules.spectral.FourierBlock.forward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, value: Tensor) -> Tensor`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.spectral.FourierBlock.forward`

### 用途

保留空间布局，两分支不允许依靠隐式广播相加。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.spectral import FourierBlock
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

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.spectral import FourierBlock

print(signature(FourierBlock.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.spectral`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/spectral.py:124`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.spectral')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-spectral-spectralconv"></a>
## `ai4e_core.abilities.modeling.modules.spectral.SpectralConv`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`SpectralConv(in_channels: int, out_channels: int, modes: tuple[int, ...], *, fft_norm: str='forward', dtype: torch.dtype=torch.float32)`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.spectral.SpectralConv`

### 用途

截断实频谱上的通道映射，无偏置。

modes 前 d-1 轴每侧保留 m 个频率，即 [0,m)、[-m,0)；最后 rFFT
轴保留 [0,m)。不静默裁断越界模式。weight_parts 是末轴为实/虚部的
实数参数，weight 是复数视图；常规 float/double/to 不会丢虚部。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.spectral import SpectralConv
```

```text
SpectralConv(in_channels: int, out_channels: int, modes: tuple[int, ...], *, fft_norm: str='forward', dtype: torch.dtype=torch.float32)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `in_channels` | `int` | `必填` |
| `out_channels` | `int` | `必填` |
| `modes` | `tuple[int, ...]` | `必填` |
| `fft_norm` | `str` | `'forward'` |
| `dtype` | `torch.dtype` | `torch.float32` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`SpectralConv`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.spectral import SpectralConv

print(signature(SpectralConv))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.spectral`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/spectral.py:15`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.spectral')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-spectral-spectralconv-forward"></a>
## `ai4e_core.abilities.modeling.modules.spectral.SpectralConv.forward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, value: Tensor) -> Tensor`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.spectral.SpectralConv.forward`

### 用途

将实数 [B,Cin,*S] 映射为 [B,Cout,*S]，显式保留奇偶尺寸。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.spectral import SpectralConv
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

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.spectral import SpectralConv

print(signature(SpectralConv.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.spectral`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/spectral.py:55`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.spectral')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-spectral-spectralconv-weight"></a>
## `ai4e_core.abilities.modeling.modules.spectral.SpectralConv.weight`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`weight(self) -> Tensor`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.spectral.SpectralConv.weight`

### 用途

复数权重视图；需写入时用 no_grad 下的 copy_，梯度读取 weight_parts。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.spectral import SpectralConv
```

```text
weight(self) -> Tensor
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

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
from ai4e_core.abilities.modeling.modules.spectral import SpectralConv

print(signature(SpectralConv.weight))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`, `parametric_pde`, `safediffcon`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `parametric_pde.advection`, `parametric_pde.burgers`, `parametric_pde.convection_diffusion`, `parametric_pde.diffusion_trapezoid`, `parametric_pde.neumann_diffusion`, `recipe_extensions.field_mapping`, `recipe_extensions.safediffcon`, `recipe_extensions.sampling`, `recipe_extensions.task_labels`, `safediffcon.burgers`, `safediffcon.tokamak`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.spectral`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/spectral.py:51`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.spectral')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
