<!-- dojo-help: {"domain": "ai4e_core.abilities.data.stats.load", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.data.stats.load 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.data.stats.load", "topic_id": "module:ai4e_core.abilities.data.stats.load"} -->
# `ai4e_core.abilities.data.stats.load` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-data-stats-load-load-statistics"></a>
## `ai4e_core.abilities.data.stats.load.load_statistics`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`load_statistics(path: str | Path) -> dict[str, Any]`
- **规范定义名**：`ai4e_core.abilities.data.stats.load.load_statistics`

### 用途

从 YAML 或 JSON 读入统计量映射。

Args:
    path: 已发布或重算后的统计量文件。

Returns:
    文件中的键值映射。

Raises:
    FileNotFoundError: 文件不存在。
    ValueError: 扩展名不支持，或内容不是映射。

### 导入与签名

```python
from ai4e_core.abilities.data.stats.load import load_statistics
```

```text
load_statistics(path: str | Path) -> dict[str, Any]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `str | Path` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, Any]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FileNotFoundError`, `TypeError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.stats.load import load_statistics

print(signature(load_statistics))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.stats.load`
- 仓库相对路径：`packages/ai4e-core/abilities/data/stats/load.py:16`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.stats.load')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-stats-load-write-statistics"></a>
## `ai4e_core.abilities.data.stats.load.write_statistics`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`write_statistics(path: str | Path, stats: dict[str, Any]) -> Path`
- **规范定义名**：`ai4e_core.abilities.data.stats.load.write_statistics`

### 用途

把统计量写成 YAML 或 JSON。

Args:
    path: 目标路径，由扩展名选择格式。
    stats: 要落盘的映射。

Returns:
    写出后的路径。

### 导入与签名

```python
from ai4e_core.abilities.data.stats.load import write_statistics
```

```text
write_statistics(path: str | Path, stats: dict[str, Any]) -> Path
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `str | Path` | `必填` |
| `stats` | `dict[str, Any]` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Path`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.stats.load import write_statistics

print(signature(write_statistics))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.stats.load`
- 仓库相对路径：`packages/ai4e-core/abilities/data/stats/load.py:46`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.stats.load')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
