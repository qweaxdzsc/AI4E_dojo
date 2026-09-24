<!-- dojo-help: {"domain": "ai4e_contrib.application.datasets.gencp.cylinder", "kind": "api", "layer": "contrib.application", "summary": "ai4e_contrib.application.datasets.gencp.cylinder 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.application.datasets.gencp.cylinder", "topic_id": "module:ai4e_contrib.application.datasets.gencp.cylinder"} -->
# `ai4e_contrib.application.datasets.gencp.cylinder` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-application-datasets-gencp-cylinder-describe"></a>
## `ai4e_contrib.application.datasets.gencp.cylinder.describe`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`describe(source, output)`
- **规范定义名**：`ai4e_contrib.application.datasets.gencp.cylinder.describe`

### 用途

核验现有5/1轨迹身份、坐标及1000帧；冻结只读来源摘要。

### 导入与签名

```python
from ai4e_contrib.application.datasets.gencp.cylinder import describe
```

```text
describe(source, output)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `source` | `未标注` | `必填` |
| `output` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.application.datasets.gencp.cylinder import describe

print(signature(describe))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`pcno_cylinder`
- 案例：`pcno.double_cylinder`, `recipe_extensions.model_block`

### 源码位置

- 模块：`ai4e_contrib.application.datasets.gencp.cylinder`
- 仓库相对路径：`packages/ai4e-contrib/application/datasets/gencp/cylinder.py:28`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.datasets.gencp.cylinder')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-datasets-gencp-cylinder-prepare"></a>
## `ai4e_contrib.application.datasets.gencp.cylinder.prepare`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`prepare(dataset, output, *, history, horizon, interval=10)`
- **规范定义名**：`ai4e_contrib.application.datasets.gencp.cylinder.prepare`

### 用途

训练统计与冻结窗口规则；不物化大规模窗口张量。

### 导入与签名

```python
from ai4e_contrib.application.datasets.gencp.cylinder import prepare
```

```text
prepare(dataset, output, *, history, horizon, interval=10)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dataset` | `未标注` | `必填` |
| `output` | `未标注` | `必填` |
| `history` | `未标注` | `必填关键字参数` |
| `horizon` | `未标注` | `必填关键字参数` |
| `interval` | `未标注` | `10` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.application.datasets.gencp.cylinder import prepare

print(signature(prepare))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `gencp`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`, `pcno_cylinder`, `safediffcon`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.shapenet_car_abupt`, `classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.sampling`, `recipe_extensions.wdno`, `safediffcon.burgers`, `safediffcon.tokamak`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.application.datasets.gencp.cylinder`
- 仓库相对路径：`packages/ai4e-contrib/application/datasets/gencp/cylinder.py:66`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.datasets.gencp.cylinder')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-datasets-gencp-cylinder-read-fields"></a>
## `ai4e_contrib.application.datasets.gencp.cylinder.read_fields`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`read_fields(path, selection)`
- **规范定义名**：`ai4e_contrib.application.datasets.gencp.cylinder.read_fields`

### 用途

裁剪保护层，保留交错分量；SDF仅沿来源约定除以100。

### 导入与签名

```python
from ai4e_contrib.application.datasets.gencp.cylinder import read_fields
```

```text
read_fields(path, selection)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `未标注` | `必填` |
| `selection` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.application.datasets.gencp.cylinder import read_fields

print(signature(read_fields))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.physical_visualization`

### 源码位置

- 模块：`ai4e_contrib.application.datasets.gencp.cylinder`
- 仓库相对路径：`packages/ai4e-contrib/application/datasets/gencp/cylinder.py:18`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.datasets.gencp.cylinder')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-datasets-gencp-cylinder-read-window"></a>
## `ai4e_contrib.application.datasets.gencp.cylinder.read_window`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`read_window(prepared, trajectory, start)`
- **规范定义名**：`ai4e_contrib.application.datasets.gencp.cylinder.read_window`

### 用途

读取单个窗口；未来标签与已知历史分开返回。

### 导入与签名

```python
from ai4e_contrib.application.datasets.gencp.cylinder import read_window
```

```text
read_window(prepared, trajectory, start)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `prepared` | `未标注` | `必填` |
| `trajectory` | `未标注` | `必填` |
| `start` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.application.datasets.gencp.cylinder import read_window

print(signature(read_window))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.datasets.gencp.cylinder`
- 仓库相对路径：`packages/ai4e-contrib/application/datasets/gencp/cylinder.py:112`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.datasets.gencp.cylinder')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
