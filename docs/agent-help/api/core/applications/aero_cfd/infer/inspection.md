<!-- dojo-help: {"domain": "ai4e_core.applications.aero_cfd.infer.inspection", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.aero_cfd.infer.inspection 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.aero_cfd.infer.inspection", "topic_id": "module:ai4e_core.applications.aero_cfd.infer.inspection"} -->
# `ai4e_core.applications.aero_cfd.infer.inspection` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-aero-cfd-infer-inspection-available-devices"></a>
## `ai4e_core.applications.aero_cfd.infer.inspection.available_devices`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`available_devices() -> list[str]`
- **规范定义名**：`ai4e_core.applications.aero_cfd.infer.inspection.available_devices`

### 用途

仅列实际可用设备，任务层另行决定占用和排队。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.infer.inspection import available_devices
```

```text
available_devices() -> list[str]
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

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
from ai4e_core.applications.aero_cfd.infer.inspection import available_devices

print(signature(available_devices))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.infer.inspection`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/infer/inspection.py:213`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.infer.inspection')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-infer-inspection-inspect-checkpoint"></a>
## `ai4e_core.applications.aero_cfd.infer.inspection.inspect_checkpoint`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`inspect_checkpoint(path, *, preparation=None, config=None) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.infer.inspection.inspect_checkpoint`

### 用途

读取轻量权重元信息；提供 preparation/config 时同时进行来源检查。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.infer.inspection import inspect_checkpoint
```

```text
inspect_checkpoint(path, *, preparation=None, config=None) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `未标注` | `必填` |
| `preparation` | `未标注` | `None` |
| `config` | `未标注` | `None` |

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
from ai4e_core.applications.aero_cfd.infer.inspection import inspect_checkpoint

print(signature(inspect_checkpoint))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.infer.inspection`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/infer/inspection.py:123`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.infer.inspection')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-infer-inspection-inspect-inputs"></a>
## `ai4e_core.applications.aero_cfd.infer.inspection.inspect_inputs`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`inspect_inputs(checkpoint, preparation, config, config_dir) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.infer.inspection.inspect_inputs`

### 用途

检查当前任务配置与固定输入；只通过配置指定的公开组件加载能力。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.infer.inspection import inspect_inputs
```

```text
inspect_inputs(checkpoint, preparation, config, config_dir) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `checkpoint` | `未标注` | `必填` |
| `preparation` | `未标注` | `必填` |
| `config` | `未标注` | `必填` |
| `config_dir` | `未标注` | `必填` |

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
from ai4e_core.applications.aero_cfd.infer.inspection import inspect_inputs

print(signature(inspect_inputs))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.infer.inspection`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/infer/inspection.py:148`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.infer.inspection')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
