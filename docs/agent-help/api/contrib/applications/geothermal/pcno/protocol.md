<!-- dojo-help: {"domain": "ai4e_contrib.application.geothermal.pcno.protocol", "kind": "api", "layer": "contrib.application", "summary": "ai4e_contrib.application.geothermal.pcno.protocol 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.application.geothermal.pcno.protocol", "topic_id": "module:ai4e_contrib.application.geothermal.pcno.protocol"} -->
# `ai4e_contrib.application.geothermal.pcno.protocol` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-application-geothermal-pcno-protocol-modelconfig"></a>
## `ai4e_contrib.application.geothermal.pcno.protocol.ModelConfig`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`class ModelConfig`
- **规范定义名**：`ai4e_contrib.application.geothermal.pcno.protocol.ModelConfig`

### 用途

PCNO 统计量、种子、原始250轮调度与分阶段损失权重：ModelConfig；保留来源算法、参数与权重布局。

### 导入与签名

```python
from ai4e_contrib.application.geothermal.pcno.protocol import ModelConfig
```

```text
class ModelConfig
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`ModelConfig`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.application.geothermal.pcno.protocol import ModelConfig

print(signature(ModelConfig))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.geothermal.pcno.protocol`
- 仓库相对路径：`packages/ai4e-contrib/application/geothermal/pcno/protocol.py:42`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.geothermal.pcno.protocol')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-geothermal-pcno-protocol-modelconfig-decode-inputs"></a>
## `ai4e_contrib.application.geothermal.pcno.protocol.ModelConfig.decode_inputs`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`decode_inputs(input_i, g_i, s)`
- **规范定义名**：`ai4e_contrib.application.geothermal.pcno.protocol.ModelConfig.decode_inputs`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.application.geothermal.pcno.protocol import ModelConfig
```

```text
decode_inputs(input_i, g_i, s)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `input_i` | `未标注` | `必填` |
| `g_i` | `未标注` | `必填` |
| `s` | `未标注` | `必填` |

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
from ai4e_contrib.application.geothermal.pcno.protocol import ModelConfig

print(signature(ModelConfig.decode_inputs))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.geothermal.pcno.protocol`
- 仓库相对路径：`packages/ai4e-contrib/application/geothermal/pcno/protocol.py:115`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.geothermal.pcno.protocol')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-geothermal-pcno-protocol-modelconfig-loss-weights"></a>
## `ai4e_contrib.application.geothermal.pcno.protocol.ModelConfig.loss_weights`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`loss_weights(ep, mse, w, g)`
- **规范定义名**：`ai4e_contrib.application.geothermal.pcno.protocol.ModelConfig.loss_weights`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.application.geothermal.pcno.protocol import ModelConfig
```

```text
loss_weights(ep, mse, w, g)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `ep` | `未标注` | `必填` |
| `mse` | `未标注` | `必填` |
| `w` | `未标注` | `必填` |
| `g` | `未标注` | `必填` |

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
from ai4e_contrib.application.geothermal.pcno.protocol import ModelConfig

print(signature(ModelConfig.loss_weights))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.geothermal.pcno.protocol`
- 仓库相对路径：`packages/ai4e-contrib/application/geothermal/pcno/protocol.py:73`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.geothermal.pcno.protocol')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-geothermal-pcno-protocol-modelconfig-loss-weights-finetune"></a>
## `ai4e_contrib.application.geothermal.pcno.protocol.ModelConfig.loss_weights_finetune`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`loss_weights_finetune()`
- **规范定义名**：`ai4e_contrib.application.geothermal.pcno.protocol.ModelConfig.loss_weights_finetune`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.application.geothermal.pcno.protocol import ModelConfig
```

```text
loss_weights_finetune()
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
from ai4e_contrib.application.geothermal.pcno.protocol import ModelConfig

print(signature(ModelConfig.loss_weights_finetune))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.geothermal.pcno.protocol`
- 仓库相对路径：`packages/ai4e-contrib/application/geothermal/pcno/protocol.py:108`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.geothermal.pcno.protocol')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-geothermal-pcno-protocol-modelconfig-lr-lambda"></a>
## `ai4e_contrib.application.geothermal.pcno.protocol.ModelConfig.lr_lambda`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`lr_lambda(base_lr, warmup_start_lr, warmup_end_lr, lr_mid, lr_min, warmup_steps, plateau_steps, cosine1_steps, cosine2_steps)`
- **规范定义名**：`ai4e_contrib.application.geothermal.pcno.protocol.ModelConfig.lr_lambda`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.application.geothermal.pcno.protocol import ModelConfig
```

```text
lr_lambda(base_lr, warmup_start_lr, warmup_end_lr, lr_mid, lr_min, warmup_steps, plateau_steps, cosine1_steps, cosine2_steps)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `base_lr` | `未标注` | `必填` |
| `warmup_start_lr` | `未标注` | `必填` |
| `warmup_end_lr` | `未标注` | `必填` |
| `lr_mid` | `未标注` | `必填` |
| `lr_min` | `未标注` | `必填` |
| `warmup_steps` | `未标注` | `必填` |
| `plateau_steps` | `未标注` | `必填` |
| `cosine1_steps` | `未标注` | `必填` |
| `cosine2_steps` | `未标注` | `必填` |

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
from ai4e_contrib.application.geothermal.pcno.protocol import ModelConfig

print(signature(ModelConfig.lr_lambda))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.geothermal.pcno.protocol`
- 仓库相对路径：`packages/ai4e-contrib/application/geothermal/pcno/protocol.py:46`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.geothermal.pcno.protocol')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-geothermal-pcno-protocol-modelconfig-scale"></a>
## `ai4e_contrib.application.geothermal.pcno.protocol.ModelConfig.scale`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`scale(base, secondary)`
- **规范定义名**：`ai4e_contrib.application.geothermal.pcno.protocol.ModelConfig.scale`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.application.geothermal.pcno.protocol import ModelConfig
```

```text
scale(base, secondary)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `base` | `未标注` | `必填` |
| `secondary` | `未标注` | `必填` |

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
from ai4e_contrib.application.geothermal.pcno.protocol import ModelConfig

print(signature(ModelConfig.scale))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.geotransolver_aero`

### 源码位置

- 模块：`ai4e_contrib.application.geothermal.pcno.protocol`
- 仓库相对路径：`packages/ai4e-contrib/application/geothermal/pcno/protocol.py:68`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.geothermal.pcno.protocol')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-geothermal-pcno-protocol-trainconfig"></a>
## `ai4e_contrib.application.geothermal.pcno.protocol.TrainConfig`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`class TrainConfig`
- **规范定义名**：`ai4e_contrib.application.geothermal.pcno.protocol.TrainConfig`

### 用途

PCNO 统计量、种子、原始250轮调度与分阶段损失权重：TrainConfig；保留来源算法、参数与权重布局。

### 导入与签名

```python
from ai4e_contrib.application.geothermal.pcno.protocol import TrainConfig
```

```text
class TrainConfig
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`TrainConfig`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.application.geothermal.pcno.protocol import TrainConfig

print(signature(TrainConfig))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.geothermal.pcno.protocol`
- 仓库相对路径：`packages/ai4e-contrib/application/geothermal/pcno/protocol.py:15`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.geothermal.pcno.protocol')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-geothermal-pcno-protocol-trainconfig-set-seed"></a>
## `ai4e_contrib.application.geothermal.pcno.protocol.TrainConfig.set_seed`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`set_seed(seed=7)`
- **规范定义名**：`ai4e_contrib.application.geothermal.pcno.protocol.TrainConfig.set_seed`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.application.geothermal.pcno.protocol import TrainConfig
```

```text
set_seed(seed=7)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `seed` | `未标注` | `7` |

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
from ai4e_contrib.application.geothermal.pcno.protocol import TrainConfig

print(signature(TrainConfig.set_seed))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.geothermal.pcno.protocol`
- 仓库相对路径：`packages/ai4e-contrib/application/geothermal/pcno/protocol.py:19`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.geothermal.pcno.protocol')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-geothermal-pcno-protocol-trainconfig-stats-to-device"></a>
## `ai4e_contrib.application.geothermal.pcno.protocol.TrainConfig.stats_to_device`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`stats_to_device(stats, device)`
- **规范定义名**：`ai4e_contrib.application.geothermal.pcno.protocol.TrainConfig.stats_to_device`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.application.geothermal.pcno.protocol import TrainConfig
```

```text
stats_to_device(stats, device)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `stats` | `未标注` | `必填` |
| `device` | `未标注` | `必填` |

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
from ai4e_contrib.application.geothermal.pcno.protocol import TrainConfig

print(signature(TrainConfig.stats_to_device))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.geothermal.pcno.protocol`
- 仓库相对路径：`packages/ai4e-contrib/application/geothermal/pcno/protocol.py:28`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.geothermal.pcno.protocol')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-geothermal-pcno-protocol-denormalize"></a>
## `ai4e_contrib.application.geothermal.pcno.protocol.denormalize`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`denormalize(tensor, mean, std)`
- **规范定义名**：`ai4e_contrib.application.geothermal.pcno.protocol.denormalize`

### 用途

使用作者冻结统计量还原。

### 导入与签名

```python
from ai4e_contrib.application.geothermal.pcno.protocol import denormalize
```

```text
denormalize(tensor, mean, std)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `tensor` | `未标注` | `必填` |
| `mean` | `未标注` | `必填` |
| `std` | `未标注` | `必填` |

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
from ai4e_contrib.application.geothermal.pcno.protocol import denormalize

print(signature(denormalize))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.geothermal.pcno.protocol`
- 仓库相对路径：`packages/ai4e-contrib/application/geothermal/pcno/protocol.py:11`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.geothermal.pcno.protocol')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
