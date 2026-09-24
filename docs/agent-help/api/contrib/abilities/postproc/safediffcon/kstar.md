<!-- dojo-help: {"domain": "ai4e_contrib.ability.postproc.safediffcon.kstar", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.postproc.safediffcon.kstar 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.postproc.safediffcon.kstar", "topic_id": "module:ai4e_contrib.ability.postproc.safediffcon.kstar"} -->
# `ai4e_contrib.ability.postproc.safediffcon.kstar` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-kstarsolver"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar.KSTARSolver`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`KSTARSolver(random_seed=0)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar.KSTARSolver`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar import KSTARSolver
```

```text
KSTARSolver(random_seed=0)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `random_seed` | `未标注` | `0` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`KSTARSolver`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.postproc.safediffcon.kstar import KSTARSolver

print(signature(KSTARSolver))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar.py:124`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-kstarsolver-control"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar.KSTARSolver.control`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`control(self, action)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar.KSTARSolver.control`

### 用途

Use actions to update inputs.

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar import KSTARSolver
```

```text
control(self, action)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `action` | `未标注` | `必填` |

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
from ai4e_contrib.ability.postproc.safediffcon.kstar import KSTARSolver

print(signature(KSTARSolver.control))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`safediffcon`
- 案例：`recipe_extensions.task_labels`, `safediffcon.burgers`, `safediffcon.tokamak`

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar.py:361`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-kstarsolver-initialize-inputs"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar.KSTARSolver.initialize_inputs`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`initialize_inputs(self)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar.KSTARSolver.initialize_inputs`

### 用途

Initialize input parameters scaled as integers.

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar import KSTARSolver
```

```text
initialize_inputs(self)
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

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
from ai4e_contrib.ability.postproc.safediffcon.kstar import KSTARSolver

print(signature(KSTARSolver.initialize_inputs))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar.py:152`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-kstarsolver-predict-0d"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar.KSTARSolver.predict_0d`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`predict_0d(self, steady=True)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar.KSTARSolver.predict_0d`

### 用途

Predict 0D plasma parameters.

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar import KSTARSolver
```

```text
predict_0d(self, steady=True)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `steady` | `未标注` | `True` |

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
from ai4e_contrib.ability.postproc.safediffcon.kstar import KSTARSolver

print(signature(KSTARSolver.predict_0d))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar.py:165`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-kstarsolver-reset-model-number"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar.KSTARSolver.reset_model_number`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`reset_model_number(self)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar.KSTARSolver.reset_model_number`

### 用途

MImic the original codes behavior 

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar import KSTARSolver
```

```text
reset_model_number(self)
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

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
from ai4e_contrib.ability.postproc.safediffcon.kstar import KSTARSolver

print(signature(KSTARSolver.reset_model_number))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar.py:157`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-kstarsolver-return-outputs"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar.KSTARSolver.return_outputs`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`return_outputs(self)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar.KSTARSolver.return_outputs`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar import KSTARSolver
```

```text
return_outputs(self)
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

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
from ai4e_contrib.ability.postproc.safediffcon.kstar import KSTARSolver

print(signature(KSTARSolver.return_outputs))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar.py:383`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-kstarsolver-simulate"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar.KSTARSolver.simulate`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`simulate(self, actions)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar.KSTARSolver.simulate`

### 用途

Run the simulation for a specified number of steps.

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar import KSTARSolver
```

```text
simulate(self, actions)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `actions` | `未标注` | `必填` |

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
from ai4e_contrib.ability.postproc.safediffcon.kstar import KSTARSolver

print(signature(KSTARSolver.simulate))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar.py:390`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-f2i"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar.f2i`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`f2i(f, decimals=decimals)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar.f2i`

### 用途

Convert float to integer by scaling.

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar import f2i
```

```text
f2i(f, decimals=decimals)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `f` | `未标注` | `必填` |
| `decimals` | `未标注` | `decimals` |

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
from ai4e_contrib.ability.postproc.safediffcon.kstar import f2i

print(signature(f2i))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar.py:116`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-i2f"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar.i2f`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`i2f(i, decimals=decimals)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar.i2f`

### 用途

Convert integer to float with fixed decimal precision.

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar import i2f
```

```text
i2f(i, decimals=decimals)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `i` | `未标注` | `必填` |
| `decimals` | `未标注` | `decimals` |

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
from ai4e_contrib.ability.postproc.safediffcon.kstar import i2f

print(signature(i2f))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar.py:112`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
