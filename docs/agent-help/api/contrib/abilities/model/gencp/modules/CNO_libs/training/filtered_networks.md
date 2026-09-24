<!-- dojo-help: {"domain": "ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks", "topic_id": "module:ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks"} -->
# `ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-training-filtered-networks-lrelu"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks.LReLu`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`LReLu(in_channels, out_channels, in_size, out_size, in_sampling_rate, out_sampling_rate, in_cutoff, out_cutoff, in_half_width, out_half_width, filter_size=6, lrelu_upsampling=2, is_critically_sampled=False, use_radial_filters=False)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks.LReLu`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks import LReLu
```

```text
LReLu(in_channels, out_channels, in_size, out_size, in_sampling_rate, out_sampling_rate, in_cutoff, out_cutoff, in_half_width, out_half_width, filter_size=6, lrelu_upsampling=2, is_critically_sampled=False, use_radial_filters=False)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `in_channels` | `未标注` | `必填` |
| `out_channels` | `未标注` | `必填` |
| `in_size` | `未标注` | `必填` |
| `out_size` | `未标注` | `必填` |
| `in_sampling_rate` | `未标注` | `必填` |
| `out_sampling_rate` | `未标注` | `必填` |
| `in_cutoff` | `未标注` | `必填` |
| `out_cutoff` | `未标注` | `必填` |
| `in_half_width` | `未标注` | `必填` |
| `out_half_width` | `未标注` | `必填` |
| `filter_size` | `未标注` | `6` |
| `lrelu_upsampling` | `未标注` | `2` |
| `is_critically_sampled` | `未标注` | `False` |
| `use_radial_filters` | `未标注` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`LReLu`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks import LReLu

print(signature(LReLu))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/training/filtered_networks.py:320`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-training-filtered-networks-lrelu-design-lowpass-filter"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks.LReLu.design_lowpass_filter`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`design_lowpass_filter(numtaps, cutoff, width, fs, radial=False)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks.LReLu.design_lowpass_filter`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks import LReLu
```

```text
design_lowpass_filter(numtaps, cutoff, width, fs, radial=False)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `numtaps` | `未标注` | `必填` |
| `cutoff` | `未标注` | `必填` |
| `width` | `未标注` | `必填` |
| `fs` | `未标注` | `必填` |
| `radial` | `未标注` | `False` |

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
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks import LReLu

print(signature(LReLu.design_lowpass_filter))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/training/filtered_networks.py:403`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-training-filtered-networks-lrelu-extra-repr"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks.LReLu.extra_repr`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`extra_repr(self)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks.LReLu.extra_repr`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks import LReLu
```

```text
extra_repr(self)
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
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks import LReLu

print(signature(LReLu.extra_repr))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/training/filtered_networks.py:425`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-training-filtered-networks-lrelu-forward"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks.LReLu.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x, noise_mode='random', force_fp32=False, update_emas=False)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks.LReLu.forward`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks import LReLu
```

```text
forward(self, x, noise_mode='random', force_fp32=False, update_emas=False)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `noise_mode` | `未标注` | `'random'` |
| `force_fp32` | `未标注` | `False` |
| `update_emas` | `未标注` | `False` |

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
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks import LReLu

print(signature(LReLu.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/training/filtered_networks.py:386`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-training-filtered-networks-lrelu-standard"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks.LReLu_standard`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`LReLu_standard(in_channels, out_channels, in_size, out_size, in_sampling_rate, out_sampling_rate)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks.LReLu_standard`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks import LReLu_standard
```

```text
LReLu_standard(in_channels, out_channels, in_size, out_size, in_sampling_rate, out_sampling_rate)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `in_channels` | `未标注` | `必填` |
| `out_channels` | `未标注` | `必填` |
| `in_size` | `未标注` | `必填` |
| `out_size` | `未标注` | `必填` |
| `in_sampling_rate` | `未标注` | `必填` |
| `out_sampling_rate` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`LReLu_standard`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks import LReLu_standard

print(signature(LReLu_standard))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/training/filtered_networks.py:438`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-training-filtered-networks-lrelu-standard-forward"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks.LReLu_standard.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks.LReLu_standard.forward`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks import LReLu_standard
```

```text
forward(self, x)
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
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks import LReLu_standard

print(signature(LReLu_standard.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/training/filtered_networks.py:462`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-training-filtered-networks-lrelu-torch"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks.LReLu_torch`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`LReLu_torch(in_channels, out_channels, in_size, out_size, in_sampling_rate, out_sampling_rate)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks.LReLu_torch`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks import LReLu_torch
```

```text
LReLu_torch(in_channels, out_channels, in_size, out_size, in_sampling_rate, out_sampling_rate)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `in_channels` | `未标注` | `必填` |
| `out_channels` | `未标注` | `必填` |
| `in_size` | `未标注` | `必填` |
| `out_size` | `未标注` | `必填` |
| `in_sampling_rate` | `未标注` | `必填` |
| `out_sampling_rate` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`LReLu_torch`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks import LReLu_torch

print(signature(LReLu_torch))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/training/filtered_networks.py:471`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-training-filtered-networks-lrelu-torch-forward"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks.LReLu_torch.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks.LReLu_torch.forward`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks import LReLu_torch
```

```text
forward(self, x)
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
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks import LReLu_torch

print(signature(LReLu_torch.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/training/filtered_networks.py:500`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-training-filtered-networks-radialconv2d"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks.RadialConv2d`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`RadialConv2d(in_channels, out_channels, kernel_size, stride, padding)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks.RadialConv2d`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks import RadialConv2d
```

```text
RadialConv2d(in_channels, out_channels, kernel_size, stride, padding)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `in_channels` | `未标注` | `必填` |
| `out_channels` | `未标注` | `必填` |
| `kernel_size` | `未标注` | `必填` |
| `stride` | `未标注` | `必填` |
| `padding` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`RadialConv2d`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks import RadialConv2d

print(signature(RadialConv2d))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/training/filtered_networks.py:133`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-training-filtered-networks-radialconv2d-forward"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks.RadialConv2d.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks.RadialConv2d.forward`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks import RadialConv2d
```

```text
forward(self, x)
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
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks import RadialConv2d

print(signature(RadialConv2d.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/training/filtered_networks.py:158`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-training-filtered-networks-radialconv2d-init-xavier"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks.RadialConv2d.init_xavier`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`init_xavier(self)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks.RadialConv2d.init_xavier`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks import RadialConv2d
```

```text
init_xavier(self)
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
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks import RadialConv2d

print(signature(RadialConv2d.init_xavier))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/training/filtered_networks.py:164`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-training-filtered-networks-synthesislayer"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks.SynthesisLayer`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`SynthesisLayer(is_critically_sampled, in_channels, out_channels, in_size, out_size, in_sampling_rate, out_sampling_rate, in_cutoff, out_cutoff, in_half_width, out_half_width, conv_kernel=3, filter_size=6, lrelu_upsampling=2, use_radial_filters=False)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks.SynthesisLayer`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks import SynthesisLayer
```

```text
SynthesisLayer(is_critically_sampled, in_channels, out_channels, in_size, out_size, in_sampling_rate, out_sampling_rate, in_cutoff, out_cutoff, in_half_width, out_half_width, conv_kernel=3, filter_size=6, lrelu_upsampling=2, use_radial_filters=False)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `is_critically_sampled` | `未标注` | `必填` |
| `in_channels` | `未标注` | `必填` |
| `out_channels` | `未标注` | `必填` |
| `in_size` | `未标注` | `必填` |
| `out_size` | `未标注` | `必填` |
| `in_sampling_rate` | `未标注` | `必填` |
| `out_sampling_rate` | `未标注` | `必填` |
| `in_cutoff` | `未标注` | `必填` |
| `out_cutoff` | `未标注` | `必填` |
| `in_half_width` | `未标注` | `必填` |
| `out_half_width` | `未标注` | `必填` |
| `conv_kernel` | `未标注` | `3` |
| `filter_size` | `未标注` | `6` |
| `lrelu_upsampling` | `未标注` | `2` |
| `use_radial_filters` | `未标注` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`SynthesisLayer`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks import SynthesisLayer

print(signature(SynthesisLayer))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/training/filtered_networks.py:182`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-training-filtered-networks-synthesislayer-design-lowpass-filter"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks.SynthesisLayer.design_lowpass_filter`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`design_lowpass_filter(numtaps, cutoff, width, fs, radial=False)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks.SynthesisLayer.design_lowpass_filter`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks import SynthesisLayer
```

```text
design_lowpass_filter(numtaps, cutoff, width, fs, radial=False)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `numtaps` | `未标注` | `必填` |
| `cutoff` | `未标注` | `必填` |
| `width` | `未标注` | `必填` |
| `fs` | `未标注` | `必填` |
| `radial` | `未标注` | `False` |

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
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks import SynthesisLayer

print(signature(SynthesisLayer.design_lowpass_filter))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/training/filtered_networks.py:283`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-training-filtered-networks-synthesislayer-extra-repr"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks.SynthesisLayer.extra_repr`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`extra_repr(self)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks.SynthesisLayer.extra_repr`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks import SynthesisLayer
```

```text
extra_repr(self)
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
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks import SynthesisLayer

print(signature(SynthesisLayer.extra_repr))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/training/filtered_networks.py:305`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-training-filtered-networks-synthesislayer-forward"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks.SynthesisLayer.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x, noise_mode='random', force_fp32=False, update_emas=False)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks.SynthesisLayer.forward`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks import SynthesisLayer
```

```text
forward(self, x, noise_mode='random', force_fp32=False, update_emas=False)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `noise_mode` | `未标注` | `'random'` |
| `force_fp32` | `未标注` | `False` |
| `update_emas` | `未标注` | `False` |

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
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks import SynthesisLayer

print(signature(SynthesisLayer.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/training/filtered_networks.py:264`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.training.filtered_networks')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
