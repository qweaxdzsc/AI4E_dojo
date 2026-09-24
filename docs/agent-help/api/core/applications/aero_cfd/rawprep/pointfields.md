<!-- dojo-help: {"domain": "ai4e_core.applications.aero_cfd.rawprep.pointfields", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.aero_cfd.rawprep.pointfields 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.aero_cfd.rawprep.pointfields", "topic_id": "module:ai4e_core.applications.aero_cfd.rawprep.pointfields"} -->
# `ai4e_core.applications.aero_cfd.rawprep.pointfields` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-aero-cfd-rawprep-pointfields-savesample"></a>
## `ai4e_core.applications.aero_cfd.rawprep.pointfields.SaveSample`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`SaveSample(raw, component, *, resume=False)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.rawprep.pointfields.SaveSample`

### 用途

逐样本目录事务；完整标记绑定源内容和所有已保存文件。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.rawprep.pointfields import SaveSample
```

```text
SaveSample(raw, component, *, resume=False)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `raw` | `未标注` | `必填` |
| `component` | `未标注` | `必填` |
| `resume` | `未标注` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`SaveSample`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FileExistsError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.rawprep.pointfields import SaveSample

print(signature(SaveSample))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.rawprep.pointfields`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/rawprep/pointfields.py:45`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.rawprep.pointfields')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-rawprep-pointfields-savesample-begin"></a>
## `ai4e_core.applications.aero_cfd.rawprep.pointfields.SaveSample.begin`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`begin(self, data, output, *, flags)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.rawprep.pointfields.SaveSample.begin`

### 用途

提交前撤下完整清单；失败不能遗留本次完整成功标记。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.rawprep.pointfields import SaveSample
```

```text
begin(self, data, output, *, flags)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `data` | `未标注` | `必填` |
| `output` | `未标注` | `必填` |
| `flags` | `未标注` | `必填关键字参数` |

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
from ai4e_core.applications.aero_cfd.rawprep.pointfields import SaveSample

print(signature(SaveSample.begin))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.rawprep.pointfields`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/rawprep/pointfields.py:60`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.rawprep.pointfields')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-rawprep-pointfields-savesample-preflight"></a>
## `ai4e_core.applications.aero_cfd.rawprep.pointfields.SaveSample.preflight`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`preflight(self, data, output, *, flags, settings)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.rawprep.pointfields.SaveSample.preflight`

### 用途

检查真实目标，干跑和提交使用同一覆盖门禁。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.rawprep.pointfields import SaveSample
```

```text
preflight(self, data, output, *, flags, settings)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `data` | `未标注` | `必填` |
| `output` | `未标注` | `必填` |
| `flags` | `未标注` | `必填关键字参数` |
| `settings` | `未标注` | `必填关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FileExistsError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.rawprep.pointfields import SaveSample

print(signature(SaveSample.preflight))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.rawprep.pointfields`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/rawprep/pointfields.py:54`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.rawprep.pointfields')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-rawprep-pointfields-prepare"></a>
## `ai4e_core.applications.aero_cfd.rawprep.pointfields.prepare`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`prepare(config, component)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.rawprep.pointfields.prepare`

### 用途

来源组件发现样本；返回只登记读取步骤的数据集。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.rawprep.pointfields import prepare
```

```text
prepare(config, component)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `未标注` | `必填` |
| `component` | `未标注` | `必填` |

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
from ai4e_core.applications.aero_cfd.rawprep.pointfields import prepare

print(signature(prepare))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `gencp`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`, `pcno_cylinder`, `safediffcon`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.shapenet_car_abupt`, `classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.sampling`, `recipe_extensions.wdno`, `safediffcon.burgers`, `safediffcon.tokamak`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.rawprep.pointfields`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/rawprep/pointfields.py:16`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.rawprep.pointfields')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-rawprep-pointfields-publish"></a>
## `ai4e_core.applications.aero_cfd.rawprep.pointfields.publish`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`publish(results, raw, component)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.rawprep.pointfields.publish`

### 用途

只以本次完整成功结果计算训练统计和发布清单。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.rawprep.pointfields import publish
```

```text
publish(results, raw, component)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `results` | `未标注` | `必填` |
| `raw` | `未标注` | `必填` |
| `component` | `未标注` | `必填` |

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
from ai4e_core.applications.aero_cfd.rawprep.pointfields import publish

print(signature(publish))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.rawprep.pointfields`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/rawprep/pointfields.py:147`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.rawprep.pointfields')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
