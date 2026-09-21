<!-- dojo-help: {"domain": "ai4e_contrib.application.geothermal.pcno.economy", "kind": "api", "layer": "contrib.application", "summary": "ai4e_contrib.application.geothermal.pcno.economy 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.application.geothermal.pcno.economy", "topic_id": "module:ai4e_contrib.application.geothermal.pcno.economy"} -->
# `ai4e_contrib.application.geothermal.pcno.economy` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-application-geothermal-pcno-economy-ensure-column"></a>
## `ai4e_contrib.application.geothermal.pcno.economy.ensure_column`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`ensure_column(arr)`
- **规范定义名**：`ai4e_contrib.application.geothermal.pcno.economy.ensure_column`

### 用途

发布字段到地热经济输入的连接；井级取均值和求和按原源码：ensure_column；保留来源算法、参数与权重布局。

### 导入与签名

```python
from ai4e_contrib.application.geothermal.pcno.economy import ensure_column
```

```text
ensure_column(arr)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `arr` | `未标注` | `必填` |

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
from ai4e_contrib.application.geothermal.pcno.economy import ensure_column

print(signature(ensure_column))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.geothermal.pcno.economy`
- 仓库相对路径：`packages/ai4e-contrib/application/geothermal/pcno/economy.py:88`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.geothermal.pcno.economy')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-geothermal-pcno-economy-evaluate-economy"></a>
## `ai4e_contrib.application.geothermal.pcno.economy.evaluate_economy`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`evaluate_economy(pred, raw, stats, T_threshold=75, CF=0.85)`
- **规范定义名**：`ai4e_contrib.application.geothermal.pcno.economy.evaluate_economy`

### 用途

只消费固定预测；Temp_drop 保留作者首例平均温度基准，不解释为物理初温降幅。

### 导入与签名

```python
from ai4e_contrib.application.geothermal.pcno.economy import evaluate_economy
```

```text
evaluate_economy(pred, raw, stats, T_threshold=75, CF=0.85)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `pred` | `未标注` | `必填` |
| `raw` | `未标注` | `必填` |
| `stats` | `未标注` | `必填` |
| `T_threshold` | `未标注` | `75` |
| `CF` | `未标注` | `0.85` |

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
from ai4e_contrib.application.geothermal.pcno.economy import evaluate_economy

print(signature(evaluate_economy))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.geothermal.pcno.economy`
- 仓库相对路径：`packages/ai4e-contrib/application/geothermal/pcno/economy.py:93`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.geothermal.pcno.economy')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-geothermal-pcno-economy-technical-results"></a>
## `ai4e_contrib.application.geothermal.pcno.economy.technical_results`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`technical_results(qout, sp, gp, Twh_list, Hwh_list, Ewh_list, Pinj_list, stats)`
- **规范定义名**：`ai4e_contrib.application.geothermal.pcno.economy.technical_results`

### 用途

发布字段到地热经济输入的连接；井级取均值和求和按原源码：technical_results；保留来源算法、参数与权重布局。

### 导入与签名

```python
from ai4e_contrib.application.geothermal.pcno.economy import technical_results
```

```text
technical_results(qout, sp, gp, Twh_list, Hwh_list, Ewh_list, Pinj_list, stats)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `qout` | `未标注` | `必填` |
| `sp` | `未标注` | `必填` |
| `gp` | `未标注` | `必填` |
| `Twh_list` | `未标注` | `必填` |
| `Hwh_list` | `未标注` | `必填` |
| `Ewh_list` | `未标注` | `必填` |
| `Pinj_list` | `未标注` | `必填` |
| `stats` | `未标注` | `必填` |

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
from ai4e_contrib.application.geothermal.pcno.economy import technical_results

print(signature(technical_results))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.geothermal.pcno.economy`
- 仓库相对路径：`packages/ai4e-contrib/application/geothermal/pcno/economy.py:11`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.geothermal.pcno.economy')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
