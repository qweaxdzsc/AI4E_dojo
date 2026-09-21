<!-- dojo-help: {"domain": "ai4e_core.applications.aero_cfd.infer.anchor_export", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.aero_cfd.infer.anchor_export 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.aero_cfd.infer.anchor_export", "topic_id": "module:ai4e_core.applications.aero_cfd.infer.anchor_export"} -->
# `ai4e_core.applications.aero_cfd.infer.anchor_export` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-aero-cfd-infer-anchor-export-save-anchor-sample"></a>
## `ai4e_core.applications.aero_cfd.infer.anchor_export.save_anchor_sample`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`save_anchor_sample(dest: str | Path, payloads: dict, *, overwrite: bool=False, export_vtk: bool=False, on_commit=None)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.infer.anchor_export.save_anchor_sample`

### 用途

把一个样本的物理预测和归一化锚点坐标写入数据目录。

点云写入同目录的 ``surface.vtp`` / ``volume.vtp``，没有原始网格单元。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.infer.anchor_export import save_anchor_sample
```

```text
save_anchor_sample(dest: str | Path, payloads: dict, *, overwrite: bool=False, export_vtk: bool=False, on_commit=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dest` | `str | Path` | `必填` |
| `payloads` | `dict` | `必填` |
| `overwrite` | `bool` | `False` |
| `export_vtk` | `bool` | `False` |
| `on_commit` | `未标注` | `None` |

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
from ai4e_core.applications.aero_cfd.infer.anchor_export import save_anchor_sample

print(signature(save_anchor_sample))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.infer.anchor_export`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/infer/anchor_export.py:16`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.infer.anchor_export')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-infer-anchor-export-save-reference-sample"></a>
## `ai4e_core.applications.aero_cfd.infer.anchor_export.save_reference_sample`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`save_reference_sample(root, index: int, payloads: dict, *, overwrite=False, export_vtk=False, on_commit=None)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.infer.anchor_export.save_reference_sample`

### 用途

按测试顺序交付兼容的单样本张量包与 VTK 路径，编号由流程生成。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.infer.anchor_export import save_reference_sample
```

```text
save_reference_sample(root, index: int, payloads: dict, *, overwrite=False, export_vtk=False, on_commit=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `root` | `未标注` | `必填` |
| `index` | `int` | `必填` |
| `payloads` | `dict` | `必填` |
| `overwrite` | `未标注` | `False` |
| `export_vtk` | `未标注` | `False` |
| `on_commit` | `未标注` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FileExistsError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.infer.anchor_export import save_reference_sample

print(signature(save_reference_sample))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.infer.anchor_export`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/infer/anchor_export.py:59`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.infer.anchor_export')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
