<!-- dojo-help: {"domain": "ai4e_contrib.ability.model.pibsnet.trapezoid_basis", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.model.pibsnet.trapezoid_basis 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.model.pibsnet.trapezoid_basis", "topic_id": "module:ai4e_contrib.ability.model.pibsnet.trapezoid_basis"} -->
# `ai4e_contrib.ability.model.pibsnet.trapezoid_basis` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-trapezoid-basis-bsfun"></a>
## `ai4e_contrib.ability.model.pibsnet.trapezoid_basis.BsFun`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`BsFun(i, d, t, knots)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.trapezoid_basis.BsFun`

### 用途

原一基索引的 Cox 递推，末端为半开区间。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.trapezoid_basis import BsFun
```

```text
BsFun(i, d, t, knots)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `i` | `未标注` | `必填` |
| `d` | `未标注` | `必填` |
| `t` | `未标注` | `必填` |
| `knots` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.pibsnet.trapezoid_basis import BsFun

print(signature(BsFun))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.trapezoid_basis`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/trapezoid_basis.py:13`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.trapezoid_basis')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-trapezoid-basis-build-bspline-basis"></a>
## `ai4e_contrib.ability.model.pibsnet.trapezoid_basis.build_bspline_basis`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`build_bspline_basis(n_cp, d, Nparam)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.trapezoid_basis.build_bspline_basis`

### 用途

保留 FP32 累加参数坐标和末值基的单项覆盖。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.trapezoid_basis import build_bspline_basis
```

```text
build_bspline_basis(n_cp, d, Nparam)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `n_cp` | `未标注` | `必填` |
| `d` | `未标注` | `必填` |
| `Nparam` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.pibsnet.trapezoid_basis import build_bspline_basis

print(signature(build_bspline_basis))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.trapezoid_basis`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/trapezoid_basis.py:24`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.trapezoid_basis')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-trapezoid-basis-build-bspline-derivatives"></a>
## `ai4e_contrib.ability.model.pibsnet.trapezoid_basis.build_bspline_derivatives`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`build_bspline_derivatives(n_cp, d, Nparam, knots, param_vals)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.trapezoid_basis.build_bspline_derivatives`

### 用途

原参数空间一二阶递推；未作物理尺度与端点修正。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.trapezoid_basis import build_bspline_derivatives
```

```text
build_bspline_derivatives(n_cp, d, Nparam, knots, param_vals)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `n_cp` | `未标注` | `必填` |
| `d` | `未标注` | `必填` |
| `Nparam` | `未标注` | `必填` |
| `knots` | `未标注` | `必填` |
| `param_vals` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.pibsnet.trapezoid_basis import build_bspline_derivatives

print(signature(build_bspline_derivatives))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.trapezoid_basis`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/trapezoid_basis.py:47`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.trapezoid_basis')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-trapezoid-basis-grid-basis"></a>
## `ai4e_contrib.ability.model.pibsnet.trapezoid_basis.grid_basis`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`grid_basis(n_cp, degree, count)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.trapezoid_basis.grid_basis`

### 用途

缓存不参与训练的轴矩阵；调用方不得原位修改返回值。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.trapezoid_basis import grid_basis
```

```text
grid_basis(n_cp, degree, count)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `n_cp` | `未标注` | `必填` |
| `degree` | `未标注` | `必填` |
| `count` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.pibsnet.trapezoid_basis import grid_basis

print(signature(grid_basis))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.trapezoid_basis`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/trapezoid_basis.py:92`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.trapezoid_basis')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
