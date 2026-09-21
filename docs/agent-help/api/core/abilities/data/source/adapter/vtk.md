<!-- dojo-help: {"domain": "ai4e_core.abilities.data.source.adapter.vtk", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.data.source.adapter.vtk 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.data.source.adapter.vtk", "topic_id": "module:ai4e_core.abilities.data.source.adapter.vtk"} -->
# `ai4e_core.abilities.data.source.adapter.vtk` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-data-source-adapter-vtk-load"></a>
## `ai4e_core.abilities.data.source.adapter.vtk.load`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`load(path: Path) -> vtkDataObject`
- **规范定义名**：`ai4e_core.abilities.data.source.adapter.vtk.load`

### 用途

读取受支持的 VTK 家族文件，保留具体类型和全部关联数组。

本函数直接返回 reader 的原生输出，不抽取数组、不转换数据类型，也不改变
PointData、CellData、FieldData 或拓扑。``.vtkh5`` 作为标准
``.vtkhdf`` 内容的兼容扩展名处理。

Args:
    path: 已确认存在的 VTK 家族文件路径。

Returns:
    VTK reader 生成的原生数据对象。

Raises:
    ValueError: 扩展名不受支持、文件损坏、内容与格式不匹配或 reader 没有输出。

### 导入与签名

```python
from ai4e_core.abilities.data.source.adapter.vtk import load
```

```text
load(path: Path) -> vtkDataObject
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `Path` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`vtkDataObject`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.source.adapter.vtk import load

print(signature(load))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`geotransolver/bumper_beam`, `geotransolver/darcy`, `parametric_pde`
- 案例：`geotransolver.bumper_beam`, `geotransolver.darcy`, `parametric_pde.advection`, `parametric_pde.burgers`, `parametric_pde.convection_diffusion`, `parametric_pde.diffusion_trapezoid`, `parametric_pde.neumann_diffusion`

### 源码位置

- 模块：`ai4e_core.abilities.data.source.adapter.vtk`
- 仓库相对路径：`packages/ai4e-core/abilities/data/source/adapter/vtk.py:29`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.source.adapter.vtk')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
