<!-- dojo-help: {"domain": "ai4e_core.abilities.data.extract.mesh_probe", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.data.extract.mesh_probe 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.data.extract.mesh_probe", "topic_id": "module:ai4e_core.abilities.data.extract.mesh_probe"} -->
# `ai4e_core.abilities.data.extract.mesh_probe` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-data-extract-mesh-probe-probe-fields"></a>
## `ai4e_core.abilities.data.extract.mesh_probe.probe_fields`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`probe_fields(mesh, points, names)`
- **规范定义名**：`ai4e_core.abilities.data.extract.mesh_probe.probe_fields`

### 用途

用真实单元插值点场；返回具名数组和布尔有效域，不启用最近点补洞。

### 导入与签名

```python
from ai4e_core.abilities.data.extract.mesh_probe import probe_fields
```

```text
probe_fields(mesh, points, names)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `mesh` | `未标注` | `必填` |
| `points` | `未标注` | `必填` |
| `names` | `未标注` | `必填` |

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
from ai4e_core.abilities.data.extract.mesh_probe import probe_fields

print(signature(probe_fields))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.extract.mesh_probe`
- 仓库相对路径：`packages/ai4e-core/abilities/data/extract/mesh_probe.py:21`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.extract.mesh_probe')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-extract-mesh-probe-probe-regular"></a>
## `ai4e_core.abilities.data.extract.mesh_probe.probe_regular`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`probe_regular(coordinates, values, valid, points)`
- **规范定义名**：`ai4e_core.abilities.data.extract.mesh_probe.probe_regular`

### 用途

规则格回贴，只接受所有插值支撑均有效的点，保持查询实体行序。

### 导入与签名

```python
from ai4e_core.abilities.data.extract.mesh_probe import probe_regular
```

```text
probe_regular(coordinates, values, valid, points)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `coordinates` | `未标注` | `必填` |
| `values` | `未标注` | `必填` |
| `valid` | `未标注` | `必填` |
| `points` | `未标注` | `必填` |

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
from ai4e_core.abilities.data.extract.mesh_probe import probe_regular

print(signature(probe_regular))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.extract.mesh_probe`
- 仓库相对路径：`packages/ai4e-core/abilities/data/extract/mesh_probe.py:42`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.extract.mesh_probe')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-extract-mesh-probe-regular-coordinates"></a>
## `ai4e_core.abilities.data.extract.mesh_probe.regular_coordinates`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`regular_coordinates(bounds, shape)`
- **规范定义名**：`ai4e_core.abilities.data.extract.mesh_probe.regular_coordinates`

### 用途

按物理包围盒生成末轴xyz、C顺序规则格，禁止退化轴。

### 导入与签名

```python
from ai4e_core.abilities.data.extract.mesh_probe import regular_coordinates
```

```text
regular_coordinates(bounds, shape)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `bounds` | `未标注` | `必填` |
| `shape` | `未标注` | `必填` |

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
from ai4e_core.abilities.data.extract.mesh_probe import regular_coordinates

print(signature(regular_coordinates))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.extract.mesh_probe`
- 仓库相对路径：`packages/ai4e-core/abilities/data/extract/mesh_probe.py:6`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.extract.mesh_probe')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
