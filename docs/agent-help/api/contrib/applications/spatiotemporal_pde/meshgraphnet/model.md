<!-- dojo-help: {"domain": "ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model", "kind": "api", "layer": "contrib.application", "summary": "ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model", "topic_id": "module:ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model"} -->
# `ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-application-spatiotemporal-pde-meshgraphnet-model-cylinderflowmodel"></a>
## `ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model.CylinderFlowModel`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`CylinderFlowModel(network: MeshGraphNet)`
- **规范定义名**：`ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model.CylinderFlowModel`

### 用途

绑定 DeepMind CylinderFlow 输入/输出归一化的模型连接。

### 导入与签名

```python
from ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model import CylinderFlowModel
```

```text
CylinderFlowModel(network: MeshGraphNet)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `network` | `MeshGraphNet` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`CylinderFlowModel`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model import CylinderFlowModel

print(signature(CylinderFlowModel))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model`
- 仓库相对路径：`packages/ai4e-contrib/application/spatiotemporal_pde/meshgraphnet/model.py:13`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-spatiotemporal-pde-meshgraphnet-model-cylinderflowmodel-forward"></a>
## `ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model.CylinderFlowModel.forward`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`forward(self, node_features: torch.Tensor, edge_features: torch.Tensor, edge_index: torch.Tensor, *, accumulate: bool=False) -> torch.Tensor`
- **规范定义名**：`ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model.CylinderFlowModel.forward`

### 用途

归一化节点与边，再调用 MeshGraphNet 预测归一化增量。

### 导入与签名

```python
from ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model import CylinderFlowModel
```

```text
forward(self, node_features: torch.Tensor, edge_features: torch.Tensor, edge_index: torch.Tensor, *, accumulate: bool=False) -> torch.Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `node_features` | `torch.Tensor` | `必填` |
| `edge_features` | `torch.Tensor` | `必填` |
| `edge_index` | `torch.Tensor` | `必填` |
| `accumulate` | `bool` | `False` |

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
from ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model import CylinderFlowModel

print(signature(CylinderFlowModel.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model`
- 仓库相对路径：`packages/ai4e-contrib/application/spatiotemporal_pde/meshgraphnet/model.py:25`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-spatiotemporal-pde-meshgraphnet-model-cylinderflowmodel-inverse-output"></a>
## `ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model.CylinderFlowModel.inverse_output`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`inverse_output(self, value: torch.Tensor) -> torch.Tensor`
- **规范定义名**：`ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model.CylinderFlowModel.inverse_output`

### 用途

把模型输出还原为物理速度增量。

### 导入与签名

```python
from ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model import CylinderFlowModel
```

```text
inverse_output(self, value: torch.Tensor) -> torch.Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `value` | `torch.Tensor` | `必填` |

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
from ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model import CylinderFlowModel

print(signature(CylinderFlowModel.inverse_output))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model`
- 仓库相对路径：`packages/ai4e-contrib/application/spatiotemporal_pde/meshgraphnet/model.py:42`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-spatiotemporal-pde-meshgraphnet-model-cylinderflowmodel-normalize-target"></a>
## `ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model.CylinderFlowModel.normalize_target`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`normalize_target(self, target: torch.Tensor, *, accumulate: bool=False) -> torch.Tensor`
- **规范定义名**：`ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model.CylinderFlowModel.normalize_target`

### 用途

按输出统计归一化监督增量。

### 导入与签名

```python
from ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model import CylinderFlowModel
```

```text
normalize_target(self, target: torch.Tensor, *, accumulate: bool=False) -> torch.Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `target` | `torch.Tensor` | `必填` |
| `accumulate` | `bool` | `False` |

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
from ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model import CylinderFlowModel

print(signature(CylinderFlowModel.normalize_target))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model`
- 仓库相对路径：`packages/ai4e-contrib/application/spatiotemporal_pde/meshgraphnet/model.py:38`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-spatiotemporal-pde-meshgraphnet-model-build-graph"></a>
## `ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model.build_graph`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`build_graph(sample: dict) -> dict[str, torch.Tensor]`
- **规范定义名**：`ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model.build_graph`

### 用途

把 CylinderFlow 物理帧映射为中立图字段。

### 导入与签名

```python
from ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model import build_graph
```

```text
build_graph(sample: dict) -> dict[str, torch.Tensor]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `sample` | `dict` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, torch.Tensor]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model import build_graph

print(signature(build_graph))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model`
- 仓库相对路径：`packages/ai4e-contrib/application/spatiotemporal_pde/meshgraphnet/model.py:61`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-spatiotemporal-pde-meshgraphnet-model-build-model"></a>
## `ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model.build_model`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`build_model(config: dict) -> CylinderFlowModel`
- **规范定义名**：`ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model.build_model`

### 用途

按配置构造 CylinderFlow 模型连接。

### 导入与签名

```python
from ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model import build_model
```

```text
build_model(config: dict) -> CylinderFlowModel
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `dict` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`CylinderFlowModel`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model import build_model

print(signature(build_model))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`, `pcno`, `pcno_cylinder`, `safediffcon`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `extension.pcno`, `extension.pcno_cylinder`, `geothermal.pcno`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.resunet`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`, `recipe_extensions.research_state`, `recipe_extensions.safediffcon`, `recipe_extensions.sampling`, `recipe_extensions.tail_batch`, `recipe_extensions.task_labels`, `safediffcon.burgers`, `safediffcon.tokamak`

### 源码位置

- 模块：`ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model`
- 仓库相对路径：`packages/ai4e-contrib/application/spatiotemporal_pde/meshgraphnet/model.py:47`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.model')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
