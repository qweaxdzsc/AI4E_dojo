<!-- dojo-help: {"domain": "ai4e_core.abilities.postproc.wellbore", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.postproc.wellbore 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.postproc.wellbore", "topic_id": "module:ai4e_core.abilities.postproc.wellbore"} -->
# `ai4e_core.abilities.postproc.wellbore` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-postproc-wellbore-wellboremodel"></a>
## `ai4e_core.abilities.postproc.wellbore.WellboreModel`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`WellboreModel(flow_rate, R_TC, R_cp, tubing_id=0.18, tubing_od=0.2, angle=90, R_rho=2500, U=10, rough=1e-05)`
- **规范定义名**：`ai4e_core.abilities.postproc.wellbore.WellboreModel`

### 用途

井筒水汽物性与数值积分；井口结果经标量求解而不保留自动微分图：WellboreModel；保留来源算法、参数与权重布局。

### 导入与签名

```python
from ai4e_core.abilities.postproc.wellbore import WellboreModel
```

```text
WellboreModel(flow_rate, R_TC, R_cp, tubing_id=0.18, tubing_od=0.2, angle=90, R_rho=2500, U=10, rough=1e-05)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `flow_rate` | `未标注` | `必填` |
| `R_TC` | `未标注` | `必填` |
| `R_cp` | `未标注` | `必填` |
| `tubing_id` | `未标注` | `0.18` |
| `tubing_od` | `未标注` | `0.2` |
| `angle` | `未标注` | `90` |
| `R_rho` | `未标注` | `2500` |
| `U` | `未标注` | `10` |
| `rough` | `未标注` | `1e-05` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`WellboreModel`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.postproc.wellbore import WellboreModel

print(signature(WellboreModel))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.wellbore`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/wellbore.py:11`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.wellbore')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-wellbore-wellboremodel-friction"></a>
## `ai4e_core.abilities.postproc.wellbore.WellboreModel.friction`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`friction(self, rho_m, mu_m, v_m)`
- **规范定义名**：`ai4e_core.abilities.postproc.wellbore.WellboreModel.friction`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_core.abilities.postproc.wellbore import WellboreModel
```

```text
friction(self, rho_m, mu_m, v_m)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `rho_m` | `未标注` | `必填` |
| `mu_m` | `未标注` | `必填` |
| `v_m` | `未标注` | `必填` |

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
from ai4e_core.abilities.postproc.wellbore import WellboreModel

print(signature(WellboreModel.friction))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.wellbore`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/wellbore.py:28`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.wellbore')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-wellbore-wellboremodel-ramey"></a>
## `ai4e_core.abilities.postproc.wellbore.WellboreModel.ramey`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`ramey(t_D)`
- **规范定义名**：`ai4e_core.abilities.postproc.wellbore.WellboreModel.ramey`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_core.abilities.postproc.wellbore import WellboreModel
```

```text
ramey(t_D)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `t_D` | `未标注` | `必填` |

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
from ai4e_core.abilities.postproc.wellbore import WellboreModel

print(signature(WellboreModel.ramey))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.wellbore`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/wellbore.py:52`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.wellbore')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-wellbore-wellboremodel-select-flow-pattern"></a>
## `ai4e_core.abilities.postproc.wellbore.WellboreModel.select_flow_pattern`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`select_flow_pattern(self, v_sg, v_sL, rho_g, rho_L, mu_g, mu_L, sigma)`
- **规范定义名**：`ai4e_core.abilities.postproc.wellbore.WellboreModel.select_flow_pattern`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_core.abilities.postproc.wellbore import WellboreModel
```

```text
select_flow_pattern(self, v_sg, v_sL, rho_g, rho_L, mu_g, mu_L, sigma)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `v_sg` | `未标注` | `必填` |
| `v_sL` | `未标注` | `必填` |
| `rho_g` | `未标注` | `必填` |
| `rho_L` | `未标注` | `必填` |
| `mu_g` | `未标注` | `必填` |
| `mu_L` | `未标注` | `必填` |
| `sigma` | `未标注` | `必填` |

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
from ai4e_core.abilities.postproc.wellbore import WellboreModel

print(signature(WellboreModel.select_flow_pattern))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.wellbore`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/wellbore.py:58`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.wellbore')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-wellbore-wellboremodel-simulate"></a>
## `ai4e_core.abilities.postproc.wellbore.WellboreModel.simulate`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`simulate(self, depth, P_btm, Tf_btm, T_grad, T_surf=15, steps=40, t_days=0.0)`
- **规范定义名**：`ai4e_core.abilities.postproc.wellbore.WellboreModel.simulate`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_core.abilities.postproc.wellbore import WellboreModel
```

```text
simulate(self, depth, P_btm, Tf_btm, T_grad, T_surf=15, steps=40, t_days=0.0)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `depth` | `未标注` | `必填` |
| `P_btm` | `未标注` | `必填` |
| `Tf_btm` | `未标注` | `必填` |
| `T_grad` | `未标注` | `必填` |
| `T_surf` | `未标注` | `15` |
| `steps` | `未标注` | `40` |
| `t_days` | `未标注` | `0.0` |

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
from ai4e_core.abilities.postproc.wellbore import WellboreModel

print(signature(WellboreModel.simulate))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.wellbore`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/wellbore.py:218`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.wellbore')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-wellbore-wellboremodel-solve-step"></a>
## `ai4e_core.abilities.postproc.wellbore.WellboreModel.solve_step`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`solve_step(self, P_MPa, h_kJkg, T_ei_C, t_days, r_wb_m=None)`
- **规范定义名**：`ai4e_core.abilities.postproc.wellbore.WellboreModel.solve_step`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_core.abilities.postproc.wellbore import WellboreModel
```

```text
solve_step(self, P_MPa, h_kJkg, T_ei_C, t_days, r_wb_m=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `P_MPa` | `未标注` | `必填` |
| `h_kJkg` | `未标注` | `必填` |
| `T_ei_C` | `未标注` | `必填` |
| `t_days` | `未标注` | `必填` |
| `r_wb_m` | `未标注` | `None` |

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
from ai4e_core.abilities.postproc.wellbore import WellboreModel

print(signature(WellboreModel.solve_step))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.wellbore`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/wellbore.py:122`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.wellbore')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-wellbore-extract-welldata"></a>
## `ai4e_core.abilities.postproc.wellbore.extract_wellData`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`extract_wellData(field, mask)`
- **规范定义名**：`ai4e_core.abilities.postproc.wellbore.extract_wellData`

### 用途

井筒水汽物性与数值积分；井口结果经标量求解而不保留自动微分图：extract_wellData；保留来源算法、参数与权重布局。

### 导入与签名

```python
from ai4e_core.abilities.postproc.wellbore import extract_wellData
```

```text
extract_wellData(field, mask)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `field` | `未标注` | `必填` |
| `mask` | `未标注` | `必填` |

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
from ai4e_core.abilities.postproc.wellbore import extract_wellData

print(signature(extract_wellData))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.wellbore`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/wellbore.py:288`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.wellbore')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-wellbore-process-wellresult"></a>
## `ai4e_core.abilities.postproc.wellbore.process_wellResult`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`process_wellResult(dz_list, grad_T_list, BHT_list, BHP_list, BHQ_list, TC_list, Cp_list)`
- **规范定义名**：`ai4e_core.abilities.postproc.wellbore.process_wellResult`

### 用途

井筒水汽物性与数值积分；井口结果经标量求解而不保留自动微分图：process_wellResult；保留来源算法、参数与权重布局。

### 导入与签名

```python
from ai4e_core.abilities.postproc.wellbore import process_wellResult
```

```text
process_wellResult(dz_list, grad_T_list, BHT_list, BHP_list, BHQ_list, TC_list, Cp_list)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dz_list` | `未标注` | `必填` |
| `grad_T_list` | `未标注` | `必填` |
| `BHT_list` | `未标注` | `必填` |
| `BHP_list` | `未标注` | `必填` |
| `BHQ_list` | `未标注` | `必填` |
| `TC_list` | `未标注` | `必填` |
| `Cp_list` | `未标注` | `必填` |

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
from ai4e_core.abilities.postproc.wellbore import process_wellResult

print(signature(process_wellResult))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.wellbore`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/wellbore.py:319`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.wellbore')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-wellbore-wellbore-model-run"></a>
## `ai4e_core.abilities.postproc.wellbore.wellbore_model_run`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`wellbore_model_run(BHT, BHP, depth, T_grad, m_dot, R_TC, R_cp)`
- **规范定义名**：`ai4e_core.abilities.postproc.wellbore.wellbore_model_run`

### 用途

井筒水汽物性与数值积分；井口结果经标量求解而不保留自动微分图：wellbore_model_run；保留来源算法、参数与权重布局。

### 导入与签名

```python
from ai4e_core.abilities.postproc.wellbore import wellbore_model_run
```

```text
wellbore_model_run(BHT, BHP, depth, T_grad, m_dot, R_TC, R_cp)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `BHT` | `未标注` | `必填` |
| `BHP` | `未标注` | `必填` |
| `depth` | `未标注` | `必填` |
| `T_grad` | `未标注` | `必填` |
| `m_dot` | `未标注` | `必填` |
| `R_TC` | `未标注` | `必填` |
| `R_cp` | `未标注` | `必填` |

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
from ai4e_core.abilities.postproc.wellbore import wellbore_model_run

print(signature(wellbore_model_run))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.wellbore`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/wellbore.py:282`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.wellbore')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
