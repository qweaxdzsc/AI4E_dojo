<!-- dojo-help: {"domain": "ai4e_contrib.ability.inference.wdno.diffusion", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.inference.wdno.diffusion 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.inference.wdno.diffusion", "topic_id": "module:ai4e_contrib.ability.inference.wdno.diffusion"} -->
# `ai4e_contrib.ability.inference.wdno.diffusion` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-inference-wdno-diffusion-gaussiandiffusion"></a>
## `ai4e_contrib.ability.inference.wdno.diffusion.GaussianDiffusion`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`GaussianDiffusion(model, *, seq_length, is_wavelet=True, pad_mode=None, wave_type=None, padded_shape=None, ori_shape=torch.tensor([81, 128]), is_super_model=False, upsample_t=1, upsample_x=1, timesteps=1000, sampling_timesteps=None, objective='pred_noise', beta_schedule='cosine', ddim_sampling_eta=0.0, auto_normalize=False, loss_layer_weight=1, is_condition_pad=True, is_condition_u0=False, is_condition_uT=False, is_condition_f=False, train_on_padded_locations=True)`
- **规范定义名**：`ai4e_contrib.ability.inference.wdno.diffusion.GaussianDiffusion`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.inference.wdno.diffusion import GaussianDiffusion
```

```text
GaussianDiffusion(model, *, seq_length, is_wavelet=True, pad_mode=None, wave_type=None, padded_shape=None, ori_shape=torch.tensor([81, 128]), is_super_model=False, upsample_t=1, upsample_x=1, timesteps=1000, sampling_timesteps=None, objective='pred_noise', beta_schedule='cosine', ddim_sampling_eta=0.0, auto_normalize=False, loss_layer_weight=1, is_condition_pad=True, is_condition_u0=False, is_condition_uT=False, is_condition_f=False, train_on_padded_locations=True)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model` | `未标注` | `必填` |
| `seq_length` | `未标注` | `必填关键字参数` |
| `is_wavelet` | `未标注` | `True` |
| `pad_mode` | `未标注` | `None` |
| `wave_type` | `未标注` | `None` |
| `padded_shape` | `未标注` | `None` |
| `ori_shape` | `未标注` | `torch.tensor([81, 128])` |
| `is_super_model` | `未标注` | `False` |
| `upsample_t` | `未标注` | `1` |
| `upsample_x` | `未标注` | `1` |
| `timesteps` | `未标注` | `1000` |
| `sampling_timesteps` | `未标注` | `None` |
| `objective` | `未标注` | `'pred_noise'` |
| `beta_schedule` | `未标注` | `'cosine'` |
| `ddim_sampling_eta` | `未标注` | `0.0` |
| `auto_normalize` | `未标注` | `False` |
| `loss_layer_weight` | `未标注` | `1` |
| `is_condition_pad` | `未标注` | `True` |
| `is_condition_u0` | `未标注` | `False` |
| `is_condition_uT` | `未标注` | `False` |
| `is_condition_f` | `未标注` | `False` |
| `train_on_padded_locations` | `未标注` | `True` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`GaussianDiffusion`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.inference.wdno.diffusion import GaussianDiffusion

print(signature(GaussianDiffusion))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.wdno.diffusion`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/wdno/diffusion.py:14`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.wdno.diffusion')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-wdno-diffusion-gaussiandiffusion-ddim-sample"></a>
## `ai4e_contrib.ability.inference.wdno.diffusion.GaussianDiffusion.ddim_sample`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`ddim_sample(self, shape, **kwargs)`
- **规范定义名**：`ai4e_contrib.ability.inference.wdno.diffusion.GaussianDiffusion.ddim_sample`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.inference.wdno.diffusion import GaussianDiffusion
```

```text
ddim_sample(self, shape, **kwargs)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `shape` | `未标注` | `必填` |
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
from ai4e_contrib.ability.inference.wdno.diffusion import GaussianDiffusion

print(signature(GaussianDiffusion.ddim_sample))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.wdno.diffusion`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/wdno/diffusion.py:348`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.wdno.diffusion')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-wdno-diffusion-gaussiandiffusion-get-guidance-options"></a>
## `ai4e_contrib.ability.inference.wdno.diffusion.GaussianDiffusion.get_guidance_options`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`get_guidance_options(self, **kwargs)`
- **规范定义名**：`ai4e_contrib.ability.inference.wdno.diffusion.GaussianDiffusion.get_guidance_options`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.inference.wdno.diffusion import GaussianDiffusion
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
from ai4e_contrib.ability.inference.wdno.diffusion import GaussianDiffusion

print(signature(GaussianDiffusion.get_guidance_options))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.wdno.diffusion`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/wdno/diffusion.py:234`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.wdno.diffusion')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-wdno-diffusion-gaussiandiffusion-interpolate"></a>
## `ai4e_contrib.ability.inference.wdno.diffusion.GaussianDiffusion.interpolate`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`interpolate(self, x1, x2, t=None, lam=0.5)`
- **规范定义名**：`ai4e_contrib.ability.inference.wdno.diffusion.GaussianDiffusion.interpolate`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.inference.wdno.diffusion import GaussianDiffusion
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
from ai4e_contrib.ability.inference.wdno.diffusion import GaussianDiffusion

print(signature(GaussianDiffusion.interpolate))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.wdno.diffusion`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/wdno/diffusion.py:471`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.wdno.diffusion')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-wdno-diffusion-gaussiandiffusion-model-predictions"></a>
## `ai4e_contrib.ability.inference.wdno.diffusion.GaussianDiffusion.model_predictions`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`model_predictions(self, x, t, x_self_cond=None, clip_x_start=False, rederive_pred_noise=False, **kwargs)`
- **规范定义名**：`ai4e_contrib.ability.inference.wdno.diffusion.GaussianDiffusion.model_predictions`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.inference.wdno.diffusion import GaussianDiffusion
```

```text
model_predictions(self, x, t, x_self_cond=None, clip_x_start=False, rederive_pred_noise=False, **kwargs)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `t` | `未标注` | `必填` |
| `x_self_cond` | `未标注` | `None` |
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
from ai4e_contrib.ability.inference.wdno.diffusion import GaussianDiffusion

print(signature(GaussianDiffusion.model_predictions))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.wdno.diffusion`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/wdno/diffusion.py:179`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.wdno.diffusion')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-wdno-diffusion-gaussiandiffusion-p-mean-variance"></a>
## `ai4e_contrib.ability.inference.wdno.diffusion.GaussianDiffusion.p_mean_variance`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`p_mean_variance(self, x, t, x_self_cond=None, **kwargs)`
- **规范定义名**：`ai4e_contrib.ability.inference.wdno.diffusion.GaussianDiffusion.p_mean_variance`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.inference.wdno.diffusion import GaussianDiffusion
```

```text
p_mean_variance(self, x, t, x_self_cond=None, **kwargs)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `t` | `未标注` | `必填` |
| `x_self_cond` | `未标注` | `None` |
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
from ai4e_contrib.ability.inference.wdno.diffusion import GaussianDiffusion

print(signature(GaussianDiffusion.p_mean_variance))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.wdno.diffusion`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/wdno/diffusion.py:216`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.wdno.diffusion')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-wdno-diffusion-gaussiandiffusion-p-sample"></a>
## `ai4e_contrib.ability.inference.wdno.diffusion.GaussianDiffusion.p_sample`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`p_sample(self, x, t: int, x_self_cond=None, **kwargs)`
- **规范定义名**：`ai4e_contrib.ability.inference.wdno.diffusion.GaussianDiffusion.p_sample`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.inference.wdno.diffusion import GaussianDiffusion
```

```text
p_sample(self, x, t: int, x_self_cond=None, **kwargs)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `t` | `int` | `必填` |
| `x_self_cond` | `未标注` | `None` |
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
from ai4e_contrib.ability.inference.wdno.diffusion import GaussianDiffusion

print(signature(GaussianDiffusion.p_sample))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.wdno.diffusion`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/wdno/diffusion.py:226`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.wdno.diffusion')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-wdno-diffusion-gaussiandiffusion-p-sample-loop"></a>
## `ai4e_contrib.ability.inference.wdno.diffusion.GaussianDiffusion.p_sample_loop`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`p_sample_loop(self, shape, **kwargs)`
- **规范定义名**：`ai4e_contrib.ability.inference.wdno.diffusion.GaussianDiffusion.p_sample_loop`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.inference.wdno.diffusion import GaussianDiffusion
```

```text
p_sample_loop(self, shape, **kwargs)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `shape` | `未标注` | `必填` |
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
from ai4e_contrib.ability.inference.wdno.diffusion import GaussianDiffusion

print(signature(GaussianDiffusion.p_sample_loop))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.wdno.diffusion`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/wdno/diffusion.py:283`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.wdno.diffusion')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-wdno-diffusion-gaussiandiffusion-predict-noise-from-start"></a>
## `ai4e_contrib.ability.inference.wdno.diffusion.GaussianDiffusion.predict_noise_from_start`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`predict_noise_from_start(self, x_t, t, x0)`
- **规范定义名**：`ai4e_contrib.ability.inference.wdno.diffusion.GaussianDiffusion.predict_noise_from_start`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.inference.wdno.diffusion import GaussianDiffusion
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
from ai4e_contrib.ability.inference.wdno.diffusion import GaussianDiffusion

print(signature(GaussianDiffusion.predict_noise_from_start))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.wdno.diffusion`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/wdno/diffusion.py:152`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.wdno.diffusion')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-wdno-diffusion-gaussiandiffusion-predict-start-from-noise"></a>
## `ai4e_contrib.ability.inference.wdno.diffusion.GaussianDiffusion.predict_start_from_noise`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`predict_start_from_noise(self, x_t, t, noise)`
- **规范定义名**：`ai4e_contrib.ability.inference.wdno.diffusion.GaussianDiffusion.predict_start_from_noise`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.inference.wdno.diffusion import GaussianDiffusion
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
from ai4e_contrib.ability.inference.wdno.diffusion import GaussianDiffusion

print(signature(GaussianDiffusion.predict_start_from_noise))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.wdno.diffusion`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/wdno/diffusion.py:146`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.wdno.diffusion')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-wdno-diffusion-gaussiandiffusion-predict-start-from-v"></a>
## `ai4e_contrib.ability.inference.wdno.diffusion.GaussianDiffusion.predict_start_from_v`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`predict_start_from_v(self, x_t, t, v)`
- **规范定义名**：`ai4e_contrib.ability.inference.wdno.diffusion.GaussianDiffusion.predict_start_from_v`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.inference.wdno.diffusion import GaussianDiffusion
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
from ai4e_contrib.ability.inference.wdno.diffusion import GaussianDiffusion

print(signature(GaussianDiffusion.predict_start_from_v))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.wdno.diffusion`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/wdno/diffusion.py:164`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.wdno.diffusion')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-wdno-diffusion-gaussiandiffusion-predict-v"></a>
## `ai4e_contrib.ability.inference.wdno.diffusion.GaussianDiffusion.predict_v`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`predict_v(self, x_start, t, noise)`
- **规范定义名**：`ai4e_contrib.ability.inference.wdno.diffusion.GaussianDiffusion.predict_v`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.inference.wdno.diffusion import GaussianDiffusion
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
from ai4e_contrib.ability.inference.wdno.diffusion import GaussianDiffusion

print(signature(GaussianDiffusion.predict_v))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.wdno.diffusion`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/wdno/diffusion.py:158`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.wdno.diffusion')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-wdno-diffusion-gaussiandiffusion-q-posterior"></a>
## `ai4e_contrib.ability.inference.wdno.diffusion.GaussianDiffusion.q_posterior`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`q_posterior(self, x_start, x_t, t)`
- **规范定义名**：`ai4e_contrib.ability.inference.wdno.diffusion.GaussianDiffusion.q_posterior`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.inference.wdno.diffusion import GaussianDiffusion
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
from ai4e_contrib.ability.inference.wdno.diffusion import GaussianDiffusion

print(signature(GaussianDiffusion.q_posterior))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.wdno.diffusion`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/wdno/diffusion.py:170`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.wdno.diffusion')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-wdno-diffusion-gaussiandiffusion-q-sample"></a>
## `ai4e_contrib.ability.inference.wdno.diffusion.GaussianDiffusion.q_sample`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`q_sample(self, x_start, t, noise=None)`
- **规范定义名**：`ai4e_contrib.ability.inference.wdno.diffusion.GaussianDiffusion.q_sample`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.inference.wdno.diffusion import GaussianDiffusion
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
from ai4e_contrib.ability.inference.wdno.diffusion import GaussianDiffusion

print(signature(GaussianDiffusion.q_sample))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.wdno.diffusion`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/wdno/diffusion.py:492`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.wdno.diffusion')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-wdno-diffusion-gaussiandiffusion-sample"></a>
## `ai4e_contrib.ability.inference.wdno.diffusion.GaussianDiffusion.sample`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`sample(self, batch_size=16, **kwargs)`
- **规范定义名**：`ai4e_contrib.ability.inference.wdno.diffusion.GaussianDiffusion.sample`

### 用途

Kwargs:
    nablaJ: 
        a gradient function returning nablaJ for diffusion guidance. 
        Can use the function get_nablaJ to construct the gradient function.
    J_scheduler: 
        Optional callable, scheduler for J, returns stepsize given t
    proj_guidance:
        Optional callable, postprocess guidance for better diffusion. 
        E.g., project nabla_J to the orthogonal direction of epsilon_theta
    u_init:
        Optional, torch.Tensor of size (batch, Nx). u at time = 0, applies when self.is_condition_u0 == True

### 导入与签名

```python
from ai4e_contrib.ability.inference.wdno.diffusion import GaussianDiffusion
```

```text
sample(self, batch_size=16, **kwargs)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `batch_size` | `未标注` | `16` |
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
from ai4e_contrib.ability.inference.wdno.diffusion import GaussianDiffusion

print(signature(GaussianDiffusion.sample))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `extension.pcno`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `recipe_extensions.geotransolver`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.physical_visualization`, `recipe_extensions.research_state`, `recipe_extensions.wdno`

### 源码位置

- 模块：`ai4e_contrib.ability.inference.wdno.diffusion`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/wdno/diffusion.py:433`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.wdno.diffusion')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-inference-wdno-diffusion-gaussiandiffusion-set-condition"></a>
## `ai4e_contrib.ability.inference.wdno.diffusion.GaussianDiffusion.set_condition`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`set_condition(self, img, u: torch.Tensor, shape, condition_type)`
- **规范定义名**：`ai4e_contrib.ability.inference.wdno.diffusion.GaussianDiffusion.set_condition`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.inference.wdno.diffusion import GaussianDiffusion
```

```text
set_condition(self, img, u: torch.Tensor, shape, condition_type)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `img` | `未标注` | `必填` |
| `u` | `torch.Tensor` | `必填` |
| `shape` | `未标注` | `必填` |
| `condition_type` | `未标注` | `必填` |

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
from ai4e_contrib.ability.inference.wdno.diffusion import GaussianDiffusion

print(signature(GaussianDiffusion.set_condition))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.inference.wdno.diffusion`
- 仓库相对路径：`packages/ai4e-contrib/ability/inference/wdno/diffusion.py:249`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.inference.wdno.diffusion')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
