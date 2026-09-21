<!-- dojo-help: {"domain": "ai4e_core.abilities.postproc.difference", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.postproc.difference 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.postproc.difference", "topic_id": "module:ai4e_core.abilities.postproc.difference"} -->
# `ai4e_core.abilities.postproc.difference` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-postproc-difference-compare-files"></a>
## `ai4e_core.abilities.postproc.difference.compare_files`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`compare_files(inputs: list[dict], output_dir: Path, options: dict) -> dict`
- **规范定义名**：`ai4e_core.abilities.postproc.difference.compare_files`

### 用途

读取 task 已校验的两个张量资产和身份清单，原子发布差值。

### 导入与签名

```python
from ai4e_core.abilities.postproc.difference import compare_files
```

```text
compare_files(inputs: list[dict], output_dir: Path, options: dict) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `inputs` | `list[dict]` | `必填` |
| `output_dir` | `Path` | `必填` |
| `options` | `dict` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.postproc.difference import compare_files

print(signature(compare_files))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.difference`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/difference.py:41`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.difference')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-difference-difference"></a>
## `ai4e_core.abilities.postproc.difference.difference`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`difference(left: dict, right: dict) -> torch.Tensor`
- **规范定义名**：`ai4e_core.abilities.postproc.difference.difference`

### 用途

校验来源、归属、单位、实体 ID、坐标和拓扑后执行 left-right。

### 导入与签名

```python
from ai4e_core.abilities.postproc.difference import difference
```

```text
difference(left: dict, right: dict) -> torch.Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `left` | `dict` | `必填` |
| `right` | `dict` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`torch.Tensor`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.postproc.difference import difference

print(signature(difference))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.inference_fields`

### 源码位置

- 模块：`ai4e_core.abilities.postproc.difference`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/difference.py:13`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.difference')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
