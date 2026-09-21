<!-- dojo-help: {"domain": "ai4e_contrib.application.datasets.geothermal_cmg.adapter", "kind": "api", "layer": "contrib.application", "summary": "ai4e_contrib.application.datasets.geothermal_cmg.adapter 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.application.datasets.geothermal_cmg.adapter", "topic_id": "module:ai4e_contrib.application.datasets.geothermal_cmg.adapter"} -->
# `ai4e_contrib.application.datasets.geothermal_cmg.adapter` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-application-datasets-geothermal-cmg-adapter-audit"></a>
## `ai4e_contrib.application.datasets.geothermal_cmg.adapter.audit`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`audit(root: Path)`
- **规范定义名**：`ai4e_contrib.application.datasets.geothermal_cmg.adapter.audit`

### 用途

核验全部发布文件，声明演示场不是独立真实值。

### 导入与签名

```python
from ai4e_contrib.application.datasets.geothermal_cmg.adapter import audit
```

```text
audit(root: Path)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `root` | `Path` | `必填` |

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
from ai4e_contrib.application.datasets.geothermal_cmg.adapter import audit

print(signature(audit))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`pcno`
- 案例：`geothermal.pcno`, `recipe_extensions.wdno`

### 源码位置

- 模块：`ai4e_contrib.application.datasets.geothermal_cmg.adapter`
- 仓库相对路径：`packages/ai4e-contrib/application/datasets/geothermal_cmg/adapter.py:48`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.datasets.geothermal_cmg.adapter')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-datasets-geothermal-cmg-adapter-finite-tensor"></a>
## `ai4e_contrib.application.datasets.geothermal_cmg.adapter.finite_tensor`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`finite_tensor(value, shape, name)`
- **规范定义名**：`ai4e_contrib.application.datasets.geothermal_cmg.adapter.finite_tensor`

### 用途

拒绝维度、精度或有限性不符合发布格式的字段。

### 导入与签名

```python
from ai4e_contrib.application.datasets.geothermal_cmg.adapter import finite_tensor
```

```text
finite_tensor(value, shape, name)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `value` | `未标注` | `必填` |
| `shape` | `未标注` | `必填` |
| `name` | `未标注` | `必填` |

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
from ai4e_contrib.application.datasets.geothermal_cmg.adapter import finite_tensor

print(signature(finite_tensor))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.datasets.geothermal_cmg.adapter`
- 仓库相对路径：`packages/ai4e-contrib/application/datasets/geothermal_cmg/adapter.py:10`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.datasets.geothermal_cmg.adapter')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-datasets-geothermal-cmg-adapter-inspect-chunk"></a>
## `ai4e_contrib.application.datasets.geothermal_cmg.adapter.inspect_chunk`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`inspect_chunk(chunk, name, *, count=3, grid=GRID, labels=True)`
- **规范定义名**：`ai4e_contrib.application.datasets.geothermal_cmg.adapter.inspect_chunk`

### 用途

核对批次及井标签行数，返回稳定的输入身份。

### 导入与签名

```python
from ai4e_contrib.application.datasets.geothermal_cmg.adapter import inspect_chunk
```

```text
inspect_chunk(chunk, name, *, count=3, grid=GRID, labels=True)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `chunk` | `未标注` | `必填` |
| `name` | `未标注` | `必填` |
| `count` | `未标注` | `3` |
| `grid` | `未标注` | `GRID` |
| `labels` | `未标注` | `True` |

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
from ai4e_contrib.application.datasets.geothermal_cmg.adapter import inspect_chunk

print(signature(inspect_chunk))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.datasets.geothermal_cmg.adapter`
- 仓库相对路径：`packages/ai4e-contrib/application/datasets/geothermal_cmg/adapter.py:17`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.datasets.geothermal_cmg.adapter')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
