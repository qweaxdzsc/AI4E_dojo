<!-- dojo-help: {"domain": "ai4e_contrib.ability.model.abupt.preparation", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.model.abupt.preparation 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.model.abupt.preparation", "topic_id": "module:ai4e_contrib.ability.model.abupt.preparation"} -->
# `ai4e_contrib.ability.model.abupt.preparation` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-model-abupt-preparation-loss"></a>
## `ai4e_contrib.ability.model.abupt.preparation.loss`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`loss(model, batch: dict, config: dict) -> dict`
- **规范定义名**：`ai4e_contrib.ability.model.abupt.preparation.loss`

### 用途

按模型的具名监督声明复用监督能力。

### 导入与签名

```python
from ai4e_contrib.ability.model.abupt.preparation import loss
```

```text
loss(model, batch: dict, config: dict) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model` | `未标注` | `必填` |
| `batch` | `dict` | `必填` |
| `config` | `dict` | `必填` |

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
from ai4e_contrib.ability.model.abupt.preparation import loss

print(signature(loss))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`, `parametric_pde`, `pcno_cylinder`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `parametric_pde.advection`, `parametric_pde.burgers`, `parametric_pde.convection_diffusion`, `parametric_pde.diffusion_trapezoid`, `parametric_pde.neumann_diffusion`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.pod_surrogate_replacement`, `recipe_extensions.research_state`, `recipe_extensions.sampling`, `recipe_extensions.tail_batch`, `recipe_extensions.wdno`

### 源码位置

- 模块：`ai4e_contrib.ability.model.abupt.preparation`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/abupt/preparation.py:42`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.abupt.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-abupt-preparation-predict-sample"></a>
## `ai4e_contrib.ability.model.abupt.preparation.predict_sample`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`predict_sample(model, sample: dict, config: dict, normalization, *, preparation_id: str) -> dict`
- **规范定义名**：`ai4e_contrib.ability.model.abupt.preparation.predict_sample`

### 用途

用固定锚点缓存查询全部物理点，不以训练抽样代替全点评价。

### 导入与签名

```python
from ai4e_contrib.ability.model.abupt.preparation import predict_sample
```

```text
predict_sample(model, sample: dict, config: dict, normalization, *, preparation_id: str) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model` | `未标注` | `必填` |
| `sample` | `dict` | `必填` |
| `config` | `dict` | `必填` |
| `normalization` | `未标注` | `必填` |
| `preparation_id` | `str` | `必填关键字参数` |

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
from ai4e_contrib.ability.model.abupt.preparation import predict_sample

print(signature(predict_sample))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.abupt.preparation`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/abupt/preparation.py:52`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.abupt.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-abupt-preparation-prepare-sample"></a>
## `ai4e_contrib.ability.model.abupt.preparation.prepare_sample`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`prepare_sample(sample: dict, config: dict, normalization, *, evaluation: bool=False, epoch: int=0) -> dict`
- **规范定义名**：`ai4e_contrib.ability.model.abupt.preparation.prepare_sample`

### 用途

复用原采样和拼批，样本条件保持单行，在模型内进行调制。

### 导入与签名

```python
from ai4e_contrib.ability.model.abupt.preparation import prepare_sample
```

```text
prepare_sample(sample: dict, config: dict, normalization, *, evaluation: bool=False, epoch: int=0) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `sample` | `dict` | `必填` |
| `config` | `dict` | `必填` |
| `normalization` | `未标注` | `必填` |
| `evaluation` | `bool` | `False` |
| `epoch` | `int` | `0` |

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
from ai4e_contrib.ability.model.abupt.preparation import prepare_sample

print(signature(prepare_sample))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.abupt.preparation`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/abupt/preparation.py:14`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.abupt.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
