<!-- dojo-help: {"domain": "ai4e_core.abilities.inference.rebuild", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.inference.rebuild 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.inference.rebuild", "topic_id": "module:ai4e_core.abilities.inference.rebuild"} -->
# `ai4e_core.abilities.inference.rebuild` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-inference-rebuild-model-restore-contract"></a>
## `ai4e_core.abilities.inference.rebuild.model_restore_contract`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`model_restore_contract(value: Any) -> Any`
- **规范定义名**：`ai4e_core.abilities.inference.rebuild.model_restore_contract`

### 用途

恢复权重要比的模型语义：结构参数和数据规格，不含采样点数。

### 导入与签名

```python
from ai4e_core.abilities.inference.rebuild import model_restore_contract
```

```text
model_restore_contract(value: Any) -> Any
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `value` | `Any` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Any`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.inference.rebuild import model_restore_contract

print(signature(model_restore_contract))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.inference.rebuild`
- 仓库相对路径：`packages/ai4e-core/abilities/inference/rebuild.py:11`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.inference.rebuild')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-inference-rebuild-rebuild"></a>
## `ai4e_core.abilities.inference.rebuild.rebuild`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`rebuild(path: str | Path, model, *, contract: dict[str, Any]) -> dict[str, Any]`
- **规范定义名**：`ai4e_core.abilities.inference.rebuild.rebuild`

### 用途

从检查点只加载模型权重，并核对版本与语义契约。

不加载优化器、调度、EMA、缩放器或随机流，因此不会推进或回退训练进度。

Args:
    path: 可信本地检查点路径。
    model: 已按当前配置构造、尚未或即将用于推理的模型。
    contract: 当前运行的语义契约，至少含 ``model_version``、``model``、
        ``trainprep`` 与 ``normalization``。``model`` 若含 parameters/data_specs，
        只比这两项，忽略采样点数。

Returns:
    含 ``model`` 权重和检查点内 ``contract`` 的字典，便于调用方再核对接线。

Raises:
    ValueError: 版本不是 2，或模型、准备、归一化语义不一致。

### 导入与签名

```python
from ai4e_core.abilities.inference.rebuild import rebuild
```

```text
rebuild(path: str | Path, model, *, contract: dict[str, Any]) -> dict[str, Any]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `str | Path` | `必填` |
| `model` | `未标注` | `必填` |
| `contract` | `dict[str, Any]` | `必填关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, Any]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.inference.rebuild import rebuild

print(signature(rebuild))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.inference.rebuild`
- 仓库相对路径：`packages/ai4e-core/abilities/inference/rebuild.py:20`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.inference.rebuild')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
