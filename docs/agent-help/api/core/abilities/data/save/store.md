<!-- dojo-help: {"domain": "ai4e_core.abilities.data.save.store", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.data.save.store 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.data.save.store", "topic_id": "module:ai4e_core.abilities.data.save.store"} -->
# `ai4e_core.abilities.data.save.store` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-data-save-store-backupcleanupwarning"></a>
## `ai4e_core.abilities.data.save.store.BackupCleanupWarning`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`class BackupCleanupWarning`
- **规范定义名**：`ai4e_core.abilities.data.save.store.BackupCleanupWarning`

### 用途

正式目录已提交，但旧备份清理失败。

### 导入与签名

```python
from ai4e_core.abilities.data.save.store import BackupCleanupWarning
```

```text
class BackupCleanupWarning
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`BackupCleanupWarning`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.save.store import BackupCleanupWarning

print(signature(BackupCleanupWarning))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.save.store`
- 仓库相对路径：`packages/ai4e-core/abilities/data/save/store.py:16`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.save.store')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-save-store-load-named-tensor"></a>
## `ai4e_core.abilities.data.save.store.load_named_tensor`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`load_named_tensor(path: str | Path) -> Any`
- **规范定义名**：`ai4e_core.abilities.data.save.store.load_named_tensor`

### 用途

仅加载张量和具名张量映射。

每次调用只记 debug，供循环按样本读取；失败仍为错误。阶段摘要由
application 输出，不在此重复 info。

### 导入与签名

```python
from ai4e_core.abilities.data.save.store import load_named_tensor
```

```text
load_named_tensor(path: str | Path) -> Any
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `str | Path` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Any`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.save.store import load_named_tensor

print(signature(load_named_tensor))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.save.store`
- 仓库相对路径：`packages/ai4e-core/abilities/data/save/store.py:118`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.save.store')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-save-store-load-named-tensors"></a>
## `ai4e_core.abilities.data.save.store.load_named_tensors`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`load_named_tensors(sample_dir: str | Path, filemap: Mapping[str, str], *, optional: Sequence[str]=()) -> dict[str, Any]`
- **规范定义名**：`ai4e_core.abilities.data.save.store.load_named_tensors`

### 用途

按对照表读回样本目录里已有的逻辑名。

对照表外的不读、不造。可选逻辑名缺文件时跳过，其余缺失或加载失败
包装为带完整路径的 ``RuntimeError``。可选性由业务层传入。

Args:
    sample_dir: 样本目录。
    filemap: 逻辑名到磁盘文件名。
    optional: 允许缺失的逻辑名。

Returns:
    逻辑名到载荷。

Raises:
    TypeError: 对照表不是映射。
    ValueError: 逻辑名或文件名非法。
    RuntimeError: 必需文件缺失或 ``torch.load`` 失败。

### 导入与签名

```python
from ai4e_core.abilities.data.save.store import load_named_tensors
```

```text
load_named_tensors(sample_dir: str | Path, filemap: Mapping[str, str], *, optional: Sequence[str]=()) -> dict[str, Any]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `sample_dir` | `str | Path` | `必填` |
| `filemap` | `Mapping[str, str]` | `必填` |
| `optional` | `Sequence[str]` | `()` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, Any]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`RuntimeError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.save.store import load_named_tensors

print(signature(load_named_tensors))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.save.store`
- 仓库相对路径：`packages/ai4e-core/abilities/data/save/store.py:131`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.save.store')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-save-store-write-named-tensors"></a>
## `ai4e_core.abilities.data.save.store.write_named_tensors`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`write_named_tensors(dest: str | Path, payloads: Mapping[str, torch.Tensor | Mapping[str, torch.Tensor]], filemap: Mapping[str, str], *, optional: Sequence[str]=(), overwrite: bool=False, extra_writers: Mapping[str, Any] | None=None) -> Path`
- **规范定义名**：`ai4e_core.abilities.data.save.store.write_named_tensors`

### 用途

预检后写同级临时目录，备份旧目录再提升；恢复失败保留所有证据。

每次提交只记 debug；循环里的常规摘要由 application 阶段输出。

### 导入与签名

```python
from ai4e_core.abilities.data.save.store import write_named_tensors
```

```text
write_named_tensors(dest: str | Path, payloads: Mapping[str, torch.Tensor | Mapping[str, torch.Tensor]], filemap: Mapping[str, str], *, optional: Sequence[str]=(), overwrite: bool=False, extra_writers: Mapping[str, Any] | None=None) -> Path
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dest` | `str | Path` | `必填` |
| `payloads` | `Mapping[str, torch.Tensor | Mapping[str, torch.Tensor]]` | `必填` |
| `filemap` | `Mapping[str, str]` | `必填` |
| `optional` | `Sequence[str]` | `()` |
| `overwrite` | `bool` | `False` |
| `extra_writers` | `Mapping[str, Any] | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Path`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FileExistsError`, `RuntimeError`, `TypeError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.save.store import write_named_tensors

print(signature(write_named_tensors))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.save.store`
- 仓库相对路径：`packages/ai4e-core/abilities/data/save/store.py:40`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.save.store')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-save-store-write-tensor-file"></a>
## `ai4e_core.abilities.data.save.store.write_tensor_file`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`write_tensor_file(path: str | Path, payload, *, overwrite: bool=False) -> Path`
- **规范定义名**：`ai4e_core.abilities.data.save.store.write_tensor_file`

### 用途

原子提交一个张量或具名张量包；失败不替换已有文件。

### 导入与签名

```python
from ai4e_core.abilities.data.save.store import write_tensor_file
```

```text
write_tensor_file(path: str | Path, payload, *, overwrite: bool=False) -> Path
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `str | Path` | `必填` |
| `payload` | `未标注` | `必填` |
| `overwrite` | `bool` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Path`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FileExistsError`, `TypeError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.save.store import write_tensor_file

print(signature(write_tensor_file))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.save.store`
- 仓库相对路径：`packages/ai4e-core/abilities/data/save/store.py:20`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.save.store')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
