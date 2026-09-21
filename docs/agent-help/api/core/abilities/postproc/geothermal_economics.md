<!-- dojo-help: {"domain": "ai4e_core.abilities.postproc.geothermal_economics", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.postproc.geothermal_economics 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.postproc.geothermal_economics", "topic_id": "module:ai4e_core.abilities.postproc.geothermal_economics"} -->
# `ai4e_core.abilities.postproc.geothermal_economics` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-postproc-geothermal-economics-cap-cost"></a>
## `ai4e_core.abilities.postproc.geothermal_economics.cap_cost`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`cap_cost(depth, well_number, enthalpy, avg_heat, stimulation=None)`
- **规范定义名**：`ai4e_core.abilities.postproc.geothermal_economics.cap_cost`

### 用途

地热二十年技术经济计算；保留原成本、折现与评分公式：cap_cost；保留来源算法、参数与权重布局。

### 导入与签名

```python
from ai4e_core.abilities.postproc.geothermal_economics import cap_cost
```

```text
cap_cost(depth, well_number, enthalpy, avg_heat, stimulation=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `depth` | `未标注` | `必填` |
| `well_number` | `未标注` | `必填` |
| `enthalpy` | `未标注` | `必填` |
| `avg_heat` | `未标注` | `必填` |
| `stimulation` | `未标注` | `None` |

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
from ai4e_core.abilities.postproc.geothermal_economics import cap_cost

print(signature(cap_cost))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.geothermal_economics`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/geothermal_economics.py:13`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.geothermal_economics')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-geothermal-economics-level-cost"></a>
## `ai4e_core.abilities.postproc.geothermal_economics.level_cost`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`level_cost(temp_year, temp_avg, heat_year, heat_avg, enth_avg, rate_year, well_num, well_dep, T_threshold, CF)`
- **规范定义名**：`ai4e_core.abilities.postproc.geothermal_economics.level_cost`

### 用途

地热二十年技术经济计算；保留原成本、折现与评分公式：level_cost；保留来源算法、参数与权重布局。

### 导入与签名

```python
from ai4e_core.abilities.postproc.geothermal_economics import level_cost
```

```text
level_cost(temp_year, temp_avg, heat_year, heat_avg, enth_avg, rate_year, well_num, well_dep, T_threshold, CF)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `temp_year` | `未标注` | `必填` |
| `temp_avg` | `未标注` | `必填` |
| `heat_year` | `未标注` | `必填` |
| `heat_avg` | `未标注` | `必填` |
| `enth_avg` | `未标注` | `必填` |
| `rate_year` | `未标注` | `必填` |
| `well_num` | `未标注` | `必填` |
| `well_dep` | `未标注` | `必填` |
| `T_threshold` | `未标注` | `必填` |
| `CF` | `未标注` | `必填` |

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
from ai4e_core.abilities.postproc.geothermal_economics import level_cost

print(signature(level_cost))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.geothermal_economics`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/geothermal_economics.py:71`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.geothermal_economics')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-geothermal-economics-ope-cost"></a>
## `ai4e_core.abilities.postproc.geothermal_economics.ope_cost`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`ope_cost(y_temp, y_heat, y_fluid_rate, capital_plant, capital_pump, capital_well)`
- **规范定义名**：`ai4e_core.abilities.postproc.geothermal_economics.ope_cost`

### 用途

地热二十年技术经济计算；保留原成本、折现与评分公式：ope_cost；保留来源算法、参数与权重布局。

### 导入与签名

```python
from ai4e_core.abilities.postproc.geothermal_economics import ope_cost
```

```text
ope_cost(y_temp, y_heat, y_fluid_rate, capital_plant, capital_pump, capital_well)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `y_temp` | `未标注` | `必填` |
| `y_heat` | `未标注` | `必填` |
| `y_fluid_rate` | `未标注` | `必填` |
| `capital_plant` | `未标注` | `必填` |
| `capital_pump` | `未标注` | `必填` |
| `capital_well` | `未标注` | `必填` |

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
from ai4e_core.abilities.postproc.geothermal_economics import ope_cost

print(signature(ope_cost))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.geothermal_economics`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/geothermal_economics.py:51`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.geothermal_economics')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-geothermal-economics-score-tech-econ"></a>
## `ai4e_core.abilities.postproc.geothermal_economics.score_tech_econ`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`score_tech_econ(eco_para, tech_para, Pinj, P)`
- **规范定义名**：`ai4e_core.abilities.postproc.geothermal_economics.score_tech_econ`

### 用途

地热二十年技术经济计算；保留原成本、折现与评分公式：score_tech_econ；保留来源算法、参数与权重布局。

### 导入与签名

```python
from ai4e_core.abilities.postproc.geothermal_economics import score_tech_econ
```

```text
score_tech_econ(eco_para, tech_para, Pinj, P)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `eco_para` | `未标注` | `必填` |
| `tech_para` | `未标注` | `必填` |
| `Pinj` | `未标注` | `必填` |
| `P` | `未标注` | `必填` |

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
from ai4e_core.abilities.postproc.geothermal_economics import score_tech_econ

print(signature(score_tech_econ))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.geothermal_economics`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/geothermal_economics.py:126`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.geothermal_economics')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-postproc-geothermal-economics-utilization-eff"></a>
## `ai4e_core.abilities.postproc.geothermal_economics.utilization_eff`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`utilization_eff(Enthalpy)`
- **规范定义名**：`ai4e_core.abilities.postproc.geothermal_economics.utilization_eff`

### 用途

地热二十年技术经济计算；保留原成本、折现与评分公式：utilization_eff；保留来源算法、参数与权重布局。

### 导入与签名

```python
from ai4e_core.abilities.postproc.geothermal_economics import utilization_eff
```

```text
utilization_eff(Enthalpy)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `Enthalpy` | `未标注` | `必填` |

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
from ai4e_core.abilities.postproc.geothermal_economics import utilization_eff

print(signature(utilization_eff))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.postproc.geothermal_economics`
- 仓库相对路径：`packages/ai4e-core/abilities/postproc/geothermal_economics.py:9`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.postproc.geothermal_economics')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
