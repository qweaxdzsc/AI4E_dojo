<!-- dojo-help: {"domain": "ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.bias_act", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.bias_act 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.bias_act", "topic_id": "module:ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.bias_act"} -->
# `ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.bias_act` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-local-torch-utils-ops-bias-act-bias-act"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.bias_act.bias_act`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`bias_act(x, b=None, dim=1, act='linear', alpha=None, gain=None, clamp=None, impl='cuda')`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.bias_act.bias_act`

### 用途

Fused bias and activation function.

Adds bias `b` to activation tensor `x`, evaluates activation function `act`,
and scales the result by `gain`. Each of the steps is optional. In most cases,
the fused op is considerably more efficient than performing the same calculation
using standard PyTorch ops. It supports first and second order gradients,
but not third order gradients.

Args:
    x:      Input activation tensor. Can be of any shape.
    b:      Bias vector, or `None` to disable. Must be a 1D tensor of the same type
            as `x`. The shape must be known, and it must match the dimension of `x`
            corresponding to `dim`.
    dim:    The dimension in `x` corresponding to the elements of `b`.
            The value of `dim` is ignored if `b` is not specified.
    act:    Name of the activation function to evaluate, or `"linear"` to disable.
            Can be e.g. `"relu"`, `"lrelu"`, `"tanh"`, `"sigmoid"`, `"swish"`, etc.
            See `activation_funcs` for a full list. `None` is not allowed.
    alpha:  Shape parameter for the activation function, or `None` to use the default.
    gain:   Scaling factor for the output tensor, or `None` to use default.
            See `activation_funcs` for the default scaling of each activation function.
            If unsure, consider specifying 1.
    clamp:  Clamp the output values to `[-clamp, +clamp]`, or `None` to disable
            the clamping (default).
    impl:   Name of the implementation to use. Can be `"ref"` or `"cuda"` (default).

Returns:
    Tensor of the same shape and datatype as `x`.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.bias_act import bias_act
```

```text
bias_act(x, b=None, dim=1, act='linear', alpha=None, gain=None, clamp=None, impl='cuda')
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `b` | `未标注` | `None` |
| `dim` | `未标注` | `1` |
| `act` | `未标注` | `'linear'` |
| `alpha` | `未标注` | `None` |
| `gain` | `未标注` | `None` |
| `clamp` | `未标注` | `None` |
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
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.bias_act import bias_act

print(signature(bias_act))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.bias_act`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/local_torch_utils/ops/bias_act.py:53`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.ops.bias_act')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
