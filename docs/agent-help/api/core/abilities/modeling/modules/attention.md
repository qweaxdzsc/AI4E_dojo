<!-- dojo-help: {"domain": "ai4e_core.abilities.modeling.modules.attention", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.modeling.modules.attention 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.modeling.modules.attention", "topic_id": "module:ai4e_core.abilities.modeling.modules.attention"} -->
# `ai4e_core.abilities.modeling.modules.attention` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-modeling-modules-attention-crossattention"></a>
## `ai4e_core.abilities.modeling.modules.attention.CrossAttention`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`CrossAttention(dim: int, num_heads: int, *, context_dim: int | None=None, dropout: float=0.0)`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.attention.CrossAttention`

### 用途

标准交叉注意力；查询宽度为 dim，上下文宽度可单独配置。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.attention import CrossAttention
```

```text
CrossAttention(dim: int, num_heads: int, *, context_dim: int | None=None, dropout: float=0.0)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dim` | `int` | `必填` |
| `num_heads` | `int` | `必填` |
| `context_dim` | `int | None` | `None` |
| `dropout` | `float` | `0.0` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`CrossAttention`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.attention import CrossAttention

print(signature(CrossAttention))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.attention`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/attention.py:40`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.attention')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-attention-crossattention-forward"></a>
## `ai4e_core.abilities.modeling.modules.attention.CrossAttention.forward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, query: torch.Tensor, context: torch.Tensor, *, key_padding_mask: torch.Tensor | None=None, attn_mask: torch.Tensor | None=None) -> torch.Tensor`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.attention.CrossAttention.forward`

### 用途

返回 [B,Q,D]；布尔掩码真表示忽略，浮点掩码按加性偏置解释。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.attention import CrossAttention
```

```text
forward(self, query: torch.Tensor, context: torch.Tensor, *, key_padding_mask: torch.Tensor | None=None, attn_mask: torch.Tensor | None=None) -> torch.Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `query` | `torch.Tensor` | `必填` |
| `context` | `torch.Tensor` | `必填` |
| `key_padding_mask` | `torch.Tensor | None` | `None` |
| `attn_mask` | `torch.Tensor | None` | `None` |

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
from ai4e_core.abilities.modeling.modules.attention import CrossAttention

print(signature(CrossAttention.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.attention`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/attention.py:58`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.attention')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-attention-selfattention"></a>
## `ai4e_core.abilities.modeling.modules.attention.SelfAttention`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`SelfAttention(dim: int, num_heads: int, *, dropout: float=0.0)`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.attention.SelfAttention`

### 用途

标准非因果自注意力；因果或其他屏蔽只能通过显式掩码传入。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.attention import SelfAttention
```

```text
SelfAttention(dim: int, num_heads: int, *, dropout: float=0.0)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dim` | `int` | `必填` |
| `num_heads` | `int` | `必填` |
| `dropout` | `float` | `0.0` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`SelfAttention`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.attention import SelfAttention

print(signature(SelfAttention))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.attention`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/attention.py:84`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.attention')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-attention-selfattention-forward"></a>
## `ai4e_core.abilities.modeling.modules.attention.SelfAttention.forward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, value: torch.Tensor, *, key_padding_mask: torch.Tensor | None=None, attn_mask: torch.Tensor | None=None) -> torch.Tensor`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.attention.SelfAttention.forward`

### 用途

查询、键和值共用输入，返回与输入相同的序列布局。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.attention import SelfAttention
```

```text
forward(self, value: torch.Tensor, *, key_padding_mask: torch.Tensor | None=None, attn_mask: torch.Tensor | None=None) -> torch.Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `value` | `torch.Tensor` | `必填` |
| `key_padding_mask` | `torch.Tensor | None` | `None` |
| `attn_mask` | `torch.Tensor | None` | `None` |

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
from ai4e_core.abilities.modeling.modules.attention import SelfAttention

print(signature(SelfAttention.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.attention`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/attention.py:90`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.attention')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
