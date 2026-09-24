<!-- dojo-help: {"domain": "ai4e_contrib.application.datasets.safediffcon.arrays", "kind": "api", "layer": "contrib.application", "summary": "ai4e_contrib.application.datasets.safediffcon.arrays 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.application.datasets.safediffcon.arrays", "topic_id": "module:ai4e_contrib.application.datasets.safediffcon.arrays"} -->
# `ai4e_contrib.application.datasets.safediffcon.arrays` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-application-datasets-safediffcon-arrays-read-burgers"></a>
## `ai4e_contrib.application.datasets.safediffcon.arrays.read_burgers`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`read_burgers(root: str | Path, split: str) -> dict[str, np.ndarray]`
- **规范定义名**：`ai4e_contrib.application.datasets.safediffcon.arrays.read_burgers`

### 用途

读取原 HDF5 状态与控制，不重划分训练/校准/测试。

### 导入与签名

```python
from ai4e_contrib.application.datasets.safediffcon.arrays import read_burgers
```

```text
read_burgers(root: str | Path, split: str) -> dict[str, np.ndarray]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `root` | `str | Path` | `必填` |
| `split` | `str` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, np.ndarray]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.application.datasets.safediffcon.arrays import read_burgers

print(signature(read_burgers))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`safediffcon`
- 案例：`recipe_extensions.task_labels`, `safediffcon.burgers`

### 源码位置

- 模块：`ai4e_contrib.application.datasets.safediffcon.arrays`
- 仓库相对路径：`packages/ai4e-contrib/application/datasets/safediffcon/arrays.py:12`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.datasets.safediffcon.arrays')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-datasets-safediffcon-arrays-read-tokamak"></a>
## `ai4e_contrib.application.datasets.safediffcon.arrays.read_tokamak`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`read_tokamak(root: str | Path, split: str) -> dict[str, np.ndarray]`
- **规范定义名**：`ai4e_contrib.application.datasets.safediffcon.arrays.read_tokamak`

### 用途

按原顺序读取四个 Arrow 分片，缺 metadata 时不要求重下载。

### 导入与签名

```python
from ai4e_contrib.application.datasets.safediffcon.arrays import read_tokamak
```

```text
read_tokamak(root: str | Path, split: str) -> dict[str, np.ndarray]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `root` | `str | Path` | `必填` |
| `split` | `str` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, np.ndarray]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FileNotFoundError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.application.datasets.safediffcon.arrays import read_tokamak

print(signature(read_tokamak))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`safediffcon`
- 案例：`safediffcon.tokamak`

### 源码位置

- 模块：`ai4e_contrib.application.datasets.safediffcon.arrays`
- 仓库相对路径：`packages/ai4e-contrib/application/datasets/safediffcon/arrays.py:21`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.datasets.safediffcon.arrays')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
