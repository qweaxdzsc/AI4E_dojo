<!-- dojo-help: {"domain": "ai4e_contrib.ability.model.pibsnet.spline", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.model.pibsnet.spline 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.model.pibsnet.spline", "topic_id": "module:ai4e_contrib.ability.model.pibsnet.spline"} -->
# `ai4e_contrib.ability.model.pibsnet.spline` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-spline-basis"></a>
## `ai4e_contrib.ability.model.pibsnet.spline.basis`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`basis(coordinates, *, bounds, control_points, degree)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.spline.basis`

### 用途

生成零、一、二阶物理导数；端点使用样条定义域内的单侧值。

节点直接位于声明坐标区间，不再遗漏原仓库参数坐标到物理坐标缩放。
SciPy 仅用于准备常量矩阵，训练对控制系数的梯度由 PyTorch 保留。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.spline import basis
```

```text
basis(coordinates, *, bounds, control_points, degree)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `coordinates` | `未标注` | `必填` |
| `bounds` | `未标注` | `必填关键字参数` |
| `control_points` | `未标注` | `必填关键字参数` |
| `degree` | `未标注` | `必填关键字参数` |

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
from ai4e_contrib.ability.model.pibsnet.spline import basis

print(signature(basis))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.spline`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/spline.py:10`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.spline')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-spline-evaluate"></a>
## `ai4e_contrib.ability.model.pibsnet.spline.evaluate`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`evaluate(coefficients, bases, *, points=None, mapping='identity', grid=False)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.spline.evaluate`

### 用途

计算场和一二阶导数；grid 使用可分离轴收缩，不展开乘积矩阵。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.spline import evaluate
```

```text
evaluate(coefficients, bases, *, points=None, mapping='identity', grid=False)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `coefficients` | `未标注` | `必填` |
| `bases` | `未标注` | `必填` |
| `points` | `未标注` | `None` |
| `mapping` | `未标注` | `'identity'` |
| `grid` | `未标注` | `False` |

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
from ai4e_contrib.ability.model.pibsnet.spline import evaluate

print(signature(evaluate))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`, `safediffcon`, `surrogate_modeling/double_cylinder`, `surrogate_modeling/nasa_crm`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.research_state`, `recipe_extensions.sampling`, `recipe_extensions.wdno`, `safediffcon.burgers`, `safediffcon.tokamak`, `surrogate_modeling.double_cylinder`, `surrogate_modeling.nasa_crm`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.spline`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/spline.py:61`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.spline')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-spline-prepare-grid"></a>
## `ai4e_contrib.ability.model.pibsnet.spline.prepare_grid`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`prepare_grid(sample, config)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.spline.prepare_grid`

### 用途

完整网格按轴准备，避免存储逐点 Kronecker 矩阵。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.spline import prepare_grid
```

```text
prepare_grid(sample, config)
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

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.pibsnet.spline import prepare_grid

print(signature(prepare_grid))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.spline`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/spline.py:48`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.spline')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-spline-prepare-points"></a>
## `ai4e_contrib.ability.model.pibsnet.spline.prepare_points`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`prepare_points(sample, points, config)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.spline.prepare_points`

### 用途

任意配点的各轴矩阵，用于按点查询。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.spline import prepare_points
```

```text
prepare_points(sample, points, config)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `sample` | `未标注` | `必填` |
| `points` | `未标注` | `必填` |
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
from ai4e_contrib.ability.model.pibsnet.spline import prepare_points

print(signature(prepare_points))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.spline`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/spline.py:36`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.spline')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
