<!-- dojo-help: {"domain": "ai4e_contrib.ability.model.safediffcon.burgers_model_utils", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.model.safediffcon.burgers_model_utils 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.model.safediffcon.burgers_model_utils", "topic_id": "module:ai4e_contrib.ability.model.safediffcon.burgers_model_utils"} -->
# `ai4e_contrib.ability.model.safediffcon.burgers_model_utils` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-model-utils-convert-image-to-fn"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_model_utils.convert_image_to_fn`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`convert_image_to_fn(img_type, image)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils.convert_image_to_fn`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import convert_image_to_fn
```

```text
convert_image_to_fn(img_type, image)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `img_type` | `未标注` | `必填` |
| `image` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import convert_image_to_fn

print(signature(convert_image_to_fn))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_model_utils.py:40`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_model_utils')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-model-utils-cosine-beta-j-schedule"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_model_utils.cosine_beta_J_schedule`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`cosine_beta_J_schedule(t, s=0.008)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils.cosine_beta_J_schedule`

### 用途

cosine schedule (returns beta = 1 - cos^2 (x / N), which is increasing.)
as proposed in https://openreview.net/forum?id=-NEXDKk8gZ

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import cosine_beta_J_schedule
```

```text
cosine_beta_J_schedule(t, s=0.008)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `t` | `未标注` | `必填` |
| `s` | `未标注` | `0.008` |

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
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import cosine_beta_J_schedule

print(signature(cosine_beta_J_schedule))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_model_utils.py:92`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_model_utils')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-model-utils-cosine-beta-schedule"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_model_utils.cosine_beta_schedule`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`cosine_beta_schedule(timesteps, s=0.008)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils.cosine_beta_schedule`

### 用途

cosine schedule
as proposed in https://openreview.net/forum?id=-NEXDKk8gZ

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import cosine_beta_schedule
```

```text
cosine_beta_schedule(timesteps, s=0.008)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `timesteps` | `未标注` | `必填` |
| `s` | `未标注` | `0.008` |

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
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import cosine_beta_schedule

print(signature(cosine_beta_schedule))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_model_utils.py:149`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_model_utils')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-model-utils-cycle"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_model_utils.cycle`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`cycle(dl)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils.cycle`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import cycle
```

```text
cycle(dl)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dl` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import cycle

print(signature(cycle))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_model_utils.py:24`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_model_utils')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-model-utils-default"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_model_utils.default`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`default(val, d)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils.default`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import default
```

```text
default(val, d)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `val` | `未标注` | `必填` |
| `d` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import default

print(signature(default))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`parametric_pde`
- 案例：`parametric_pde.advection`, `parametric_pde.burgers`, `parametric_pde.convection_diffusion`, `parametric_pde.diffusion_trapezoid`, `parametric_pde.neumann_diffusion`

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_model_utils.py:16`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_model_utils')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-model-utils-exists"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_model_utils.exists`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`exists(x)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils.exists`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import exists
```

```text
exists(x)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import exists

print(signature(exists))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_model_utils.py:13`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_model_utils')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-model-utils-extract"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_model_utils.extract`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`extract(a, t, x_shape)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils.extract`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import extract
```

```text
extract(a, t, x_shape)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `a` | `未标注` | `必填` |
| `t` | `未标注` | `必填` |
| `x_shape` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import extract

print(signature(extract))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`geotransolver/bumper_beam`, `geotransolver/darcy`
- 案例：`geotransolver.bumper_beam`, `geotransolver.darcy`

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_model_utils.py:8`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_model_utils')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-model-utils-get-nablaj"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_model_utils.get_nablaJ`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`get_nablaJ(loss_fn: callable)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils.get_nablaJ`

### 用途

Use explicit loss for guided inference in diffusion.
J is the loss here, not Jacobian.

Arguments:
    loss_fn: callable, calculates the loss.
        Arguments: 
            x: state + control
        Returns: loss (requires_grad)

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import get_nablaJ
```

```text
get_nablaJ(loss_fn: callable)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `loss_fn` | `callable` | `必填` |

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
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import get_nablaJ

print(signature(get_nablaJ))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_model_utils.py:55`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_model_utils')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-model-utils-get-proj-ep-orthogonal-func"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_model_utils.get_proj_ep_orthogonal_func`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`get_proj_ep_orthogonal_func(norm='F')`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils.get_proj_ep_orthogonal_func`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import get_proj_ep_orthogonal_func
```

```text
get_proj_ep_orthogonal_func(norm='F')
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `norm` | `未标注` | `'F'` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`NotImplementedError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import get_proj_ep_orthogonal_func

print(signature(get_proj_ep_orthogonal_func))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_model_utils.py:72`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_model_utils')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-model-utils-get-scheduler"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_model_utils.get_scheduler`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`get_scheduler(scheduler_name: Optional[str]) -> Optional[Callable]`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils.get_scheduler`

### 用途

Get scheduler function based on name

Args:
    scheduler_name: Name of scheduler
    
Returns:
    Optional[Callable]: Scheduler function or None

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import get_scheduler
```

```text
get_scheduler(scheduler_name: Optional[str]) -> Optional[Callable]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `scheduler_name` | `Optional[str]` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Optional[Callable]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import get_scheduler

print(signature(get_scheduler))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_model_utils.py:161`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_model_utils')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-model-utils-has-int-squareroot"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_model_utils.has_int_squareroot`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`has_int_squareroot(num)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils.has_int_squareroot`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import has_int_squareroot
```

```text
has_int_squareroot(num)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `num` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import has_int_squareroot

print(signature(has_int_squareroot))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_model_utils.py:29`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_model_utils')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-model-utils-identity"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_model_utils.identity`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`identity(t, *args, **kwargs)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils.identity`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import identity
```

```text
identity(t, *args, **kwargs)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `t` | `未标注` | `必填` |
| `*args` | `未标注` | `可变位置参数` |
| `**kwargs` | `未标注` | `可变关键字参数` |

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
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import identity

print(signature(identity))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.sampling`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_model_utils.py:21`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_model_utils')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-model-utils-linear-beta-schedule"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_model_utils.linear_beta_schedule`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`linear_beta_schedule(timesteps)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils.linear_beta_schedule`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import linear_beta_schedule
```

```text
linear_beta_schedule(timesteps)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `timesteps` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import linear_beta_schedule

print(signature(linear_beta_schedule))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_model_utils.py:143`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_model_utils')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-model-utils-linear-schedule"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_model_utils.linear_schedule`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`linear_schedule(t)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils.linear_schedule`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import linear_schedule
```

```text
linear_schedule(t)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `t` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import linear_schedule

print(signature(linear_schedule))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_model_utils.py:134`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_model_utils')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-model-utils-normalize-to-neg-one-to-one"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_model_utils.normalize_to_neg_one_to_one`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`normalize_to_neg_one_to_one(img)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils.normalize_to_neg_one_to_one`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import normalize_to_neg_one_to_one
```

```text
normalize_to_neg_one_to_one(img)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `img` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import normalize_to_neg_one_to_one

print(signature(normalize_to_neg_one_to_one))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_model_utils.py:47`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_model_utils')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-model-utils-num-to-groups"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_model_utils.num_to_groups`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`num_to_groups(num, divisor)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils.num_to_groups`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import num_to_groups
```

```text
num_to_groups(num, divisor)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `num` | `未标注` | `必填` |
| `divisor` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import num_to_groups

print(signature(num_to_groups))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_model_utils.py:32`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_model_utils')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-model-utils-plain-cosine-schedule"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_model_utils.plain_cosine_schedule`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`plain_cosine_schedule(t, s=0.0)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils.plain_cosine_schedule`

### 用途

cosine schedule, which is decreasing...

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import plain_cosine_schedule
```

```text
plain_cosine_schedule(t, s=0.0)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `t` | `未标注` | `必填` |
| `s` | `未标注` | `0.0` |

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
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import plain_cosine_schedule

print(signature(plain_cosine_schedule))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_model_utils.py:105`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_model_utils')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-model-utils-sigmoid-schedule"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_model_utils.sigmoid_schedule`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`sigmoid_schedule(t, start=-3, end=3, tau=1, clamp_min=1e-05)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils.sigmoid_schedule`

### 用途

sigmoid schedule
proposed in https://arxiv.org/abs/2212.11972 - Figure 8
better for images > 64x64, when used during training

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import sigmoid_schedule
```

```text
sigmoid_schedule(t, start=-3, end=3, tau=1, clamp_min=1e-05)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `t` | `未标注` | `必填` |
| `start` | `未标注` | `-3` |
| `end` | `未标注` | `3` |
| `tau` | `未标注` | `1` |
| `clamp_min` | `未标注` | `1e-05` |

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
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import sigmoid_schedule

print(signature(sigmoid_schedule))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_model_utils.py:115`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_model_utils')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-model-utils-sigmoid-schedule-flip"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_model_utils.sigmoid_schedule_flip`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`sigmoid_schedule_flip(t)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils.sigmoid_schedule_flip`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import sigmoid_schedule_flip
```

```text
sigmoid_schedule_flip(t)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `t` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import sigmoid_schedule_flip

print(signature(sigmoid_schedule_flip))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_model_utils.py:131`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_model_utils')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-model-utils-unnormalize-to-zero-to-one"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_model_utils.unnormalize_to_zero_to_one`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`unnormalize_to_zero_to_one(t)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils.unnormalize_to_zero_to_one`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import unnormalize_to_zero_to_one
```

```text
unnormalize_to_zero_to_one(t)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `t` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.safediffcon.burgers_model_utils import unnormalize_to_zero_to_one

print(signature(unnormalize_to_zero_to_one))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_model_utils`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_model_utils.py:50`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_model_utils')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
