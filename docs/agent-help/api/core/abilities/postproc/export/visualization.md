<!-- dojo-help: {"domain": "ai4e_core.abilities.postproc.export.visualization", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.postproc.export.visualization 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.postproc.export.visualization", "topic_id": "module:ai4e_core.abilities.postproc.export.visualization"} -->
# `ai4e_core.abilities.postproc.export.visualization` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-postproc-export-visualization-save-image"></a>
## `ai4e_core.abilities.postproc.export.visualization.save_image`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`save_image(image: Any, path: str | Path) -> Path`
- **规范定义名**：`ai4e_core.abilities.postproc.export.visualization.save_image`

### 用途

写出 RGB/RGBA PNG，拒绝错误尺寸、类型或后缀。

### 导入与签名

```python
from ai4e_core.abilities.postproc.export.visualization import save_image
```

```text
save_image(image: Any, path: str | Path) -> Path
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `image` | `Any` | `必填` |
| `path` | `str | Path` | `必填` |

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
from ai4e_core.abilities.postproc.export.visualization import save_image

print(signature(save_image))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.export.visualization`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/export/visualization.py:14`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.export.visualization')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-export-visualization-save-mesh"></a>
## `ai4e_core.abilities.postproc.export.visualization.save_mesh`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`save_mesh(mesh: Any, path: str | Path) -> Path`
- **规范定义名**：`ai4e_core.abilities.postproc.export.visualization.save_mesh`

### 用途

以 VTP 或 VTU 保留数组和真实拓扑，禁止静默丢失体单元。

### 导入与签名

```python
from ai4e_core.abilities.postproc.export.visualization import save_mesh
```

```text
save_mesh(mesh: Any, path: str | Path) -> Path
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `mesh` | `Any` | `必填` |
| `path` | `str | Path` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Path`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`OSError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.postproc.export.visualization import save_mesh

print(signature(save_mesh))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.export.visualization`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/export/visualization.py:29`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.export.visualization')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-export-visualization-save-profile"></a>
## `ai4e_core.abilities.postproc.export.visualization.save_profile`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`save_profile(profile: dict, path: str | Path) -> Path`
- **规范定义名**：`ai4e_core.abilities.postproc.export.visualization.save_profile`

### 用途

采样表保留域外点和完整分量，无效数据列留空。

### 导入与签名

```python
from ai4e_core.abilities.postproc.export.visualization import save_profile
```

```text
save_profile(profile: dict, path: str | Path) -> Path
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `profile` | `dict` | `必填` |
| `path` | `str | Path` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Path`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.postproc.export.visualization import save_profile

print(signature(save_profile))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.export.visualization`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/export/visualization.py:57`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.export.visualization')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
