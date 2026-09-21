<!-- dojo-help: {"domain": "ai4e_core.abilities.transform.field_encoding", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.transform.field_encoding 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.transform.field_encoding", "topic_id": "module:ai4e_core.abilities.transform.field_encoding"} -->
# `ai4e_core.abilities.transform.field_encoding` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-transform-field-encoding-decode-position-trajectory"></a>
## `ai4e_core.abilities.transform.field_encoding.decode_position_trajectory`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`decode_position_trajectory(raw, item, *, frames, channels, position_stats, physical)`
- **规范定义名**：`ai4e_core.abilities.transform.field_encoding.decode_position_trajectory`

### 用途

还原输出布局并加回初态坐标，按需反归一化位置通道。

### 导入与签名

```python
from ai4e_core.abilities.transform.field_encoding import decode_position_trajectory
```

```text
decode_position_trajectory(raw, item, *, frames, channels, position_stats, physical)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `raw` | `未标注` | `必填` |
| `item` | `未标注` | `必填` |
| `frames` | `未标注` | `必填关键字参数` |
| `channels` | `未标注` | `必填关键字参数` |
| `position_stats` | `未标注` | `必填关键字参数` |
| `physical` | `未标注` | `必填关键字参数` |

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
from ai4e_core.abilities.transform.field_encoding import decode_position_trajectory

print(signature(decode_position_trajectory))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.transform.field_encoding`
- 仓库相对路径：`packages/ai4e-core/abilities/transform/field_encoding.py:76`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.transform.field_encoding')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-transform-field-encoding-decode-scalar-field"></a>
## `ai4e_core.abilities.transform.field_encoding.decode_scalar_field`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`decode_scalar_field(raw, item, *, stats, physical=True)`
- **规范定义名**：`ai4e_core.abilities.transform.field_encoding.decode_scalar_field`

### 用途

将标量输出还原为 [B,1,N,1] 物理场。

### 导入与签名

```python
from ai4e_core.abilities.transform.field_encoding import decode_scalar_field
```

```text
decode_scalar_field(raw, item, *, stats, physical=True)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `raw` | `未标注` | `必填` |
| `item` | `未标注` | `必填` |
| `stats` | `未标注` | `必填关键字参数` |
| `physical` | `未标注` | `True` |

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
from ai4e_core.abilities.transform.field_encoding import decode_scalar_field

print(signature(decode_scalar_field))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.transform.field_encoding`
- 仓库相对路径：`packages/ai4e-core/abilities/transform/field_encoding.py:70`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.transform.field_encoding')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-transform-field-encoding-encode-position-trajectory"></a>
## `ai4e_core.abilities.transform.field_encoding.encode_position_trajectory`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`encode_position_trajectory(arrays, stats, *, position_name, dynamic_name, condition_name)`
- **规范定义名**：`ai4e_core.abilities.transform.field_encoding.encode_position_trajectory`

### 用途

归一化位置并保留动态场尺度；初帧为输入，后续帧为目标。

### 导入与签名

```python
from ai4e_core.abilities.transform.field_encoding import encode_position_trajectory
```

```text
encode_position_trajectory(arrays, stats, *, position_name, dynamic_name, condition_name)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `arrays` | `未标注` | `必填` |
| `stats` | `未标注` | `必填` |
| `position_name` | `未标注` | `必填关键字参数` |
| `dynamic_name` | `未标注` | `必填关键字参数` |
| `condition_name` | `未标注` | `必填关键字参数` |

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
from ai4e_core.abilities.transform.field_encoding import encode_position_trajectory

print(signature(encode_position_trajectory))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.transform.field_encoding`
- 仓库相对路径：`packages/ai4e-core/abilities/transform/field_encoding.py:50`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.transform.field_encoding')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-transform-field-encoding-encode-scalar-grid"></a>
## `ai4e_core.abilities.transform.field_encoding.encode_scalar_grid`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`encode_scalar_grid(arrays, stats, *, input_name, target_name, coordinate_name)`
- **规范定义名**：`ai4e_core.abilities.transform.field_encoding.encode_scalar_grid`

### 用途

合并坐标与归一化输入，保存归一化目标及物理真值。

### 导入与签名

```python
from ai4e_core.abilities.transform.field_encoding import encode_scalar_grid
```

```text
encode_scalar_grid(arrays, stats, *, input_name, target_name, coordinate_name)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `arrays` | `未标注` | `必填` |
| `stats` | `未标注` | `必填` |
| `input_name` | `未标注` | `必填关键字参数` |
| `target_name` | `未标注` | `必填关键字参数` |
| `coordinate_name` | `未标注` | `必填关键字参数` |

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
from ai4e_core.abilities.transform.field_encoding import encode_scalar_grid

print(signature(encode_scalar_grid))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.transform.field_encoding`
- 仓库相对路径：`packages/ai4e-core/abilities/transform/field_encoding.py:34`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.transform.field_encoding')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-transform-field-encoding-position-statistics"></a>
## `ai4e_core.abilities.transform.field_encoding.position_statistics`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`position_statistics(arrays, *, name)`
- **规范定义名**：`ai4e_core.abilities.transform.field_encoding.position_statistics`

### 用途

逐样本等权平方矩位置统计；最终分母包含参考的额外 epsilon。

### 导入与签名

```python
from ai4e_core.abilities.transform.field_encoding import position_statistics
```

```text
position_statistics(arrays, *, name)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `arrays` | `未标注` | `必填` |
| `name` | `未标注` | `必填关键字参数` |

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
from ai4e_core.abilities.transform.field_encoding import position_statistics

print(signature(position_statistics))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.transform.field_encoding`
- 仓库相对路径：`packages/ai4e-core/abilities/transform/field_encoding.py:23`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.transform.field_encoding')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-transform-field-encoding-preserve-geometry"></a>
## `ai4e_core.abilities.transform.field_encoding.preserve_geometry`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`preserve_geometry(encoded, arrays)`
- **规范定义名**：`ai4e_core.abilities.transform.field_encoding.preserve_geometry`

### 用途

附带原实体身份及面连接，供独立推理/后处理重建网格。

### 导入与签名

```python
from ai4e_core.abilities.transform.field_encoding import preserve_geometry
```

```text
preserve_geometry(encoded, arrays)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `encoded` | `未标注` | `必填` |
| `arrays` | `未标注` | `必填` |

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
from ai4e_core.abilities.transform.field_encoding import preserve_geometry

print(signature(preserve_geometry))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.transform.field_encoding`
- 仓库相对路径：`packages/ai4e-core/abilities/transform/field_encoding.py:86`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.transform.field_encoding')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-transform-field-encoding-scalar-statistics"></a>
## `ai4e_core.abilities.transform.field_encoding.scalar_statistics`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`scalar_statistics(arrays, *, names)`
- **规范定义名**：`ai4e_core.abilities.transform.field_encoding.scalar_statistics`

### 用途

多个具名标量各自按样本及实体轴计算标量统计。

### 导入与签名

```python
from ai4e_core.abilities.transform.field_encoding import scalar_statistics
```

```text
scalar_statistics(arrays, *, names)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `arrays` | `未标注` | `必填` |
| `names` | `未标注` | `必填关键字参数` |

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
from ai4e_core.abilities.transform.field_encoding import scalar_statistics

print(signature(scalar_statistics))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.transform.field_encoding`
- 仓库相对路径：`packages/ai4e-core/abilities/transform/field_encoding.py:14`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.transform.field_encoding')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-transform-field-encoding-standardizer"></a>
## `ai4e_core.abilities.transform.field_encoding.standardizer`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`standardizer(stats)`
- **规范定义名**：`ai4e_core.abilities.transform.field_encoding.standardizer`

### 用途

将冻结统计构造成可微正反变换。

### 导入与签名

```python
from ai4e_core.abilities.transform.field_encoding import standardizer
```

```text
standardizer(stats)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `stats` | `未标注` | `必填` |

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
from ai4e_core.abilities.transform.field_encoding import standardizer

print(signature(standardizer))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.transform.field_encoding`
- 仓库相对路径：`packages/ai4e-core/abilities/transform/field_encoding.py:29`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.transform.field_encoding')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
