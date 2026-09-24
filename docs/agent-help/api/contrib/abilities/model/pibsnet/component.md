<!-- dojo-help: {"domain": "ai4e_contrib.ability.model.pibsnet.component", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.model.pibsnet.component 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.model.pibsnet.component", "topic_id": "module:ai4e_contrib.ability.model.pibsnet.component"} -->
# `ai4e_contrib.ability.model.pibsnet.component` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-component-build"></a>
## `ai4e_contrib.ability.model.pibsnet.component.build`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`build(config)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.component.build`

### 用途

按已验证声明构建唯一模型；不启动优化器或运行会话。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.component import build
```

```text
build(config)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.pibsnet.component import build

print(signature(build))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.component`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/component.py:39`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.component')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-component-equation"></a>
## `ai4e_contrib.ability.model.pibsnet.component.equation`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`equation(case, values, parameters, *, points=None)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.component.equation`

### 用途

用普通函数绑定本案例残差；用户可通过训练步入口替换。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.component import equation
```

```text
equation(case, values, parameters, *, points=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `case` | `未标注` | `必填` |
| `values` | `未标注` | `必填` |
| `parameters` | `未标注` | `必填` |
| `points` | `未标注` | `None` |

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
from ai4e_contrib.ability.model.pibsnet.component import equation

print(signature(equation))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.component`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/component.py:175`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.component')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-component-predictions"></a>
## `ai4e_contrib.ability.model.pibsnet.component.predictions`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`predictions(model, prepared, config)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.component.predictions`

### 用途

公开完整场求值，保持数组轴顺序；返回全部物理导数。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.component import predictions
```

```text
predictions(model, prepared, config)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model` | `未标注` | `必填` |
| `prepared` | `未标注` | `必填` |
| `config` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.pibsnet.component import predictions

print(signature(predictions))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `gencp`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`, `parametric_pde`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `parametric_pde.advection`, `parametric_pde.burgers`, `parametric_pde.convection_diffusion`, `parametric_pde.diffusion_trapezoid`, `parametric_pde.neumann_diffusion`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.component`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/component.py:142`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.component')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-component-prepare"></a>
## `ai4e_contrib.ability.model.pibsnet.component.prepare`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`prepare(sample, config)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.component.prepare`

### 用途

准备冻结点集、标签及样条矩阵；不修改用户配置。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.component import prepare
```

```text
prepare(sample, config)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `sample` | `未标注` | `必填` |
| `config` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.pibsnet.component import prepare

print(signature(prepare))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `gencp`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`, `pcno_cylinder`, `safediffcon`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.shapenet_car_abupt`, `classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.sampling`, `recipe_extensions.wdno`, `safediffcon.burgers`, `safediffcon.tokamak`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.component`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/component.py:84`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.component')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-component-step"></a>
## `ai4e_contrib.ability.model.pibsnet.component.step`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`step(model, prepared, config)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.component.step`

### 用途

原生 PyTorch 单实例训练计算；损失/梯度聚合交给现有训练循环。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.component import step
```

```text
step(model, prepared, config)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model` | `未标注` | `必填` |
| `prepared` | `未标注` | `必填` |
| `config` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.pibsnet.component import step

print(signature(step))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `gencp`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`, `parametric_pde`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `parametric_pde.advection`, `parametric_pde.burgers`, `parametric_pde.convection_diffusion`, `parametric_pde.diffusion_trapezoid`, `parametric_pde.neumann_diffusion`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.research_state`, `recipe_extensions.wdno`

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.component`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/component.py:210`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.component')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
