<!-- dojo-help: {"domain": "ai4e_core.abilities.modeling.models.fourier_unet3d", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.modeling.models.fourier_unet3d 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.modeling.models.fourier_unet3d", "topic_id": "module:ai4e_core.abilities.modeling.models.fourier_unet3d"} -->
# `ai4e_core.abilities.modeling.models.fourier_unet3d` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-modeling-models-fourier-unet3d-fourierunet3d"></a>
## `ai4e_core.abilities.modeling.models.fourier_unet3d.FourierUNet3d`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`FourierUNet3d(in_channels, out_channels, history=3, horizon=12, width=8, modes=(4, 4, 4), blocks=4, global_dim=0)`
- **规范定义名**：`ai4e_core.abilities.modeling.models.fourier_unet3d.FourierUNet3d`

### 用途

历史 B/H/X/Y/C 到未来 B/T/X/Y/C；时间坐标为预测窗口内相对位置。

### 导入与签名

```python
from ai4e_core.abilities.modeling.models.fourier_unet3d import FourierUNet3d
```

```text
FourierUNet3d(in_channels, out_channels, history=3, horizon=12, width=8, modes=(4, 4, 4), blocks=4, global_dim=0)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `in_channels` | `未标注` | `必填` |
| `out_channels` | `未标注` | `必填` |
| `history` | `未标注` | `3` |
| `horizon` | `未标注` | `12` |
| `width` | `未标注` | `8` |
| `modes` | `未标注` | `(4, 4, 4)` |
| `blocks` | `未标注` | `4` |
| `global_dim` | `未标注` | `0` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`FourierUNet3d`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.models.fourier_unet3d import FourierUNet3d

print(signature(FourierUNet3d))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.models.fourier_unet3d`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/models/fourier_unet3d.py:70`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.models.fourier_unet3d')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-models-fourier-unet3d-fourierunet3d-forward"></a>
## `ai4e_core.abilities.modeling.models.fourier_unet3d.FourierUNet3d.forward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, history, global_parameters=None)`
- **规范定义名**：`ai4e_core.abilities.modeling.models.fourier_unet3d.FourierUNet3d.forward`

### 用途

不接收目标或未来几何；可选全局参数须由调用者显式给定。

### 导入与签名

```python
from ai4e_core.abilities.modeling.models.fourier_unet3d import FourierUNet3d
```

```text
forward(self, history, global_parameters=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `history` | `未标注` | `必填` |
| `global_parameters` | `未标注` | `None` |

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
from ai4e_core.abilities.modeling.models.fourier_unet3d import FourierUNet3d

print(signature(FourierUNet3d.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.models.fourier_unet3d`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/models/fourier_unet3d.py:103`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.models.fourier_unet3d')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-models-fourier-unet3d-spatialunet2d"></a>
## `ai4e_core.abilities.modeling.models.fourier_unet3d.SpatialUNet2d`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`SpatialUNet2d(width)`
- **规范定义名**：`ai4e_core.abilities.modeling.models.fourier_unet3d.SpatialUNet2d`

### 用途

二维空间局部特征；时间片共享权重，不沿时间池化。

### 导入与签名

```python
from ai4e_core.abilities.modeling.models.fourier_unet3d import SpatialUNet2d
```

```text
SpatialUNet2d(width)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `width` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`SpatialUNet2d`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.models.fourier_unet3d import SpatialUNet2d

print(signature(SpatialUNet2d))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.models.fourier_unet3d`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/models/fourier_unet3d.py:43`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.models.fourier_unet3d')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-models-fourier-unet3d-spatialunet2d-forward"></a>
## `ai4e_core.abilities.modeling.models.fourier_unet3d.SpatialUNet2d.forward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, value)`
- **规范定义名**：`ai4e_core.abilities.modeling.models.fourier_unet3d.SpatialUNet2d.forward`

### 用途

计算保留原空间分辨率的局部特征。

### 导入与签名

```python
from ai4e_core.abilities.modeling.models.fourier_unet3d import SpatialUNet2d
```

```text
forward(self, value)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `value` | `未标注` | `必填` |

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
from ai4e_core.abilities.modeling.models.fourier_unet3d import SpatialUNet2d

print(signature(SpatialUNet2d.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.models.fourier_unet3d`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/models/fourier_unet3d.py:62`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.models.fourier_unet3d')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-models-fourier-unet3d-spectralconv3d"></a>
## `ai4e_core.abilities.modeling.models.fourier_unet3d.SpectralConv3d`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`SpectralConv3d(width, modes)`
- **规范定义名**：`ai4e_core.abilities.modeling.models.fourier_unet3d.SpectralConv3d`

### 用途

对 X/Y/T 计算实数 FFT 的四象限低频线性映射。

### 导入与签名

```python
from ai4e_core.abilities.modeling.models.fourier_unet3d import SpectralConv3d
```

```text
SpectralConv3d(width, modes)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `width` | `未标注` | `必填` |
| `modes` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`SpectralConv3d`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.models.fourier_unet3d import SpectralConv3d

print(signature(SpectralConv3d))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.models.fourier_unet3d`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/models/fourier_unet3d.py:14`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.models.fourier_unet3d')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-models-fourier-unet3d-spectralconv3d-forward"></a>
## `ai4e_core.abilities.modeling.models.fourier_unet3d.SpectralConv3d.forward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, value)`
- **规范定义名**：`ai4e_core.abilities.modeling.models.fourier_unet3d.SpectralConv3d.forward`

### 用途

将 B/C/X/Y/T 张量映射到相同形状。

### 导入与签名

```python
from ai4e_core.abilities.modeling.models.fourier_unet3d import SpectralConv3d
```

```text
forward(self, value)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `value` | `未标注` | `必填` |

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
from ai4e_core.abilities.modeling.models.fourier_unet3d import SpectralConv3d

print(signature(SpectralConv3d.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.models.fourier_unet3d`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/models/fourier_unet3d.py:22`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.models.fourier_unet3d')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
