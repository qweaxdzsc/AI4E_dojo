<!-- dojo-help: {"domain": "ai4e_core.applications.aero_cfd.rawprep.read", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.aero_cfd.rawprep.read 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.aero_cfd.rawprep.read", "topic_id": "module:ai4e_core.applications.aero_cfd.rawprep.read"} -->
# `ai4e_core.applications.aero_cfd.rawprep.read` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-aero-cfd-rawprep-read-domainresult"></a>
## `ai4e_core.applications.aero_cfd.rawprep.read.DomainResult`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`class DomainResult`
- **规范定义名**：`ai4e_core.applications.aero_cfd.rawprep.read.DomainResult`

### 用途

域内原 VTK 引用、共享数组及字段描述；mask 仅对应原点序。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.rawprep.read import DomainResult
```

```text
class DomainResult
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`DomainResult`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.rawprep.read import DomainResult

print(signature(DomainResult))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.rawprep.read`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/rawprep/read.py:26`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.rawprep.read')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-rawprep-read-fieldconfig"></a>
## `ai4e_core.applications.aero_cfd.rawprep.read.FieldConfig`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`class FieldConfig`
- **规范定义名**：`ai4e_core.applications.aero_cfd.rawprep.read.FieldConfig`

### 用途

物理量的原始数组名称、点/单元归属和分量类别。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.rawprep.read import FieldConfig
```

```text
class FieldConfig
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`FieldConfig`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.rawprep.read import FieldConfig

print(signature(FieldConfig))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.rawprep.read`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/rawprep/read.py:18`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.rawprep.read')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-rawprep-read-dataread"></a>
## `ai4e_core.applications.aero_cfd.rawprep.read.dataread`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`dataread(ctx: dict, *, config: dict | None=None) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.rawprep.read.dataread`

### 用途

校验全部来源配置后按样本读取，复用同源 VTK；不提取字段。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.rawprep.read import dataread
```

```text
dataread(ctx: dict, *, config: dict | None=None) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `ctx` | `dict` | `必填` |
| `config` | `dict | None` | `None` |

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
from ai4e_core.applications.aero_cfd.rawprep.read import dataread

print(signature(dataread))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.rawprep.read`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/rawprep/read.py:122`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.rawprep.read')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-rawprep-read-discover-samples"></a>
## `ai4e_core.applications.aero_cfd.rawprep.read.discover_samples`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`discover_samples(ctx: dict, *, config: dict | None=None) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.rawprep.read.discover_samples`

### 用途

发现稳定排序的样本引用；支持显式相对路径、glob 或参数分片。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.rawprep.read import discover_samples
```

```text
discover_samples(ctx: dict, *, config: dict | None=None) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `ctx` | `dict` | `必填` |
| `config` | `dict | None` | `None` |

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
from ai4e_core.applications.aero_cfd.rawprep.read import discover_samples

print(signature(discover_samples))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.rawprep.read`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/rawprep/read.py:208`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.rawprep.read')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-rawprep-read-enumerate-sample-relatives"></a>
## `ai4e_core.applications.aero_cfd.rawprep.read.enumerate_sample_relatives`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`enumerate_sample_relatives(root, *, param_count=9, exclude=None, expected_total=None)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.rawprep.read.enumerate_sample_relatives`

### 用途

保留参数分片业务枚举接口；不执行任何样本。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.rawprep.read import enumerate_sample_relatives
```

```text
enumerate_sample_relatives(root, *, param_count=9, exclude=None, expected_total=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `root` | `未标注` | `必填` |
| `param_count` | `未标注` | `9` |
| `exclude` | `未标注` | `None` |
| `expected_total` | `未标注` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FileNotFoundError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.rawprep.read import enumerate_sample_relatives

print(signature(enumerate_sample_relatives))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.rawprep.read`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/rawprep/read.py:190`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.rawprep.read')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-rawprep-read-extract-configured-sample"></a>
## `ai4e_core.applications.aero_cfd.rawprep.read.extract_configured_sample`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`extract_configured_sample(config: dict, *, sample_relative=None) -> dict[str, DomainResult]`
- **规范定义名**：`ai4e_core.applications.aero_cfd.rawprep.read.extract_configured_sample`

### 用途

直接读取并提取单样本的便捷入口，内部复用两个独立步骤。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.rawprep.read import extract_configured_sample
```

```text
extract_configured_sample(config: dict, *, sample_relative=None) -> dict[str, DomainResult]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `dict` | `必填` |
| `sample_relative` | `未标注` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, DomainResult]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.rawprep.read import extract_configured_sample

print(signature(extract_configured_sample))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.rawprep.read`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/rawprep/read.py:185`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.rawprep.read')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-rawprep-read-extract-fields"></a>
## `ai4e_core.applications.aero_cfd.rawprep.read.extract_fields`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`extract_fields(ctx: dict) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.rawprep.read.extract_fields`

### 用途

从已加载 VTK 提取字段与坐标，保持原身份；不执行几何或筛选。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.rawprep.read import extract_fields
```

```text
extract_fields(ctx: dict) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `ctx` | `dict` | `必填` |

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
from ai4e_core.applications.aero_cfd.rawprep.read import extract_fields

print(signature(extract_fields))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.rawprep.read`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/rawprep/read.py:152`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.rawprep.read')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
