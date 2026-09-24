<!-- dojo-help: {"domain": "ai4e_contrib.application.spatiotemporal_pde.pcno.inference", "kind": "api", "layer": "contrib.application", "summary": "ai4e_contrib.application.spatiotemporal_pde.pcno.inference 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.application.spatiotemporal_pde.pcno.inference", "topic_id": "module:ai4e_contrib.application.spatiotemporal_pde.pcno.inference"} -->
# `ai4e_contrib.application.spatiotemporal_pde.pcno.inference` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-application-spatiotemporal-pde-pcno-inference-evaluation-records"></a>
## `ai4e_contrib.application.spatiotemporal_pde.pcno.inference.evaluation_records`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`evaluation_records(prepared, split)`
- **规范定义名**：`ai4e_contrib.application.spatiotemporal_pde.pcno.inference.evaluation_records`

### 用途

确定性非重叠目标窗口名单，不根据测试效果选择窗口。

### 导入与签名

```python
from ai4e_contrib.application.spatiotemporal_pde.pcno.inference import evaluation_records
```

```text
evaluation_records(prepared, split)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `prepared` | `未标注` | `必填` |
| `split` | `未标注` | `必填` |

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
from ai4e_contrib.application.spatiotemporal_pde.pcno.inference import evaluation_records

print(signature(evaluation_records))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`pcno_cylinder`
- 案例：`pcno.double_cylinder`

### 源码位置

- 模块：`ai4e_contrib.application.spatiotemporal_pde.pcno.inference`
- 仓库相对路径：`packages/ai4e-contrib/application/spatiotemporal_pde/pcno/inference.py:50`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.spatiotemporal_pde.pcno.inference')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-spatiotemporal-pde-pcno-inference-load-networks"></a>
## `ai4e_contrib.application.spatiotemporal_pde.pcno.inference.load_networks`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`load_networks(cfg, preparation, checkpoints)`
- **规范定义名**：`ai4e_contrib.application.spatiotemporal_pde.pcno.inference.load_networks`

### 用途

校验三个最终分支及准备摘要，恢复本次真实构造器。

### 导入与签名

```python
from ai4e_contrib.application.spatiotemporal_pde.pcno.inference import load_networks
```

```text
load_networks(cfg, preparation, checkpoints)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cfg` | `未标注` | `必填` |
| `preparation` | `未标注` | `必填` |
| `checkpoints` | `未标注` | `必填` |

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
from ai4e_contrib.application.spatiotemporal_pde.pcno.inference import load_networks

print(signature(load_networks))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`pcno`, `pcno_cylinder`
- 案例：`geothermal.pcno`, `pcno.double_cylinder`

### 源码位置

- 模块：`ai4e_contrib.application.spatiotemporal_pde.pcno.inference`
- 仓库相对路径：`packages/ai4e-contrib/application/spatiotemporal_pde/pcno/inference.py:15`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.spatiotemporal_pde.pcno.inference')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-spatiotemporal-pde-pcno-inference-predictor"></a>
## `ai4e_contrib.application.spatiotemporal_pde.pcno.inference.predictor`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`predictor(prepared, networks, provenance)`
- **规范定义名**：`ai4e_contrib.application.spatiotemporal_pde.pcno.inference.predictor`

### 用途

构造联合预测；网络调用仅收到input，不接收physical/target。

### 导入与签名

```python
from ai4e_contrib.application.spatiotemporal_pde.pcno.inference import predictor
```

```text
predictor(prepared, networks, provenance)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `prepared` | `未标注` | `必填` |
| `networks` | `未标注` | `必填` |
| `provenance` | `未标注` | `必填` |

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
from ai4e_contrib.application.spatiotemporal_pde.pcno.inference import predictor

print(signature(predictor))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`pcno_cylinder`, `surrogate_modeling/double_cylinder`, `surrogate_modeling/nasa_crm`
- 案例：`pcno.double_cylinder`, `surrogate_modeling.double_cylinder`, `surrogate_modeling.nasa_crm`

### 源码位置

- 模块：`ai4e_contrib.application.spatiotemporal_pde.pcno.inference`
- 仓库相对路径：`packages/ai4e-contrib/application/spatiotemporal_pde/pcno/inference.py:64`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.spatiotemporal_pde.pcno.inference')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-spatiotemporal-pde-pcno-inference-reader"></a>
## `ai4e_contrib.application.spatiotemporal_pde.pcno.inference.reader`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`reader(prepared)`
- **规范定义名**：`ai4e_contrib.application.spatiotemporal_pde.pcno.inference.reader`

### 用途

返回领域窗口读取函数。

### 导入与签名

```python
from ai4e_contrib.application.spatiotemporal_pde.pcno.inference import reader
```

```text
reader(prepared)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `prepared` | `未标注` | `必填` |

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
from ai4e_contrib.application.spatiotemporal_pde.pcno.inference import reader

print(signature(reader))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`gencp`, `pcno_cylinder`, `safediffcon`, `wdno`
- 案例：`gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `pcno.double_cylinder`, `recipe_extensions.task_labels`, `recipe_extensions.wdno`, `safediffcon.burgers`, `safediffcon.tokamak`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.application.spatiotemporal_pde.pcno.inference`
- 仓库相对路径：`packages/ai4e-contrib/application/spatiotemporal_pde/pcno/inference.py:59`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.spatiotemporal_pde.pcno.inference')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
