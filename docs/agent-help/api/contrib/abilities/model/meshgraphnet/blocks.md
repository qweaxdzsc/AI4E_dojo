<!-- dojo-help: {"domain": "ai4e_contrib.ability.model.meshgraphnet.blocks", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.model.meshgraphnet.blocks 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.model.meshgraphnet.blocks", "topic_id": "module:ai4e_contrib.ability.model.meshgraphnet.blocks"} -->
# `ai4e_contrib.ability.model.meshgraphnet.blocks` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-model-meshgraphnet-blocks-graphdecoder"></a>
## `ai4e_contrib.ability.model.meshgraphnet.blocks.GraphDecoder`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`GraphDecoder(hidden_dim: int, output_dim: int)`
- **规范定义名**：`ai4e_contrib.ability.model.meshgraphnet.blocks.GraphDecoder`

### 用途

从最终节点隐状态读出物理状态增量。

### 导入与签名

```python
from ai4e_contrib.ability.model.meshgraphnet.blocks import GraphDecoder
```

```text
GraphDecoder(hidden_dim: int, output_dim: int)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `hidden_dim` | `int` | `必填` |
| `output_dim` | `int` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`GraphDecoder`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.meshgraphnet.blocks import GraphDecoder

print(signature(GraphDecoder))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.meshgraphnet.blocks`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/meshgraphnet/blocks.py:49`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.meshgraphnet.blocks')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-meshgraphnet-blocks-graphdecoder-forward"></a>
## `ai4e_contrib.ability.model.meshgraphnet.blocks.GraphDecoder.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, nodes: torch.Tensor) -> torch.Tensor`
- **规范定义名**：`ai4e_contrib.ability.model.meshgraphnet.blocks.GraphDecoder.forward`

### 用途

把节点隐状态解码为节点输出。

### 导入与签名

```python
from ai4e_contrib.ability.model.meshgraphnet.blocks import GraphDecoder
```

```text
forward(self, nodes: torch.Tensor) -> torch.Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `nodes` | `torch.Tensor` | `必填` |

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
from ai4e_contrib.ability.model.meshgraphnet.blocks import GraphDecoder

print(signature(GraphDecoder.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_contrib.ability.model.meshgraphnet.blocks`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/meshgraphnet/blocks.py:56`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.meshgraphnet.blocks')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-meshgraphnet-blocks-graphencoder"></a>
## `ai4e_contrib.ability.model.meshgraphnet.blocks.GraphEncoder`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`GraphEncoder(node_input_dim: int, edge_input_dim: int, hidden_dim: int)`
- **规范定义名**：`ai4e_contrib.ability.model.meshgraphnet.blocks.GraphEncoder`

### 用途

把原始节点和边特征分别编码到公共隐空间。

### 导入与签名

```python
from ai4e_contrib.ability.model.meshgraphnet.blocks import GraphEncoder
```

```text
GraphEncoder(node_input_dim: int, edge_input_dim: int, hidden_dim: int)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `node_input_dim` | `int` | `必填` |
| `edge_input_dim` | `int` | `必填` |
| `hidden_dim` | `int` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`GraphEncoder`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.meshgraphnet.blocks import GraphEncoder

print(signature(GraphEncoder))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.meshgraphnet.blocks`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/meshgraphnet/blocks.py:11`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.meshgraphnet.blocks')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-meshgraphnet-blocks-graphencoder-forward"></a>
## `ai4e_contrib.ability.model.meshgraphnet.blocks.GraphEncoder.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, nodes: torch.Tensor, edges: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]`
- **规范定义名**：`ai4e_contrib.ability.model.meshgraphnet.blocks.GraphEncoder.forward`

### 用途

返回编码后的节点与边。

### 导入与签名

```python
from ai4e_contrib.ability.model.meshgraphnet.blocks import GraphEncoder
```

```text
forward(self, nodes: torch.Tensor, edges: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `nodes` | `torch.Tensor` | `必填` |
| `edges` | `torch.Tensor` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`tuple[torch.Tensor, torch.Tensor]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.meshgraphnet.blocks import GraphEncoder

print(signature(GraphEncoder.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_contrib.ability.model.meshgraphnet.blocks`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/meshgraphnet/blocks.py:19`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.meshgraphnet.blocks')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-meshgraphnet-blocks-graphprocessor"></a>
## `ai4e_contrib.ability.model.meshgraphnet.blocks.GraphProcessor`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`GraphProcessor(hidden_dim: int, layers: int)`
- **规范定义名**：`ai4e_contrib.ability.model.meshgraphnet.blocks.GraphProcessor`

### 用途

顺序应用固定数量的残差消息传递块。

### 导入与签名

```python
from ai4e_contrib.ability.model.meshgraphnet.blocks import GraphProcessor
```

```text
GraphProcessor(hidden_dim: int, layers: int)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `hidden_dim` | `int` | `必填` |
| `layers` | `int` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`GraphProcessor`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.meshgraphnet.blocks import GraphProcessor

print(signature(GraphProcessor))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.meshgraphnet.blocks`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/meshgraphnet/blocks.py:26`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.meshgraphnet.blocks')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-meshgraphnet-blocks-graphprocessor-forward"></a>
## `ai4e_contrib.ability.model.meshgraphnet.blocks.GraphProcessor.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, nodes: torch.Tensor, edges: torch.Tensor, edge_index: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]`
- **规范定义名**：`ai4e_contrib.ability.model.meshgraphnet.blocks.GraphProcessor.forward`

### 用途

执行全部消息传递层并返回最终图状态。

### 导入与签名

```python
from ai4e_contrib.ability.model.meshgraphnet.blocks import GraphProcessor
```

```text
forward(self, nodes: torch.Tensor, edges: torch.Tensor, edge_index: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `nodes` | `torch.Tensor` | `必填` |
| `edges` | `torch.Tensor` | `必填` |
| `edge_index` | `torch.Tensor` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`tuple[torch.Tensor, torch.Tensor]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.meshgraphnet.blocks import GraphProcessor

print(signature(GraphProcessor.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_contrib.ability.model.meshgraphnet.blocks`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/meshgraphnet/blocks.py:40`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.meshgraphnet.blocks')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
