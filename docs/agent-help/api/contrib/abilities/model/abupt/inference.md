<!-- dojo-help: {"domain": "ai4e_contrib.ability.model.abupt.inference", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.model.abupt.inference 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.model.abupt.inference", "topic_id": "module:ai4e_contrib.ability.model.abupt.inference"} -->
# `ai4e_contrib.ability.model.abupt.inference` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-model-abupt-inference-inferencecontext"></a>
## `ai4e_contrib.ability.model.abupt.inference.InferenceContext`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`InferenceContext(model, inputs, *, preparation_id)`
- **规范定义名**：`ai4e_contrib.ability.model.abupt.inference.InferenceContext`

### 用途

绑定准备记录，预填充一次并显式释放缓存。

### 导入与签名

```python
from ai4e_contrib.ability.model.abupt.inference import InferenceContext
```

```text
InferenceContext(model, inputs, *, preparation_id)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model` | `未标注` | `必填` |
| `inputs` | `未标注` | `必填` |
| `preparation_id` | `未标注` | `必填关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`InferenceContext`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.abupt.inference import InferenceContext

print(signature(InferenceContext))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.abupt.inference`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/abupt/inference.py:72`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.abupt.inference')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-abupt-inference-inferencecontext-chunks"></a>
## `ai4e_contrib.ability.model.abupt.inference.InferenceContext.chunks`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`chunks(self, positions, *, features=None, chunk_size=1024, preparation_id)`
- **规范定义名**：`ai4e_contrib.ability.model.abupt.inference.InferenceContext.chunks`

### 用途

按域分别分块，拼接恢复查询顺序。

### 导入与签名

```python
from ai4e_contrib.ability.model.abupt.inference import InferenceContext
```

```text
chunks(self, positions, *, features=None, chunk_size=1024, preparation_id)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `positions` | `未标注` | `必填` |
| `features` | `未标注` | `None` |
| `chunk_size` | `未标注` | `1024` |
| `preparation_id` | `未标注` | `必填关键字参数` |

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
from ai4e_contrib.ability.model.abupt.inference import InferenceContext

print(signature(InferenceContext.chunks))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.abupt.inference`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/abupt/inference.py:93`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.abupt.inference')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-abupt-inference-inferencecontext-close"></a>
## `ai4e_contrib.ability.model.abupt.inference.InferenceContext.close`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`close(self)`
- **规范定义名**：`ai4e_contrib.ability.model.abupt.inference.InferenceContext.close`

### 用途

释放所有持有的张量并使后续调用失败。

### 导入与签名

```python
from ai4e_contrib.ability.model.abupt.inference import InferenceContext
```

```text
close(self)
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

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
from ai4e_contrib.ability.model.abupt.inference import InferenceContext

print(signature(InferenceContext.close))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.abupt.inference`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/abupt/inference.py:120`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.abupt.inference')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-abupt-inference-inferencecontext-query"></a>
## `ai4e_contrib.ability.model.abupt.inference.InferenceContext.query`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`query(self, positions, *, features=None, preparation_id)`
- **规范定义名**：`ai4e_contrib.ability.model.abupt.inference.InferenceContext.query`

### 用途

只改变查询坐标和局部查询特征，不改变锚点或条件。

### 导入与签名

```python
from ai4e_contrib.ability.model.abupt.inference import InferenceContext
```

```text
query(self, positions, *, features=None, preparation_id)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `positions` | `未标注` | `必填` |
| `features` | `未标注` | `None` |
| `preparation_id` | `未标注` | `必填关键字参数` |

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
from ai4e_contrib.ability.model.abupt.inference import InferenceContext

print(signature(InferenceContext.query))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_contrib.ability.model.abupt.inference`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/abupt/inference.py:85`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.abupt.inference')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-abupt-inference-modelcache"></a>
## `ai4e_contrib.ability.model.abupt.inference.ModelCache`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`class ModelCache`
- **规范定义名**：`ai4e_contrib.ability.model.abupt.inference.ModelCache`

### 用途

进程内推理状态，不允许序列化为检查点。

### 导入与签名

```python
from ai4e_contrib.ability.model.abupt.inference import ModelCache
```

```text
class ModelCache
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`ModelCache`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`TypeError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.abupt.inference import ModelCache

print(signature(ModelCache))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.abupt.inference`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/abupt/inference.py:23`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.abupt.inference')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-abupt-inference-modelcache-geometry-only"></a>
## `ai4e_contrib.ability.model.abupt.inference.ModelCache.geometry_only`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`geometry_only(self)`
- **规范定义名**：`ai4e_contrib.ability.model.abupt.inference.ModelCache.geometry_only`

### 用途

保留几何编码，允许重新编码 anchors；几何条件必须一致。

### 导入与签名

```python
from ai4e_contrib.ability.model.abupt.inference import ModelCache
```

```text
geometry_only(self)
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

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
from ai4e_contrib.ability.model.abupt.inference import ModelCache

print(signature(ModelCache.geometry_only))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.abupt.inference`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/abupt/inference.py:55`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.abupt.inference')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-abupt-inference-modelcache-validate"></a>
## `ai4e_contrib.ability.model.abupt.inference.ModelCache.validate`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`validate(self, model)`
- **规范定义名**：`ai4e_contrib.ability.model.abupt.inference.ModelCache.validate`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.abupt.inference import ModelCache
```

```text
validate(self, model)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.abupt.inference import ModelCache

print(signature(ModelCache.validate))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`gencp`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `parametric_pde`, `pcno`, `pcno_cylinder`, `wdno`
- 案例：`extension.pcno`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `geothermal.pcno`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `parametric_pde.advection`, `parametric_pde.burgers`, `parametric_pde.convection_diffusion`, `parametric_pde.diffusion_trapezoid`, `parametric_pde.neumann_diffusion`, `pcno.double_cylinder`, `recipe_extensions.wdno`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.ability.model.abupt.inference`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/abupt/inference.py:36`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.abupt.inference')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-abupt-inference-model-signature"></a>
## `ai4e_contrib.ability.model.abupt.inference.model_signature`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`model_signature(model)`
- **规范定义名**：`ai4e_contrib.ability.model.abupt.inference.model_signature`

### 用途

对象身份和版本计数检测正常更新、加载及设备/精度变更。

### 导入与签名

```python
from ai4e_contrib.ability.model.abupt.inference import model_signature
```

```text
model_signature(model)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.abupt.inference import model_signature

print(signature(model_signature))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.abupt.inference`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/abupt/inference.py:8`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.abupt.inference')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
