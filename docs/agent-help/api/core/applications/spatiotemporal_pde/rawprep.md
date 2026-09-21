<!-- dojo-help: {"domain": "ai4e_core.applications.spatiotemporal_pde.rawprep", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.spatiotemporal_pde.rawprep 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.spatiotemporal_pde.rawprep", "topic_id": "module:ai4e_core.applications.spatiotemporal_pde.rawprep"} -->
# `ai4e_core.applications.spatiotemporal_pde.rawprep` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-spatiotemporal-pde-rawprep-prepare-named-trajectories"></a>
## `ai4e_core.applications.spatiotemporal_pde.rawprep.prepare_named_trajectories`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`prepare_named_trajectories(samples, reader, output, *, session, metadata: dict)`
- **规范定义名**：`ai4e_core.applications.spatiotemporal_pde.rawprep.prepare_named_trajectories`

### 用途

交付带时间字段的原始网格样本，保留原 point/cell 关联及所有帧。

### 导入与签名

```python
from ai4e_core.applications.spatiotemporal_pde.rawprep import prepare_named_trajectories
```

```text
prepare_named_trajectories(samples, reader, output, *, session, metadata: dict)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `samples` | `未标注` | `必填` |
| `reader` | `未标注` | `必填` |
| `output` | `未标注` | `必填` |
| `session` | `未标注` | `必填关键字参数` |
| `metadata` | `dict` | `必填关键字参数` |

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
from ai4e_core.applications.spatiotemporal_pde.rawprep import prepare_named_trajectories

print(signature(prepare_named_trajectories))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`geotransolver/bumper_beam`
- 案例：`geotransolver.bumper_beam`

### 源码位置

- 模块：`ai4e_core.applications.spatiotemporal_pde.rawprep`
- 仓库相对路径：`packages/ai4e-core/applications/spatiotemporal_pde/rawprep.py:22`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.spatiotemporal_pde.rawprep')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-spatiotemporal-pde-rawprep-prepare-physical"></a>
## `ai4e_core.applications.spatiotemporal_pde.rawprep.prepare_physical`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`prepare_physical(reader, options: dict, output: str) -> dict`
- **规范定义名**：`ai4e_core.applications.spatiotemporal_pde.rawprep.prepare_physical`

### 用途

冻结所选轨迹和来源，物理数组与模型输入分开保存。

### 导入与签名

```python
from ai4e_core.applications.spatiotemporal_pde.rawprep import prepare_physical
```

```text
prepare_physical(reader, options: dict, output: str) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `reader` | `未标注` | `必填` |
| `options` | `dict` | `必填` |
| `output` | `str` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.spatiotemporal_pde.rawprep import prepare_physical

print(signature(prepare_physical))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`wdno`
- 案例：`wdno.burgers_base`

### 源码位置

- 模块：`ai4e_core.applications.spatiotemporal_pde.rawprep`
- 仓库相对路径：`packages/ai4e-core/applications/spatiotemporal_pde/rawprep.py:8`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.spatiotemporal_pde.rawprep')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
