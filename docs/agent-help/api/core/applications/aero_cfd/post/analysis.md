<!-- dojo-help: {"domain": "ai4e_core.applications.aero_cfd.post.analysis", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.aero_cfd.post.analysis 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.aero_cfd.post.analysis", "topic_id": "module:ai4e_core.applications.aero_cfd.post.analysis"} -->
# `ai4e_core.applications.aero_cfd.post.analysis` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-aero-cfd-post-analysis-analysissource"></a>
## `ai4e_core.applications.aero_cfd.post.analysis.AnalysisSource`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`class AnalysisSource`
- **规范定义名**：`ai4e_core.applications.aero_cfd.post.analysis.AnalysisSource`

### 用途

仅持有样本引用和固定来源，不持有批量数组或网格。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.post.analysis import AnalysisSource
```

```text
class AnalysisSource
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`AnalysisSource`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.post.analysis import AnalysisSource

print(signature(AnalysisSource))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.post.analysis`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/post/analysis.py:16`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.post.analysis')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-post-analysis-check-analysis"></a>
## `ai4e_core.applications.aero_cfd.post.analysis.check_analysis`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`check_analysis(source: AnalysisSource, *, settings: dict) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.post.analysis.check_analysis`

### 用途

检查已声明字段和输出能力参数，不发布产物。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.post.analysis import check_analysis
```

```text
check_analysis(source: AnalysisSource, *, settings: dict) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `source` | `AnalysisSource` | `必填` |
| `settings` | `dict` | `必填关键字参数` |

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
from ai4e_core.applications.aero_cfd.post.analysis import check_analysis

print(signature(check_analysis))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.geotransolver_aero`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.post.analysis`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/post/analysis.py:42`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.post.analysis')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-post-analysis-open-analysis"></a>
## `ai4e_core.applications.aero_cfd.post.analysis.open_analysis`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`open_analysis(reference: Any, *, samples: Any=None) -> AnalysisSource`
- **规范定义名**：`ai4e_core.applications.aero_cfd.post.analysis.open_analysis`

### 用途

打开已提交推理清单并选择样本；不加载模型与网格。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.post.analysis import open_analysis
```

```text
open_analysis(reference: Any, *, samples: Any=None) -> AnalysisSource
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `reference` | `Any` | `必填` |
| `samples` | `Any` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`AnalysisSource`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.post.analysis import open_analysis

print(signature(open_analysis))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.geotransolver_aero`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.post.analysis`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/post/analysis.py:24`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.post.analysis')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-post-analysis-publish-analysis"></a>
## `ai4e_core.applications.aero_cfd.post.analysis.publish_analysis`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`publish_analysis(rows: list[dict], *, source: AnalysisSource, output: str | Path, failures: Any=()) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.post.analysis.publish_analysis`

### 用途

汇总已提交样本的等权指标，保留原推理结果引用以兼容消费者。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.post.analysis import publish_analysis
```

```text
publish_analysis(rows: list[dict], *, source: AnalysisSource, output: str | Path, failures: Any=()) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `rows` | `list[dict]` | `必填` |
| `source` | `AnalysisSource` | `必填关键字参数` |
| `output` | `str | Path` | `必填关键字参数` |
| `failures` | `Any` | `()` |

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
from ai4e_core.applications.aero_cfd.post.analysis import publish_analysis

print(signature(publish_analysis))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.geotransolver_aero`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.post.analysis`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/post/analysis.py:62`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.post.analysis')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
