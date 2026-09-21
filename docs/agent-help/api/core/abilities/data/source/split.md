<!-- dojo-help: {"domain": "ai4e_core.abilities.data.source.split", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.data.source.split 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.data.source.split", "topic_id": "module:ai4e_core.abilities.data.source.split"} -->
# `ai4e_core.abilities.data.source.split` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-data-source-split-apply-declared-split"></a>
## `ai4e_core.abilities.data.source.split.apply_declared_split`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`apply_declared_split(index, config: Mapping[str, Any], overlay=None) -> None`
- **规范定义名**：`ai4e_core.abilities.data.source.split.apply_declared_split`

### 用途

把准备记录里的名单或当前 ``trainprep.split`` 套到已打开的清单索引。

### 导入与签名

```python
from ai4e_core.abilities.data.source.split import apply_declared_split
```

```text
apply_declared_split(index, config: Mapping[str, Any], overlay=None) -> None
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `index` | `未标注` | `必填` |
| `config` | `Mapping[str, Any]` | `必填` |
| `overlay` | `未标注` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`None`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.source.split import apply_declared_split

print(signature(apply_declared_split))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.source.split`
- 仓库相对路径：`packages/ai4e-core/abilities/data/source/split.py:232`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.source.split')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-source-split-complete-split-buckets"></a>
## `ai4e_core.abilities.data.source.split.complete_split_buckets`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`complete_split_buckets(partitions: Mapping[str, Sequence[str]] | None) -> dict[str, list[str]]`
- **规范定义名**：`ai4e_core.abilities.data.source.split.complete_split_buckets`

### 用途

补齐固定三分片；缺的桶为空名单。旧 validation 并进 eval。

### 导入与签名

```python
from ai4e_core.abilities.data.source.split import complete_split_buckets
```

```text
complete_split_buckets(partitions: Mapping[str, Sequence[str]] | None) -> dict[str, list[str]]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `partitions` | `Mapping[str, Sequence[str]] | None` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, list[str]]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.source.split import complete_split_buckets

print(signature(complete_split_buckets))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.source.split`
- 仓库相对路径：`packages/ai4e-core/abilities/data/source/split.py:95`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.source.split')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-source-split-default-counts"></a>
## `ai4e_core.abilities.data.source.split.default_counts`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`default_counts(partitions: Mapping[str, Sequence[str]]) -> dict[str, int]`
- **规范定义名**：`ai4e_core.abilities.data.source.split.default_counts`

### 用途

用原分片人数作默认值；缺的桶为 0，未识别分片并进 train。

### 导入与签名

```python
from ai4e_core.abilities.data.source.split import default_counts
```

```text
default_counts(partitions: Mapping[str, Sequence[str]]) -> dict[str, int]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `partitions` | `Mapping[str, Sequence[str]]` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, int]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.source.split import default_counts

print(signature(default_counts))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.source.split`
- 仓库相对路径：`packages/ai4e-core/abilities/data/source/split.py:145`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.source.split')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-source-split-draw-random"></a>
## `ai4e_core.abilities.data.source.split.draw_random`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`draw_random(samples: Sequence[str], counts: Mapping[str, Any], seed: int) -> dict[str, list[str]]`
- **规范定义名**：`ai4e_core.abilities.data.source.split.draw_random`

### 用途

按种子打乱后切成 train/test/eval；空桶不进入结果。

### 导入与签名

```python
from ai4e_core.abilities.data.source.split import draw_random
```

```text
draw_random(samples: Sequence[str], counts: Mapping[str, Any], seed: int) -> dict[str, list[str]]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `samples` | `Sequence[str]` | `必填` |
| `counts` | `Mapping[str, Any]` | `必填` |
| `seed` | `int` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, list[str]]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.source.split import draw_random

print(signature(draw_random))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.source.split`
- 仓库相对路径：`packages/ai4e-core/abilities/data/source/split.py:205`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.source.split')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-source-split-flatten-samples"></a>
## `ai4e_core.abilities.data.source.split.flatten_samples`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`flatten_samples(partitions: Mapping[str, Sequence[str]]) -> list[str]`
- **规范定义名**：`ai4e_core.abilities.data.source.split.flatten_samples`

### 用途

跨原分片去重保序，得到当前清单已经处理出来的全部样本。

### 导入与签名

```python
from ai4e_core.abilities.data.source.split import flatten_samples
```

```text
flatten_samples(partitions: Mapping[str, Sequence[str]]) -> list[str]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `partitions` | `Mapping[str, Sequence[str]]` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`list[str]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.source.split import flatten_samples

print(signature(flatten_samples))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.source.split`
- 仓库相对路径：`packages/ai4e-core/abilities/data/source/split.py:75`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.source.split')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-source-split-load-split-expected"></a>
## `ai4e_core.abilities.data.source.split.load_split_expected`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`load_split_expected(source: str | Path | Mapping[str, Any]) -> dict[str, int]`
- **规范定义名**：`ai4e_core.abilities.data.source.split.load_split_expected`

### 用途

读取分片文件里的期望人数；没有则返回空映射。

### 导入与签名

```python
from ai4e_core.abilities.data.source.split import load_split_expected
```

```text
load_split_expected(source: str | Path | Mapping[str, Any]) -> dict[str, int]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `source` | `str | Path | Mapping[str, Any]` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, int]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`TypeError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.source.split import load_split_expected

print(signature(load_split_expected))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.source.split`
- 仓库相对路径：`packages/ai4e-core/abilities/data/source/split.py:42`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.source.split')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-source-split-load-split-lists"></a>
## `ai4e_core.abilities.data.source.split.load_split_lists`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`load_split_lists(source: str | Path | Mapping[str, Any]) -> dict[str, list[str]]`
- **规范定义名**：`ai4e_core.abilities.data.source.split.load_split_lists`

### 用途

从映射或 YAML 取出分片相对路径名单，保持原顺序。

忽略 ``expected`` 等非名单键。名单值必须是字符串序列。

Args:
    source: 已展开的映射，或 YAML 路径。

Returns:
    分片名到相对路径列表。

Raises:
    TypeError: 根节点或名单不是映射/序列。
    FileNotFoundError: YAML 不存在。

### 导入与签名

```python
from ai4e_core.abilities.data.source.split import load_split_lists
```

```text
load_split_lists(source: str | Path | Mapping[str, Any]) -> dict[str, list[str]]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `source` | `str | Path | Mapping[str, Any]` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, list[str]]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`TypeError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.source.split import load_split_lists

print(signature(load_split_lists))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.source.split`
- 仓库相对路径：`packages/ai4e-core/abilities/data/source/split.py:16`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.source.split')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-source-split-named-slice"></a>
## `ai4e_core.abilities.data.source.split.named_slice`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`named_slice(name: Any, default: str='train') -> str`
- **规范定义名**：`ai4e_core.abilities.data.source.split.named_slice`

### 用途

分片名缺省为 default；旧 validation 并进 eval。

### 导入与签名

```python
from ai4e_core.abilities.data.source.split import named_slice
```

```text
named_slice(name: Any, default: str='train') -> str
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `name` | `Any` | `必填` |
| `default` | `str` | `'train'` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`str`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.source.split import named_slice

print(signature(named_slice))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.source.split`
- 仓库相对路径：`packages/ai4e-core/abilities/data/source/split.py:89`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.source.split')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-source-split-published-slices"></a>
## `ai4e_core.abilities.data.source.split.published_slices`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`published_slices(record: Mapping[str, Any] | None) -> list[dict[str, Any]]`
- **规范定义名**：`ai4e_core.abilities.data.source.split.published_slices`

### 用途

从准备记录读出 train/test/eval；不改历史文件，缺的切片人数为 0。

### 导入与签名

```python
from ai4e_core.abilities.data.source.split import published_slices
```

```text
published_slices(record: Mapping[str, Any] | None) -> list[dict[str, Any]]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `record` | `Mapping[str, Any] | None` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`list[dict[str, Any]]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.source.split import published_slices

print(signature(published_slices))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.source.split`
- 仓库相对路径：`packages/ai4e-core/abilities/data/source/split.py:106`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.source.split')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-source-split-require-split-counts"></a>
## `ai4e_core.abilities.data.source.split.require_split_counts`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`require_split_counts(splits: Mapping[str, Sequence[str]], expected: Mapping[str, int]) -> None`
- **规范定义名**：`ai4e_core.abilities.data.source.split.require_split_counts`

### 用途

校验各分片人数。人数不对则失败，不改名单。

Args:
    splits: 分片名到相对路径。
    expected: 分片名到期望人数。

Raises:
    ValueError: 某分片人数与期望不符。
    TypeError: 期望表不是映射。

### 导入与签名

```python
from ai4e_core.abilities.data.source.split import require_split_counts
```

```text
require_split_counts(splits: Mapping[str, Sequence[str]], expected: Mapping[str, int]) -> None
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `splits` | `Mapping[str, Sequence[str]]` | `必填` |
| `expected` | `Mapping[str, int]` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`None`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`TypeError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.source.split import require_split_counts

print(signature(require_split_counts))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.source.split`
- 仓库相对路径：`packages/ai4e-core/abilities/data/source/split.py:53`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.source.split')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-source-split-resolve-split"></a>
## `ai4e_core.abilities.data.source.split.resolve_split`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`resolve_split(partitions: Mapping[str, Sequence[str]], split: Mapping[str, Any] | None) -> dict[str, list[str]]`
- **规范定义名**：`ai4e_core.abilities.data.source.split.resolve_split`

### 用途

按准备声明重划 train/test/eval；不改张量，只返回新名单。

``method=original`` 保持原成员（未识别分片并进 train），忽略数量改写。
``method=random`` 打平后按种子抽取，数量之和必须等于全部样本，train 至少一个。
可选 ``samples`` 先限定执行范围，再划分。

### 导入与签名

```python
from ai4e_core.abilities.data.source.split import resolve_split
```

```text
resolve_split(partitions: Mapping[str, Sequence[str]], split: Mapping[str, Any] | None) -> dict[str, list[str]]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `partitions` | `Mapping[str, Sequence[str]]` | `必填` |
| `split` | `Mapping[str, Any] | None` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, list[str]]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.source.split import resolve_split

print(signature(resolve_split))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.source.split`
- 仓库相对路径：`packages/ai4e-core/abilities/data/source/split.py:179`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.source.split')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-source-split-restrict-partitions"></a>
## `ai4e_core.abilities.data.source.split.restrict_partitions`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`restrict_partitions(partitions: Mapping[str, Sequence[str]], samples: Sequence[str] | None) -> dict[str, list[str]]`
- **规范定义名**：`ai4e_core.abilities.data.source.split.restrict_partitions`

### 用途

执行范围指定样本时先缩小样本池；未指定则保持全部已处理样本。

### 导入与签名

```python
from ai4e_core.abilities.data.source.split import restrict_partitions
```

```text
restrict_partitions(partitions: Mapping[str, Sequence[str]], samples: Sequence[str] | None) -> dict[str, list[str]]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `partitions` | `Mapping[str, Sequence[str]]` | `必填` |
| `samples` | `Sequence[str] | None` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, list[str]]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.source.split import restrict_partitions

print(signature(restrict_partitions))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.source.split`
- 仓库相对路径：`packages/ai4e-core/abilities/data/source/split.py:155`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.source.split')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
