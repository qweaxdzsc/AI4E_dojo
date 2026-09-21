<!-- dojo-help: {"domain": "ai4e_contrib.ability.model.meshgraphnet.network", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.model.meshgraphnet.network 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.model.meshgraphnet.network", "topic_id": "module:ai4e_contrib.ability.model.meshgraphnet.network"} -->
# `ai4e_contrib.ability.model.meshgraphnet.network` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-model-meshgraphnet-network-meshgraphnet"></a>
## `ai4e_contrib.ability.model.meshgraphnet.network.MeshGraphNet`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`MeshGraphNet(node_input_dim: int=11, edge_input_dim: int=3, output_dim: int=2, hidden_dim: int=128, processor_layers: int=15)`
- **规范定义名**：`ai4e_contrib.ability.model.meshgraphnet.network.MeshGraphNet`

### 用途

编码节点/边、执行图处理并输出节点增量。

### 导入与签名

```python
from ai4e_contrib.ability.model.meshgraphnet.network import MeshGraphNet
```

```text
MeshGraphNet(node_input_dim: int=11, edge_input_dim: int=3, output_dim: int=2, hidden_dim: int=128, processor_layers: int=15)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `node_input_dim` | `int` | `11` |
| `edge_input_dim` | `int` | `3` |
| `output_dim` | `int` | `2` |
| `hidden_dim` | `int` | `128` |
| `processor_layers` | `int` | `15` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`MeshGraphNet`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.meshgraphnet.network import MeshGraphNet

print(signature(MeshGraphNet))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`
- 案例：`aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.shapenet_car_meshgraphnet`

### 源码位置

- 模块：`ai4e_contrib.ability.model.meshgraphnet.network`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/meshgraphnet/network.py:15`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.meshgraphnet.network')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-meshgraphnet-network-meshgraphnet-forward"></a>
## `ai4e_contrib.ability.model.meshgraphnet.network.MeshGraphNet.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, node_features: torch.Tensor, edge_features: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor`
- **规范定义名**：`ai4e_contrib.ability.model.meshgraphnet.network.MeshGraphNet.forward`

### 用途

编码图特征，经 Processor 更新后解码节点增量。

### 导入与签名

```python
from ai4e_contrib.ability.model.meshgraphnet.network import MeshGraphNet
```

```text
forward(self, node_features: torch.Tensor, edge_features: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `node_features` | `torch.Tensor` | `必填` |
| `edge_features` | `torch.Tensor` | `必填` |
| `edge_index` | `torch.Tensor` | `必填` |

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
from ai4e_contrib.ability.model.meshgraphnet.network import MeshGraphNet

print(signature(MeshGraphNet.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.meshgraphnet.network`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/meshgraphnet/network.py:33`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.meshgraphnet.network')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-meshgraphnet-network-predict"></a>
## `ai4e_contrib.ability.model.meshgraphnet.network.predict`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`predict(model: MeshGraphNet, graph: dict[str, torch.Tensor]) -> torch.Tensor`
- **规范定义名**：`ai4e_contrib.ability.model.meshgraphnet.network.predict`

### 用途

对已装配图执行无梯度节点预测。

### 导入与签名

```python
from ai4e_contrib.ability.model.meshgraphnet.network import predict
```

```text
predict(model: MeshGraphNet, graph: dict[str, torch.Tensor]) -> torch.Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model` | `MeshGraphNet` | `必填` |
| `graph` | `dict[str, torch.Tensor]` | `必填` |

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
from ai4e_contrib.ability.model.meshgraphnet.network import predict

print(signature(predict))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `pcno_cylinder`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.sampling`, `recipe_extensions.wdno`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.ability.model.meshgraphnet.network`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/meshgraphnet/network.py:42`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.meshgraphnet.network')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
