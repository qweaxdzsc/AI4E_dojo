<!-- dojo-help: {"domain": "ai4e_core.applications.aero_cfd.rawprep.derive", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.aero_cfd.rawprep.derive 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.aero_cfd.rawprep.derive", "topic_id": "module:ai4e_core.applications.aero_cfd.rawprep.derive"} -->
# `ai4e_core.applications.aero_cfd.rawprep.derive` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-aero-cfd-rawprep-derive-geometrydomaininput"></a>
## `ai4e_core.applications.aero_cfd.rawprep.derive.GeometryDomainInput`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`class GeometryDomainInput`
- **规范定义名**：`ai4e_core.applications.aero_cfd.rawprep.derive.GeometryDomainInput`

### 用途

几何域最低输入仅为 vtk；可附带已有提取结果，保持共享引用。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.rawprep.derive import GeometryDomainInput
```

```text
class GeometryDomainInput
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`GeometryDomainInput`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.rawprep.derive import GeometryDomainInput

print(signature(GeometryDomainInput))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.rawprep.derive`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/rawprep/derive.py:31`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.rawprep.derive')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-rawprep-derive-geometrydomainresult"></a>
## `ai4e_core.applications.aero_cfd.rawprep.derive.GeometryDomainResult`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`class GeometryDomainResult`
- **规范定义名**：`ai4e_core.applications.aero_cfd.rawprep.derive.GeometryDomainResult`

### 用途

保留已有提取内容，并按启用能力添加原点序几何量。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.rawprep.derive import GeometryDomainResult
```

```text
class GeometryDomainResult
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`GeometryDomainResult`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.rawprep.derive import GeometryDomainResult

print(signature(GeometryDomainResult))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.rawprep.derive`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/rawprep/derive.py:37`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.rawprep.derive')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-rawprep-derive-configured-geometry-enabled"></a>
## `ai4e_core.applications.aero_cfd.rawprep.derive.configured_geometry_enabled`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`configured_geometry_enabled(config: Mapping[str, object]) -> tuple[GeometryAbility, ...]`
- **规范定义名**：`ai4e_core.applications.aero_cfd.rawprep.derive.configured_geometry_enabled`

### 用途

读取 pre.geometry.enabled；缺省为空，显式值须为无重复的能力列表。

不执行能力，也不读取数据；配置结构错误抛 ValueError。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.rawprep.derive import configured_geometry_enabled
```

```text
configured_geometry_enabled(config: Mapping[str, object]) -> tuple[GeometryAbility, ...]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `Mapping[str, object]` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`tuple[GeometryAbility, ...]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.rawprep.derive import configured_geometry_enabled

print(signature(configured_geometry_enabled))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.rawprep.derive`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/rawprep/derive.py:80`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.rawprep.derive')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-rawprep-derive-derive-configured-geometry"></a>
## `ai4e_core.applications.aero_cfd.rawprep.derive.derive_configured_geometry`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`derive_configured_geometry(extracted: Mapping[str, GeometryDomainInput], *, enabled: Sequence[str], parameters: Mapping[str, Mapping[str, float]] | None=None) -> dict[str, GeometryDomainResult]`
- **规范定义名**：`ai4e_core.applications.aero_cfd.rawprep.derive.derive_configured_geometry`

### 用途

仅从域内 VTK 获取坐标/拓扑，执行显式选择的能力并保留已有内容。

表面法向仅需 surface；最近顶点距离、体积法向及其他能力需要 surface/volume。空 enabled 透传，
不访问 vtk。全体所选能力先做输入门禁和输出冲突检查，失败不执行算法。
输入字段及额外域保持引用；不套 mask、不改输入、不落盘。不验证物理场。
返回原域映射副本与所选派生量；缺域、非法能力或同名输出冲突抛 ValueError。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.rawprep.derive import derive_configured_geometry
```

```text
derive_configured_geometry(extracted: Mapping[str, GeometryDomainInput], *, enabled: Sequence[str], parameters: Mapping[str, Mapping[str, float]] | None=None) -> dict[str, GeometryDomainResult]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `extracted` | `Mapping[str, GeometryDomainInput]` | `必填` |
| `enabled` | `Sequence[str]` | `必填关键字参数` |
| `parameters` | `Mapping[str, Mapping[str, float]] | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, GeometryDomainResult]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`TypeError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.rawprep.derive import derive_configured_geometry

print(signature(derive_configured_geometry))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.rawprep.derive`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/rawprep/derive.py:97`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.rawprep.derive')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-rawprep-derive-derive-geometry"></a>
## `ai4e_core.applications.aero_cfd.rawprep.derive.derive_geometry`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`derive_geometry(ctx: dict, *, enabled, parameters=None) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.rawprep.derive.derive_geometry`

### 用途

业务步骤只计算显式启用项，独立原子 API 保持不变。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.rawprep.derive import derive_geometry
```

```text
derive_geometry(ctx: dict, *, enabled, parameters=None) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `ctx` | `dict` | `必填` |
| `enabled` | `未标注` | `必填关键字参数` |
| `parameters` | `未标注` | `None` |

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
from ai4e_core.applications.aero_cfd.rawprep.derive import derive_geometry

print(signature(derive_geometry))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.rawprep.derive`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/rawprep/derive.py:177`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.rawprep.derive')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
