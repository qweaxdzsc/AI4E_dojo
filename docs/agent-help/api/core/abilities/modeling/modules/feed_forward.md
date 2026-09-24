<!-- dojo-help: {"domain": "ai4e_core.abilities.modeling.modules.feed_forward", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.modeling.modules.feed_forward 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.modeling.modules.feed_forward", "topic_id": "module:ai4e_core.abilities.modeling.modules.feed_forward"} -->
# `ai4e_core.abilities.modeling.modules.feed_forward` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-modeling-modules-feed-forward-feedforward"></a>
## `ai4e_core.abilities.modeling.modules.feed_forward.FeedForward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`FeedForward(in_features: int, out_features: int, hidden_features: tuple[int, ...]=(64,), activation: str='gelu', final_activation: str | None=None, dropout: float=0.0)`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.feed_forward.FeedForward`

### 用途

共享多层前馈块，保持输入的所有前导维度。

参数 ``hidden_features`` 是各隐藏宽度；``activation`` 使用投影模块的显式
激活名称。每个隐藏层执行线性、激活、dropout，末层仅线性及可选
``final_activation``，不对末层附加 dropout。默认有偏置，无归一化或残差。
旧 Mlp 的结构和权重键不受此类影响。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.feed_forward import FeedForward
```

```text
FeedForward(in_features: int, out_features: int, hidden_features: tuple[int, ...]=(64,), activation: str='gelu', final_activation: str | None=None, dropout: float=0.0)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `in_features` | `int` | `必填` |
| `out_features` | `int` | `必填` |
| `hidden_features` | `tuple[int, ...]` | `(64,)` |
| `activation` | `str` | `'gelu'` |
| `final_activation` | `str | None` | `None` |
| `dropout` | `float` | `0.0` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`FeedForward`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`TypeError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.feed_forward import FeedForward

print(signature(FeedForward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.feed_forward`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/feed_forward.py:34`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.feed_forward')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-feed-forward-feedforward-forward"></a>
## `ai4e_core.abilities.modeling.modules.feed_forward.FeedForward.forward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x: torch.Tensor) -> torch.Tensor`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.feed_forward.FeedForward.forward`

### 用途

将 ``[..., in_features]`` 映射到 ``[..., out_features]``。

不展平样本、节点或网格轴；末轴不匹配时抛出 ValueError。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.feed_forward import FeedForward
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
from ai4e_core.abilities.modeling.modules.feed_forward import FeedForward

print(signature(FeedForward.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.feed_forward`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/feed_forward.py:76`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.feed_forward')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-feed-forward-mlp"></a>
## `ai4e_core.abilities.modeling.modules.feed_forward.Mlp`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`Mlp(dim: int)`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.feed_forward.Mlp`

### 用途

MLP as used in transformers nn.Linear(dim, dim * 4) -> GELU -> nn.Linear(dim * 4, dim).

Args:
    dim: Input dimension of the MLP.

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.feed_forward import Mlp
```

```text
Mlp(dim: int)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dim` | `int` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Mlp`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.feed_forward import Mlp

print(signature(Mlp))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.feed_forward`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/feed_forward.py:14`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.feed_forward')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-feed-forward-mlp-forward"></a>
## `ai4e_core.abilities.modeling.modules.feed_forward.Mlp.forward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x: torch.Tensor) -> torch.Tensor`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.feed_forward.Mlp.forward`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.feed_forward import Mlp
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

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.feed_forward import Mlp

print(signature(Mlp.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.feed_forward`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/feed_forward.py:27`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.feed_forward')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
