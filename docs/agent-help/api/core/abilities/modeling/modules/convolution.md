<!-- dojo-help: {"domain": "ai4e_core.abilities.modeling.modules.convolution", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.modeling.modules.convolution 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.modeling.modules.convolution", "topic_id": "module:ai4e_core.abilities.modeling.modules.convolution"} -->
# `ai4e_core.abilities.modeling.modules.convolution` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-modeling-modules-convolution-convblock"></a>
## `ai4e_core.abilities.modeling.modules.convolution.ConvBlock`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`ConvBlock(in_channels: int, out_channels: int, *, spatial_dim: int, kernel_size: int=3, stride: int=1, normalization: str='none', activation: str='gelu')`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.convolution.ConvBlock`

### 用途

卷积后归一化再激活；奇数卷积核采用对称零填充。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.convolution import ConvBlock
```

```text
ConvBlock(in_channels: int, out_channels: int, *, spatial_dim: int, kernel_size: int=3, stride: int=1, normalization: str='none', activation: str='gelu')
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `in_channels` | `int` | `必填` |
| `out_channels` | `int` | `必填` |
| `spatial_dim` | `int` | `必填关键字参数` |
| `kernel_size` | `int` | `3` |
| `stride` | `int` | `1` |
| `normalization` | `str` | `'none'` |
| `activation` | `str` | `'gelu'` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`ConvBlock`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.convolution import ConvBlock

print(signature(ConvBlock))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.convolution`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/convolution.py:6`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.convolution')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-convolution-convblock-forward"></a>
## `ai4e_core.abilities.modeling.modules.convolution.ConvBlock.forward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, value: Tensor) -> Tensor`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.convolution.ConvBlock.forward`

### 用途

接收[B,C,*空间]浮点张量，返回通道在前的特征。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.convolution import ConvBlock
```

```text
forward(self, value: Tensor) -> Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `value` | `Tensor` | `必填` |

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
from ai4e_core.abilities.modeling.modules.convolution import ConvBlock

print(signature(ConvBlock.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.convolution`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/convolution.py:46`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.convolution')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-convolution-convblock2d"></a>
## `ai4e_core.abilities.modeling.modules.convolution.ConvBlock2d`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`ConvBlock2d(in_channels: int, out_channels: int, **kwargs)`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.convolution.ConvBlock2d`

### 用途

二维卷积特征块；输入[B,C,H,W]。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.convolution import ConvBlock2d
```

```text
ConvBlock2d(in_channels: int, out_channels: int, **kwargs)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `in_channels` | `int` | `必填` |
| `out_channels` | `int` | `必填` |
| `**kwargs` | `未标注` | `可变关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`ConvBlock2d`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.convolution import ConvBlock2d

print(signature(ConvBlock2d))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.convolution`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/convolution.py:55`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.convolution')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-convolution-convblock3d"></a>
## `ai4e_core.abilities.modeling.modules.convolution.ConvBlock3d`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`ConvBlock3d(in_channels: int, out_channels: int, **kwargs)`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.convolution.ConvBlock3d`

### 用途

三维卷积特征块；输入[B,C,X,Y,Z]。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.convolution import ConvBlock3d
```

```text
ConvBlock3d(in_channels: int, out_channels: int, **kwargs)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `in_channels` | `int` | `必填` |
| `out_channels` | `int` | `必填` |
| `**kwargs` | `未标注` | `可变关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`ConvBlock3d`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.convolution import ConvBlock3d

print(signature(ConvBlock3d))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.convolution`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/convolution.py:62`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.convolution')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
