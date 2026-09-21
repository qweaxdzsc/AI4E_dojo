<!-- dojo-help: {"domain": "ai4e_core.abilities.modeling.modules.flare_attention", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.modeling.modules.flare_attention 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.modeling.modules.flare_attention", "topic_id": "module:ai4e_core.abilities.modeling.modules.flare_attention"} -->
# `ai4e_core.abilities.modeling.modules.flare_attention` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-modeling-modules-flare-attention-flareplusplus"></a>
## `ai4e_core.abilities.modeling.modules.flare_attention.FLAREPlusPlus`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`FLAREPlusPlus(dim: int, heads: int=8, dim_head: int=64, dropout: float=0.0, n_global_queries: int=64, use_te: bool=False, attn_scale: float | None=None)`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.flare_attention.FLAREPlusPlus`

### 用途

根据当前输入合成路由的注意力层，可由用户放入自己的网络。

参数:
    dim: 输入和输出的特征数，正整数。
    heads: 注意力头数，正整数。
    dim_head: 每头内部特征数，正整数；无需 heads * dim_head 等于 dim。
    dropout: 输出投影之后的丢弃概率，范围 [0, 1]；eval 时关闭。
    n_global_queries: 学习 seed 和动态路由的数量，正整数。
    use_te: 只接受 False；本组件不依赖 Transformer Engine。
    attn_scale: 三次注意力共同使用的正有限缩放；None 为 dim_head**-0.5。

输入/输出为浮点张量 (batch, tokens, dim)。同批样本长度相同，tokens
必须非零；跨调用可改变长度。不提供 padding mask、因果注意力、几何
上下文或 token 分片。需要这些语义时应另写明确的局部连接，不能把补零
当作被屏蔽的 token。普通 state_dict 可保存和恢复学习参数。

非法构造参数或张量形状抛 ValueError，非浮点输入抛 TypeError；TE 与
token 分片不支持。此层不包含残差、归一化或 MLP，不自动替换已有模型。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.flare_attention import FLAREPlusPlus
```

```text
FLAREPlusPlus(dim: int, heads: int=8, dim_head: int=64, dropout: float=0.0, n_global_queries: int=64, use_te: bool=False, attn_scale: float | None=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dim` | `int` | `必填` |
| `heads` | `int` | `8` |
| `dim_head` | `int` | `64` |
| `dropout` | `float` | `0.0` |
| `n_global_queries` | `int` | `64` |
| `use_te` | `bool` | `False` |
| `attn_scale` | `float | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`FLAREPlusPlus`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`NotImplementedError`, `TypeError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.flare_attention import FLAREPlusPlus

print(signature(FLAREPlusPlus))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.flare_attention`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/flare_attention.py:18`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.flare_attention')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-flare-attention-flareplusplus-forward"></a>
## `ai4e_core.abilities.modeling.modules.flare_attention.FLAREPlusPlus.forward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x: torch.Tensor) -> torch.Tensor`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.flare_attention.FLAREPlusPlus.forward`

### 用途

将 (B, N, dim) 特征映射为同形特征，保留 autograd 与调用设备。

学习 seed 先汇聚当前输入以生成路由，再汇聚物理特征并回传到输入
token；仅输出投影后使用 dropout。非法形状、空 token 和整数输入
在计算前拒绝；DTensor/token 分片会因缺少全局归一化而明确拒绝。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.flare_attention import FLAREPlusPlus
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

`NotImplementedError`, `TypeError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.flare_attention import FLAREPlusPlus

print(signature(FLAREPlusPlus.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.flare_attention`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/flare_attention.py:77`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.flare_attention')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
