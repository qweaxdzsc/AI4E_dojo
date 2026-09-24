<!-- dojo-help: {"domain": "ai4e_core.abilities.training.algebraic", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.training.algebraic 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.training.algebraic", "topic_id": "module:ai4e_core.abilities.training.algebraic"} -->
# `ai4e_core.abilities.training.algebraic` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-training-algebraic-fit-least-squares"></a>
## `ai4e_core.abilities.training.algebraic.fit_least_squares`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`fit_least_squares(design, targets, *, ridge: float=0.0) -> dict`
- **规范定义名**：`ai4e_core.abilities.training.algebraic.fit_least_squares`

### 用途

通过经济型 SVD 拟合；ridge 显式惩罚全部系数，含常数项。

默认满列秩，不用伪逆掩盖不可识别的模型；显式正则化允许欠定设计，
仍记录原设计的秩和条件数。没有正规方程求逆或静默添加稳定项。

### 导入与签名

```python
from ai4e_core.abilities.training.algebraic import fit_least_squares
```

```text
fit_least_squares(design, targets, *, ridge: float=0.0) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `design` | `未标注` | `必填` |
| `targets` | `未标注` | `必填` |
| `ridge` | `float` | `0.0` |

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
from ai4e_core.abilities.training.algebraic import fit_least_squares

print(signature(fit_least_squares))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.training.algebraic`
- 仓库相对路径：`packages/ai4e-core/abilities/training/algebraic.py:28`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.algebraic')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-algebraic-fit-rbf"></a>
## `ai4e_core.abilities.training.algebraic.fit_rbf`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`fit_rbf(inputs, targets, *, radial=None, polynomial=None, smoothing: float=0.0) -> dict`
- **规范定义名**：`ai4e_core.abilities.training.algebraic.fit_rbf`

### 用途

解 [K+lambda*I,P;P.T,0] 增广系统，多输出共用一次分解。

固定中心为输入训练行；尾项用中心包围盒平移缩放改善量级，但核距离仍
使用原输入。重复中心仅在零平滑时拒绝；尾项始终要求满列秩。

### 导入与签名

```python
from ai4e_core.abilities.training.algebraic import fit_rbf
```

```text
fit_rbf(inputs, targets, *, radial=None, polynomial=None, smoothing: float=0.0) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `inputs` | `未标注` | `必填` |
| `targets` | `未标注` | `必填` |
| `radial` | `未标注` | `None` |
| `polynomial` | `未标注` | `None` |
| `smoothing` | `float` | `0.0` |

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
from ai4e_core.abilities.training.algebraic import fit_rbf

print(signature(fit_rbf))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.training.algebraic`
- 仓库相对路径：`packages/ai4e-core/abilities/training/algebraic.py:69`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.algebraic')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-training-algebraic-fit-rsm"></a>
## `ai4e_core.abilities.training.algebraic.fit_rsm`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`fit_rsm(inputs, targets, *, degree: int=2, basis=None, ridge: float=0.0) -> dict`
- **规范定义名**：`ai4e_core.abilities.training.algebraic.fit_rsm`

### 用途

用共享多项式基拟合一次/二次响应面；返回可重建预测器的状态。

### 导入与签名

```python
from ai4e_core.abilities.training.algebraic import fit_rsm
```

```text
fit_rsm(inputs, targets, *, degree: int=2, basis=None, ridge: float=0.0) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `inputs` | `未标注` | `必填` |
| `targets` | `未标注` | `必填` |
| `degree` | `int` | `2` |
| `basis` | `未标注` | `None` |
| `ridge` | `float` | `0.0` |

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
from ai4e_core.abilities.training.algebraic import fit_rsm

print(signature(fit_rsm))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.training.algebraic`
- 仓库相对路径：`packages/ai4e-core/abilities/training/algebraic.py:59`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.training.algebraic')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
