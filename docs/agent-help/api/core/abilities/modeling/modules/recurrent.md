<!-- dojo-help: {"domain": "ai4e_core.abilities.modeling.modules.recurrent", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.modeling.modules.recurrent 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.modeling.modules.recurrent", "topic_id": "module:ai4e_core.abilities.modeling.modules.recurrent"} -->
# `ai4e_core.abilities.modeling.modules.recurrent` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-modeling-modules-recurrent-recurrentblock"></a>
## `ai4e_core.abilities.modeling.modules.recurrent.RecurrentBlock`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`RecurrentBlock(in_features: int, hidden_size: int, nonlinearity: str='tanh')`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.recurrent.RecurrentBlock`

### 用途

单向 Elman 循环块，支持 tanh 或 relu，零缺省初始状态。

直接使用原生单层 RNN 的双偏置和数值语义，不复制循环单元公式。
``in_features`` 为输入末轴宽度，``hidden_size`` 为循环特征宽度。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.recurrent import RecurrentBlock
```

```text
RecurrentBlock(in_features: int, hidden_size: int, nonlinearity: str='tanh')
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `in_features` | `int` | `必填` |
| `hidden_size` | `int` | `必填` |
| `nonlinearity` | `str` | `'tanh'` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`RecurrentBlock`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.recurrent import RecurrentBlock

print(signature(RecurrentBlock))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.recurrent`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/recurrent.py:7`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.recurrent')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-recurrent-recurrentblock-forward"></a>
## `ai4e_core.abilities.modeling.modules.recurrent.RecurrentBlock.forward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x: torch.Tensor, state: torch.Tensor | None=None) -> tuple[torch.Tensor, torch.Tensor]`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.recurrent.RecurrentBlock.forward`

### 用途

输入 ``[B,T,C]`` 及可选 ``[1,B,H]``，返回序列与末状态。

空时间轴、错误形状、状态设备或精度不一致均抛出 ValueError。
不自动搬移状态、不分离其梯度；截断反向传播由调用方显式决定。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.recurrent import RecurrentBlock
```

```text
forward(self, x: torch.Tensor, state: torch.Tensor | None=None) -> tuple[torch.Tensor, torch.Tensor]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `torch.Tensor` | `必填` |
| `state` | `torch.Tensor | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`tuple[torch.Tensor, torch.Tensor]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.recurrent import RecurrentBlock

print(signature(RecurrentBlock.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.recurrent`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/recurrent.py:26`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.recurrent')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
