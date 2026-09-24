<!-- dojo-help: {"domain": "ai4e_contrib.application.classic_networks.preparation", "kind": "api", "layer": "contrib.application", "summary": "ai4e_contrib.application.classic_networks.preparation 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.application.classic_networks.preparation", "topic_id": "module:ai4e_contrib.application.classic_networks.preparation"} -->
# `ai4e_contrib.application.classic_networks.preparation` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-application-classic-networks-preparation-dataset-binding"></a>
## `ai4e_contrib.application.classic_networks.preparation.dataset_binding`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`dataset_binding(case)`
- **规范定义名**：`ai4e_contrib.application.classic_networks.preparation.dataset_binding`

### 用途

选择来源语义模块，核心运行器不解释案例名称。

### 导入与签名

```python
from ai4e_contrib.application.classic_networks.preparation import dataset_binding
```

```text
dataset_binding(case)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `case` | `未标注` | `必填` |

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
from ai4e_contrib.application.classic_networks.preparation import dataset_binding

print(signature(dataset_binding))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.classic_networks.preparation`
- 仓库相对路径：`packages/ai4e-contrib/application/classic_networks/preparation.py:16`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.classic_networks.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-classic-networks-preparation-original-samples"></a>
## `ai4e_contrib.application.classic_networks.preparation.original_samples`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`original_samples(path, split, identities)`
- **规范定义名**：`ai4e_contrib.application.classic_networks.preparation.original_samples`

### 用途

从准备内物理快照按显式样本身份读取回贴目标，不依赖原始源。

### 导入与签名

```python
from ai4e_contrib.application.classic_networks.preparation import original_samples
```

```text
original_samples(path, split, identities)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `未标注` | `必填` |
| `split` | `未标注` | `必填` |
| `identities` | `未标注` | `必填` |

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
from ai4e_contrib.application.classic_networks.preparation import original_samples

print(signature(original_samples))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`
- 案例：`classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`

### 源码位置

- 模块：`ai4e_contrib.application.classic_networks.preparation`
- 仓库相对路径：`packages/ai4e-contrib/application/classic_networks/preparation.py:150`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.classic_networks.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-classic-networks-preparation-physical-source"></a>
## `ai4e_contrib.application.classic_networks.preparation.physical_source`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`physical_source(cfg, output, session)`
- **规范定义名**：`ai4e_contrib.application.classic_networks.preparation.physical_source`

### 用途

保存真实输入并发布完整名单，源目录保持只读。

### 导入与签名

```python
from ai4e_contrib.application.classic_networks.preparation import physical_source
```

```text
physical_source(cfg, output, session)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cfg` | `未标注` | `必填` |
| `output` | `未标注` | `必填` |
| `session` | `未标注` | `必填` |

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
from ai4e_contrib.application.classic_networks.preparation import physical_source

print(signature(physical_source))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`
- 案例：`classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`

### 源码位置

- 模块：`ai4e_contrib.application.classic_networks.preparation`
- 仓库相对路径：`packages/ai4e-contrib/application/classic_networks/preparation.py:25`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.classic_networks.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-classic-networks-preparation-prepare"></a>
## `ai4e_contrib.application.classic_networks.preparation.prepare`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`prepare(physical, output, dataset, session)`
- **规范定义名**：`ai4e_contrib.application.classic_networks.preparation.prepare`

### 用途

转换模型独立准备；网格尺寸和窗口为数据规格，不包含网络私有字段。

### 导入与签名

```python
from ai4e_contrib.application.classic_networks.preparation import prepare
```

```text
prepare(physical, output, dataset, session)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `physical` | `未标注` | `必填` |
| `output` | `未标注` | `必填` |
| `dataset` | `未标注` | `必填` |
| `session` | `未标注` | `必填` |

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
from ai4e_contrib.application.classic_networks.preparation import prepare

print(signature(prepare))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `gencp`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`, `pcno_cylinder`, `safediffcon`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.shapenet_car_abupt`, `classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.sampling`, `recipe_extensions.wdno`, `safediffcon.burgers`, `safediffcon.tokamak`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.application.classic_networks.preparation`
- 仓库相对路径：`packages/ai4e-contrib/application/classic_networks/preparation.py:51`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.classic_networks.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-classic-networks-preparation-read-prepared"></a>
## `ai4e_contrib.application.classic_networks.preparation.read_prepared`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`read_prepared(path, split)`
- **规范定义名**：`ai4e_contrib.application.classic_networks.preparation.read_prepared`

### 用途

校验可搬移数组清单，不回读原始源或其他模型配置。

### 导入与签名

```python
from ai4e_contrib.application.classic_networks.preparation import read_prepared
```

```text
read_prepared(path, split)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `未标注` | `必填` |
| `split` | `未标注` | `必填` |

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
from ai4e_contrib.application.classic_networks.preparation import read_prepared

print(signature(read_prepared))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`, `surrogate_modeling/double_cylinder`, `surrogate_modeling/nasa_crm`
- 案例：`classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `surrogate_modeling.double_cylinder`, `surrogate_modeling.nasa_crm`

### 源码位置

- 模块：`ai4e_contrib.application.classic_networks.preparation`
- 仓库相对路径：`packages/ai4e-contrib/application/classic_networks/preparation.py:138`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.classic_networks.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
