<!-- dojo-help: {"domain": "ai4e_core.abilities.data.source.read", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.data.source.read 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.data.source.read", "topic_id": "module:ai4e_core.abilities.data.source.read"} -->
# `ai4e_core.abilities.data.source.read` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-data-source-read-infer-format"></a>
## `ai4e_core.abilities.data.source.read.infer_format`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`infer_format(path: str | Path) -> str`
- **规范定义名**：`ai4e_core.abilities.data.source.read.infer_format`

### 用途

根据扩展名推断格式名。

Raises:
    ValueError: 扩展名没有对应适配器。

### 导入与签名

```python
from ai4e_core.abilities.data.source.read import infer_format
```

```text
infer_format(path: str | Path) -> str
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `str | Path` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`str`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.source.read import infer_format

print(signature(infer_format))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.source.read`
- 仓库相对路径：`packages/ai4e-core/abilities/data/source/read.py:22`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.source.read')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-source-read-read-file"></a>
## `ai4e_core.abilities.data.source.read.read_file`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`read_file(path: str | Path, *, format: str | None=None) -> NativeData`
- **规范定义名**：`ai4e_core.abilities.data.source.read.read_file`

### 用途

读取单个文件。文件不在或格式不认识时不打开适配器。

Args:
    path: 本地文件路径。
    format: 显式格式名；缺省时按扩展名推断。

Returns:
    统一的 VTK 数据对象；无网格数组使用 FieldData 承载。

Raises:
    FileNotFoundError: 目标文件不存在。
    ValueError: 格式不支持或数据转换失败。
    TypeError: 适配器未返回 VTK 对象。

### 导入与签名

```python
from ai4e_core.abilities.data.source.read import read_file
```

```text
read_file(path: str | Path, *, format: str | None=None) -> NativeData
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `str | Path` | `必填` |
| `format` | `str | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`NativeData`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FileNotFoundError`, `TypeError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.source.read import read_file

print(signature(read_file))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.source.read`
- 仓库相对路径：`packages/ai4e-core/abilities/data/source/read.py:36`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.source.read')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-source-read-read-many"></a>
## `ai4e_core.abilities.data.source.read.read_many`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`read_many(paths: list[str | Path], *, format: str | None=None) -> list[NativeData]`
- **规范定义名**：`ai4e_core.abilities.data.source.read.read_many`

### 用途

按顺序读取多个文件，返回 VTK 对象列表；每项均校验返回契约。

### 导入与签名

```python
from ai4e_core.abilities.data.source.read import read_many
```

```text
read_many(paths: list[str | Path], *, format: str | None=None) -> list[NativeData]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `paths` | `list[str | Path]` | `必填` |
| `format` | `str | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`list[NativeData]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.source.read import read_many

print(signature(read_many))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.source.read`
- 仓库相对路径：`packages/ai4e-core/abilities/data/source/read.py:64`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.source.read')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-source-read-read-tree"></a>
## `ai4e_core.abilities.data.source.read.read_tree`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`read_tree(root: str | Path, *, recursive: bool=True, format: str | None=None) -> list[tuple[Path, NativeData]]`
- **规范定义名**：`ai4e_core.abilities.data.source.read.read_tree`

### 用途

读取目录中已登记格式的文件，逐个转换为 VTK 对象。

Args:
    root: 目录根。
    recursive: 是否进入子目录。
    format: 若给出，只读该格式。

Returns:
    ``(路径, VTK 内存对象)`` 列表，按路径排序。

### 导入与签名

```python
from ai4e_core.abilities.data.source.read import read_tree
```

```text
read_tree(root: str | Path, *, recursive: bool=True, format: str | None=None) -> list[tuple[Path, NativeData]]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `root` | `str | Path` | `必填` |
| `recursive` | `bool` | `True` |
| `format` | `str | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`list[tuple[Path, NativeData]]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FileNotFoundError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.source.read import read_tree

print(signature(read_tree))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.source.read`
- 仓库相对路径：`packages/ai4e-core/abilities/data/source/read.py:73`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.source.read')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
