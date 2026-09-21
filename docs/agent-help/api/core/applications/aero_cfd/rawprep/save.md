<!-- dojo-help: {"domain": "ai4e_core.applications.aero_cfd.rawprep.save", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.aero_cfd.rawprep.save 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.aero_cfd.rawprep.save", "topic_id": "module:ai4e_core.applications.aero_cfd.rawprep.save"} -->
# `ai4e_core.applications.aero_cfd.rawprep.save` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-aero-cfd-rawprep-save-sampleresult"></a>
## `ai4e_core.applications.aero_cfd.rawprep.save.SampleResult`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`class SampleResult`
- **规范定义名**：`ai4e_core.applications.aero_cfd.rawprep.save.SampleResult`

### 用途

已提交或预检后的轻量样本结果，不携带网格或数组。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.rawprep.save import SampleResult
```

```text
class SampleResult
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`SampleResult`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.rawprep.save import SampleResult

print(signature(SampleResult))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.rawprep.save`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/rawprep/save.py:12`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.rawprep.save')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-rawprep-save-sample-destination"></a>
## `ai4e_core.applications.aero_cfd.rawprep.save.sample_destination`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`sample_destination(config: dict, sample: str | Path | None) -> Path`
- **规范定义名**：`ai4e_core.applications.aero_cfd.rawprep.save.sample_destination`

### 用途

解析实际样本目录，禁止样本或子目录逃离输出根。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.rawprep.save import sample_destination
```

```text
sample_destination(config: dict, sample: str | Path | None) -> Path
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `dict` | `必填` |
| `sample` | `str | Path | None` | `必填` |

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
from ai4e_core.applications.aero_cfd.rawprep.save import sample_destination

print(signature(sample_destination))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.rawprep.save`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/rawprep/save.py:34`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.rawprep.save')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-rawprep-save-tensorize"></a>
## `ai4e_core.applications.aero_cfd.rawprep.save.tensorize`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`tensorize(ctx: dict) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.rawprep.save.tensorize`

### 用途

按显式路由打包张量；单元场与点场均由业务配置选择。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.rawprep.save import tensorize
```

```text
tensorize(ctx: dict) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `ctx` | `dict` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.rawprep.save import tensorize

print(signature(tensorize))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.rawprep.save`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/rawprep/save.py:49`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.rawprep.save')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-rawprep-save-write-tensors"></a>
## `ai4e_core.applications.aero_cfd.rawprep.save.write_tensors`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`write_tensors(ctx: dict) -> dict[str, SampleResult]`
- **规范定义名**：`ai4e_core.applications.aero_cfd.rawprep.save.write_tensors`

### 用途

dry-run 和提交共用预检；只返回轻量结果，不把整批数组带回 run。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.rawprep.save import write_tensors
```

```text
write_tensors(ctx: dict) -> dict[str, SampleResult]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `ctx` | `dict` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, SampleResult]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.rawprep.save import write_tensors

print(signature(write_tensors))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.rawprep.save`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/rawprep/save.py:68`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.rawprep.save')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
