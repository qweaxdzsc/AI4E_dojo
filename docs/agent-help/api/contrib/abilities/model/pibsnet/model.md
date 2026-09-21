<!-- dojo-help: {"domain": "ai4e_contrib.ability.model.pibsnet.model", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.model.pibsnet.model 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.model.pibsnet.model", "topic_id": "module:ai4e_contrib.ability.model.pibsnet.model"} -->
# `ai4e_contrib.ability.model.pibsnet.model` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-model-pibsnet"></a>
## `ai4e_contrib.ability.model.pibsnet.model.PIBSNet`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`PIBSNet(parameter_names, control_points, *, hidden_dim=64, hard_boundaries=None)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.model.PIBSNet`

### 用途

两层 ReLU MLP；硬定值边界通过开放样条边界控制系数实现。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.model import PIBSNet
```

```text
PIBSNet(parameter_names, control_points, *, hidden_dim=64, hard_boundaries=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `parameter_names` | `未标注` | `必填` |
| `control_points` | `未标注` | `必填` |
| `hidden_dim` | `未标注` | `64` |
| `hard_boundaries` | `未标注` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`PIBSNet`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.pibsnet.model import PIBSNet

print(signature(PIBSNet))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.model`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/model.py:11`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.model')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-model-pibsnet-forward"></a>
## `ai4e_contrib.ability.model.pibsnet.model.PIBSNet.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, parameters)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.model.PIBSNet.forward`

### 用途

返回 [batch, control_t, control_x] 或 [batch,t,eta,xi] 控制网格。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.model import PIBSNet
```

```text
forward(self, parameters)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `parameters` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.pibsnet.model import PIBSNet

print(signature(PIBSNet.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.model`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/model.py:48`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.model')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-model-evaluate-fields"></a>
## `ai4e_contrib.ability.model.pibsnet.model.evaluate_fields`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`evaluate_fields(model, sample, bases, *, points, grid=False, hard_initial=False)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.model.evaluate_fields`

### 用途

公开场与物理导数计算；Advection 可用解析初值 lifting 严格满足初值。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.model import evaluate_fields
```

```text
evaluate_fields(model, sample, bases, *, points, grid=False, hard_initial=False)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model` | `未标注` | `必填` |
| `sample` | `未标注` | `必填` |
| `bases` | `未标注` | `必填` |
| `points` | `未标注` | `必填关键字参数` |
| `grid` | `未标注` | `False` |
| `hard_initial` | `未标注` | `False` |

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
from ai4e_contrib.ability.model.pibsnet.model import evaluate_fields

print(signature(evaluate_fields))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `gencp`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `recipe_extensions.gencp`, `recipe_extensions.geotransolver_aero`

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.model`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/model.py:58`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.model')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
