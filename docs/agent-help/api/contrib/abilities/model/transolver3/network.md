<!-- dojo-help: {"domain": "ai4e_contrib.ability.model.transolver3.network", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.model.transolver3.network 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.model.transolver3.network", "topic_id": "module:ai4e_contrib.ability.model.transolver3.network"} -->
# `ai4e_contrib.ability.model.transolver3.network` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-model-transolver3-network-mlp"></a>
## `ai4e_contrib.ability.model.transolver3.network.MLP`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`MLP(n_input, n_hidden, n_output, n_layers=1, act='gelu', res=True)`
- **规范定义名**：`ai4e_contrib.ability.model.transolver3.network.MLP`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.transolver3.network import MLP
```

```text
MLP(n_input, n_hidden, n_output, n_layers=1, act='gelu', res=True)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `n_input` | `未标注` | `必填` |
| `n_hidden` | `未标注` | `必填` |
| `n_output` | `未标注` | `必填` |
| `n_layers` | `未标注` | `1` |
| `act` | `未标注` | `'gelu'` |
| `res` | `未标注` | `True` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`MLP`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`NotImplementedError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.transolver3.network import MLP

print(signature(MLP))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.operator_branch_replacement`, `recipe_extensions.pod_surrogate_replacement`

### 源码位置

- 模块：`ai4e_contrib.ability.model.transolver3.network`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/transolver3/network.py:168`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.transolver3.network')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-transolver3-network-mlp-forward"></a>
## `ai4e_contrib.ability.model.transolver3.network.MLP.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x)`
- **规范定义名**：`ai4e_contrib.ability.model.transolver3.network.MLP.forward`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.transolver3.network import MLP
```

```text
forward(self, x)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.transolver3.network import MLP

print(signature(MLP.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_contrib.ability.model.transolver3.network`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/transolver3/network.py:183`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.transolver3.network')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-transolver3-network-model"></a>
## `ai4e_contrib.ability.model.transolver3.network.Model`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`Model(space_dim=1, n_layers=5, n_hidden=256, dropout=0, n_head=8, act='gelu', mlp_ratio=1, fun_dim=1, out_dim=1, slice_num=32, ref=8, unified_pos=False)`
- **规范定义名**：`ai4e_contrib.ability.model.transolver3.network.Model`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.transolver3.network import Model
```

```text
Model(space_dim=1, n_layers=5, n_hidden=256, dropout=0, n_head=8, act='gelu', mlp_ratio=1, fun_dim=1, out_dim=1, slice_num=32, ref=8, unified_pos=False)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `space_dim` | `未标注` | `1` |
| `n_layers` | `未标注` | `5` |
| `n_hidden` | `未标注` | `256` |
| `dropout` | `未标注` | `0` |
| `n_head` | `未标注` | `8` |
| `act` | `未标注` | `'gelu'` |
| `mlp_ratio` | `未标注` | `1` |
| `fun_dim` | `未标注` | `1` |
| `out_dim` | `未标注` | `1` |
| `slice_num` | `未标注` | `32` |
| `ref` | `未标注` | `8` |
| `unified_pos` | `未标注` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Model`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.transolver3.network import Model

print(signature(Model))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.transolver3.network`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/transolver3/network.py:280`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.transolver3.network')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-transolver3-network-model-forward"></a>
## `ai4e_contrib.ability.model.transolver3.network.Model.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, data, use_checkpoint=True, input_list=True)`
- **规范定义名**：`ai4e_contrib.ability.model.transolver3.network.Model.forward`

### 用途

data: list of feature tensors when input_list=True, or a single feature tensor otherwise.
Returns a list of per-chunk outputs when input_list=True.

### 导入与签名

```python
from ai4e_contrib.ability.model.transolver3.network import Model
```

```text
forward(self, data, use_checkpoint=True, input_list=True)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `data` | `未标注` | `必填` |
| `use_checkpoint` | `未标注` | `True` |
| `input_list` | `未标注` | `True` |

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
from ai4e_contrib.ability.model.transolver3.network import Model

print(signature(Model.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_contrib.ability.model.transolver3.network`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/transolver3/network.py:341`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.transolver3.network')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-transolver3-network-model-initialize-weights"></a>
## `ai4e_contrib.ability.model.transolver3.network.Model.initialize_weights`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`initialize_weights(self)`
- **规范定义名**：`ai4e_contrib.ability.model.transolver3.network.Model.initialize_weights`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.transolver3.network import Model
```

```text
initialize_weights(self)
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

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
from ai4e_contrib.ability.model.transolver3.network import Model

print(signature(Model.initialize_weights))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.transolver3.network`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/transolver3/network.py:329`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.transolver3.network')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-transolver3-network-physics-attention-irregular-mesh"></a>
## `ai4e_contrib.ability.model.transolver3.network.Physics_Attention_Irregular_Mesh`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`Physics_Attention_Irregular_Mesh(dim, heads=8, dim_head=64, dropout=0.0, slice_num=64)`
- **规范定义名**：`ai4e_contrib.ability.model.transolver3.network.Physics_Attention_Irregular_Mesh`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.transolver3.network import Physics_Attention_Irregular_Mesh
```

```text
Physics_Attention_Irregular_Mesh(dim, heads=8, dim_head=64, dropout=0.0, slice_num=64)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dim` | `未标注` | `必填` |
| `heads` | `未标注` | `8` |
| `dim_head` | `未标注` | `64` |
| `dropout` | `未标注` | `0.0` |
| `slice_num` | `未标注` | `64` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Physics_Attention_Irregular_Mesh`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.transolver3.network import Physics_Attention_Irregular_Mesh

print(signature(Physics_Attention_Irregular_Mesh))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.transolver3.network`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/transolver3/network.py:26`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.transolver3.network')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-transolver3-network-physics-attention-irregular-mesh-chunk-deslice-to-out"></a>
## `ai4e_contrib.ability.model.transolver3.network.Physics_Attention_Irregular_Mesh.chunk_deslice_to_out`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`chunk_deslice_to_out(self, x: torch.Tensor, out_slice_token: torch.Tensor, slice_weights=None)`
- **规范定义名**：`ai4e_contrib.ability.model.transolver3.network.Physics_Attention_Irregular_Mesh.chunk_deslice_to_out`

### 用途

Deslice back to point space using associativity of linear operators:
instead of deslice then project (O(N*HD*C)),
project in slice domain first then deslice (O(G*HD*C) + O(N*G*C)).

### 导入与签名

```python
from ai4e_contrib.ability.model.transolver3.network import Physics_Attention_Irregular_Mesh
```

```text
chunk_deslice_to_out(self, x: torch.Tensor, out_slice_token: torch.Tensor, slice_weights=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `torch.Tensor` | `必填` |
| `out_slice_token` | `torch.Tensor` | `必填` |
| `slice_weights` | `未标注` | `None` |

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
from ai4e_contrib.ability.model.transolver3.network import Physics_Attention_Irregular_Mesh

print(signature(Physics_Attention_Irregular_Mesh.chunk_deslice_to_out))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.transolver3.network`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/transolver3/network.py:139`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.transolver3.network')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-transolver3-network-physics-attention-irregular-mesh-chunk-stats"></a>
## `ai4e_contrib.ability.model.transolver3.network.Physics_Attention_Irregular_Mesh.chunk_stats`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`chunk_stats(self, x: torch.Tensor)`
- **规范定义名**：`ai4e_contrib.ability.model.transolver3.network.Physics_Attention_Irregular_Mesh.chunk_stats`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.transolver3.network import Physics_Attention_Irregular_Mesh
```

```text
chunk_stats(self, x: torch.Tensor)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `torch.Tensor` | `必填` |

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
from ai4e_contrib.ability.model.transolver3.network import Physics_Attention_Irregular_Mesh

print(signature(Physics_Attention_Irregular_Mesh.chunk_stats))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.transolver3.network`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/transolver3/network.py:73`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.transolver3.network')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-transolver3-network-physics-attention-irregular-mesh-chunk-weights"></a>
## `ai4e_contrib.ability.model.transolver3.network.Physics_Attention_Irregular_Mesh.chunk_weights`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`chunk_weights(self, x: torch.Tensor, fused_w=None, fused_b=None)`
- **规范定义名**：`ai4e_contrib.ability.model.transolver3.network.Physics_Attention_Irregular_Mesh.chunk_weights`

### 用途

Compute per-point slice assignment weights via a single C -> G matmul.

### 导入与签名

```python
from ai4e_contrib.ability.model.transolver3.network import Physics_Attention_Irregular_Mesh
```

```text
chunk_weights(self, x: torch.Tensor, fused_w=None, fused_b=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `torch.Tensor` | `必填` |
| `fused_w` | `未标注` | `None` |
| `fused_b` | `未标注` | `None` |

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
from ai4e_contrib.ability.model.transolver3.network import Physics_Attention_Irregular_Mesh

print(signature(Physics_Attention_Irregular_Mesh.chunk_weights))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.transolver3.network`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/transolver3/network.py:128`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.transolver3.network')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-transolver3-network-physics-attention-irregular-mesh-forward"></a>
## `ai4e_contrib.ability.model.transolver3.network.Physics_Attention_Irregular_Mesh.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x)`
- **规范定义名**：`ai4e_contrib.ability.model.transolver3.network.Physics_Attention_Irregular_Mesh.forward`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.transolver3.network import Physics_Attention_Irregular_Mesh
```

```text
forward(self, x)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.transolver3.network import Physics_Attention_Irregular_Mesh

print(signature(Physics_Attention_Irregular_Mesh.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_contrib.ability.model.transolver3.network`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/transolver3/network.py:48`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.transolver3.network')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-transolver3-network-physics-attention-irregular-mesh-slice-attend"></a>
## `ai4e_contrib.ability.model.transolver3.network.Physics_Attention_Irregular_Mesh.slice_attend`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`slice_attend(self, slice_token: torch.Tensor)`
- **规范定义名**：`ai4e_contrib.ability.model.transolver3.network.Physics_Attention_Irregular_Mesh.slice_attend`

### 用途

slice_token: (B,H,G,D) -> out_slice_token: (B,H,G,D)

### 导入与签名

```python
from ai4e_contrib.ability.model.transolver3.network import Physics_Attention_Irregular_Mesh
```

```text
slice_attend(self, slice_token: torch.Tensor)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `slice_token` | `torch.Tensor` | `必填` |

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
from ai4e_contrib.ability.model.transolver3.network import Physics_Attention_Irregular_Mesh

print(signature(Physics_Attention_Irregular_Mesh.slice_attend))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.transolver3.network`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/transolver3/network.py:100`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.transolver3.network')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-transolver3-network-transolver-block"></a>
## `ai4e_contrib.ability.model.transolver3.network.Transolver_block`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`Transolver_block(num_heads: int, hidden_dim: int, dropout: float, act='gelu', mlp_ratio=4, last_layer=False, out_dim=1, slice_num=32)`
- **规范定义名**：`ai4e_contrib.ability.model.transolver3.network.Transolver_block`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.transolver3.network import Transolver_block
```

```text
Transolver_block(num_heads: int, hidden_dim: int, dropout: float, act='gelu', mlp_ratio=4, last_layer=False, out_dim=1, slice_num=32)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `num_heads` | `int` | `必填` |
| `hidden_dim` | `int` | `必填` |
| `dropout` | `float` | `必填` |
| `act` | `未标注` | `'gelu'` |
| `mlp_ratio` | `未标注` | `4` |
| `last_layer` | `未标注` | `False` |
| `out_dim` | `未标注` | `1` |
| `slice_num` | `未标注` | `32` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Transolver_block`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.transolver3.network import Transolver_block

print(signature(Transolver_block))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.transolver3.network`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/transolver3/network.py:194`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.transolver3.network')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-transolver3-network-transolver-block-forward"></a>
## `ai4e_contrib.ability.model.transolver3.network.Transolver_block.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, fx)`
- **规范定义名**：`ai4e_contrib.ability.model.transolver3.network.Transolver_block.forward`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.transolver3.network import Transolver_block
```

```text
forward(self, fx)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `fx` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.transolver3.network import Transolver_block

print(signature(Transolver_block.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_contrib.ability.model.transolver3.network`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/transolver3/network.py:224`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.transolver3.network')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-transolver3-network-transolver-block-forward-chunks"></a>
## `ai4e_contrib.ability.model.transolver3.network.Transolver_block.forward_chunks`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward_chunks(self, fx_list, eps=1e-05, use_checkpoint=True)`
- **规范定义名**：`ai4e_contrib.ability.model.transolver3.network.Transolver_block.forward_chunks`

### 用途

fx_list: list of tensors [(B,n1,C), (B,n2,C), ...]
Returns list with same chunking, updated for the next layer.

### 导入与签名

```python
from ai4e_contrib.ability.model.transolver3.network import Transolver_block
```

```text
forward_chunks(self, fx_list, eps=1e-05, use_checkpoint=True)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `fx_list` | `未标注` | `必填` |
| `eps` | `未标注` | `1e-05` |
| `use_checkpoint` | `未标注` | `True` |

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
from ai4e_contrib.ability.model.transolver3.network import Transolver_block

print(signature(Transolver_block.forward_chunks))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.transolver3.network`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/transolver3/network.py:231`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.transolver3.network')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
