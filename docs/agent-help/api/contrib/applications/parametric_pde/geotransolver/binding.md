<!-- dojo-help: {"domain": "ai4e_contrib.application.parametric_pde.geotransolver.binding", "kind": "api", "layer": "contrib.application", "summary": "ai4e_contrib.application.parametric_pde.geotransolver.binding 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.application.parametric_pde.geotransolver.binding", "topic_id": "module:ai4e_contrib.application.parametric_pde.geotransolver.binding"} -->
# `ai4e_contrib.application.parametric_pde.geotransolver.binding` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-application-parametric-pde-geotransolver-binding-decoder"></a>
## `ai4e_contrib.application.parametric_pde.geotransolver.binding.decoder`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`decoder(stats, *, physical)`
- **规范定义名**：`ai4e_contrib.application.parametric_pde.geotransolver.binding.decoder`

### 用途

Darcy 损失和评价均选物理空间解码。

### 导入与签名

```python
from ai4e_contrib.application.parametric_pde.geotransolver.binding import decoder
```

```text
decoder(stats, *, physical)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `stats` | `未标注` | `必填` |
| `physical` | `未标注` | `必填关键字参数` |

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
from ai4e_contrib.application.parametric_pde.geotransolver.binding import decoder

print(signature(decoder))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`geotransolver/bumper_beam`, `geotransolver/darcy`
- 案例：`geotransolver.bumper_beam`, `geotransolver.darcy`

### 源码位置

- 模块：`ai4e_contrib.application.parametric_pde.geotransolver.binding`
- 仓库相对路径：`packages/ai4e-contrib/application/parametric_pde/geotransolver/binding.py:55`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.parametric_pde.geotransolver.binding')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-parametric-pde-geotransolver-binding-extract"></a>
## `ai4e_contrib.application.parametric_pde.geotransolver.binding.extract`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`extract(path, *, stride=5)`
- **规范定义名**：`ai4e_contrib.application.parametric_pde.geotransolver.binding.extract`

### 用途

绑定 coeff/sol；共享实体索引连接坐标、输入和目标。

### 导入与签名

```python
from ai4e_contrib.application.parametric_pde.geotransolver.binding import extract
```

```text
extract(path, *, stride=5)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `未标注` | `必填` |
| `stride` | `未标注` | `5` |

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
from ai4e_contrib.application.parametric_pde.geotransolver.binding import extract

print(signature(extract))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`geotransolver/bumper_beam`, `geotransolver/darcy`
- 案例：`geotransolver.bumper_beam`, `geotransolver.darcy`

### 源码位置

- 模块：`ai4e_contrib.application.parametric_pde.geotransolver.binding`
- 仓库相对路径：`packages/ai4e-contrib/application/parametric_pde/geotransolver/binding.py:27`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.parametric_pde.geotransolver.binding')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-parametric-pde-geotransolver-binding-objective-binding"></a>
## `ai4e_contrib.application.parametric_pde.geotransolver.binding.objective_binding`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`objective_binding(stats)`
- **规范定义名**：`ai4e_contrib.application.parametric_pde.geotransolver.binding.objective_binding`

### 用途

目标字段身份，供公开训练步骤连接。

### 导入与签名

```python
from ai4e_contrib.application.parametric_pde.geotransolver.binding import objective_binding
```

```text
objective_binding(stats)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `stats` | `未标注` | `必填` |

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
from ai4e_contrib.application.parametric_pde.geotransolver.binding import objective_binding

print(signature(objective_binding))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`geotransolver/bumper_beam`, `geotransolver/darcy`
- 案例：`geotransolver.bumper_beam`, `geotransolver.darcy`

### 源码位置

- 模块：`ai4e_contrib.application.parametric_pde.geotransolver.binding`
- 仓库相对路径：`packages/ai4e-contrib/application/parametric_pde/geotransolver/binding.py:60`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.parametric_pde.geotransolver.binding')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-parametric-pde-geotransolver-binding-source"></a>
## `ai4e_contrib.application.parametric_pde.geotransolver.binding.source`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`source(path)`
- **规范定义名**：`ai4e_contrib.application.parametric_pde.geotransolver.binding.source`

### 用途

公开 smooth1 前1000与 smooth2 前200。

### 导入与签名

```python
from ai4e_contrib.application.parametric_pde.geotransolver.binding import source
```

```text
source(path)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `未标注` | `必填` |

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
from ai4e_contrib.application.parametric_pde.geotransolver.binding import source

print(signature(source))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `gencp`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`, `pcno`, `pcno_cylinder`, `safediffcon`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `extension.pcno`, `extension.pcno_cylinder`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `geothermal.pcno`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.sampling`, `recipe_extensions.wdno`, `safediffcon.burgers`, `safediffcon.tokamak`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.application.parametric_pde.geotransolver.binding`
- 仓库相对路径：`packages/ai4e-contrib/application/parametric_pde/geotransolver/binding.py:22`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.parametric_pde.geotransolver.binding')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-parametric-pde-geotransolver-binding-statistics"></a>
## `ai4e_contrib.application.parametric_pde.geotransolver.binding.statistics`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`statistics(arrays)`
- **规范定义名**：`ai4e_contrib.application.parametric_pde.geotransolver.binding.statistics`

### 用途

选择参考的全局标量统计。

### 导入与签名

```python
from ai4e_contrib.application.parametric_pde.geotransolver.binding import statistics
```

```text
statistics(arrays)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `arrays` | `未标注` | `必填` |

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
from ai4e_contrib.application.parametric_pde.geotransolver.binding import statistics

print(signature(statistics))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_contrib.application.parametric_pde.geotransolver.binding`
- 仓库相对路径：`packages/ai4e-contrib/application/parametric_pde/geotransolver/binding.py:40`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.parametric_pde.geotransolver.binding')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-parametric-pde-geotransolver-binding-transform"></a>
## `ai4e_contrib.application.parametric_pde.geotransolver.binding.transform`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`transform(arrays, stats)`
- **规范定义名**：`ai4e_contrib.application.parametric_pde.geotransolver.binding.transform`

### 用途

选择坐标+系数输入、解目标和可复制几何。

### 导入与签名

```python
from ai4e_contrib.application.parametric_pde.geotransolver.binding import transform
```

```text
transform(arrays, stats)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `arrays` | `未标注` | `必填` |
| `stats` | `未标注` | `必填` |

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
from ai4e_contrib.application.parametric_pde.geotransolver.binding import transform

print(signature(transform))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`gencp`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `safediffcon`, `wdno`
- 案例：`gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `recipe_extensions.gencp`, `recipe_extensions.wdno`, `safediffcon.burgers`, `safediffcon.tokamak`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.application.parametric_pde.geotransolver.binding`
- 仓库相对路径：`packages/ai4e-contrib/application/parametric_pde/geotransolver/binding.py:45`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.parametric_pde.geotransolver.binding')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
