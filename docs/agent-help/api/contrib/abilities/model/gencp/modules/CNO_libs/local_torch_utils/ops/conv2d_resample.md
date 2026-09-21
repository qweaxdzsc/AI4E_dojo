<!-- dojo-help: {"domain": "ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.conv2d_resample", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.conv2d_resample 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.conv2d_resample", "topic_id": "module:ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.conv2d_resample"} -->
# `ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.conv2d_resample` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-local-torch-utils-ops-conv2d-resample-conv2d-resample"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.conv2d_resample.conv2d_resample`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`conv2d_resample(x, w, f=None, up=1, down=1, padding=0, groups=1, flip_weight=True, flip_filter=False)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.conv2d_resample.conv2d_resample`

### 用途

2D convolution with optional up/downsampling.

Padding is performed only once at the beginning, not between the operations.

Args:
    x:              Input tensor of shape
                    `[batch_size, in_channels, in_height, in_width]`.
    w:              Weight tensor of shape
                    `[out_channels, in_channels//groups, kernel_height, kernel_width]`.
    f:              Low-pass filter for up/downsampling. Must be prepared beforehand by
                    calling upfirdn2d.setup_filter(). None = identity (default).
    up:             Integer upsampling factor (default: 1).
    down:           Integer downsampling factor (default: 1).
    padding:        Padding with respect to the upsampled image. Can be a single number
                    or a list/tuple `[x, y]` or `[x_before, x_after, y_before, y_after]`
                    (default: 0).
    groups:         Split input channels into N groups (default: 1).
    flip_weight:    False = convolution, True = correlation (default: True).
    flip_filter:    False = convolution, True = correlation (default: False).

Returns:
    Tensor of the shape `[batch_size, num_channels, out_height, out_width]`.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.conv2d_resample import conv2d_resample
```

```text
conv2d_resample(x, w, f=None, up=1, down=1, padding=0, groups=1, flip_weight=True, flip_filter=False)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `w` | `未标注` | `必填` |
| `f` | `未标注` | `None` |
| `up` | `未标注` | `1` |
| `down` | `未标注` | `1` |
| `padding` | `未标注` | `0` |
| `groups` | `未标注` | `1` |
| `flip_weight` | `未标注` | `True` |
| `flip_filter` | `未标注` | `False` |

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
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.conv2d_resample import conv2d_resample

print(signature(conv2d_resample))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.conv2d_resample`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/local_torch_utils/ops/conv2d_resample.py:47`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.conv2d_resample')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
