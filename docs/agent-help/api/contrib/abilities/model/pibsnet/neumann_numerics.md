<!-- dojo-help: {"domain": "ai4e_contrib.ability.model.pibsnet.neumann_numerics", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.model.pibsnet.neumann_numerics 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.model.pibsnet.neumann_numerics", "topic_id": "module:ai4e_contrib.ability.model.pibsnet.neumann_numerics"} -->
# `ai4e_contrib.ability.model.pibsnet.neumann_numerics` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-neumann-numerics-bsnetloss"></a>
## `ai4e_contrib.ability.model.pibsnet.neumann_numerics.BSNetLoss`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`BSNetLoss(n_cp_t, n_cp_x, hidden=128)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.neumann_numerics.BSNetLoss`

### 用途

保留锁定原仓库的BSNetLoss数值行为；导数为参数坐标，非物理坐标。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.neumann_numerics import BSNetLoss
```

```text
BSNetLoss(n_cp_t, n_cp_x, hidden=128)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `n_cp_t` | `未标注` | `必填` |
| `n_cp_x` | `未标注` | `必填` |
| `hidden` | `未标注` | `128` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`BSNetLoss`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.pibsnet.neumann_numerics import BSNetLoss

print(signature(BSNetLoss))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.neumann_numerics`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/neumann_numerics.py:100`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.neumann_numerics')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-neumann-numerics-bsnetloss-forward-u"></a>
## `ai4e_contrib.ability.model.pibsnet.neumann_numerics.BSNetLoss.forward_U`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward_U(self, nu)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.neumann_numerics.BSNetLoss.forward_U`

### 用途

原控制系数网络前向计算。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.neumann_numerics import BSNetLoss
```

```text
forward_U(self, nu)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `nu` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.pibsnet.neumann_numerics import BSNetLoss

print(signature(BSNetLoss.forward_U))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.neumann_numerics`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/neumann_numerics.py:108`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.neumann_numerics')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-neumann-numerics-bsfun"></a>
## `ai4e_contrib.ability.model.pibsnet.neumann_numerics.BsFun`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`BsFun(i, d, t, Ln)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.neumann_numerics.BsFun`

### 用途

保留锁定原仓库的BsFun数值行为；导数为参数坐标，非物理坐标。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.neumann_numerics import BsFun
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
from ai4e_contrib.ability.model.pibsnet.neumann_numerics import BsFun

print(signature(BsFun))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.neumann_numerics`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/neumann_numerics.py:7`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.neumann_numerics')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-neumann-numerics-bsfun-derivative"></a>
## `ai4e_contrib.ability.model.pibsnet.neumann_numerics.BsFun_derivative`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`BsFun_derivative(i, d, t, Ln)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.neumann_numerics.BsFun_derivative`

### 用途

保留锁定原仓库的BsFun_derivative数值行为；导数为参数坐标，非物理坐标。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.neumann_numerics import BsFun_derivative
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
from ai4e_contrib.ability.model.pibsnet.neumann_numerics import BsFun_derivative

print(signature(BsFun_derivative))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.neumann_numerics`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/neumann_numerics.py:16`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.neumann_numerics')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-neumann-numerics-bsfun-second-derivative"></a>
## `ai4e_contrib.ability.model.pibsnet.neumann_numerics.BsFun_second_derivative`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`BsFun_second_derivative(i, d, t, Ln)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.neumann_numerics.BsFun_second_derivative`

### 用途

保留锁定原仓库的BsFun_second_derivative数值行为；导数为参数坐标，非物理坐标。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.neumann_numerics import BsFun_second_derivative
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
from ai4e_contrib.ability.model.pibsnet.neumann_numerics import BsFun_second_derivative

print(signature(BsFun_second_derivative))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.neumann_numerics`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/neumann_numerics.py:25`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.neumann_numerics')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-neumann-numerics-bsknots"></a>
## `ai4e_contrib.ability.model.pibsnet.neumann_numerics.BsKnots`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`BsKnots(n_cp, d, Ns)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.neumann_numerics.BsKnots`

### 用途

保留锁定原仓库的BsKnots数值行为；导数为参数坐标，非物理坐标。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.neumann_numerics import BsKnots
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
from ai4e_contrib.ability.model.pibsnet.neumann_numerics import BsKnots

print(signature(BsKnots))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.neumann_numerics`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/neumann_numerics.py:41`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.neumann_numerics')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-neumann-numerics-bsknots-derivatives"></a>
## `ai4e_contrib.ability.model.pibsnet.neumann_numerics.BsKnots_derivatives`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`BsKnots_derivatives(n_cp, d, Ns, Ln, tk)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.neumann_numerics.BsKnots_derivatives`

### 用途

保留锁定原仓库的BsKnots_derivatives数值行为；导数为参数坐标，非物理坐标。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.neumann_numerics import BsKnots_derivatives
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
from ai4e_contrib.ability.model.pibsnet.neumann_numerics import BsKnots_derivatives

print(signature(BsKnots_derivatives))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.neumann_numerics`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/neumann_numerics.py:57`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.neumann_numerics')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-neumann-numerics-controlpointnet"></a>
## `ai4e_contrib.ability.model.pibsnet.neumann_numerics.ControlPointNet`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`ControlPointNet(n_cp_t, n_cp_x, hidden=128)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.neumann_numerics.ControlPointNet`

### 用途

保留锁定原仓库的ControlPointNet数值行为；导数为参数坐标，非物理坐标。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.neumann_numerics import ControlPointNet
```

```text
ControlPointNet(n_cp_t, n_cp_x, hidden=128)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `n_cp_t` | `未标注` | `必填` |
| `n_cp_x` | `未标注` | `必填` |
| `hidden` | `未标注` | `128` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`ControlPointNet`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.pibsnet.neumann_numerics import ControlPointNet

print(signature(ControlPointNet))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.neumann_numerics`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/neumann_numerics.py:81`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.neumann_numerics')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-neumann-numerics-controlpointnet-forward"></a>
## `ai4e_contrib.ability.model.pibsnet.neumann_numerics.ControlPointNet.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, nu)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.neumann_numerics.ControlPointNet.forward`

### 用途

原控制系数网络前向计算。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.neumann_numerics import ControlPointNet
```

```text
forward(self, nu)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `nu` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.pibsnet.neumann_numerics import ControlPointNet

print(signature(ControlPointNet.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.neumann_numerics`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/neumann_numerics.py:95`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.neumann_numerics')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-neumann-numerics-bspline-derivs"></a>
## `ai4e_contrib.ability.model.pibsnet.neumann_numerics.bspline_derivs`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`bspline_derivs(U, Bt, Bx, Bt_d1, Bx_d1, Bt_d2, Bx_d2)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.neumann_numerics.bspline_derivs`

### 用途

保留锁定原仓库的bspline_derivs数值行为；导数为参数坐标，非物理坐标。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.neumann_numerics import bspline_derivs
```

```text
bspline_derivs(U, Bt, Bx, Bt_d1, Bx_d1, Bt_d2, Bx_d2)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `U` | `未标注` | `必填` |
| `Bt` | `未标注` | `必填` |
| `Bx` | `未标注` | `必填` |
| `Bt_d1` | `未标注` | `必填` |
| `Bx_d1` | `未标注` | `必填` |
| `Bt_d2` | `未标注` | `必填` |
| `Bx_d2` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.pibsnet.neumann_numerics import bspline_derivs

print(signature(bspline_derivs))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.neumann_numerics`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/neumann_numerics.py:73`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.neumann_numerics')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-pibsnet-neumann-numerics-bspline-eval"></a>
## `ai4e_contrib.ability.model.pibsnet.neumann_numerics.bspline_eval`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`bspline_eval(U, Bt, Bx)`
- **规范定义名**：`ai4e_contrib.ability.model.pibsnet.neumann_numerics.bspline_eval`

### 用途

保留锁定原仓库的bspline_eval数值行为；导数为参数坐标，非物理坐标。

### 导入与签名

```python
from ai4e_contrib.ability.model.pibsnet.neumann_numerics import bspline_eval
```

```text
bspline_eval(U, Bt, Bx)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `U` | `未标注` | `必填` |
| `Bt` | `未标注` | `必填` |
| `Bx` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.pibsnet.neumann_numerics import bspline_eval

print(signature(bspline_eval))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.pibsnet.neumann_numerics`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/pibsnet/neumann_numerics.py:68`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.pibsnet.neumann_numerics')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
