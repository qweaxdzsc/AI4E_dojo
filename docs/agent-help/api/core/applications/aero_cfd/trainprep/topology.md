<!-- dojo-help: {"domain": "ai4e_core.applications.aero_cfd.trainprep.topology", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.aero_cfd.trainprep.topology 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.aero_cfd.trainprep.topology", "topic_id": "module:ai4e_core.applications.aero_cfd.trainprep.topology"} -->
# `ai4e_core.applications.aero_cfd.trainprep.topology` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-topology-topologyview"></a>
## `ai4e_core.applications.aero_cfd.trainprep.topology.TopologyView`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`TopologyView(view, settings: dict, output: str | Path, sampling: dict | None=None)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.topology.TopologyView`

### 用途

为物理视图附加中立图拓扑；底层平台数据保持只读。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.topology import TopologyView
```

```text
TopologyView(view, settings: dict, output: str | Path, sampling: dict | None=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `view` | `未标注` | `必填` |
| `settings` | `dict` | `必填` |
| `output` | `str | Path` | `必填` |
| `sampling` | `dict | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`TopologyView`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.topology import TopologyView

print(signature(TopologyView))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.topology`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/topology.py:18`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.topology')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-topology-topologyview-content-digest"></a>
## `ai4e_core.applications.aero_cfd.trainprep.topology.TopologyView.content_digest`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`content_digest(self) -> str`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.topology.TopologyView.content_digest`

### 用途

平台数据摘要已覆盖 VTKHDF；设置另进入准备记录。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.topology import TopologyView
```

```text
content_digest(self) -> str
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`str`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.topology import TopologyView

print(signature(TopologyView.content_digest))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.topology`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/topology.py:38`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.topology')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-topology-topologyview-describe"></a>
## `ai4e_core.applications.aero_cfd.trainprep.topology.TopologyView.describe`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`describe(self) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.topology.TopologyView.describe`

### 用途

保留物理视图说明并追加拓扑准备声明。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.topology import TopologyView
```

```text
describe(self) -> dict
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.topology import TopologyView

print(signature(TopologyView.describe))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`pcno_cylinder`
- 案例：`pcno.double_cylinder`, `recipe_extensions.model_block`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.topology`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/topology.py:34`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.topology')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-topology-topologyview-read"></a>
## `ai4e_core.applications.aero_cfd.trainprep.topology.TopologyView.read`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`read(self, partition: str, index: int=0, **kwargs) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.topology.TopologyView.read`

### 用途

读取物理样本，并为已声明域附加图缓存内容。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.topology import TopologyView
```

```text
read(self, partition: str, index: int=0, **kwargs) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `partition` | `str` | `必填` |
| `index` | `int` | `0` |
| `**kwargs` | `未标注` | `可变关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.topology import TopologyView

print(signature(TopologyView.read))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `geotransolver/shapenet_car`, `pcno_cylinder`, `wdno`
- 案例：`aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.free_wiring`, `recipe_extensions.physical_visualization`, `recipe_extensions.research_state`, `recipe_extensions.sampling`, `recipe_extensions.wdno`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.topology`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/topology.py:42`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.topology')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-topology-topologyview-remap-partitions"></a>
## `ai4e_core.applications.aero_cfd.trainprep.topology.TopologyView.remap_partitions`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`remap_partitions(self, partitions) -> None`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.topology.TopologyView.remap_partitions`

### 用途

把切片重挂委托给底层视图。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.topology import TopologyView
```

```text
remap_partitions(self, partitions) -> None
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `partitions` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`None`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.topology import TopologyView

print(signature(TopologyView.remap_partitions))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.topology`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/topology.py:29`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.topology')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-topology-topologyview-validate-all"></a>
## `ai4e_core.applications.aero_cfd.trainprep.topology.TopologyView.validate_all`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`validate_all(self) -> None`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.topology.TopologyView.validate_all`

### 用途

逐样本建立或核对缓存，使准备阶段尽早暴露身份错误。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.topology import TopologyView
```

```text
validate_all(self) -> None
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`None`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.topology import TopologyView

print(signature(TopologyView.validate_all))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.topology`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/topology.py:60`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.topology')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-topology-bind-topology"></a>
## `ai4e_core.applications.aero_cfd.trainprep.topology.bind_topology`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`bind_topology(data, *, settings, output, sampling=None) -> object`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.topology.bind_topology`

### 用途

把平台网格及当前分区预算绑定到物理准备，并验证全部已声明样本。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.topology import bind_topology
```

```text
bind_topology(data, *, settings, output, sampling=None) -> object
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `data` | `未标注` | `必填` |
| `settings` | `未标注` | `必填关键字参数` |
| `output` | `未标注` | `必填关键字参数` |
| `sampling` | `未标注` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`object`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.topology import bind_topology

print(signature(bind_topology))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`
- 案例：`aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.shapenet_car_meshgraphnet`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.topology`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/topology.py:124`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.topology')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-topology-graph-from-vtkhdf"></a>
## `ai4e_core.applications.aero_cfd.trainprep.topology.graph_from_vtkhdf`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`graph_from_vtkhdf(path: Path, positions: torch.Tensor, source_ids: torch.Tensor) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.topology.graph_from_vtkhdf`

### 用途

读取规范网格，按 PT 原点 ID 对齐坐标并构造诱导子图。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.topology import graph_from_vtkhdf
```

```text
graph_from_vtkhdf(path: Path, positions: torch.Tensor, source_ids: torch.Tensor) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `Path` | `必填` |
| `positions` | `torch.Tensor` | `必填` |
| `source_ids` | `torch.Tensor` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.topology import graph_from_vtkhdf

print(signature(graph_from_vtkhdf))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.topology`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/topology.py:170`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.topology')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-topology-topology-digest"></a>
## `ai4e_core.applications.aero_cfd.trainprep.topology.topology_digest`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`topology_digest(path: Path, ids: torch.Tensor) -> str`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.topology.topology_digest`

### 用途

以完整 VTKHDF 字节和 PT 原点身份标识图缓存。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.topology import topology_digest
```

```text
topology_digest(path: Path, ids: torch.Tensor) -> str
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `Path` | `必填` |
| `ids` | `torch.Tensor` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`str`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.topology import topology_digest

print(signature(topology_digest))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.topology`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/topology.py:160`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.topology')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
