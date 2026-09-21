<!-- dojo-help: {"domain": "ai4e_core.abilities.data.source.adapter.npy", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.data.source.adapter.npy 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.data.source.adapter.npy", "topic_id": "module:ai4e_core.abilities.data.source.adapter.npy"} -->
# `ai4e_core.abilities.data.source.adapter.npy` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-data-source-adapter-npy-load"></a>
## `ai4e_core.abilities.data.source.adapter.npy.load`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`load(path: Path) -> vtkDataObject`
- **规范定义名**：`ai4e_core.abilities.data.source.adapter.npy.load`

### 用途

读取 NPY 并转为包含 values 和恢复元数据的 VTK FieldData。

数组按 C 顺序展平为单分量数组，不猜测坐标、向量或网格归属。
VTK 持有数据副本，原始 NumPy 数组释放后仍可使用。元数据中的
schema_version、shape、dtype、order 分别记录表示版本和恢复规则。

Args:
    path: 已确认存在的 NPY 文件路径。

Returns:
    无网格 vtkDataObject；values 存数值，__ai4e_npy_metadata 存 JSON。
    支持 bool、8/16/32/64 位整数及 float32/64。布尔用 uint8 承载，
    其他数值保持精度；非本机字节序转本机字节序，元数据保留原 dtype。

Raises:
    ValueError: 文件损坏、需要 pickle 或 dtype 不在支持范围内。

### 导入与签名

```python
from ai4e_core.abilities.data.source.adapter.npy import load
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
from ai4e_core.abilities.data.source.adapter.npy import load

print(signature(load))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`geotransolver/bumper_beam`, `geotransolver/darcy`, `parametric_pde`
- 案例：`geotransolver.bumper_beam`, `geotransolver.darcy`, `parametric_pde.advection`, `parametric_pde.burgers`, `parametric_pde.convection_diffusion`, `parametric_pde.diffusion_trapezoid`, `parametric_pde.neumann_diffusion`

### 源码位置

- 模块：`ai4e_core.abilities.data.source.adapter.npy`
- 仓库相对路径：`packages/ai4e-core/abilities/data/source/adapter/npy.py:14`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.source.adapter.npy')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
