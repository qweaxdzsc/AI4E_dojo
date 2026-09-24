<!-- dojo-help: {"domain": "ai4e_contrib.ability.inference.safediffcon.burgers", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.inference.safediffcon.burgers 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.inference.safediffcon.burgers", "topic_id": "module:ai4e_contrib.ability.inference.safediffcon.burgers"} -->
# `ai4e_contrib.ability.inference.safediffcon.burgers` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-inference-safediffcon-burgers-gaussiandiffusion"></a>
## `ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`GaussianDiffusion(model, *, seq_length, timesteps=1000, sampling_timesteps=None, objective='pred_noise', beta_schedule='cosine', ddim_sampling_eta=0.0, auto_normalize=False, guidance_u0=True, conditioned_on_residual=None, residual_on_u0=False, temporal=False, use_conv2d=False, is_condition_u0=False, is_condition_uT=False, is_condition_u0_zero_pred_noise=True, is_condition_uT_zero_pred_noise=True, condition_idx=10, recurrence=False, recurrence_k=1, normalize_beta=False, train_on_padded_locations=False, train_on_partially_observed=None, set_unobserved_to_zero_during_sampling=False, is_model_w=False, eval_two_models=False, expand_condition=False, prior_beta=1)`
- **规范定义名**：`ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion
```

```text
GaussianDiffusion(model, *, seq_length, timesteps=1000, sampling_timesteps=None, objective='pred_noise', beta_schedule='cosine', ddim_sampling_eta=0.0, auto_normalize=False, guidance_u0=True, conditioned_on_residual=None, residual_on_u0=False, temporal=False, use_conv2d=False, is_condition_u0=False, is_condition_uT=False, is_condition_u0_zero_pred_noise=True, is_condition_uT_zero_pred_noise=True, condition_idx=10, recurrence=False, recurrence_k=1, normalize_beta=False, train_on_padded_locations=False, train_on_partially_observed=None, set_unobserved_to_zero_during_sampling=False, is_model_w=False, eval_two_models=False, expand_condition=False, prior_beta=1)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model` | `未标注` | `必填` |
| `seq_length` | `未标注` | `必填关键字参数` |
| `timesteps` | `未标注` | `1000` |
| `sampling_timesteps` | `未标注` | `None` |
| `objective` | `未标注` | `'pred_noise'` |
| `beta_schedule` | `未标注` | `'cosine'` |
| `ddim_sampling_eta` | `未标注` | `0.0` |
| `auto_normalize` | `未标注` | `False` |
| `guidance_u0` | `未标注` | `True` |
| `conditioned_on_residual` | `未标注` | `None` |
| `residual_on_u0` | `未标注` | `False` |
| `temporal` | `未标注` | `False` |
| `use_conv2d` | `未标注` | `False` |
| `is_condition_u0` | `未标注` | `False` |
| `is_condition_uT` | `未标注` | `False` |
| `is_condition_u0_zero_pred_noise` | `未标注` | `True` |
| `is_condition_uT_zero_pred_noise` | `未标注` | `True` |
| `condition_idx` | `未标注` | `10` |
| `recurrence` | `未标注` | `False` |
| `recurrence_k` | `未标注` | `1` |
| `normalize_beta` | `未标注` | `False` |
| `train_on_padded_locations` | `未标注` | `False` |
| `train_on_partially_observed` | `未标注` | `None` |
| `set_unobserved_to_zero_during_sampling` | `未标注` | `False` |
| `is_model_w` | `未标注` | `False` |
| `eval_two_models` | `未标注` | `False` |
| `expand_condition` | `未标注` | `False` |
| `prior_beta` | `未标注` | `1` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`GaussianDiffusion`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`NotImplementedError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion

print(signature(GaussianDiffusion))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.safediffcon.burgers`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/safediffcon/burgers.py:22`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.safediffcon.burgers')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-safediffcon-burgers-gaussiandiffusion-ddim-sample"></a>
## `ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.ddim_sample`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`ddim_sample(self, shape, return_all_timesteps=False, w_groundtruth=None, enable_grad=False, **kwargs)`
- **规范定义名**：`ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.ddim_sample`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion
```

```text
ddim_sample(self, shape, return_all_timesteps=False, w_groundtruth=None, enable_grad=False, **kwargs)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `shape` | `未标注` | `必填` |
| `return_all_timesteps` | `未标注` | `False` |
| `w_groundtruth` | `未标注` | `None` |
| `enable_grad` | `未标注` | `False` |
| `**kwargs` | `未标注` | `可变关键字参数` |

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
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion

print(signature(GaussianDiffusion.ddim_sample))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.safediffcon.burgers`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/safediffcon/burgers.py:453`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.safediffcon.burgers')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-safediffcon-burgers-gaussiandiffusion-forward"></a>
## `ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, img, *args, **kwargs)`
- **规范定义名**：`ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.forward`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion
```

```text
forward(self, img, *args, **kwargs)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `img` | `未标注` | `必填` |
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
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion

print(signature(GaussianDiffusion.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_contrib.ability.inference.safediffcon.burgers`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/safediffcon/burgers.py:736`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.safediffcon.burgers')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-safediffcon-burgers-gaussiandiffusion-get-guidance-options"></a>
## `ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.get_guidance_options`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`get_guidance_options(self, **kwargs)`
- **规范定义名**：`ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.get_guidance_options`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion
```

```text
get_guidance_options(self, **kwargs)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
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
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion

print(signature(GaussianDiffusion.get_guidance_options))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.safediffcon.burgers`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/safediffcon/burgers.py:322`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.safediffcon.burgers')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-safediffcon-burgers-gaussiandiffusion-interpolate"></a>
## `ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.interpolate`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`interpolate(self, x1, x2, t=None, lam=0.5)`
- **规范定义名**：`ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.interpolate`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion
```

```text
interpolate(self, x1, x2, t=None, lam=0.5)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x1` | `未标注` | `必填` |
| `x2` | `未标注` | `必填` |
| `t` | `未标注` | `None` |
| `lam` | `未标注` | `0.5` |

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
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion

print(signature(GaussianDiffusion.interpolate))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.safediffcon.burgers`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/safediffcon/burgers.py:611`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.safediffcon.burgers')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-safediffcon-burgers-gaussiandiffusion-model-predictions"></a>
## `ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.model_predictions`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`model_predictions(self, x, t, x_self_cond=None, residual=None, clip_x_start=False, rederive_pred_noise=False, **kwargs)`
- **规范定义名**：`ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.model_predictions`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion
```

```text
model_predictions(self, x, t, x_self_cond=None, residual=None, clip_x_start=False, rederive_pred_noise=False, **kwargs)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `t` | `未标注` | `必填` |
| `x_self_cond` | `未标注` | `None` |
| `residual` | `未标注` | `None` |
| `clip_x_start` | `未标注` | `False` |
| `rederive_pred_noise` | `未标注` | `False` |
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
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion

print(signature(GaussianDiffusion.model_predictions))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.safediffcon.burgers`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/safediffcon/burgers.py:227`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.safediffcon.burgers')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-safediffcon-burgers-gaussiandiffusion-p-losses"></a>
## `ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.p_losses`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`p_losses(self, x_start, t, noise=None, mean=True)`
- **规范定义名**：`ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.p_losses`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion
```

```text
p_losses(self, x_start, t, noise=None, mean=True)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x_start` | `未标注` | `必填` |
| `t` | `未标注` | `必填` |
| `noise` | `未标注` | `None` |
| `mean` | `未标注` | `True` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`NotImplementedError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion

print(signature(GaussianDiffusion.p_losses))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.safediffcon.burgers`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/safediffcon/burgers.py:639`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.safediffcon.burgers')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-safediffcon-burgers-gaussiandiffusion-p-mean-variance"></a>
## `ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.p_mean_variance`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`p_mean_variance(self, x, t, x_self_cond=None, residual=None, **kwargs)`
- **规范定义名**：`ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.p_mean_variance`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion
```

```text
p_mean_variance(self, x, t, x_self_cond=None, residual=None, **kwargs)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `t` | `未标注` | `必填` |
| `x_self_cond` | `未标注` | `None` |
| `residual` | `未标注` | `None` |
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
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion

print(signature(GaussianDiffusion.p_mean_variance))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.safediffcon.burgers`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/safediffcon/burgers.py:289`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.safediffcon.burgers')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-safediffcon-burgers-gaussiandiffusion-p-sample"></a>
## `ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.p_sample`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`p_sample(self, x, t: int, x_self_cond=None, residual=None, **kwargs)`
- **规范定义名**：`ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.p_sample`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion
```

```text
p_sample(self, x, t: int, x_self_cond=None, residual=None, **kwargs)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `t` | `int` | `必填` |
| `x_self_cond` | `未标注` | `None` |
| `residual` | `未标注` | `None` |
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
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion

print(signature(GaussianDiffusion.p_sample))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.safediffcon.burgers`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/safediffcon/burgers.py:301`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.safediffcon.burgers')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-safediffcon-burgers-gaussiandiffusion-p-sample-loop"></a>
## `ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.p_sample_loop`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`p_sample_loop(self, shape, w_groundtruth=None, enable_grad=True, **kwargs)`
- **规范定义名**：`ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.p_sample_loop`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion
```

```text
p_sample_loop(self, shape, w_groundtruth=None, enable_grad=True, **kwargs)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `shape` | `未标注` | `必填` |
| `w_groundtruth` | `未标注` | `None` |
| `enable_grad` | `未标注` | `True` |
| `**kwargs` | `未标注` | `可变关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`NotImplementedError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion

print(signature(GaussianDiffusion.p_sample_loop))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.safediffcon.burgers`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/safediffcon/burgers.py:370`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.safediffcon.burgers')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-safediffcon-burgers-gaussiandiffusion-predict-noise-from-start"></a>
## `ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.predict_noise_from_start`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`predict_noise_from_start(self, x_t, t, x0)`
- **规范定义名**：`ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.predict_noise_from_start`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion
```

```text
predict_noise_from_start(self, x_t, t, x0)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x_t` | `未标注` | `必填` |
| `t` | `未标注` | `必填` |
| `x0` | `未标注` | `必填` |

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
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion

print(signature(GaussianDiffusion.predict_noise_from_start))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.safediffcon.burgers`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/safediffcon/burgers.py:200`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.safediffcon.burgers')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-safediffcon-burgers-gaussiandiffusion-predict-start-from-noise"></a>
## `ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.predict_start_from_noise`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`predict_start_from_noise(self, x_t, t, noise)`
- **规范定义名**：`ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.predict_start_from_noise`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion
```

```text
predict_start_from_noise(self, x_t, t, noise)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x_t` | `未标注` | `必填` |
| `t` | `未标注` | `必填` |
| `noise` | `未标注` | `必填` |

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
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion

print(signature(GaussianDiffusion.predict_start_from_noise))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.safediffcon.burgers`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/safediffcon/burgers.py:194`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.safediffcon.burgers')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-safediffcon-burgers-gaussiandiffusion-predict-start-from-v"></a>
## `ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.predict_start_from_v`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`predict_start_from_v(self, x_t, t, v)`
- **规范定义名**：`ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.predict_start_from_v`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion
```

```text
predict_start_from_v(self, x_t, t, v)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x_t` | `未标注` | `必填` |
| `t` | `未标注` | `必填` |
| `v` | `未标注` | `必填` |

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
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion

print(signature(GaussianDiffusion.predict_start_from_v))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.safediffcon.burgers`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/safediffcon/burgers.py:212`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.safediffcon.burgers')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-safediffcon-burgers-gaussiandiffusion-predict-v"></a>
## `ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.predict_v`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`predict_v(self, x_start, t, noise)`
- **规范定义名**：`ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.predict_v`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion
```

```text
predict_v(self, x_start, t, noise)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x_start` | `未标注` | `必填` |
| `t` | `未标注` | `必填` |
| `noise` | `未标注` | `必填` |

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
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion

print(signature(GaussianDiffusion.predict_v))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.safediffcon.burgers`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/safediffcon/burgers.py:206`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.safediffcon.burgers')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-safediffcon-burgers-gaussiandiffusion-q-posterior"></a>
## `ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.q_posterior`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`q_posterior(self, x_start, x_t, t)`
- **规范定义名**：`ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.q_posterior`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion
```

```text
q_posterior(self, x_start, x_t, t)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x_start` | `未标注` | `必填` |
| `x_t` | `未标注` | `必填` |
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
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion

print(signature(GaussianDiffusion.q_posterior))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.safediffcon.burgers`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/safediffcon/burgers.py:218`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.safediffcon.burgers')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-safediffcon-burgers-gaussiandiffusion-q-sample"></a>
## `ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.q_sample`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`q_sample(self, x_start, t, noise=None)`
- **规范定义名**：`ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.q_sample`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion
```

```text
q_sample(self, x_start, t, noise=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x_start` | `未标注` | `必填` |
| `t` | `未标注` | `必填` |
| `noise` | `未标注` | `None` |

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
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion

print(signature(GaussianDiffusion.q_sample))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.safediffcon.burgers`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/safediffcon/burgers.py:631`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.safediffcon.burgers')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-safediffcon-burgers-gaussiandiffusion-recurrent-sample"></a>
## `ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.recurrent_sample`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`recurrent_sample(self, x_tm1, t: int)`
- **规范定义名**：`ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.recurrent_sample`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion
```

```text
recurrent_sample(self, x_tm1, t: int)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x_tm1` | `未标注` | `必填` |
| `t` | `int` | `必填` |

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
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion

print(signature(GaussianDiffusion.recurrent_sample))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.safediffcon.burgers`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/safediffcon/burgers.py:309`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.safediffcon.burgers')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-safediffcon-burgers-gaussiandiffusion-sample"></a>
## `ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.sample`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`sample(self, batch_size=16, clip_denoised=True, w_groundtruth=None, enable_grad=True, **kwargs)`
- **规范定义名**：`ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.sample`

### 用途

Kwargs:
    clip_denoised: 
        boolean, clip generated x
    nablaJ: 
        a gradient function returning nablaJ for diffusion guidance. 
        Can use the function get_nablaJ to construct the gradient function.
    J_scheduler: 
        Optional callable, scheduler for J, returns stepsize given t
    proj_guidance:
        Optional callable, postprocess guidance for better diffusion. 
        E.g., project nabla_J to the orthogonal direction of epsilon_theta
    guidance_u0:
        Optional, boolean. If true, use guidance inside the model_pred
    u_init:
        Optional, torch.Tensor of size (batch, Nx). u at time = 0, applies when self.is_condition_u0 == True
    w_groundtruth:
        Optional, torch.Tensor []. Groundtruth of w in calibration set.
        As condition during sampling p(u,c|w).

### 导入与签名

```python
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion
```

```text
sample(self, batch_size=16, clip_denoised=True, w_groundtruth=None, enable_grad=True, **kwargs)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `batch_size` | `未标注` | `16` |
| `clip_denoised` | `未标注` | `True` |
| `w_groundtruth` | `未标注` | `None` |
| `enable_grad` | `未标注` | `True` |
| `**kwargs` | `未标注` | `可变关键字参数` |

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
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion

print(signature(GaussianDiffusion.sample))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `extension.pcno`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `recipe_extensions.geotransolver`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.physical_visualization`, `recipe_extensions.research_state`, `recipe_extensions.wdno`

### 源码位置

- 模块：`ai4e_contrib.ability.inference.safediffcon.burgers`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/safediffcon/burgers.py:559`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.safediffcon.burgers')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-safediffcon-burgers-gaussiandiffusion-set-condition"></a>
## `ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.set_condition`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`set_condition(self, img, u: torch.Tensor, shape, u0_or_uT)`
- **规范定义名**：`ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.set_condition`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion
```

```text
set_condition(self, img, u: torch.Tensor, shape, u0_or_uT)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `img` | `未标注` | `必填` |
| `u` | `torch.Tensor` | `必填` |
| `shape` | `未标注` | `必填` |
| `u0_or_uT` | `未标注` | `必填` |

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
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion

print(signature(GaussianDiffusion.set_condition))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.safediffcon.burgers`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/safediffcon/burgers.py:337`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.safediffcon.burgers')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-safediffcon-burgers-gaussiandiffusion-set-pad-condition"></a>
## `ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.set_pad_condition`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`set_pad_condition(self, img, origin_img=None)`
- **规范定义名**：`ai4e_contrib.ability.inference.safediffcon.burgers.GaussianDiffusion.set_pad_condition`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion
```

```text
set_pad_condition(self, img, origin_img=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `img` | `未标注` | `必填` |
| `origin_img` | `未标注` | `None` |

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
from ai4e_contrib.ability.inference.safediffcon.burgers import GaussianDiffusion

print(signature(GaussianDiffusion.set_pad_condition))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.safediffcon.burgers`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/safediffcon/burgers.py:361`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.safediffcon.burgers')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
