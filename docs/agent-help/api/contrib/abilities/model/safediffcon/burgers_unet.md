<!-- dojo-help: {"domain": "ai4e_contrib.ability.model.safediffcon.burgers_unet", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.model.safediffcon.burgers_unet 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.model.safediffcon.burgers_unet", "topic_id": "module:ai4e_contrib.ability.model.safediffcon.burgers_unet"} -->
# `ai4e_contrib.ability.model.safediffcon.burgers_unet` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-unet-attention"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_unet.Attention`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`Attention(dim, heads=4, dim_head=32, conv_2d=False)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_unet.Attention`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_unet import Attention
```

```text
Attention(dim, heads=4, dim_head=32, conv_2d=False)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dim` | `未标注` | `必填` |
| `heads` | `未标注` | `4` |
| `dim_head` | `未标注` | `32` |
| `conv_2d` | `未标注` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Attention`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.safediffcon.burgers_unet import Attention

print(signature(Attention))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_unet`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_unet.py:225`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_unet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-unet-attention-forward"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_unet.Attention.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_unet.Attention.forward`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_unet import Attention
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
from ai4e_contrib.ability.model.safediffcon.burgers_unet import Attention

print(signature(Attention.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_unet`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_unet.py:240`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_unet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-unet-block"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_unet.Block`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`Block(dim, dim_out, groups=8, conv_2d=False)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_unet.Block`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_unet import Block
```

```text
Block(dim, dim_out, groups=8, conv_2d=False)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dim` | `未标注` | `必填` |
| `dim_out` | `未标注` | `必填` |
| `groups` | `未标注` | `8` |
| `conv_2d` | `未标注` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Block`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.safediffcon.burgers_unet import Block

print(signature(Block))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_unet`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_unet.py:129`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_unet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-unet-block-forward"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_unet.Block.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x, scale_shift=None)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_unet.Block.forward`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_unet import Block
```

```text
forward(self, x, scale_shift=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `scale_shift` | `未标注` | `None` |

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
from ai4e_contrib.ability.model.safediffcon.burgers_unet import Block

print(signature(Block.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_unet`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_unet.py:139`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_unet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-unet-downsample"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_unet.Downsample`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`Downsample(dim, dim_out=None)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_unet.Downsample`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_unet import Downsample
```

```text
Downsample(dim, dim_out=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dim` | `未标注` | `必填` |
| `dim_out` | `未标注` | `None` |

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
from ai4e_contrib.ability.model.safediffcon.burgers_unet import Downsample

print(signature(Downsample))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_unet`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_unet.py:31`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_unet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-unet-downsample2d"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_unet.Downsample2d`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`Downsample2d(dim, dim_out=None)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_unet.Downsample2d`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_unet import Downsample2d
```

```text
Downsample2d(dim, dim_out=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dim` | `未标注` | `必填` |
| `dim_out` | `未标注` | `None` |

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
from ai4e_contrib.ability.model.safediffcon.burgers_unet import Downsample2d

print(signature(Downsample2d))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_unet`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_unet.py:40`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_unet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-unet-layernorm"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_unet.LayerNorm`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`LayerNorm(dim)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_unet.LayerNorm`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_unet import LayerNorm
```

```text
LayerNorm(dim)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dim` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`LayerNorm`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.safediffcon.burgers_unet import LayerNorm

print(signature(LayerNorm))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_unet`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_unet.py:54`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_unet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-unet-layernorm-forward"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_unet.LayerNorm.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_unet.LayerNorm.forward`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_unet import LayerNorm
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
from ai4e_contrib.ability.model.safediffcon.burgers_unet import LayerNorm

print(signature(LayerNorm.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_unet`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_unet.py:59`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_unet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-unet-linearattention"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_unet.LinearAttention`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`LinearAttention(dim, heads=4, dim_head=32, conv_2d=False)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_unet.LinearAttention`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_unet import LinearAttention
```

```text
LinearAttention(dim, heads=4, dim_head=32, conv_2d=False)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dim` | `未标注` | `必填` |
| `heads` | `未标注` | `4` |
| `dim_head` | `未标注` | `32` |
| `conv_2d` | `未标注` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`LinearAttention`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.safediffcon.burgers_unet import LinearAttention

print(signature(LinearAttention))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_unet`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_unet.py:183`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_unet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-unet-linearattention-forward"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_unet.LinearAttention.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_unet.LinearAttention.forward`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_unet import LinearAttention
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
from ai4e_contrib.ability.model.safediffcon.burgers_unet import LinearAttention

print(signature(LinearAttention.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_unet`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_unet.py:203`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_unet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-unet-prenorm"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_unet.PreNorm`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`PreNorm(dim, fn, conv_2d=False)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_unet.PreNorm`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_unet import PreNorm
```

```text
PreNorm(dim, fn, conv_2d=False)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dim` | `未标注` | `必填` |
| `fn` | `未标注` | `必填` |
| `conv_2d` | `未标注` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`PreNorm`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.safediffcon.burgers_unet import PreNorm

print(signature(PreNorm))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_unet`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_unet.py:66`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_unet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-unet-prenorm-forward"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_unet.PreNorm.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_unet.PreNorm.forward`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_unet import PreNorm
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
from ai4e_contrib.ability.model.safediffcon.burgers_unet import PreNorm

print(signature(PreNorm.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_unet`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_unet.py:75`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_unet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-unet-rmsnorm"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_unet.RMSNorm`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`RMSNorm(dim)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_unet.RMSNorm`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_unet import RMSNorm
```

```text
RMSNorm(dim)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dim` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`RMSNorm`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.safediffcon.burgers_unet import RMSNorm

print(signature(RMSNorm))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_unet`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_unet.py:46`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_unet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-unet-rmsnorm-forward"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_unet.RMSNorm.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_unet.RMSNorm.forward`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_unet import RMSNorm
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
from ai4e_contrib.ability.model.safediffcon.burgers_unet import RMSNorm

print(signature(RMSNorm.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_unet`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_unet.py:51`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_unet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-unet-randomorlearnedsinusoidalposemb"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_unet.RandomOrLearnedSinusoidalPosEmb`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`RandomOrLearnedSinusoidalPosEmb(dim, is_random=False)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_unet.RandomOrLearnedSinusoidalPosEmb`

### 用途

following @crowsonkb 's lead with random (learned optional) sinusoidal pos emb 

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_unet import RandomOrLearnedSinusoidalPosEmb
```

```text
RandomOrLearnedSinusoidalPosEmb(dim, is_random=False)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dim` | `未标注` | `必填` |
| `is_random` | `未标注` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`RandomOrLearnedSinusoidalPosEmb`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.safediffcon.burgers_unet import RandomOrLearnedSinusoidalPosEmb

print(signature(RandomOrLearnedSinusoidalPosEmb))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_unet`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_unet.py:110`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_unet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-unet-randomorlearnedsinusoidalposemb-forward"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_unet.RandomOrLearnedSinusoidalPosEmb.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_unet.RandomOrLearnedSinusoidalPosEmb.forward`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_unet import RandomOrLearnedSinusoidalPosEmb
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
from ai4e_contrib.ability.model.safediffcon.burgers_unet import RandomOrLearnedSinusoidalPosEmb

print(signature(RandomOrLearnedSinusoidalPosEmb.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_unet`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_unet.py:120`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_unet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-unet-residual"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_unet.Residual`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`Residual(fn)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_unet.Residual`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_unet import Residual
```

```text
Residual(fn)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `fn` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Residual`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.safediffcon.burgers_unet import Residual

print(signature(Residual))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_unet`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_unet.py:17`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_unet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-unet-residual-forward"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_unet.Residual.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x, *args, **kwargs)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_unet.Residual.forward`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_unet import Residual
```

```text
forward(self, x, *args, **kwargs)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
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
from ai4e_contrib.ability.model.safediffcon.burgers_unet import Residual

print(signature(Residual.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_unet`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_unet.py:22`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_unet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-unet-resnetblock"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_unet.ResnetBlock`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`ResnetBlock(dim, dim_out, *, time_emb_dim=None, groups=8, conv_2d=False)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_unet.ResnetBlock`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_unet import ResnetBlock
```

```text
ResnetBlock(dim, dim_out, *, time_emb_dim=None, groups=8, conv_2d=False)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dim` | `未标注` | `必填` |
| `dim_out` | `未标注` | `必填` |
| `time_emb_dim` | `未标注` | `None` |
| `groups` | `未标注` | `8` |
| `conv_2d` | `未标注` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`ResnetBlock`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.safediffcon.burgers_unet import ResnetBlock

print(signature(ResnetBlock))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_unet`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_unet.py:150`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_unet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-unet-resnetblock-forward"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_unet.ResnetBlock.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x, time_emb=None)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_unet.ResnetBlock.forward`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_unet import ResnetBlock
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
from ai4e_contrib.ability.model.safediffcon.burgers_unet import ResnetBlock

print(signature(ResnetBlock.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_unet`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_unet.py:167`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_unet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-unet-sinusoidalposemb"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_unet.SinusoidalPosEmb`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`SinusoidalPosEmb(dim, theta=10000)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_unet.SinusoidalPosEmb`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_unet import SinusoidalPosEmb
```

```text
SinusoidalPosEmb(dim, theta=10000)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dim` | `未标注` | `必填` |
| `theta` | `未标注` | `10000` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`SinusoidalPosEmb`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.safediffcon.burgers_unet import SinusoidalPosEmb

print(signature(SinusoidalPosEmb))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_unet`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_unet.py:82`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_unet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-unet-sinusoidalposemb-forward"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_unet.SinusoidalPosEmb.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_unet.SinusoidalPosEmb.forward`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_unet import SinusoidalPosEmb
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
from ai4e_contrib.ability.model.safediffcon.burgers_unet import SinusoidalPosEmb

print(signature(SinusoidalPosEmb.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_unet`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_unet.py:88`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_unet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-unet-unet1d"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_unet.Unet1D`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`Unet1D(dim, init_dim=None, out_dim=None, dim_mults=(1, 2, 4, 8), channels=21, self_condition=False, resnet_block_groups=8, learned_variance=False, learned_sinusoidal_cond=False, random_fourier_features=False, learned_sinusoidal_dim=16, sinusoidal_pos_emb_theta=10000, attn_dim_head=32, attn_heads=4)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_unet.Unet1D`

### 用途

Estimate the noise given the last diffusion step.
Treat the time dimension OR the space dimension as channel.

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_unet import Unet1D
```

```text
Unet1D(dim, init_dim=None, out_dim=None, dim_mults=(1, 2, 4, 8), channels=21, self_condition=False, resnet_block_groups=8, learned_variance=False, learned_sinusoidal_cond=False, random_fourier_features=False, learned_sinusoidal_dim=16, sinusoidal_pos_emb_theta=10000, attn_dim_head=32, attn_heads=4)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dim` | `未标注` | `必填` |
| `init_dim` | `未标注` | `None` |
| `out_dim` | `未标注` | `None` |
| `dim_mults` | `未标注` | `(1, 2, 4, 8)` |
| `channels` | `未标注` | `21` |
| `self_condition` | `未标注` | `False` |
| `resnet_block_groups` | `未标注` | `8` |
| `learned_variance` | `未标注` | `False` |
| `learned_sinusoidal_cond` | `未标注` | `False` |
| `random_fourier_features` | `未标注` | `False` |
| `learned_sinusoidal_dim` | `未标注` | `16` |
| `sinusoidal_pos_emb_theta` | `未标注` | `10000` |
| `attn_dim_head` | `未标注` | `32` |
| `attn_heads` | `未标注` | `4` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Unet1D`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.safediffcon.burgers_unet import Unet1D

print(signature(Unet1D))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_unet`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_unet.py:429`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_unet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-unet-unet1d-forward"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_unet.Unet1D.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x, time, x_self_cond=None)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_unet.Unet1D.forward`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_unet import Unet1D
```

```text
forward(self, x, time, x_self_cond=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `time` | `未标注` | `必填` |
| `x_self_cond` | `未标注` | `None` |

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
from ai4e_contrib.ability.model.safediffcon.burgers_unet import Unet1D

print(signature(Unet1D.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_unet`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_unet.py:525`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_unet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-unet-unet2d"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_unet.Unet2D`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`Unet2D(dim, init_dim=None, out_dim=None, dim_mults=(1, 2, 4, 8), channels=2, self_condition=False, resnet_block_groups=8, learned_variance=False, learned_sinusoidal_cond=False, random_fourier_features=False, learned_sinusoidal_dim=16, sinusoidal_pos_emb_theta=10000, attn_dim_head=32, attn_heads=4, condition_on_residual=None)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_unet.Unet2D`

### 用途

Estimates the noise given the last diffusion step
The time dimension and the space dimension are treated equally

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_unet import Unet2D
```

```text
Unet2D(dim, init_dim=None, out_dim=None, dim_mults=(1, 2, 4, 8), channels=2, self_condition=False, resnet_block_groups=8, learned_variance=False, learned_sinusoidal_cond=False, random_fourier_features=False, learned_sinusoidal_dim=16, sinusoidal_pos_emb_theta=10000, attn_dim_head=32, attn_heads=4, condition_on_residual=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dim` | `未标注` | `必填` |
| `init_dim` | `未标注` | `None` |
| `out_dim` | `未标注` | `None` |
| `dim_mults` | `未标注` | `(1, 2, 4, 8)` |
| `channels` | `未标注` | `2` |
| `self_condition` | `未标注` | `False` |
| `resnet_block_groups` | `未标注` | `8` |
| `learned_variance` | `未标注` | `False` |
| `learned_sinusoidal_cond` | `未标注` | `False` |
| `random_fourier_features` | `未标注` | `False` |
| `learned_sinusoidal_dim` | `未标注` | `16` |
| `sinusoidal_pos_emb_theta` | `未标注` | `10000` |
| `attn_dim_head` | `未标注` | `32` |
| `attn_heads` | `未标注` | `4` |
| `condition_on_residual` | `未标注` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Unet2D`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`NotImplementedError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.safediffcon.burgers_unet import Unet2D

print(signature(Unet2D))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_unet`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_unet.py:264`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_unet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-unet-unet2d-forward"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_unet.Unet2D.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x, time, x_self_cond=None, residual=None)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_unet.Unet2D.forward`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_unet import Unet2D
```

```text
forward(self, x, time, x_self_cond=None, residual=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `time` | `未标注` | `必填` |
| `x_self_cond` | `未标注` | `None` |
| `residual` | `未标注` | `None` |

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
from ai4e_contrib.ability.model.safediffcon.burgers_unet import Unet2D

print(signature(Unet2D.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_unet`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_unet.py:383`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_unet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-unet-upsample"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_unet.Upsample`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`Upsample(dim, dim_out=None)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_unet.Upsample`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_unet import Upsample
```

```text
Upsample(dim, dim_out=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dim` | `未标注` | `必填` |
| `dim_out` | `未标注` | `None` |

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
from ai4e_contrib.ability.model.safediffcon.burgers_unet import Upsample

print(signature(Upsample))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_unet`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_unet.py:25`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_unet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-safediffcon-burgers-unet-upsample2d"></a>
## `ai4e_contrib.ability.model.safediffcon.burgers_unet.Upsample2d`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`Upsample2d(dim, dim_out=None)`
- **规范定义名**：`ai4e_contrib.ability.model.safediffcon.burgers_unet.Upsample2d`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.safediffcon.burgers_unet import Upsample2d
```

```text
Upsample2d(dim, dim_out=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dim` | `未标注` | `必填` |
| `dim_out` | `未标注` | `None` |

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
from ai4e_contrib.ability.model.safediffcon.burgers_unet import Upsample2d

print(signature(Upsample2d))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.safediffcon.burgers_unet`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/safediffcon/burgers_unet.py:34`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.safediffcon.burgers_unet')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
