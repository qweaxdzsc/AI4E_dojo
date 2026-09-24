<!-- dojo-help: {"domain": "ai4e_core.abilities.modeling.models.deeponet", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.modeling.models.deeponet 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.modeling.models.deeponet", "topic_id": "module:ai4e_core.abilities.modeling.models.deeponet"} -->
# `ai4e_core.abilities.modeling.models.deeponet` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-modeling-models-deeponet-deeponet"></a>
## `ai4e_core.abilities.modeling.models.deeponet.DeepONet`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`DeepONet(sensor_features: int, query_dim: int, latent_dim: int, out_channels: int=1, multi_output: str | None=None, *, branch_hidden: tuple[int, ...]=(64, 64), trunk_hidden: tuple[int, ...]=(64, 64), activation: str='tanh', trunk_final_activation: str | None='tanh', branch: nn.Module | None=None, trunk: nn.Module | None=None, readout: nn.Module | None=None)`
- **规范定义名**：`ai4e_core.abilities.modeling.models.deeponet.DeepONet`

### 用途

分支编码固定传感器，主干编码查询，末层激活由主干明确提供。

自定义 branch/trunk/readout 均正常注册；自定义主干自行负责末层激活。
传感器选择、排列和缺失支撑属于调用方，本类不缓存分支或切断梯度。

### 导入与签名

```python
from ai4e_core.abilities.modeling.models.deeponet import DeepONet
```

```text
DeepONet(sensor_features: int, query_dim: int, latent_dim: int, out_channels: int=1, multi_output: str | None=None, *, branch_hidden: tuple[int, ...]=(64, 64), trunk_hidden: tuple[int, ...]=(64, 64), activation: str='tanh', trunk_final_activation: str | None='tanh', branch: nn.Module | None=None, trunk: nn.Module | None=None, readout: nn.Module | None=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `sensor_features` | `int` | `必填` |
| `query_dim` | `int` | `必填` |
| `latent_dim` | `int` | `必填` |
| `out_channels` | `int` | `1` |
| `multi_output` | `str | None` | `None` |
| `branch_hidden` | `tuple[int, ...]` | `(64, 64)` |
| `trunk_hidden` | `tuple[int, ...]` | `(64, 64)` |
| `activation` | `str` | `'tanh'` |
| `trunk_final_activation` | `str | None` | `'tanh'` |
| `branch` | `nn.Module | None` | `None` |
| `trunk` | `nn.Module | None` | `None` |
| `readout` | `nn.Module | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`DeepONet`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`TypeError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.models.deeponet import DeepONet

print(signature(DeepONet))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.models.deeponet`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/models/deeponet.py:13`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.models.deeponet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-models-deeponet-deeponet-forward"></a>
## `ai4e_core.abilities.modeling.models.deeponet.DeepONet.forward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, branch_input: Tensor, queries: Tensor, *, query_layout: str='shared') -> Tensor`
- **规范定义名**：`ai4e_core.abilities.modeling.models.deeponet.DeepONet.forward`

### 用途

返回 [B,Q,O]；输入为 [B,F] 与 [Q,D] 或 [B,Q,D]。

可改变查询集合；改变固定传感器含义需重新准备并记录模型配置。

### 导入与签名

```python
from ai4e_core.abilities.modeling.models.deeponet import DeepONet
```

```text
forward(self, branch_input: Tensor, queries: Tensor, *, query_layout: str='shared') -> Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `branch_input` | `Tensor` | `必填` |
| `queries` | `Tensor` | `必填` |
| `query_layout` | `str` | `'shared'` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Tensor`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.models.deeponet import DeepONet

print(signature(DeepONet.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.models.deeponet`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/models/deeponet.py:62`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.models.deeponet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
