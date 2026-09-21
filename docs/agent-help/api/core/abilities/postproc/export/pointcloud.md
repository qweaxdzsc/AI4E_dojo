<!-- dojo-help: {"domain": "ai4e_core.abilities.postproc.export.pointcloud", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.postproc.export.pointcloud 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.postproc.export.pointcloud", "topic_id": "module:ai4e_core.abilities.postproc.export.pointcloud"} -->
# `ai4e_core.abilities.postproc.export.pointcloud` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-postproc-export-pointcloud-write-pointcloud"></a>
## `ai4e_core.abilities.postproc.export.pointcloud.write_pointcloud`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`write_pointcloud(path: str | Path, positions, fields: dict, *, field_data: dict | None=None) -> Path`
- **规范定义名**：`ai4e_core.abilities.postproc.export.pointcloud.write_pointcloud`

### 用途

写出每个点带一个 VTK_VERTEX 的 ``.vtp`` 点云，保留输入数值类型。

这是锚点预览，不是完整网格回贴。标量 ``(N, 1)`` 压成一维，矢量保留分量。
``field_data`` 写单值字符串，用于 ``sample_id`` 等对照身份。

Args:
    path: 目标 ``.vtp`` 路径。
    positions: 点坐标，形状必须是 ``(N, 3)``。
    fields: 点数据场，首维必须等于点数。
    field_data: 可选网格级字符串属性。

Returns:
    已提交的目标路径。

Raises:
    ValueError: 坐标不是 ``(N, 3)``，或场点数对不上。
    RuntimeError: VTK 写出失败。

### 导入与签名

```python
from ai4e_core.abilities.postproc.export.pointcloud import write_pointcloud
```

```text
write_pointcloud(path: str | Path, positions, fields: dict, *, field_data: dict | None=None) -> Path
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `str | Path` | `必填` |
| `positions` | `未标注` | `必填` |
| `fields` | `dict` | `必填` |
| `field_data` | `dict | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Path`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`RuntimeError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.postproc.export.pointcloud import write_pointcloud

print(signature(write_pointcloud))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.export.pointcloud`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/export/pointcloud.py:11`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.export.pointcloud')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
