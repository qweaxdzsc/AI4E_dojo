<!-- dojo-help: {"domain": "ai4e_contrib.ability.model.gencp.cno", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.model.gencp.cno 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.model.gencp.cno", "topic_id": "module:ai4e_contrib.ability.model.gencp.cno"} -->
# `ai4e_contrib.ability.model.gencp.cno` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-model-gencp-cno-cno3d"></a>
## `ai4e_contrib.ability.model.gencp.cno.CNO3d`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`CNO3d(in_dim, in_size, N_layers, N_res=1, N_res_neck=6, channel_multiplier=32, conv_kernel=3, cutoff_den=2.0001, filter_size=6, lrelu_upsampling=2, half_width_mult=0.8, radial=False, batch_norm=True, out_dim=1, out_dim_mult=1, out_size=1, expand_input=False, latent_lift_proj_dim=64, add_inv=True, activation='LeakyReLU', dataset_name='turek_hron_data', x0_is_use_noise=True, stage='fuel', time_dim=128)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.cno.CNO3d`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.cno import CNO3d
```

```text
CNO3d(in_dim, in_size, N_layers, N_res=1, N_res_neck=6, channel_multiplier=32, conv_kernel=3, cutoff_den=2.0001, filter_size=6, lrelu_upsampling=2, half_width_mult=0.8, radial=False, batch_norm=True, out_dim=1, out_dim_mult=1, out_size=1, expand_input=False, latent_lift_proj_dim=64, add_inv=True, activation='LeakyReLU', dataset_name='turek_hron_data', x0_is_use_noise=True, stage='fuel', time_dim=128)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `in_dim` | `未标注` | `必填` |
| `in_size` | `未标注` | `必填` |
| `N_layers` | `未标注` | `必填` |
| `N_res` | `未标注` | `1` |
| `N_res_neck` | `未标注` | `6` |
| `channel_multiplier` | `未标注` | `32` |
| `conv_kernel` | `未标注` | `3` |
| `cutoff_den` | `未标注` | `2.0001` |
| `filter_size` | `未标注` | `6` |
| `lrelu_upsampling` | `未标注` | `2` |
| `half_width_mult` | `未标注` | `0.8` |
| `radial` | `未标注` | `False` |
| `batch_norm` | `未标注` | `True` |
| `out_dim` | `未标注` | `1` |
| `out_dim_mult` | `未标注` | `1` |
| `out_size` | `未标注` | `1` |
| `expand_input` | `未标注` | `False` |
| `latent_lift_proj_dim` | `未标注` | `64` |
| `add_inv` | `未标注` | `True` |
| `activation` | `未标注` | `'LeakyReLU'` |
| `dataset_name` | `未标注` | `'turek_hron_data'` |
| `x0_is_use_noise` | `未标注` | `True` |
| `stage` | `未标注` | `'fuel'` |
| `time_dim` | `未标注` | `128` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`CNO3d`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.cno import CNO3d

print(signature(CNO3d))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.cno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/cno.py:308`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.cno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-cno-cno3d-forward"></a>
## `ai4e_contrib.ability.model.gencp.cno.CNO3d.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x, t, x0_or_cond=None, cond=None, **kwargs)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.cno.CNO3d.forward`

### 用途

Compatible forward for both FSI and NTcouple.

- FSI:        forward(xt, t, x0, cond)   (or keyword x0=..., cond=...)
- NTcouple:   forward(x_joint, t, cond)  (cond can be passed as 3rd positional or as cond=...)

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.cno import CNO3d
```

```text
forward(self, x, t, x0_or_cond=None, cond=None, **kwargs)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `t` | `未标注` | `必填` |
| `x0_or_cond` | `未标注` | `None` |
| `cond` | `未标注` | `None` |
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
from ai4e_contrib.ability.model.gencp.cno import CNO3d

print(signature(CNO3d.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.cno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/cno.py:609`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.cno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-cno-cnoblock3d"></a>
## `ai4e_contrib.ability.model.gencp.cno.CNOBlock3d`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`CNOBlock3d(in_channels, out_channels, in_size, out_size, cutoff_den=2.0001, conv_kernel=3, filter_size=6, lrelu_upsampling=2, half_width_mult=0.8, radial=False, batch_norm=True, activation='cno_lrelu', time_dim=None)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.cno.CNOBlock3d`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.cno import CNOBlock3d
```

```text
CNOBlock3d(in_channels, out_channels, in_size, out_size, cutoff_den=2.0001, conv_kernel=3, filter_size=6, lrelu_upsampling=2, half_width_mult=0.8, radial=False, batch_norm=True, activation='cno_lrelu', time_dim=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `in_channels` | `未标注` | `必填` |
| `out_channels` | `未标注` | `必填` |
| `in_size` | `未标注` | `必填` |
| `out_size` | `未标注` | `必填` |
| `cutoff_den` | `未标注` | `2.0001` |
| `conv_kernel` | `未标注` | `3` |
| `filter_size` | `未标注` | `6` |
| `lrelu_upsampling` | `未标注` | `2` |
| `half_width_mult` | `未标注` | `0.8` |
| `radial` | `未标注` | `False` |
| `batch_norm` | `未标注` | `True` |
| `activation` | `未标注` | `'cno_lrelu'` |
| `time_dim` | `未标注` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`CNOBlock3d`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.cno import CNOBlock3d

print(signature(CNOBlock3d))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.cno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/cno.py:69`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.cno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-cno-cnoblock3d-forward"></a>
## `ai4e_contrib.ability.model.gencp.cno.CNOBlock3d.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x, time_emb=None)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.cno.CNOBlock3d.forward`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.cno import CNOBlock3d
```

```text
forward(self, x, time_emb=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `time_emb` | `未标注` | `None` |

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
from ai4e_contrib.ability.model.gencp.cno import CNOBlock3d

print(signature(CNOBlock3d.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.cno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/cno.py:142`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.cno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-cno-film"></a>
## `ai4e_contrib.ability.model.gencp.cno.FiLM`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`FiLM(time_dim, channels)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.cno.FiLM`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.cno import FiLM
```

```text
FiLM(time_dim, channels)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `time_dim` | `未标注` | `必填` |
| `channels` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`FiLM`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.cno import FiLM

print(signature(FiLM))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.cno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/cno.py:42`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.cno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-cno-film-forward"></a>
## `ai4e_contrib.ability.model.gencp.cno.FiLM.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x, time_emb)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.cno.FiLM.forward`

### 用途

Modulate features using time embedding
Args:
    x: [B, C, T, H, W] feature map
    time_emb: [B, time_dim] time embedding
Returns:
    Modulated feature map

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.cno import FiLM
```

```text
forward(self, x, time_emb)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `time_emb` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.gencp.cno import FiLM

print(signature(FiLM.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.cno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/cno.py:47`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.cno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-cno-liftprojectblock3d"></a>
## `ai4e_contrib.ability.model.gencp.cno.LiftProjectBlock3d`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`LiftProjectBlock3d(in_channels, out_channels, in_size, out_size, latent_dim=64, cutoff_den=2.0001, conv_kernel=3, filter_size=6, lrelu_upsampling=2, half_width_mult=0.8, radial=False, batch_norm=True, activation='cno_lrelu', time_dim=None)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.cno.LiftProjectBlock3d`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.cno import LiftProjectBlock3d
```

```text
LiftProjectBlock3d(in_channels, out_channels, in_size, out_size, latent_dim=64, cutoff_den=2.0001, conv_kernel=3, filter_size=6, lrelu_upsampling=2, half_width_mult=0.8, radial=False, batch_norm=True, activation='cno_lrelu', time_dim=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `in_channels` | `未标注` | `必填` |
| `out_channels` | `未标注` | `必填` |
| `in_size` | `未标注` | `必填` |
| `out_size` | `未标注` | `必填` |
| `latent_dim` | `未标注` | `64` |
| `cutoff_den` | `未标注` | `2.0001` |
| `conv_kernel` | `未标注` | `3` |
| `filter_size` | `未标注` | `6` |
| `lrelu_upsampling` | `未标注` | `2` |
| `half_width_mult` | `未标注` | `0.8` |
| `radial` | `未标注` | `False` |
| `batch_norm` | `未标注` | `True` |
| `activation` | `未标注` | `'cno_lrelu'` |
| `time_dim` | `未标注` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`LiftProjectBlock3d`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.cno import LiftProjectBlock3d

print(signature(LiftProjectBlock3d))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.cno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/cno.py:156`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.cno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-cno-liftprojectblock3d-forward"></a>
## `ai4e_contrib.ability.model.gencp.cno.LiftProjectBlock3d.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x, time_emb=None)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.cno.LiftProjectBlock3d.forward`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.cno import LiftProjectBlock3d
```

```text
forward(self, x, time_emb=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `time_emb` | `未标注` | `None` |

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
from ai4e_contrib.ability.model.gencp.cno import LiftProjectBlock3d

print(signature(LiftProjectBlock3d.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.cno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/cno.py:202`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.cno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-cno-residualblock3d"></a>
## `ai4e_contrib.ability.model.gencp.cno.ResidualBlock3d`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`ResidualBlock3d(channels, size, cutoff_den=2.0001, conv_kernel=3, filter_size=6, lrelu_upsampling=2, half_width_mult=0.8, radial=False, batch_norm=True, activation='cno_lrelu', time_dim=None)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.cno.ResidualBlock3d`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.cno import ResidualBlock3d
```

```text
ResidualBlock3d(channels, size, cutoff_den=2.0001, conv_kernel=3, filter_size=6, lrelu_upsampling=2, half_width_mult=0.8, radial=False, batch_norm=True, activation='cno_lrelu', time_dim=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `channels` | `未标注` | `必填` |
| `size` | `未标注` | `必填` |
| `cutoff_den` | `未标注` | `2.0001` |
| `conv_kernel` | `未标注` | `3` |
| `filter_size` | `未标注` | `6` |
| `lrelu_upsampling` | `未标注` | `2` |
| `half_width_mult` | `未标注` | `0.8` |
| `radial` | `未标注` | `False` |
| `batch_norm` | `未标注` | `True` |
| `activation` | `未标注` | `'cno_lrelu'` |
| `time_dim` | `未标注` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`ResidualBlock3d`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.cno import ResidualBlock3d

print(signature(ResidualBlock3d))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.cno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/cno.py:219`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.cno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-cno-residualblock3d-forward"></a>
## `ai4e_contrib.ability.model.gencp.cno.ResidualBlock3d.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x, time_emb=None)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.cno.ResidualBlock3d.forward`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.cno import ResidualBlock3d
```

```text
forward(self, x, time_emb=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `time_emb` | `未标注` | `None` |

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
from ai4e_contrib.ability.model.gencp.cno import ResidualBlock3d

print(signature(ResidualBlock3d.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.cno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/cno.py:288`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.cno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-cno-timeembedding"></a>
## `ai4e_contrib.ability.model.gencp.cno.TimeEmbedding`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`TimeEmbedding(dim)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.cno.TimeEmbedding`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.cno import TimeEmbedding
```

```text
TimeEmbedding(dim)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dim` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`TimeEmbedding`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.cno import TimeEmbedding

print(signature(TimeEmbedding))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.cno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/cno.py:21`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.cno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-cno-timeembedding-forward"></a>
## `ai4e_contrib.ability.model.gencp.cno.TimeEmbedding.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, t)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.cno.TimeEmbedding.forward`

### 用途

Encode timestep t as sinusoidal positional encoding
Args:
    t: [batch_size] timestep
Returns:
    time_emb: [batch_size, dim] time embedding

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.cno import TimeEmbedding
```

```text
forward(self, t)
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
from ai4e_contrib.ability.model.gencp.cno import TimeEmbedding

print(signature(TimeEmbedding.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.cno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/cno.py:26`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.cno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
