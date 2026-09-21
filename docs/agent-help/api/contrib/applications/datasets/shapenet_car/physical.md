<!-- dojo-help: {"domain": "ai4e_contrib.application.datasets.shapenet_car.physical", "kind": "api", "layer": "contrib.application", "summary": "ai4e_contrib.application.datasets.shapenet_car.physical 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.application.datasets.shapenet_car.physical", "topic_id": "module:ai4e_contrib.application.datasets.shapenet_car.physical"} -->
# `ai4e_contrib.application.datasets.shapenet_car.physical` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-application-datasets-shapenet-car-physical-comparison-mesh"></a>
## `ai4e_contrib.application.datasets.shapenet_car.physical.comparison_mesh`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`comparison_mesh(config: dict, sample: str, domain: str, points)`
- **规范定义名**：`ai4e_contrib.application.datasets.shapenet_car.physical.comparison_mesh`

### 用途

数据集解释原始表面和体积文件名；不承担切面或渲染。

### 导入与签名

```python
from ai4e_contrib.application.datasets.shapenet_car.physical import comparison_mesh
```

```text
comparison_mesh(config: dict, sample: str, domain: str, points)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `dict` | `必填` |
| `sample` | `str` | `必填` |
| `domain` | `str` | `必填` |
| `points` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FileNotFoundError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.application.datasets.shapenet_car.physical import comparison_mesh

print(signature(comparison_mesh))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.datasets.shapenet_car.physical`
- 仓库相对路径：`packages/ai4e-contrib/application/datasets/shapenet_car/physical.py:32`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.datasets.shapenet_car.physical')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-datasets-shapenet-car-physical-comparison-metadata"></a>
## `ai4e_contrib.application.datasets.shapenet_car.physical.comparison_metadata`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`comparison_metadata(config, sample, domain)`
- **规范定义名**：`ai4e_contrib.application.datasets.shapenet_car.physical.comparison_metadata`

### 用途

提供来源拓扑身份与已知物理单位，未知单位不猜测。

### 导入与签名

```python
from ai4e_contrib.application.datasets.shapenet_car.physical import comparison_metadata
```

```text
comparison_metadata(config, sample, domain)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `未标注` | `必填` |
| `sample` | `未标注` | `必填` |
| `domain` | `未标注` | `必填` |

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
from ai4e_contrib.application.datasets.shapenet_car.physical import comparison_metadata

print(signature(comparison_metadata))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.datasets.shapenet_car.physical`
- 仓库相对路径：`packages/ai4e-contrib/application/datasets/shapenet_car/physical.py:47`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.datasets.shapenet_car.physical')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-datasets-shapenet-car-physical-inference-fields"></a>
## `ai4e_contrib.application.datasets.shapenet_car.physical.inference_fields`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`inference_fields() -> dict`
- **规范定义名**：`ai4e_contrib.application.datasets.shapenet_car.physical.inference_fields`

### 用途

返回本数据集真实物理量的显示和分量说明。

### 导入与签名

```python
from ai4e_contrib.application.datasets.shapenet_car.physical import inference_fields
```

```text
inference_fields() -> dict
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
from ai4e_contrib.application.datasets.shapenet_car.physical import inference_fields

print(signature(inference_fields))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.inference_fields`

### 源码位置

- 模块：`ai4e_contrib.application.datasets.shapenet_car.physical`
- 仓库相对路径：`packages/ai4e-contrib/application/datasets/shapenet_car/physical.py:72`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.datasets.shapenet_car.physical')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-datasets-shapenet-car-physical-open-physical"></a>
## `ai4e_contrib.application.datasets.shapenet_car.physical.open_physical`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`open_physical(config: dict) -> PhysicalView`
- **规范定义名**：`ai4e_contrib.application.datasets.shapenet_car.physical.open_physical`

### 用途

按产物清单读取旧文件映射，行身份保持为 artifact 而非虚构原 ID。

### 导入与签名

```python
from ai4e_contrib.application.datasets.shapenet_car.physical import open_physical
```

```text
open_physical(config: dict) -> PhysicalView
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `dict` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`PhysicalView`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.application.datasets.shapenet_car.physical import open_physical

print(signature(open_physical))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.datasets.shapenet_car.physical`
- 仓库相对路径：`packages/ai4e-contrib/application/datasets/shapenet_car/physical.py:24`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.datasets.shapenet_car.physical')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
