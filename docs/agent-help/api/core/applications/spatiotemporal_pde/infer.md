<!-- dojo-help: {"domain": "ai4e_core.applications.spatiotemporal_pde.infer", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.spatiotemporal_pde.infer 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.spatiotemporal_pde.infer", "topic_id": "module:ai4e_core.applications.spatiotemporal_pde.infer"} -->
# `ai4e_core.applications.spatiotemporal_pde.infer` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-spatiotemporal-pde-infer-predict-named-trajectories"></a>
## `ai4e_core.applications.spatiotemporal_pde.infer.predict_named_trajectories`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`predict_named_trajectories(*args, **kwargs)`
- **规范定义名**：`ai4e_core.applications.spatiotemporal_pde.infer.predict_named_trajectories`

### 用途

按显式时间和通道解码固定轨迹，复用具名物理结果交付。

### 导入与签名

```python
from ai4e_core.applications.spatiotemporal_pde.infer import predict_named_trajectories
```

```text
predict_named_trajectories(*args, **kwargs)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `*args` | `未标注` | `可变位置参数` |
| `**kwargs` | `未标注` | `可变关键字参数` |

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
from ai4e_core.applications.spatiotemporal_pde.infer import predict_named_trajectories

print(signature(predict_named_trajectories))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`geotransolver/bumper_beam`
- 案例：`geotransolver.bumper_beam`

### 源码位置

- 模块：`ai4e_core.applications.spatiotemporal_pde.infer`
- 仓库相对路径：`packages/ai4e-core/applications/spatiotemporal_pde/infer.py:51`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.spatiotemporal_pde.infer')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-spatiotemporal-pde-infer-predict-split"></a>
## `ai4e_core.applications.spatiotemporal_pde.infer.predict_split`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`predict_split(model, physical: str, output: str, predict, *, batch_size: int, provenance: dict, derived=None) -> str`
- **规范定义名**：`ai4e_core.applications.spatiotemporal_pde.infer.predict_split`

### 用途

逐批预测保留样本身份；任何批次失败均不发布完整清单。

### 导入与签名

```python
from ai4e_core.applications.spatiotemporal_pde.infer import predict_split
```

```text
predict_split(model, physical: str, output: str, predict, *, batch_size: int, provenance: dict, derived=None) -> str
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model` | `未标注` | `必填` |
| `physical` | `str` | `必填` |
| `output` | `str` | `必填` |
| `predict` | `未标注` | `必填` |
| `batch_size` | `int` | `必填关键字参数` |
| `provenance` | `dict` | `必填关键字参数` |
| `derived` | `未标注` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`str`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.spatiotemporal_pde.infer import predict_split

print(signature(predict_split))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.spatiotemporal_pde.infer`
- 仓库相对路径：`packages/ai4e-core/applications/spatiotemporal_pde/infer.py:11`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.spatiotemporal_pde.infer')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
