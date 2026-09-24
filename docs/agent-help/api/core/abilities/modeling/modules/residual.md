<!-- dojo-help: {"domain": "ai4e_core.abilities.modeling.modules.residual", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.modeling.modules.residual 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.modeling.modules.residual", "topic_id": "module:ai4e_core.abilities.modeling.modules.residual"} -->
# `ai4e_core.abilities.modeling.modules.residual` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-modeling-modules-residual-basicresidualblock"></a>
## `ai4e_core.abilities.modeling.modules.residual.BasicResidualBlock`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`BasicResidualBlock(in_channels: int, channels: int, *, spatial_dim: int, stride: int=1)`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.residual.BasicResidualBlock`

### 用途

两次3卷积后加恒等/投影捷径，再执行ReLU。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.residual import BasicResidualBlock
```

```text
BasicResidualBlock(in_channels: int, channels: int, *, spatial_dim: int, stride: int=1)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `in_channels` | `int` | `必填` |
| `channels` | `int` | `必填` |
| `spatial_dim` | `int` | `必填关键字参数` |
| `stride` | `int` | `1` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`BasicResidualBlock`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.residual import BasicResidualBlock

print(signature(BasicResidualBlock))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.residual`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/residual.py:11`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.residual')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-residual-basicresidualblock-forward"></a>
## `ai4e_core.abilities.modeling.modules.residual.BasicResidualBlock.forward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, value: Tensor) -> Tensor`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.residual.BasicResidualBlock.forward`

### 用途

同一输入分别进入主支与捷径，相加后激活。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.residual import BasicResidualBlock
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

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.residual import BasicResidualBlock

print(signature(BasicResidualBlock.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.residual`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/residual.py:41`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.residual')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-residual-basicresidualblock2d"></a>
## `ai4e_core.abilities.modeling.modules.residual.BasicResidualBlock2d`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`BasicResidualBlock2d(in_channels: int, channels: int, *, stride: int=1)`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.residual.BasicResidualBlock2d`

### 用途

二维基本残差块。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.residual import BasicResidualBlock2d
```

```text
BasicResidualBlock2d(in_channels: int, channels: int, *, stride: int=1)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `in_channels` | `int` | `必填` |
| `channels` | `int` | `必填` |
| `stride` | `int` | `1` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`BasicResidualBlock2d`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.residual import BasicResidualBlock2d

print(signature(BasicResidualBlock2d))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.resunet`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.residual`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/residual.py:86`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.residual')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-residual-basicresidualblock3d"></a>
## `ai4e_core.abilities.modeling.modules.residual.BasicResidualBlock3d`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`BasicResidualBlock3d(in_channels: int, channels: int, *, stride: int=1)`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.residual.BasicResidualBlock3d`

### 用途

三维基本残差块。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.residual import BasicResidualBlock3d
```

```text
BasicResidualBlock3d(in_channels: int, channels: int, *, stride: int=1)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `in_channels` | `int` | `必填` |
| `channels` | `int` | `必填` |
| `stride` | `int` | `1` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`BasicResidualBlock3d`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.residual import BasicResidualBlock3d

print(signature(BasicResidualBlock3d))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.resunet`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.residual`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/residual.py:93`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.residual')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-residual-bottleneck"></a>
## `ai4e_core.abilities.modeling.modules.residual.Bottleneck`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`Bottleneck(in_channels: int, channels: int, *, spatial_dim: int, stride: int=1)`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.residual.Bottleneck`

### 用途

1/3/1卷积瓶颈，输出通道为内部宽度四倍。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.residual import Bottleneck
```

```text
Bottleneck(in_channels: int, channels: int, *, spatial_dim: int, stride: int=1)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `in_channels` | `int` | `必填` |
| `channels` | `int` | `必填` |
| `spatial_dim` | `int` | `必填关键字参数` |
| `stride` | `int` | `1` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Bottleneck`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.residual import Bottleneck

print(signature(Bottleneck))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.residual`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/residual.py:46`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.residual')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-residual-bottleneck-forward"></a>
## `ai4e_core.abilities.modeling.modules.residual.Bottleneck.forward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, value: Tensor) -> Tensor`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.residual.Bottleneck.forward`

### 用途

执行主支、捷径和后激活，不重排归一化。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.residual import Bottleneck
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

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.residual import Bottleneck

print(signature(Bottleneck.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.residual`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/residual.py:81`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.residual')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-residual-bottleneck2d"></a>
## `ai4e_core.abilities.modeling.modules.residual.Bottleneck2d`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`Bottleneck2d(in_channels: int, channels: int, *, stride: int=1)`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.residual.Bottleneck2d`

### 用途

二维瓶颈残差块。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.residual import Bottleneck2d
```

```text
Bottleneck2d(in_channels: int, channels: int, *, stride: int=1)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `in_channels` | `int` | `必填` |
| `channels` | `int` | `必填` |
| `stride` | `int` | `1` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Bottleneck2d`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.residual import Bottleneck2d

print(signature(Bottleneck2d))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.residual`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/residual.py:100`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.residual')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-residual-bottleneck3d"></a>
## `ai4e_core.abilities.modeling.modules.residual.Bottleneck3d`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`Bottleneck3d(in_channels: int, channels: int, *, stride: int=1)`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.residual.Bottleneck3d`

### 用途

三维瓶颈残差块。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.residual import Bottleneck3d
```

```text
Bottleneck3d(in_channels: int, channels: int, *, stride: int=1)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `in_channels` | `int` | `必填` |
| `channels` | `int` | `必填` |
| `stride` | `int` | `1` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Bottleneck3d`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.residual import Bottleneck3d

print(signature(Bottleneck3d))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.residual`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/residual.py:107`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.residual')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
