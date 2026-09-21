<!-- dojo-help: {"domain": "ai4e_contrib.ability.model.gencp.sit_fno", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.model.gencp.sit_fno 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.model.gencp.sit_fno", "topic_id": "module:ai4e_contrib.ability.model.gencp.sit_fno"} -->
# `ai4e_contrib.ability.model.gencp.sit_fno` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-compactfnofinallayer"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.CompactFNOFinalLayer`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`CompactFNOFinalLayer(hidden_size, patch_size, out_channels, modes=16)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.CompactFNOFinalLayer`

### 用途

A compact 1D FNO-based final layer for SiT.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import CompactFNOFinalLayer
```

```text
CompactFNOFinalLayer(hidden_size, patch_size, out_channels, modes=16)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `hidden_size` | `未标注` | `必填` |
| `patch_size` | `未标注` | `必填` |
| `out_channels` | `未标注` | `必填` |
| `modes` | `未标注` | `16` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`CompactFNOFinalLayer`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.sit_fno import CompactFNOFinalLayer

print(signature(CompactFNOFinalLayer))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:221`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-compactfnofinallayer-forward"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.CompactFNOFinalLayer.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x, c)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.CompactFNOFinalLayer.forward`

### 用途

x: (N, num_patches, hidden_size) - patch tokens
c: (N, hidden_size) - conditioning

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import CompactFNOFinalLayer
```

```text
forward(self, x, c)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `c` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.gencp.sit_fno import CompactFNOFinalLayer

print(signature(CompactFNOFinalLayer.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:259`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-finallayer"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.FinalLayer`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`FinalLayer(hidden_size, patch_size, out_channels)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.FinalLayer`

### 用途

The final layer of SiT.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import FinalLayer
```

```text
FinalLayer(hidden_size, patch_size, out_channels)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `hidden_size` | `未标注` | `必填` |
| `patch_size` | `未标注` | `必填` |
| `out_channels` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`FinalLayer`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.sit_fno import FinalLayer

print(signature(FinalLayer))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:290`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-finallayer-forward"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.FinalLayer.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x, c)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.FinalLayer.forward`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import FinalLayer
```

```text
forward(self, x, c)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `c` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.gencp.sit_fno import FinalLayer

print(signature(FinalLayer.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:308`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-labelembedder"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.LabelEmbedder`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`LabelEmbedder(num_classes, hidden_size, dropout_prob)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.LabelEmbedder`

### 用途

Embeds class labels into vector representations. Also handles label dropout for classifier-free guidance.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import LabelEmbedder
```

```text
LabelEmbedder(num_classes, hidden_size, dropout_prob)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `num_classes` | `未标注` | `必填` |
| `hidden_size` | `未标注` | `必填` |
| `dropout_prob` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`LabelEmbedder`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.sit_fno import LabelEmbedder

print(signature(LabelEmbedder))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:163`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-labelembedder-forward"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.LabelEmbedder.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, labels, train, force_drop_ids=None)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.LabelEmbedder.forward`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import LabelEmbedder
```

```text
forward(self, labels, train, force_drop_ids=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `labels` | `未标注` | `必填` |
| `train` | `未标注` | `必填` |
| `force_drop_ids` | `未标注` | `None` |

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
from ai4e_contrib.ability.model.gencp.sit_fno import LabelEmbedder

print(signature(LabelEmbedder.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:185`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-labelembedder-token-drop"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.LabelEmbedder.token_drop`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`token_drop(self, labels, force_drop_ids=None)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.LabelEmbedder.token_drop`

### 用途

Drops labels to enable classifier-free guidance.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import LabelEmbedder
```

```text
token_drop(self, labels, force_drop_ids=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `labels` | `未标注` | `必填` |
| `force_drop_ids` | `未标注` | `None` |

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
from ai4e_contrib.ability.model.gencp.sit_fno import LabelEmbedder

print(signature(LabelEmbedder.token_drop))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:174`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-sitblock"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.SiTBlock`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`SiTBlock(hidden_size, num_heads, mlp_ratio=4.0, **block_kwargs)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.SiTBlock`

### 用途

A SiT block with adaptive layer norm zero (adaLN-Zero) conditioning.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import SiTBlock
```

```text
SiTBlock(hidden_size, num_heads, mlp_ratio=4.0, **block_kwargs)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `hidden_size` | `未标注` | `必填` |
| `num_heads` | `未标注` | `必填` |
| `mlp_ratio` | `未标注` | `4.0` |
| `**block_kwargs` | `未标注` | `可变关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`SiTBlock`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.sit_fno import SiTBlock

print(signature(SiTBlock))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:197`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-sitblock-forward"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.SiTBlock.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x, c)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.SiTBlock.forward`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import SiTBlock
```

```text
forward(self, x, c)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `c` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.gencp.sit_fno import SiTBlock

print(signature(SiTBlock.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:214`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-sit-b-2"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.SiT_B_2`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`SiT_B_2(**kwargs)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.SiT_B_2`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_B_2
```

```text
SiT_B_2(**kwargs)
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
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_B_2

print(signature(SiT_B_2))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:836`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-sit-b-4"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.SiT_B_4`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`SiT_B_4(**kwargs)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.SiT_B_4`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_B_4
```

```text
SiT_B_4(**kwargs)
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
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_B_4

print(signature(SiT_B_4))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:839`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-sit-b-8"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.SiT_B_8`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`SiT_B_8(**kwargs)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.SiT_B_8`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_B_8
```

```text
SiT_B_8(**kwargs)
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
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_B_8

print(signature(SiT_B_8))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:842`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-sit-fno"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.SiT_FNO`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`SiT_FNO(input_size=(64, 64), patch_size=(2, 2), in_channels=4, out_channels=3, hidden_size=1152, depth=28, num_heads=16, mlp_ratio=4.0, num_frames=16, class_dropout_prob=0.1, num_classes=1000, learn_sigma=False, x0_is_use_noise=True, dataset_name='turek_hron_data', stage='fluid', forward_type='latte', use_surrogate=False, modes=16)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.SiT_FNO`

### 用途

Diffusion model with a Transformer backbone.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_FNO
```

```text
SiT_FNO(input_size=(64, 64), patch_size=(2, 2), in_channels=4, out_channels=3, hidden_size=1152, depth=28, num_heads=16, mlp_ratio=4.0, num_frames=16, class_dropout_prob=0.1, num_classes=1000, learn_sigma=False, x0_is_use_noise=True, dataset_name='turek_hron_data', stage='fluid', forward_type='latte', use_surrogate=False, modes=16)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `input_size` | `未标注` | `(64, 64)` |
| `patch_size` | `未标注` | `(2, 2)` |
| `in_channels` | `未标注` | `4` |
| `out_channels` | `未标注` | `3` |
| `hidden_size` | `未标注` | `1152` |
| `depth` | `未标注` | `28` |
| `num_heads` | `未标注` | `16` |
| `mlp_ratio` | `未标注` | `4.0` |
| `num_frames` | `未标注` | `16` |
| `class_dropout_prob` | `未标注` | `0.1` |
| `num_classes` | `未标注` | `1000` |
| `learn_sigma` | `未标注` | `False` |
| `x0_is_use_noise` | `未标注` | `True` |
| `dataset_name` | `未标注` | `'turek_hron_data'` |
| `stage` | `未标注` | `'fluid'` |
| `forward_type` | `未标注` | `'latte'` |
| `use_surrogate` | `未标注` | `False` |
| `modes` | `未标注` | `16` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`SiT_FNO`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_FNO

print(signature(SiT_FNO))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`gencp`
- 案例：`gencp.double_cylinder_sit_fno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_sit_fno`

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:315`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-sit-fno-apply-mask"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.SiT_FNO.apply_mask`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`apply_mask(self, xt, x0=None)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.SiT_FNO.apply_mask`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_FNO
```

```text
apply_mask(self, xt, x0=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `xt` | `未标注` | `必填` |
| `x0` | `未标注` | `None` |

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
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_FNO

print(signature(SiT_FNO.apply_mask))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:720`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-sit-fno-data-postprocess"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.SiT_FNO.data_postprocess`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`data_postprocess(self, x, T2=None)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.SiT_FNO.data_postprocess`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_FNO
```

```text
data_postprocess(self, x, T2=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `T2` | `未标注` | `None` |

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
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_FNO

print(signature(SiT_FNO.data_postprocess))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:478`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-sit-fno-data-preprocess"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.SiT_FNO.data_preprocess`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`data_preprocess(self, xt, x0)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.SiT_FNO.data_preprocess`

### 用途

Improved Latte forward pass based on official implementation.
xt: (N, T1, H, W, C) - target frames to denoise
x0: (N, T2, H, W, C) - initial frames  
t: (N,) - diffusion timesteps
cond: additional conditioning information

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_FNO
```

```text
data_preprocess(self, xt, x0)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `xt` | `未标注` | `必填` |
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
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_FNO

print(signature(SiT_FNO.data_preprocess))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:451`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-sit-fno-forward"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.SiT_FNO.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x, t, x0_or_cond=None, cond=None, **kwargs)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.SiT_FNO.forward`

### 用途

Compatible forward for both FSI and NTcouple.

- FSI:        forward(xt, t, x0, cond)   (or keyword x0=..., cond=...)
- NTcouple:   forward(x_joint, t, cond)  (cond can be passed as 3rd positional or as cond=...)

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_FNO
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
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_FNO

print(signature(SiT_FNO.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:673`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-sit-fno-forward-sit"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.SiT_FNO.forward_SiT`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward_SiT(self, xt, t, x0, cond)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.SiT_FNO.forward_SiT`

### 用途

Forward pass of SiT.
xt: (N, C, H, W) 
t: (N,) tensor of diffusion timesteps
x0: (N, C, H, W) 
channel: pressure, x_velocity, y_velocity, sdf

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_FNO
```

```text
forward_SiT(self, xt, t, x0, cond)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `xt` | `未标注` | `必填` |
| `t` | `未标注` | `必填` |
| `x0` | `未标注` | `必填` |
| `cond` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_FNO

print(signature(SiT_FNO.forward_SiT))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:486`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-sit-fno-forward-latte"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.SiT_FNO.forward_latte`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward_latte(self, xt, t, x0, cond)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.SiT_FNO.forward_latte`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_FNO
```

```text
forward_latte(self, xt, t, x0, cond)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `xt` | `未标注` | `必填` |
| `t` | `未标注` | `必填` |
| `x0` | `未标注` | `必填` |
| `cond` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_FNO

print(signature(SiT_FNO.forward_latte))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:536`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-sit-fno-forward-with-cfg"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.SiT_FNO.forward_with_cfg`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward_with_cfg(self, x, t, y, cfg_scale)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.SiT_FNO.forward_with_cfg`

### 用途

Forward pass of SiT, but also batches the unconSiTional forward pass for classifier-free guidance.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_FNO
```

```text
forward_with_cfg(self, x, t, y, cfg_scale)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `t` | `未标注` | `必填` |
| `y` | `未标注` | `必填` |
| `cfg_scale` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_FNO

print(signature(SiT_FNO.forward_with_cfg))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:698`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-sit-fno-initialize-weights"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.SiT_FNO.initialize_weights`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`initialize_weights(self)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.SiT_FNO.initialize_weights`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_FNO
```

```text
initialize_weights(self)
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
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_FNO

print(signature(SiT_FNO.initialize_weights))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:388`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-sit-fno-load-checkpoint"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.SiT_FNO.load_checkpoint`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`load_checkpoint(self, checkpoint_path)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.SiT_FNO.load_checkpoint`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_FNO
```

```text
load_checkpoint(self, checkpoint_path)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `checkpoint_path` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_FNO

print(signature(SiT_FNO.load_checkpoint))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:716`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-sit-fno-unpatchify"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.SiT_FNO.unpatchify`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`unpatchify(self, x)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.SiT_FNO.unpatchify`

### 用途

x: (N, T, patch_size**2 * C)
imgs: (N, H, W, C)

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_FNO
```

```text
unpatchify(self, x)
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
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_FNO

print(signature(SiT_FNO.unpatchify))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:435`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-sit-l-2"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.SiT_L_2`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`SiT_L_2(**kwargs)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.SiT_L_2`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_L_2
```

```text
SiT_L_2(**kwargs)
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
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_L_2

print(signature(SiT_L_2))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:827`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-sit-l-4"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.SiT_L_4`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`SiT_L_4(**kwargs)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.SiT_L_4`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_L_4
```

```text
SiT_L_4(**kwargs)
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
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_L_4

print(signature(SiT_L_4))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:830`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-sit-l-8"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.SiT_L_8`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`SiT_L_8(**kwargs)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.SiT_L_8`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_L_8
```

```text
SiT_L_8(**kwargs)
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
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_L_8

print(signature(SiT_L_8))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:833`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-sit-s-2"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.SiT_S_2`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`SiT_S_2(**kwargs)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.SiT_S_2`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_S_2
```

```text
SiT_S_2(**kwargs)
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
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_S_2

print(signature(SiT_S_2))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:845`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-sit-s-4"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.SiT_S_4`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`SiT_S_4(**kwargs)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.SiT_S_4`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_S_4
```

```text
SiT_S_4(**kwargs)
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
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_S_4

print(signature(SiT_S_4))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:848`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-sit-s-8"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.SiT_S_8`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`SiT_S_8(**kwargs)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.SiT_S_8`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_S_8
```

```text
SiT_S_8(**kwargs)
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
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_S_8

print(signature(SiT_S_8))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:851`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-sit-xl-2"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.SiT_XL_2`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`SiT_XL_2(**kwargs)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.SiT_XL_2`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_XL_2
```

```text
SiT_XL_2(**kwargs)
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
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_XL_2

print(signature(SiT_XL_2))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:818`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-sit-xl-4"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.SiT_XL_4`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`SiT_XL_4(**kwargs)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.SiT_XL_4`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_XL_4
```

```text
SiT_XL_4(**kwargs)
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
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_XL_4

print(signature(SiT_XL_4))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:821`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-sit-xl-8"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.SiT_XL_8`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`SiT_XL_8(**kwargs)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.SiT_XL_8`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_XL_8
```

```text
SiT_XL_8(**kwargs)
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
from ai4e_contrib.ability.model.gencp.sit_fno import SiT_XL_8

print(signature(SiT_XL_8))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:824`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-spectralconv1d"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.SpectralConv1d`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`SpectralConv1d(in_channels, out_channels, modes1)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.SpectralConv1d`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import SpectralConv1d
```

```text
SpectralConv1d(in_channels, out_channels, modes1)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `in_channels` | `未标注` | `必填` |
| `out_channels` | `未标注` | `必填` |
| `modes1` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`SpectralConv1d`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.sit_fno import SpectralConv1d

print(signature(SpectralConv1d))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:81`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-spectralconv1d-compl-mul1d"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.SpectralConv1d.compl_mul1d`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`compl_mul1d(self, input, weights)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.SpectralConv1d.compl_mul1d`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import SpectralConv1d
```

```text
compl_mul1d(self, input, weights)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `input` | `未标注` | `必填` |
| `weights` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.gencp.sit_fno import SpectralConv1d

print(signature(SpectralConv1d.compl_mul1d))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:98`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-spectralconv1d-forward"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.SpectralConv1d.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.SpectralConv1d.forward`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import SpectralConv1d
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
from ai4e_contrib.ability.model.gencp.sit_fno import SpectralConv1d

print(signature(SpectralConv1d.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:102`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-spectralconv3d"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.SpectralConv3d`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`SpectralConv3d(in_channels, out_channels, modes1, modes2, modes3)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.SpectralConv3d`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import SpectralConv3d
```

```text
SpectralConv3d(in_channels, out_channels, modes1, modes2, modes3)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `in_channels` | `未标注` | `必填` |
| `out_channels` | `未标注` | `必填` |
| `modes1` | `未标注` | `必填` |
| `modes2` | `未标注` | `必填` |
| `modes3` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`SpectralConv3d`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.sit_fno import SpectralConv3d

print(signature(SpectralConv3d))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:26`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-spectralconv3d-compl-mul3d"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.SpectralConv3d.compl_mul3d`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`compl_mul3d(self, input, weights)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.SpectralConv3d.compl_mul3d`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import SpectralConv3d
```

```text
compl_mul3d(self, input, weights)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `input` | `未标注` | `必填` |
| `weights` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.gencp.sit_fno import SpectralConv3d

print(signature(SpectralConv3d.compl_mul3d))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:56`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-spectralconv3d-forward"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.SpectralConv3d.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.SpectralConv3d.forward`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import SpectralConv3d
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
from ai4e_contrib.ability.model.gencp.sit_fno import SpectralConv3d

print(signature(SpectralConv3d.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:60`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-timestepembedder"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.TimestepEmbedder`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`TimestepEmbedder(hidden_size, frequency_embedding_size=256)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.TimestepEmbedder`

### 用途

Embeds scalar timesteps into vector representations.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import TimestepEmbedder
```

```text
TimestepEmbedder(hidden_size, frequency_embedding_size=256)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `hidden_size` | `未标注` | `必填` |
| `frequency_embedding_size` | `未标注` | `256` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`TimestepEmbedder`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.sit_fno import TimestepEmbedder

print(signature(TimestepEmbedder))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:123`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-timestepembedder-forward"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.TimestepEmbedder.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, t)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.TimestepEmbedder.forward`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import TimestepEmbedder
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
from ai4e_contrib.ability.model.gencp.sit_fno import TimestepEmbedder

print(signature(TimestepEmbedder.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:157`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-timestepembedder-timestep-embedding"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.TimestepEmbedder.timestep_embedding`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`timestep_embedding(t, dim, max_period=10000)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.TimestepEmbedder.timestep_embedding`

### 用途

Create sinusoidal timestep embeddings.
:param t: a 1-D Tensor of N indices, one per batch element.
                  These may be fractional.
:param dim: the dimension of the output.
:param max_period: controls the minimum frequency of the embeddings.
:return: an (N, D) Tensor of positional embeddings.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import TimestepEmbedder
```

```text
timestep_embedding(t, dim, max_period=10000)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `t` | `未标注` | `必填` |
| `dim` | `未标注` | `必填` |
| `max_period` | `未标注` | `10000` |

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
from ai4e_contrib.ability.model.gencp.sit_fno import TimestepEmbedder

print(signature(TimestepEmbedder.timestep_embedding))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:137`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-get-1d-sincos-pos-embed-from-grid"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.get_1d_sincos_pos_embed_from_grid`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`get_1d_sincos_pos_embed_from_grid(embed_dim, pos)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.get_1d_sincos_pos_embed_from_grid`

### 用途

embed_dim: output dimension for each position
pos: a list of positions to be encoded: size (M,)
out: (M, D)

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import get_1d_sincos_pos_embed_from_grid
```

```text
get_1d_sincos_pos_embed_from_grid(embed_dim, pos)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `embed_dim` | `未标注` | `必填` |
| `pos` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.gencp.sit_fno import get_1d_sincos_pos_embed_from_grid

print(signature(get_1d_sincos_pos_embed_from_grid))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:793`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-get-1d-sincos-temp-embed"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.get_1d_sincos_temp_embed`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`get_1d_sincos_temp_embed(embed_dim, length)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.get_1d_sincos_temp_embed`

### 用途

Generate 1D sinusoidal temporal embeddings.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import get_1d_sincos_temp_embed
```

```text
get_1d_sincos_temp_embed(embed_dim, length)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `embed_dim` | `未标注` | `必填` |
| `length` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.gencp.sit_fno import get_1d_sincos_temp_embed

print(signature(get_1d_sincos_temp_embed))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:754`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-get-2d-sincos-pos-embed"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.get_2d_sincos_pos_embed`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`get_2d_sincos_pos_embed(embed_dim, grid_height, grid_width=None, cls_token=False, extra_tokens=0)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.get_2d_sincos_pos_embed`

### 用途

grid_height, grid_width: int of the grid height and width (can be different for rectangular images)
return:
pos_embed: [grid_height*grid_width, embed_dim] or [1+grid_height*grid_width, embed_dim] (w/ or w/o cls_token)

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import get_2d_sincos_pos_embed
```

```text
get_2d_sincos_pos_embed(embed_dim, grid_height, grid_width=None, cls_token=False, extra_tokens=0)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `embed_dim` | `未标注` | `必填` |
| `grid_height` | `未标注` | `必填` |
| `grid_width` | `未标注` | `None` |
| `cls_token` | `未标注` | `False` |
| `extra_tokens` | `未标注` | `0` |

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
from ai4e_contrib.ability.model.gencp.sit_fno import get_2d_sincos_pos_embed

print(signature(get_2d_sincos_pos_embed))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:761`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-get-2d-sincos-pos-embed-from-grid"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.get_2d_sincos_pos_embed_from_grid`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`get_2d_sincos_pos_embed_from_grid(embed_dim, grid)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.get_2d_sincos_pos_embed_from_grid`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import get_2d_sincos_pos_embed_from_grid
```

```text
get_2d_sincos_pos_embed_from_grid(embed_dim, grid)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `embed_dim` | `未标注` | `必填` |
| `grid` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.gencp.sit_fno import get_2d_sincos_pos_embed_from_grid

print(signature(get_2d_sincos_pos_embed_from_grid))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:782`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-sit-fno-modulate"></a>
## `ai4e_contrib.ability.model.gencp.sit_fno.modulate`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`modulate(x, shift, scale)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.sit_fno.modulate`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.sit_fno import modulate
```

```text
modulate(x, shift, scale)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `shift` | `未标注` | `必填` |
| `scale` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.gencp.sit_fno import modulate

print(signature(modulate))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.sit_fno`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/sit_fno.py:19`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.sit_fno')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
