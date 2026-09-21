<!-- dojo-help: {"domain": "ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d", "topic_id": "module:ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d"} -->
# `ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-local-torch-utils-ops-upfirdn2d-downsample2d"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d.downsample2d`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`downsample2d(x, f, down=2, padding=0, flip_filter=False, gain=1, impl='cuda')`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d.downsample2d`

### 用途

Downsample a batch of 2D images using the given 2D FIR filter.

By default, the result is padded so that its shape is a fraction of the input.
User-specified padding is applied on top of that, with negative values
indicating cropping. Pixels outside the image are assumed to be zero.

Args:
    x:           Float32/float64/float16 input tensor of the shape
                 `[batch_size, num_channels, in_height, in_width]`.
    f:           Float32 FIR filter of the shape
                 `[filter_height, filter_width]` (non-separable),
                 `[filter_taps]` (separable), or
                 `None` (identity).
    down:        Integer downsampling factor. Can be a single int or a list/tuple
                 `[x, y]` (default: 1).
    padding:     Padding with respect to the input. Can be a single number or a
                 list/tuple `[x, y]` or `[x_before, x_after, y_before, y_after]`
                 (default: 0).
    flip_filter: False = convolution, True = correlation (default: False).
    gain:        Overall scaling factor for signal magnitude (default: 1).
    impl:        Implementation to use. Can be `'ref'` or `'cuda'` (default: `'cuda'`).

Returns:
    Tensor of the shape `[batch_size, num_channels, out_height, out_width]`.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d import downsample2d
```

```text
downsample2d(x, f, down=2, padding=0, flip_filter=False, gain=1, impl='cuda')
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `f` | `未标注` | `必填` |
| `down` | `未标注` | `2` |
| `padding` | `未标注` | `0` |
| `flip_filter` | `未标注` | `False` |
| `gain` | `未标注` | `1` |
| `impl` | `未标注` | `'cuda'` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d import downsample2d

print(signature(downsample2d))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/local_torch_utils/ops/upfirdn2d.py:353`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-local-torch-utils-ops-upfirdn2d-filter2d"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d.filter2d`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`filter2d(x, f, padding=0, flip_filter=False, gain=1, impl='cuda')`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d.filter2d`

### 用途

Filter a batch of 2D images using the given 2D FIR filter.

By default, the result is padded so that its shape matches the input.
User-specified padding is applied on top of that, with negative values
indicating cropping. Pixels outside the image are assumed to be zero.

Args:
    x:           Float32/float64/float16 input tensor of the shape
                 `[batch_size, num_channels, in_height, in_width]`.
    f:           Float32 FIR filter of the shape
                 `[filter_height, filter_width]` (non-separable),
                 `[filter_taps]` (separable), or
                 `None` (identity).
    padding:     Padding with respect to the output. Can be a single number or a
                 list/tuple `[x, y]` or `[x_before, x_after, y_before, y_after]`
                 (default: 0).
    flip_filter: False = convolution, True = correlation (default: False).
    gain:        Overall scaling factor for signal magnitude (default: 1).
    impl:        Implementation to use. Can be `'ref'` or `'cuda'` (default: `'cuda'`).

Returns:
    Tensor of the shape `[batch_size, num_channels, out_height, out_width]`.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d import filter2d
```

```text
filter2d(x, f, padding=0, flip_filter=False, gain=1, impl='cuda')
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `f` | `未标注` | `必填` |
| `padding` | `未标注` | `0` |
| `flip_filter` | `未标注` | `False` |
| `gain` | `未标注` | `1` |
| `impl` | `未标注` | `'cuda'` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d import filter2d

print(signature(filter2d))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/local_torch_utils/ops/upfirdn2d.py:278`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-local-torch-utils-ops-upfirdn2d-setup-filter"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d.setup_filter`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`setup_filter(f, device=torch.device('cpu'), normalize=True, flip_filter=False, gain=1, separable=None)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d.setup_filter`

### 用途

Convenience function to setup 2D FIR filter for `upfirdn2d()`.

Args:
    f:           Torch tensor, numpy array, or python list of the shape
                 `[filter_height, filter_width]` (non-separable),
                 `[filter_taps]` (separable),
                 `[]` (impulse), or
                 `None` (identity).
    device:      Result device (default: cpu).
    normalize:   Normalize the filter so that it retains the magnitude
                 for constant input signal (DC)? (default: True).
    flip_filter: Flip the filter? (default: False).
    gain:        Overall scaling factor for signal magnitude (default: 1).
    separable:   Return a separable filter? (default: select automatically).

Returns:
    Float32 tensor of the shape
    `[filter_height, filter_width]` (non-separable) or
    `[filter_taps]` (separable).

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d import setup_filter
```

```text
setup_filter(f, device=torch.device('cpu'), normalize=True, flip_filter=False, gain=1, separable=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `f` | `未标注` | `必填` |
| `device` | `未标注` | `torch.device('cpu')` |
| `normalize` | `未标注` | `True` |
| `flip_filter` | `未标注` | `False` |
| `gain` | `未标注` | `1` |
| `separable` | `未标注` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d import setup_filter

print(signature(setup_filter))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/local_torch_utils/ops/upfirdn2d.py:71`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-local-torch-utils-ops-upfirdn2d-upfirdn2d"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d.upfirdn2d`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`upfirdn2d(x, f, up=1, down=1, padding=0, flip_filter=False, gain=1, impl='cuda')`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d.upfirdn2d`

### 用途

Pad, upsample, filter, and downsample a batch of 2D images.

Performs the following sequence of operations for each channel:

1. Upsample the image by inserting N-1 zeros after each pixel (`up`).

2. Pad the image with the specified number of zeros on each side (`padding`).
   Negative padding corresponds to cropping the image.

3. Convolve the image with the specified 2D FIR filter (`f`), shrinking it
   so that the footprint of all output pixels lies within the input image.

4. Downsample the image by keeping every Nth pixel (`down`).

This sequence of operations bears close resemblance to scipy.signal.upfirdn().
The fused op is considerably more efficient than performing the same calculation
using standard PyTorch ops. It supports gradients of arbitrary order.

Args:
    x:           Float32/float64/float16 input tensor of the shape
                 `[batch_size, num_channels, in_height, in_width]`.
    f:           Float32 FIR filter of the shape
                 `[filter_height, filter_width]` (non-separable),
                 `[filter_taps]` (separable), or
                 `None` (identity).
    up:          Integer upsampling factor. Can be a single int or a list/tuple
                 `[x, y]` (default: 1).
    down:        Integer downsampling factor. Can be a single int or a list/tuple
                 `[x, y]` (default: 1).
    padding:     Padding with respect to the upsampled image. Can be a single number
                 or a list/tuple `[x, y]` or `[x_before, x_after, y_before, y_after]`
                 (default: 0).
    flip_filter: False = convolution, True = correlation (default: False).
    gain:        Overall scaling factor for signal magnitude (default: 1).
    impl:        Implementation to use. Can be `'ref'` or `'cuda'` (default: `'cuda'`).

Returns:
    Tensor of the shape `[batch_size, num_channels, out_height, out_width]`.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d import upfirdn2d
```

```text
upfirdn2d(x, f, up=1, down=1, padding=0, flip_filter=False, gain=1, impl='cuda')
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `f` | `未标注` | `必填` |
| `up` | `未标注` | `1` |
| `down` | `未标注` | `1` |
| `padding` | `未标注` | `0` |
| `flip_filter` | `未标注` | `False` |
| `gain` | `未标注` | `1` |
| `impl` | `未标注` | `'cuda'` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d import upfirdn2d

print(signature(upfirdn2d))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/local_torch_utils/ops/upfirdn2d.py:119`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-local-torch-utils-ops-upfirdn2d-upsample2d"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d.upsample2d`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`upsample2d(x, f, up=2, padding=0, flip_filter=False, gain=1, impl='cuda')`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d.upsample2d`

### 用途

Upsample a batch of 2D images using the given 2D FIR filter.

By default, the result is padded so that its shape is a multiple of the input.
User-specified padding is applied on top of that, with negative values
indicating cropping. Pixels outside the image are assumed to be zero.

Args:
    x:           Float32/float64/float16 input tensor of the shape
                 `[batch_size, num_channels, in_height, in_width]`.
    f:           Float32 FIR filter of the shape
                 `[filter_height, filter_width]` (non-separable),
                 `[filter_taps]` (separable), or
                 `None` (identity).
    up:          Integer upsampling factor. Can be a single int or a list/tuple
                 `[x, y]` (default: 1).
    padding:     Padding with respect to the output. Can be a single number or a
                 list/tuple `[x, y]` or `[x_before, x_after, y_before, y_after]`
                 (default: 0).
    flip_filter: False = convolution, True = correlation (default: False).
    gain:        Overall scaling factor for signal magnitude (default: 1).
    impl:        Implementation to use. Can be `'ref'` or `'cuda'` (default: `'cuda'`).

Returns:
    Tensor of the shape `[batch_size, num_channels, out_height, out_width]`.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d import upsample2d
```

```text
upsample2d(x, f, up=2, padding=0, flip_filter=False, gain=1, impl='cuda')
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `f` | `未标注` | `必填` |
| `up` | `未标注` | `2` |
| `padding` | `未标注` | `0` |
| `flip_filter` | `未标注` | `False` |
| `gain` | `未标注` | `1` |
| `impl` | `未标注` | `'cuda'` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d import upsample2d

print(signature(upsample2d))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/local_torch_utils/ops/upfirdn2d.py:314`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.upfirdn2d')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
