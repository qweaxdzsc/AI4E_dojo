<!-- dojo-help: {"domain": "ai4e_core.abilities.data.source.manifest", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.data.source.manifest 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.data.source.manifest", "topic_id": "module:ai4e_core.abilities.data.source.manifest"} -->
# `ai4e_core.abilities.data.source.manifest` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-data-source-manifest-manifestindex"></a>
## `ai4e_core.abilities.data.source.manifest.ManifestIndex`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`ManifestIndex(path: str | Path)`
- **规范定义名**：`ai4e_core.abilities.data.source.manifest.ManifestIndex`

### 用途

校验物理清单并建立稳定的分片与样本身份索引。

### 导入与签名

```python
from ai4e_core.abilities.data.source.manifest import ManifestIndex
```

```text
ManifestIndex(path: str | Path)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `str | Path` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`ManifestIndex`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FileNotFoundError`, `IndexError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.source.manifest import ManifestIndex

print(signature(ManifestIndex))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.source.manifest`
- 仓库相对路径：`packages/ai4e-core/abilities/data/source/manifest.py:12`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.source.manifest')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-source-manifest-manifestindex-content-digest"></a>
## `ai4e_core.abilities.data.source.manifest.ManifestIndex.content_digest`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`content_digest(self)`
- **规范定义名**：`ai4e_core.abilities.data.source.manifest.ManifestIndex.content_digest`

### 用途

逐文件摘要，维持既有准备身份的精确算法。

### 导入与签名

```python
from ai4e_core.abilities.data.source.manifest import ManifestIndex
```

```text
content_digest(self)
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.source.manifest import ManifestIndex

print(signature(ManifestIndex.content_digest))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.source.manifest`
- 仓库相对路径：`packages/ai4e-core/abilities/data/source/manifest.py:146`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.source.manifest')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-source-manifest-manifestindex-describe"></a>
## `ai4e_core.abilities.data.source.manifest.ManifestIndex.describe`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`describe(self)`
- **规范定义名**：`ai4e_core.abilities.data.source.manifest.ManifestIndex.describe`

### 用途

返回已发布清单的结构声明。

### 导入与签名

```python
from ai4e_core.abilities.data.source.manifest import ManifestIndex
```

```text
describe(self)
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

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
from ai4e_core.abilities.data.source.manifest import ManifestIndex

print(signature(ManifestIndex.describe))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`pcno_cylinder`
- 案例：`pcno.double_cylinder`, `recipe_extensions.model_block`

### 源码位置

- 模块：`ai4e_core.abilities.data.source.manifest`
- 仓库相对路径：`packages/ai4e-core/abilities/data/source/manifest.py:142`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.source.manifest')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-source-manifest-manifestindex-read"></a>
## `ai4e_core.abilities.data.source.manifest.ManifestIndex.read`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`read(self, partition: str, index: int=0, *, fields=None, selection=None)`
- **规范定义名**：`ai4e_core.abilities.data.source.manifest.ManifestIndex.read`

### 用途

读取指定样本，校验每个字段的空间状态、形状与类型。

### 导入与签名

```python
from ai4e_core.abilities.data.source.manifest import ManifestIndex
```

```text
read(self, partition: str, index: int=0, *, fields=None, selection=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `partition` | `str` | `必填` |
| `index` | `int` | `0` |
| `fields` | `未标注` | `None` |
| `selection` | `未标注` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`IndexError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.source.manifest import ManifestIndex

print(signature(ManifestIndex.read))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `geotransolver/shapenet_car`, `pcno_cylinder`, `wdno`
- 案例：`aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.free_wiring`, `recipe_extensions.physical_visualization`, `recipe_extensions.sampling`, `recipe_extensions.wdno`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_core.abilities.data.source.manifest`
- 仓库相对路径：`packages/ai4e-core/abilities/data/source/manifest.py:76`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.source.manifest')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-source-manifest-manifestindex-remap-partitions"></a>
## `ai4e_core.abilities.data.source.manifest.ManifestIndex.remap_partitions`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`remap_partitions(self, partitions: Mapping[str, Sequence[str]]) -> None`
- **规范定义名**：`ai4e_core.abilities.data.source.manifest.ManifestIndex.remap_partitions`

### 用途

按样本名重挂分片；张量路径不变，空分片不进入索引。

### 导入与签名

```python
from ai4e_core.abilities.data.source.manifest import ManifestIndex
```

```text
remap_partitions(self, partitions: Mapping[str, Sequence[str]]) -> None
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `partitions` | `Mapping[str, Sequence[str]]` | `必填` |

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
from ai4e_core.abilities.data.source.manifest import ManifestIndex

print(signature(ManifestIndex.remap_partitions))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.source.manifest`
- 仓库相对路径：`packages/ai4e-core/abilities/data/source/manifest.py:39`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.source.manifest')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-source-manifest-manifestindex-resolve-asset"></a>
## `ai4e_core.abilities.data.source.manifest.ManifestIndex.resolve_asset`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`resolve_asset(self, partition: str, index: int, name: str) -> Path`
- **规范定义名**：`ai4e_core.abilities.data.source.manifest.ManifestIndex.resolve_asset`

### 用途

解析样本清单显式声明的资产，拒绝未登记文件和路径越界。

``name`` 可以是 ``assets`` 中的文件名，也可以是 ``meshes`` 中的
逻辑网格名。调用方不能借此接口遍历样本目录或读取历史残留文件。

### 导入与签名

```python
from ai4e_core.abilities.data.source.manifest import ManifestIndex
```

```text
resolve_asset(self, partition: str, index: int, name: str) -> Path
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `partition` | `str` | `必填` |
| `index` | `int` | `必填` |
| `name` | `str` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Path`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FileNotFoundError`, `IndexError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.source.manifest import ManifestIndex

print(signature(ManifestIndex.resolve_asset))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.source.manifest`
- 仓库相对路径：`packages/ai4e-core/abilities/data/source/manifest.py:119`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.source.manifest')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
