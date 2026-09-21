<!-- dojo-help: {"domain": "ai4e_core.abilities.data.extract.vtk_fields", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.data.extract.vtk_fields 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.data.extract.vtk_fields", "topic_id": "module:ai4e_core.abilities.data.extract.vtk_fields"} -->
# `ai4e_core.abilities.data.extract.vtk_fields` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-data-extract-vtk-fields-extract-coordinates"></a>
## `ai4e_core.abilities.data.extract.vtk_fields.extract_coordinates`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`extract_coordinates(data: vtkDataObject) -> np.ndarray`
- **规范定义名**：`ai4e_core.abilities.data.extract.vtk_fields.extract_coordinates`

### 用途

提取原点序的 ``(N, 3)`` 坐标，不计算单元中心。

返回值优先共享 VTK 存储，不强制连续化、复制或转换 dtype。
修改共享数组可能改变 VTK；替换点表或拓扑后必须重新提取。

Args:
    data: 带点的 VTK 数据集。

Returns:
    原点序坐标数组；不保证所有 VTK 后端都支持零复制。

Raises:
    TypeError: 输入不是 VTK 数据集。
    ValueError: 没有坐标或坐标形状不是 (N, 3)。

### 导入与签名

```python
from ai4e_core.abilities.data.extract.vtk_fields import extract_coordinates
```

```text
extract_coordinates(data: vtkDataObject) -> np.ndarray
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `data` | `vtkDataObject` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`np.ndarray`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.extract.vtk_fields import extract_coordinates

print(signature(extract_coordinates))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.extract.vtk_fields`
- 仓库相对路径：`packages/ai4e-core/abilities/data/extract/vtk_fields.py:19`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.extract.vtk_fields')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-extract-vtk-fields-extract-field"></a>
## `ai4e_core.abilities.data.extract.vtk_fields.extract_field`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`extract_field(data: vtkDataObject, *, name: str, association: Association, kind: FieldKind) -> np.ndarray`
- **规范定义名**：`ai4e_core.abilities.data.extract.vtk_fields.extract_field`

### 用途

按名称与归属提取数值字段，不依赖活动字段或转换点/单元场。

Args:
    data: VTK 数据集。
    name: VTK 原始数组精确名称。
    association: point 读取 PointData，cell 读取 CellData。
    kind: scalar 要求一个分量；vector 要求三个分量。

Returns:
    标量 (N,) 或矢量 (N, 3)，N 为相应点数或单元数。优先共享 VTK
    存储，不复制或强制转 dtype。调用方修改数组可能改变原场；替换字段
    数组或改变拓扑、点序后必须重新提取，所有后端不保证零复制。

Raises:
    TypeError: 输入不是数据集，或字段不是数值数组。
    ValueError: 名称/归属/类别无效、字段缺失、分量数或元组数错误。

### 导入与签名

```python
from ai4e_core.abilities.data.extract.vtk_fields import extract_field
```

```text
extract_field(data: vtkDataObject, *, name: str, association: Association, kind: FieldKind) -> np.ndarray
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `data` | `vtkDataObject` | `必填` |
| `name` | `str` | `必填关键字参数` |
| `association` | `Association` | `必填关键字参数` |
| `kind` | `FieldKind` | `必填关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`np.ndarray`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`TypeError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.extract.vtk_fields import extract_field

print(signature(extract_field))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.extract.vtk_fields`
- 仓库相对路径：`packages/ai4e-core/abilities/data/extract/vtk_fields.py:46`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.extract.vtk_fields')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-extract-vtk-fields-extract-scalars"></a>
## `ai4e_core.abilities.data.extract.vtk_fields.extract_scalars`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`extract_scalars(data: vtkDataObject, *, name: str, association: Association) -> np.ndarray`
- **规范定义名**：`ai4e_core.abilities.data.extract.vtk_fields.extract_scalars`

### 用途

按显式名称和归属提取单分量字段，共享行为与错误契约同 extract_field。

### 导入与签名

```python
from ai4e_core.abilities.data.extract.vtk_fields import extract_scalars
```

```text
extract_scalars(data: vtkDataObject, *, name: str, association: Association) -> np.ndarray
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `data` | `vtkDataObject` | `必填` |
| `name` | `str` | `必填关键字参数` |
| `association` | `Association` | `必填关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`np.ndarray`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.extract.vtk_fields import extract_scalars

print(signature(extract_scalars))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.extract.vtk_fields`
- 仓库相对路径：`packages/ai4e-core/abilities/data/extract/vtk_fields.py:94`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.extract.vtk_fields')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-extract-vtk-fields-extract-vectors"></a>
## `ai4e_core.abilities.data.extract.vtk_fields.extract_vectors`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`extract_vectors(data: vtkDataObject, *, name: str, association: Association) -> np.ndarray`
- **规范定义名**：`ai4e_core.abilities.data.extract.vtk_fields.extract_vectors`

### 用途

按显式名称和归属提取三分量字段，共享行为与错误契约同 extract_field。

### 导入与签名

```python
from ai4e_core.abilities.data.extract.vtk_fields import extract_vectors
```

```text
extract_vectors(data: vtkDataObject, *, name: str, association: Association) -> np.ndarray
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `data` | `vtkDataObject` | `必填` |
| `name` | `str` | `必填关键字参数` |
| `association` | `Association` | `必填关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`np.ndarray`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.extract.vtk_fields import extract_vectors

print(signature(extract_vectors))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.extract.vtk_fields`
- 仓库相对路径：`packages/ai4e-core/abilities/data/extract/vtk_fields.py:99`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.extract.vtk_fields')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
