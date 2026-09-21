<!-- dojo-help: {"domain": "ai4e_core.applications.aero_cfd.rawprep.descriptor", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.aero_cfd.rawprep.descriptor 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.aero_cfd.rawprep.descriptor", "topic_id": "module:ai4e_core.applications.aero_cfd.rawprep.descriptor"} -->
# `ai4e_core.applications.aero_cfd.rawprep.descriptor` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-aero-cfd-rawprep-descriptor-dataset-component"></a>
## `ai4e_core.applications.aero_cfd.rawprep.descriptor.dataset_component`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`dataset_component(config)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.rawprep.descriptor.dataset_component`

### 用途

解析已声明的组件；仅历史配置识别留在算法边界。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.rawprep.descriptor import dataset_component
```

```text
dataset_component(config)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `未标注` | `必填` |

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
from ai4e_core.applications.aero_cfd.rawprep.descriptor import dataset_component

print(signature(dataset_component))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`, `parametric_pde`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `parametric_pde.advection`, `parametric_pde.burgers`, `parametric_pde.convection_diffusion`, `parametric_pde.diffusion_trapezoid`, `parametric_pde.neumann_diffusion`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.rawprep.descriptor`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/rawprep/descriptor.py:79`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.rawprep.descriptor')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-rawprep-descriptor-load-description"></a>
## `ai4e_core.applications.aero_cfd.rawprep.descriptor.load_description`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`load_description(path, config=None) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.rawprep.descriptor.load_description`

### 用途

读取组件提供的 manifest；旧自定义 manifest 可继承已安装的处理描述。

来源文件名写入 source_files，并补到对应域的输出，供页面回填提取对话框。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.rawprep.descriptor import load_description
```

```text
load_description(path, config=None) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `未标注` | `必填` |
| `config` | `未标注` | `None` |

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
from ai4e_core.applications.aero_cfd.rawprep.descriptor import load_description

print(signature(load_description))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.rawprep.descriptor`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/rawprep/descriptor.py:44`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.rawprep.descriptor')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-rawprep-descriptor-merge-defaults"></a>
## `ai4e_core.applications.aero_cfd.rawprep.descriptor.merge_defaults`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`merge_defaults(defaults: dict, values: dict) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.rawprep.descriptor.merge_defaults`

### 用途

递归补缺；显式空映射、空列表及 False 保持用户意图。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.rawprep.descriptor import merge_defaults
```

```text
merge_defaults(defaults: dict, values: dict) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `defaults` | `dict` | `必填` |
| `values` | `dict` | `必填` |

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
from ai4e_core.applications.aero_cfd.rawprep.descriptor import merge_defaults

print(signature(merge_defaults))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.rawprep.descriptor`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/rawprep/descriptor.py:10`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.rawprep.descriptor')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-rawprep-descriptor-primary-format"></a>
## `ai4e_core.applications.aero_cfd.rawprep.descriptor.primary_format`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`primary_format(formats: list[str]) -> str`
- **规范定义名**：`ai4e_core.applications.aero_cfd.rawprep.descriptor.primary_format`

### 用途

读盘优先 PT，否则取声明的第一种格式。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.rawprep.descriptor import primary_format
```

```text
primary_format(formats: list[str]) -> str
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `formats` | `list[str]` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`str`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.rawprep.descriptor import primary_format

print(signature(primary_format))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.rawprep.descriptor`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/rawprep/descriptor.py:171`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.rawprep.descriptor')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-rawprep-descriptor-reconcile-format-keys"></a>
## `ai4e_core.applications.aero_cfd.rawprep.descriptor.reconcile_format_keys`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`reconcile_format_keys(defaults: dict, user: dict, merged: dict) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.rawprep.descriptor.reconcile_format_keys`

### 用途

平台已提供的格式选项覆盖清单默认和旧单键，生成配置不向用户报冲突。

页面写 `formats`。清单或历史文件里的 `format` 只在没有平台列表时使用。
两键并存时只保留平台列表，不提示、不拒绝。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.rawprep.descriptor import reconcile_format_keys
```

```text
reconcile_format_keys(defaults: dict, user: dict, merged: dict) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `defaults` | `dict` | `必填` |
| `user` | `dict` | `必填` |
| `merged` | `dict` | `必填` |

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
from ai4e_core.applications.aero_cfd.rawprep.descriptor import reconcile_format_keys

print(signature(reconcile_format_keys))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.rawprep.descriptor`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/rawprep/descriptor.py:22`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.rawprep.descriptor')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-rawprep-descriptor-resolve-rawprep"></a>
## `ai4e_core.applications.aero_cfd.rawprep.descriptor.resolve_rawprep`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`resolve_rawprep(config, *, validate=False, config_path=None)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.rawprep.descriptor.resolve_rawprep`

### 用途

返回统一公开配置；无描述的用户组件保持原样。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.rawprep.descriptor import resolve_rawprep
```

```text
resolve_rawprep(config, *, validate=False, config_path=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `未标注` | `必填` |
| `validate` | `未标注` | `False` |
| `config_path` | `未标注` | `None` |

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
from ai4e_core.applications.aero_cfd.rawprep.descriptor import resolve_rawprep

print(signature(resolve_rawprep))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.rawprep.descriptor`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/rawprep/descriptor.py:88`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.rawprep.descriptor')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-rawprep-descriptor-resolved-formats"></a>
## `ai4e_core.applications.aero_cfd.rawprep.descriptor.resolved_formats`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`resolved_formats(raw: dict) -> list[str]`
- **规范定义名**：`ai4e_core.applications.aero_cfd.rawprep.descriptor.resolved_formats`

### 用途

解析输出格式；平台 `formats` 覆盖旧 `format`，两键并存不拒绝。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.rawprep.descriptor import resolved_formats
```

```text
resolved_formats(raw: dict) -> list[str]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `raw` | `dict` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`list[str]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.rawprep.descriptor import resolved_formats

print(signature(resolved_formats))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.rawprep.descriptor`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/rawprep/descriptor.py:153`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.rawprep.descriptor')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-rawprep-descriptor-resolved-workers"></a>
## `ai4e_core.applications.aero_cfd.rawprep.descriptor.resolved_workers`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`resolved_workers(raw: dict) -> int`
- **规范定义名**：`ai4e_core.applications.aero_cfd.rawprep.descriptor.resolved_workers`

### 用途

解析并行样本线程数；缺省 1，超出 1–64 拒绝。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.rawprep.descriptor import resolved_workers
```

```text
resolved_workers(raw: dict) -> int
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `raw` | `dict` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`int`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.rawprep.descriptor import resolved_workers

print(signature(resolved_workers))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.rawprep.descriptor`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/rawprep/descriptor.py:176`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.rawprep.descriptor')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-rawprep-descriptor-selected-outputs"></a>
## `ai4e_core.applications.aero_cfd.rawprep.descriptor.selected_outputs`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`selected_outputs(raw, profile)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.rawprep.descriptor.selected_outputs`

### 用途

将逐场选择映射为来源和文件名；旧容器独立保留。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.rawprep.descriptor import selected_outputs
```

```text
selected_outputs(raw, profile)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `raw` | `未标注` | `必填` |
| `profile` | `未标注` | `必填` |

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
from ai4e_core.applications.aero_cfd.rawprep.descriptor import selected_outputs

print(signature(selected_outputs))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.rawprep.descriptor`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/rawprep/descriptor.py:134`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.rawprep.descriptor')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-rawprep-descriptor-validate-rawprep"></a>
## `ai4e_core.applications.aero_cfd.rawprep.descriptor.validate_rawprep`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`validate_rawprep(raw: dict, profile: dict) -> None`
- **规范定义名**：`ai4e_core.applications.aero_cfd.rawprep.descriptor.validate_rawprep`

### 用途

校验可表达的处理配置与功能依赖；未知扩展由复制 recipe 自行声明。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.rawprep.descriptor import validate_rawprep
```

```text
validate_rawprep(raw: dict, profile: dict) -> None
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `raw` | `dict` | `必填` |
| `profile` | `dict` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`None`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.rawprep.descriptor import validate_rawprep

print(signature(validate_rawprep))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.rawprep.descriptor`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/rawprep/descriptor.py:184`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.rawprep.descriptor')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
