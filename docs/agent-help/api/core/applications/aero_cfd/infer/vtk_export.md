<!-- dojo-help: {"domain": "ai4e_core.applications.aero_cfd.infer.vtk_export", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.aero_cfd.infer.vtk_export 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.aero_cfd.infer.vtk_export", "topic_id": "module:ai4e_core.applications.aero_cfd.infer.vtk_export"} -->
# `ai4e_core.applications.aero_cfd.infer.vtk_export` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-aero-cfd-infer-vtk-export-merge-full-mesh-record"></a>
## `ai4e_core.applications.aero_cfd.infer.vtk_export.merge_full_mesh_record`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`merge_full_mesh_record(metadata: dict, domain: str, record: dict) -> None`
- **规范定义名**：`ai4e_core.applications.aero_cfd.infer.vtk_export.merge_full_mesh_record`

### 用途

完整网格占用域键；已有锚点点云改挂 ``{domain}_anchors``。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.infer.vtk_export import merge_full_mesh_record
```

```text
merge_full_mesh_record(metadata: dict, domain: str, record: dict) -> None
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `metadata` | `dict` | `必填` |
| `domain` | `str` | `必填` |
| `record` | `dict` | `必填` |

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
from ai4e_core.applications.aero_cfd.infer.vtk_export import merge_full_mesh_record

print(signature(merge_full_mesh_record))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.infer.vtk_export`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/infer/vtk_export.py:212`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.infer.vtk_export')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-infer-vtk-export-original-dataset-root"></a>
## `ai4e_core.applications.aero_cfd.infer.vtk_export.original_dataset_root`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`original_dataset_root(config: dict) -> Path | None`
- **规范定义名**：`ai4e_core.applications.aero_cfd.infer.vtk_export.original_dataset_root`

### 用途

原始网格根目录；平台配置常把路径放在 inputs.rawprep.source，不回写用户树。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.infer.vtk_export import original_dataset_root
```

```text
original_dataset_root(config: dict) -> Path | None
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `dict` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Path | None`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.infer.vtk_export import original_dataset_root

print(signature(original_dataset_root))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.infer.vtk_export`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/infer/vtk_export.py:23`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.infer.vtk_export')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-infer-vtk-export-record-vtk-status"></a>
## `ai4e_core.applications.aero_cfd.infer.vtk_export.record_vtk_status`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`record_vtk_status(manifest_path: str | Path, status: dict, *, channel: str | None=None) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.infer.vtk_export.record_vtk_status`

### 用途

把 VTK 状态写进样本清单；点云与网格化分频道，跳过一种不盖掉另一种。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.infer.vtk_export import record_vtk_status
```

```text
record_vtk_status(manifest_path: str | Path, status: dict, *, channel: str | None=None) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `manifest_path` | `str | Path` | `必填` |
| `status` | `dict` | `必填` |
| `channel` | `str | None` | `None` |

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
from ai4e_core.applications.aero_cfd.infer.vtk_export import record_vtk_status

print(signature(record_vtk_status))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.infer.vtk_export`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/infer/vtk_export.py:67`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.infer.vtk_export')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-infer-vtk-export-sample-identity"></a>
## `ai4e_core.applications.aero_cfd.infer.vtk_export.sample_identity`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`sample_identity(metadata: dict, *, fallback: str | None=None) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.infer.vtk_export.sample_identity`

### 用途

稳定样本身份；外流沿用 param1/<设计号>，与处理后目录同一编号。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.infer.vtk_export import sample_identity
```

```text
sample_identity(metadata: dict, *, fallback: str | None=None) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `metadata` | `dict` | `必填` |
| `fallback` | `str | None` | `None` |

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
from ai4e_core.applications.aero_cfd.infer.vtk_export import sample_identity

print(signature(sample_identity))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.infer.vtk_export`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/infer/vtk_export.py:38`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.infer.vtk_export')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-infer-vtk-export-skip-vtk"></a>
## `ai4e_core.applications.aero_cfd.infer.vtk_export.skip_vtk`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`skip_vtk(manifest_path: str | Path, reason: str, *, channel: str | None=None, **extra) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.infer.vtk_export.skip_vtk`

### 用途

明确记录未写出 VTK 的原因，并打阶段日志。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.infer.vtk_export import skip_vtk
```

```text
skip_vtk(manifest_path: str | Path, reason: str, *, channel: str | None=None, **extra) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `manifest_path` | `str | Path` | `必填` |
| `reason` | `str` | `必填` |
| `channel` | `str | None` | `None` |
| `**extra` | `未标注` | `可变关键字参数` |

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
from ai4e_core.applications.aero_cfd.infer.vtk_export import skip_vtk

print(signature(skip_vtk))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.infer.vtk_export`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/infer/vtk_export.py:112`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.infer.vtk_export')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-infer-vtk-export-stamp-mesh-identity"></a>
## `ai4e_core.applications.aero_cfd.infer.vtk_export.stamp_mesh_identity`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`stamp_mesh_identity(path: str | Path, identity: dict) -> None`
- **规范定义名**：`ai4e_core.applications.aero_cfd.infer.vtk_export.stamp_mesh_identity`

### 用途

给已写出的 VTP/VTU 补样本身份，不改点场。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.infer.vtk_export import stamp_mesh_identity
```

```text
stamp_mesh_identity(path: str | Path, identity: dict) -> None
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `str | Path` | `必填` |
| `identity` | `dict` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`None`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`OSError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.infer.vtk_export import stamp_mesh_identity

print(signature(stamp_mesh_identity))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.infer.vtk_export`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/infer/vtk_export.py:221`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.infer.vtk_export')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-infer-vtk-export-vtk-status"></a>
## `ai4e_core.applications.aero_cfd.infer.vtk_export.vtk_status`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`vtk_status(*, exported: bool, reason: str | None=None, kind: str | None=None, **extra) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.infer.vtk_export.vtk_status`

### 用途

给清单和页面的跳过/成功记录，不能只用缺文件表示关闭。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.infer.vtk_export import vtk_status
```

```text
vtk_status(*, exported: bool, reason: str | None=None, kind: str | None=None, **extra) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `exported` | `bool` | `必填关键字参数` |
| `reason` | `str | None` | `None` |
| `kind` | `str | None` | `None` |
| `**extra` | `未标注` | `可变关键字参数` |

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
from ai4e_core.applications.aero_cfd.infer.vtk_export import vtk_status

print(signature(vtk_status))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.infer.vtk_export`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/infer/vtk_export.py:52`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.infer.vtk_export')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-infer-vtk-export-write-anchor-prediction-vtk"></a>
## `ai4e_core.applications.aero_cfd.infer.vtk_export.write_anchor_prediction_vtk`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`write_anchor_prediction_vtk(manifest_path: str | Path, *, overwrite: bool=False, committed=None) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.infer.vtk_export.write_anchor_prediction_vtk`

### 用途

把已保存的预测和真值写成同目录点云 VTK，场名沿用 ``.prediction`` / ``.truth``。

锚点没有完整单元，不能冒充原始网格；完整网格由查询步骤另行交付。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.infer.vtk_export import write_anchor_prediction_vtk
```

```text
write_anchor_prediction_vtk(manifest_path: str | Path, *, overwrite: bool=False, committed=None) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `manifest_path` | `str | Path` | `必填` |
| `overwrite` | `bool` | `False` |
| `committed` | `未标注` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FileExistsError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.infer.vtk_export import write_anchor_prediction_vtk

print(signature(write_anchor_prediction_vtk))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.infer.vtk_export`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/infer/vtk_export.py:127`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.infer.vtk_export')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
