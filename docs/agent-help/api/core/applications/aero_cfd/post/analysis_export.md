<!-- dojo-help: {"domain": "ai4e_core.applications.aero_cfd.post.analysis_export", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.aero_cfd.post.analysis_export 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.aero_cfd.post.analysis_export", "topic_id": "module:ai4e_core.applications.aero_cfd.post.analysis_export"} -->
# `ai4e_core.applications.aero_cfd.post.analysis_export` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-aero-cfd-post-analysis-export-safe-name"></a>
## `ai4e_core.applications.aero_cfd.post.analysis_export.safe_name`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`safe_name(value: Any) -> str`
- **规范定义名**：`ai4e_core.applications.aero_cfd.post.analysis_export.safe_name`

### 用途

仅允许单个可移植文件名，禁止相对目录穿越。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.post.analysis_export import safe_name
```

```text
safe_name(value: Any) -> str
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `value` | `Any` | `必填` |

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
from ai4e_core.applications.aero_cfd.post.analysis_export import safe_name

print(signature(safe_name))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.post.analysis_export`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/post/analysis_export.py:20`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.post.analysis_export')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-post-analysis-export-save-sample"></a>
## `ai4e_core.applications.aero_cfd.post.analysis_export.save_sample`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`save_sample(sample: dict, *, output: str | Path, meshes: dict | None=None, images: dict | None=None, profiles: dict | None=None, metrics: list[dict] | None=None, statistics: dict | None=None, overwrite: bool=False) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.post.analysis_export.save_sample`

### 用途

同目录暂存整份样本；失败保留原成品，不发布成功清单。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.post.analysis_export import save_sample
```

```text
save_sample(sample: dict, *, output: str | Path, meshes: dict | None=None, images: dict | None=None, profiles: dict | None=None, metrics: list[dict] | None=None, statistics: dict | None=None, overwrite: bool=False) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `sample` | `dict` | `必填` |
| `output` | `str | Path` | `必填关键字参数` |
| `meshes` | `dict | None` | `None` |
| `images` | `dict | None` | `None` |
| `profiles` | `dict | None` | `None` |
| `metrics` | `list[dict] | None` | `None` |
| `statistics` | `dict | None` | `None` |
| `overwrite` | `bool` | `False` |

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
from ai4e_core.applications.aero_cfd.post.analysis_export import save_sample

print(signature(save_sample))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.physical_visualization`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.post.analysis_export`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/post/analysis_export.py:83`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.post.analysis_export')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-post-analysis-export-write-metrics"></a>
## `ai4e_core.applications.aero_cfd.post.analysis_export.write_metrics`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`write_metrics(path: str | Path, rows: list[dict], statistics: dict | None=None) -> None`
- **规范定义名**：`ai4e_core.applications.aero_cfd.post.analysis_export.write_metrics`

### 用途

长表完整保存逐指标值、数量和不可定义原因。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.post.analysis_export import write_metrics
```

```text
write_metrics(path: str | Path, rows: list[dict], statistics: dict | None=None) -> None
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `str | Path` | `必填` |
| `rows` | `list[dict]` | `必填` |
| `statistics` | `dict | None` | `None` |

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
from ai4e_core.applications.aero_cfd.post.analysis_export import write_metrics

print(signature(write_metrics))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.post.analysis_export`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/post/analysis_export.py:28`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.post.analysis_export')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
