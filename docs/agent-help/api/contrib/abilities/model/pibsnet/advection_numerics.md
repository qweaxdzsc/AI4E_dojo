<!-- dojo-help: {"domain": "ai4e_contrib.ability.model.pibsnet.advection_numerics", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.model.pibsnet.advection_numerics 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.model.pibsnet.advection_numerics", "topic_id": "module:ai4e_contrib.ability.model.pibsnet.advection_numerics"} -->
# `ai4e_contrib.ability.model.pibsnet.advection_numerics` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-advection-numerics-betaphasecontrolpointnet"></a>
## `ai4e_contrib.ability.model.pibsnet.advection_numerics.BetaPhaseControlPointNet`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`BetaPhaseControlPointNet(n_cp_x, n_cp_t, hidden_dim=64)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.advection_numerics.BetaPhaseControlPointNet`

### 用途

保留锁定原仓库的BetaPhaseControlPointNet数值行为；导数为参数坐标，非物理坐标。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.advection_numerics import BetaPhaseControlPointNet
```

```text
BetaPhaseControlPointNet(n_cp_x, n_cp_t, hidden_dim=64)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `n_cp_x` | `未标注` | `必填` |
| `n_cp_t` | `未标注` | `必填` |
| `hidden_dim` | `未标注` | `64` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`BetaPhaseControlPointNet`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.pibsnet.advection_numerics import BetaPhaseControlPointNet

print(signature(BetaPhaseControlPointNet))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.advection_numerics`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/advection_numerics.py:78`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.advection_numerics')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-advection-numerics-betaphasecontrolpointnet-forward"></a>
## `ai4e_contrib.ability.model.pibsnet.advection_numerics.BetaPhaseControlPointNet.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, beta, phase)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.advection_numerics.BetaPhaseControlPointNet.forward`

### 用途

原控制系数网络前向计算。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.advection_numerics import BetaPhaseControlPointNet
```

```text
forward(self, beta, phase)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `beta` | `未标注` | `必填` |
| `phase` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.pibsnet.advection_numerics import BetaPhaseControlPointNet

print(signature(BetaPhaseControlPointNet.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.advection_numerics`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/advection_numerics.py:89`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.advection_numerics')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-advection-numerics-bsfun"></a>
## `ai4e_contrib.ability.model.pibsnet.advection_numerics.BsFun`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`BsFun(i, d, t, Ln)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.advection_numerics.BsFun`

### 用途

保留锁定原仓库的BsFun数值行为；导数为参数坐标，非物理坐标。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.advection_numerics import BsFun
```

```text
BsFun(i, d, t, Ln)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `i` | `未标注` | `必填` |
| `d` | `未标注` | `必填` |
| `t` | `未标注` | `必填` |
| `Ln` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.pibsnet.advection_numerics import BsFun

print(signature(BsFun))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.advection_numerics`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/advection_numerics.py:8`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.advection_numerics')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-advection-numerics-bsfun-derivative"></a>
## `ai4e_contrib.ability.model.pibsnet.advection_numerics.BsFun_derivative`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`BsFun_derivative(i, d, t, Ln)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.advection_numerics.BsFun_derivative`

### 用途

保留锁定原仓库的BsFun_derivative数值行为；导数为参数坐标，非物理坐标。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.advection_numerics import BsFun_derivative
```

```text
BsFun_derivative(i, d, t, Ln)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `i` | `未标注` | `必填` |
| `d` | `未标注` | `必填` |
| `t` | `未标注` | `必填` |
| `Ln` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.pibsnet.advection_numerics import BsFun_derivative

print(signature(BsFun_derivative))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.advection_numerics`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/advection_numerics.py:18`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.advection_numerics')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-advection-numerics-bsfun-second-derivative"></a>
## `ai4e_contrib.ability.model.pibsnet.advection_numerics.BsFun_second_derivative`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`BsFun_second_derivative(i, d, t, Ln)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.advection_numerics.BsFun_second_derivative`

### 用途

保留锁定原仓库的BsFun_second_derivative数值行为；导数为参数坐标，非物理坐标。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.advection_numerics import BsFun_second_derivative
```

```text
BsFun_second_derivative(i, d, t, Ln)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `i` | `未标注` | `必填` |
| `d` | `未标注` | `必填` |
| `t` | `未标注` | `必填` |
| `Ln` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.pibsnet.advection_numerics import BsFun_second_derivative

print(signature(BsFun_second_derivative))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.advection_numerics`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/advection_numerics.py:28`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.advection_numerics')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-advection-numerics-bsknots"></a>
## `ai4e_contrib.ability.model.pibsnet.advection_numerics.BsKnots`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`BsKnots(n_cp, d, Ns)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.advection_numerics.BsKnots`

### 用途

保留锁定原仓库的BsKnots数值行为；导数为参数坐标，非物理坐标。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.advection_numerics import BsKnots
```

```text
BsKnots(n_cp, d, Ns)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `n_cp` | `未标注` | `必填` |
| `d` | `未标注` | `必填` |
| `Ns` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.pibsnet.advection_numerics import BsKnots

print(signature(BsKnots))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.advection_numerics`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/advection_numerics.py:47`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.advection_numerics')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-advection-numerics-bsknots-derivatives"></a>
## `ai4e_contrib.ability.model.pibsnet.advection_numerics.BsKnots_derivatives`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`BsKnots_derivatives(n_cp, d, Ns, Ln, tk)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.advection_numerics.BsKnots_derivatives`

### 用途

保留锁定原仓库的BsKnots_derivatives数值行为；导数为参数坐标，非物理坐标。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.advection_numerics import BsKnots_derivatives
```

```text
BsKnots_derivatives(n_cp, d, Ns, Ln, tk)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `n_cp` | `未标注` | `必填` |
| `d` | `未标注` | `必填` |
| `Ns` | `未标注` | `必填` |
| `Ln` | `未标注` | `必填` |
| `tk` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.pibsnet.advection_numerics import BsKnots_derivatives

print(signature(BsKnots_derivatives))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.advection_numerics`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/advection_numerics.py:65`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.advection_numerics')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-advection-numerics-assign-first-row-direct"></a>
## `ai4e_contrib.ability.model.pibsnet.advection_numerics.assign_first_row_direct`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`assign_first_row_direct(U_pred, u0_values)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.advection_numerics.assign_first_row_direct`

### 用途

保留锁定原仓库的assign_first_row_direct数值行为；导数为参数坐标，非物理坐标。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.advection_numerics import assign_first_row_direct
```

```text
assign_first_row_direct(U_pred, u0_values)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `U_pred` | `未标注` | `必填` |
| `u0_values` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.pibsnet.advection_numerics import assign_first_row_direct

print(signature(assign_first_row_direct))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.advection_numerics`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/advection_numerics.py:107`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.advection_numerics')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-advection-numerics-compute-bspline-derivatives"></a>
## `ai4e_contrib.ability.model.pibsnet.advection_numerics.compute_bspline_derivatives`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`compute_bspline_derivatives(U_full, Bit_t, Bit_x, Bit_t_derivative, Bit_x_derivative)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.advection_numerics.compute_bspline_derivatives`

### 用途

保留锁定原仓库的compute_bspline_derivatives数值行为；导数为参数坐标，非物理坐标。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.advection_numerics import compute_bspline_derivatives
```

```text
compute_bspline_derivatives(U_full, Bit_t, Bit_x, Bit_t_derivative, Bit_x_derivative)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `U_full` | `未标注` | `必填` |
| `Bit_t` | `未标注` | `必填` |
| `Bit_x` | `未标注` | `必填` |
| `Bit_t_derivative` | `未标注` | `必填` |
| `Bit_x_derivative` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.pibsnet.advection_numerics import compute_bspline_derivatives

print(signature(compute_bspline_derivatives))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.advection_numerics`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/advection_numerics.py:99`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.advection_numerics')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
