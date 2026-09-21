<!-- dojo-help: {"domain": "ai4e_core.abilities.postproc.visualization.trajectory", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.postproc.visualization.trajectory 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.postproc.visualization.trajectory", "topic_id": "module:ai4e_core.abilities.postproc.visualization.trajectory"} -->
# `ai4e_core.abilities.postproc.visualization.trajectory` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-postproc-visualization-trajectory-plot-error-curve"></a>
## `ai4e_core.abilities.postproc.visualization.trajectory.plot_error_curve`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`plot_error_curve(frame_components, path)`
- **规范定义名**：`ai4e_core.abilities.postproc.visualization.trajectory.plot_error_curve`

### 用途

按物理帧绘制各分量相对误差，不能混作生成流时间。

### 导入与签名

```python
from ai4e_core.abilities.postproc.visualization.trajectory import plot_error_curve
```

```text
plot_error_curve(frame_components, path)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `frame_components` | `未标注` | `必填` |
| `path` | `未标注` | `必填` |

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
from ai4e_core.abilities.postproc.visualization.trajectory import plot_error_curve

print(signature(plot_error_curve))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.visualization.trajectory`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/visualization/trajectory.py:27`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.visualization.trajectory')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-visualization-trajectory-plot-frame"></a>
## `ai4e_core.abilities.postproc.visualization.trajectory.plot_frame`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`plot_frame(prediction, target, path, *, sample=0, frame=-1, component=0)`
- **规范定义名**：`ai4e_core.abilities.postproc.visualization.trajectory.plot_frame`

### 用途

保存同色标真值/预测及误差图；不调用模型。

### 导入与签名

```python
from ai4e_core.abilities.postproc.visualization.trajectory import plot_frame
```

```text
plot_frame(prediction, target, path, *, sample=0, frame=-1, component=0)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `prediction` | `未标注` | `必填` |
| `target` | `未标注` | `必填` |
| `path` | `未标注` | `必填` |
| `sample` | `未标注` | `0` |
| `frame` | `未标注` | `-1` |
| `component` | `未标注` | `0` |

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
from ai4e_core.abilities.postproc.visualization.trajectory import plot_frame

print(signature(plot_frame))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.visualization.trajectory`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/visualization/trajectory.py:4`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.visualization.trajectory')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-visualization-trajectory-plot-named-field"></a>
## `ai4e_core.abilities.postproc.visualization.trajectory.plot_named_field`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`plot_named_field(path, prediction, target, coordinates, *, field: str, unit: str)`
- **规范定义名**：`ai4e_core.abilities.postproc.visualization.trajectory.plot_named_field`

### 用途

最后一帧同一场的真值/预测/误差散点图，适用于二维或表面坐标。

### 导入与签名

```python
from ai4e_core.abilities.postproc.visualization.trajectory import plot_named_field
```

```text
plot_named_field(path, prediction, target, coordinates, *, field: str, unit: str)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `未标注` | `必填` |
| `prediction` | `未标注` | `必填` |
| `target` | `未标注` | `必填` |
| `coordinates` | `未标注` | `必填` |
| `field` | `str` | `必填关键字参数` |
| `unit` | `str` | `必填关键字参数` |

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
from ai4e_core.abilities.postproc.visualization.trajectory import plot_named_field

print(signature(plot_named_field))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.visualization.trajectory`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/visualization/trajectory.py:69`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.visualization.trajectory')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-visualization-trajectory-plot-named-frames"></a>
## `ai4e_core.abilities.postproc.visualization.trajectory.plot_named_frames`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`plot_named_frames(path, metrics: dict, *, time_unit: str)`
- **规范定义名**：`ai4e_core.abilities.postproc.visualization.trajectory.plot_named_frames`

### 用途

具名场随显式物理时间的样本平均误差图，单位从调用方提供。

### 导入与签名

```python
from ai4e_core.abilities.postproc.visualization.trajectory import plot_named_frames
```

```text
plot_named_frames(path, metrics: dict, *, time_unit: str)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `未标注` | `必填` |
| `metrics` | `dict` | `必填` |
| `time_unit` | `str` | `必填关键字参数` |

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
from ai4e_core.abilities.postproc.visualization.trajectory import plot_named_frames

print(signature(plot_named_frames))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.visualization.trajectory`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/visualization/trajectory.py:46`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.visualization.trajectory')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
