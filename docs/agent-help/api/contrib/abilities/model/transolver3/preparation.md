<!-- dojo-help: {"domain": "ai4e_contrib.ability.model.transolver3.preparation", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.model.transolver3.preparation 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.model.transolver3.preparation", "topic_id": "module:ai4e_contrib.ability.model.transolver3.preparation"} -->
# `ai4e_contrib.ability.model.transolver3.preparation` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-model-transolver3-preparation-arrays"></a>
## `ai4e_contrib.ability.model.transolver3.preparation.arrays`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`arrays(sample: dict, config: dict, normalization) -> tuple[torch.Tensor, torch.Tensor]`
- **规范定义名**：`ai4e_contrib.ability.model.transolver3.preparation.arrays`

### 用途

按具名字段顺序拼接特征，工况在模型输入处广播。

### 导入与签名

```python
from ai4e_contrib.ability.model.transolver3.preparation import arrays
```

```text
arrays(sample: dict, config: dict, normalization) -> tuple[torch.Tensor, torch.Tensor]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `sample` | `dict` | `必填` |
| `config` | `dict` | `必填` |
| `normalization` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`tuple[torch.Tensor, torch.Tensor]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.transolver3.preparation import arrays

print(signature(arrays))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`geotransolver/bumper_beam`, `geotransolver/darcy`, `pcno`, `pcno_cylinder`, `safediffcon`
- 案例：`extension.pcno`, `extension.pcno_cylinder`, `geothermal.pcno`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `pcno.double_cylinder`, `recipe_extensions.geotransolver`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.wdno`, `safediffcon.burgers`, `safediffcon.tokamak`

### 源码位置

- 模块：`ai4e_contrib.ability.model.transolver3.preparation`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/transolver3/preparation.py:18`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.transolver3.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-transolver3-preparation-domain-binding"></a>
## `ai4e_contrib.ability.model.transolver3.preparation.domain_binding`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`domain_binding(config: dict) -> tuple[str, dict]`
- **规范定义名**：`ai4e_contrib.ability.model.transolver3.preparation.domain_binding`

### 用途

一次 Transolver 训练只消费一个显式域。

### 导入与签名

```python
from ai4e_contrib.ability.model.transolver3.preparation import domain_binding
```

```text
domain_binding(config: dict) -> tuple[str, dict]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `dict` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`tuple[str, dict]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.transolver3.preparation import domain_binding

print(signature(domain_binding))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.transolver3.preparation`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/transolver3/preparation.py:10`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.transolver3.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-transolver3-preparation-loss"></a>
## `ai4e_contrib.ability.model.transolver3.preparation.loss`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`loss(model, batch: dict, config: dict) -> dict`
- **规范定义名**：`ai4e_contrib.ability.model.transolver3.preparation.loss`

### 用途

等权标准化逐元素均方误差。

### 导入与签名

```python
from ai4e_contrib.ability.model.transolver3.preparation import loss
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

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.transolver3.preparation import loss

print(signature(loss))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`, `parametric_pde`, `pcno_cylinder`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `parametric_pde.advection`, `parametric_pde.burgers`, `parametric_pde.convection_diffusion`, `parametric_pde.diffusion_trapezoid`, `parametric_pde.neumann_diffusion`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.sampling`, `recipe_extensions.wdno`

### 源码位置

- 模块：`ai4e_contrib.ability.model.transolver3.preparation`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/transolver3/preparation.py:68`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.transolver3.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-transolver3-preparation-predict-sample"></a>
## `ai4e_contrib.ability.model.transolver3.preparation.predict_sample`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`predict_sample(model, sample: dict, config: dict, normalization, *, preparation_id: str) -> dict`
- **规范定义名**：`ai4e_contrib.ability.model.transolver3.preparation.predict_sample`

### 用途

完整域逐层状态汇总后解码；原点顺序回贴物理具名输出。

### 导入与签名

```python
from ai4e_contrib.ability.model.transolver3.preparation import predict_sample
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
from ai4e_contrib.ability.model.transolver3.preparation import predict_sample

print(signature(predict_sample))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.transolver3.preparation`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/transolver3/preparation.py:85`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.transolver3.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-transolver3-preparation-prepare-sample"></a>
## `ai4e_contrib.ability.model.transolver3.preparation.prepare_sample`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`prepare_sample(sample: dict, config: dict, normalization, *, evaluation: bool=False, epoch: int=0) -> dict`
- **规范定义名**：`ai4e_contrib.ability.model.transolver3.preparation.prepare_sample`

### 用途

训练随机块与起点，准备检查固定块；保留计算项原点身份。

### 导入与签名

```python
from ai4e_contrib.ability.model.transolver3.preparation import prepare_sample
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

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.transolver3.preparation import prepare_sample

print(signature(prepare_sample))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.transolver3.preparation`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/transolver3/preparation.py:47`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.transolver3.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
