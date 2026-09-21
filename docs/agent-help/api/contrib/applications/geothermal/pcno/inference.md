<!-- dojo-help: {"domain": "ai4e_contrib.application.geothermal.pcno.inference", "kind": "api", "layer": "contrib.application", "summary": "ai4e_contrib.application.geothermal.pcno.inference 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.application.geothermal.pcno.inference", "topic_id": "module:ai4e_contrib.application.geothermal.pcno.inference"} -->
# `ai4e_contrib.application.geothermal.pcno.inference` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-application-geothermal-pcno-inference-load-networks"></a>
## `ai4e_contrib.application.geothermal.pcno.inference.load_networks`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`load_networks(cfg, preparation, checkpoints, construct)`
- **规范定义名**：`ai4e_contrib.application.geothermal.pcno.inference.load_networks`

### 用途

核对固定分支来源、数据和结构后加载，只导入明确指定的权重。

### 导入与签名

```python
from ai4e_contrib.application.geothermal.pcno.inference import load_networks
```

```text
load_networks(cfg, preparation, checkpoints, construct)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cfg` | `未标注` | `必填` |
| `preparation` | `未标注` | `必填` |
| `checkpoints` | `未标注` | `必填` |
| `construct` | `未标注` | `必填` |

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
from ai4e_contrib.application.geothermal.pcno.inference import load_networks

print(signature(load_networks))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`pcno`, `pcno_cylinder`
- 案例：`geothermal.pcno`, `pcno.double_cylinder`

### 源码位置

- 模块：`ai4e_contrib.application.geothermal.pcno.inference`
- 仓库相对路径：`packages/ai4e-contrib/application/geothermal/pcno/inference.py:33`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.geothermal.pcno.inference')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-geothermal-pcno-inference-predict-cases"></a>
## `ai4e_contrib.application.geothermal.pcno.inference.predict_cases`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`predict_cases(cfg, preparation, networks, *, session)`
- **规范定义名**：`ai4e_contrib.application.geothermal.pcno.inference.predict_cases`

### 用途

按显式名单预测或回放作者结果；标签仅进入保存后的评价字段。

### 导入与签名

```python
from ai4e_contrib.application.geothermal.pcno.inference import predict_cases
```

```text
predict_cases(cfg, preparation, networks, *, session)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cfg` | `未标注` | `必填` |
| `preparation` | `未标注` | `必填` |
| `networks` | `未标注` | `必填` |
| `session` | `未标注` | `必填关键字参数` |

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
from ai4e_contrib.application.geothermal.pcno.inference import predict_cases

print(signature(predict_cases))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`pcno`
- 案例：`geothermal.pcno`

### 源码位置

- 模块：`ai4e_contrib.application.geothermal.pcno.inference`
- 仓库相对路径：`packages/ai4e-contrib/application/geothermal/pcno/inference.py:63`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.geothermal.pcno.inference')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-geothermal-pcno-inference-publish-checkpoints"></a>
## `ai4e_contrib.application.geothermal.pcno.inference.publish_checkpoints`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`publish_checkpoints(pressure, temperature, output)`
- **规范定义名**：`ai4e_contrib.application.geothermal.pcno.inference.publish_checkpoints`

### 用途

只有两个分支预算都完成才发布可独立消费的权重组合。

### 导入与签名

```python
from ai4e_contrib.application.geothermal.pcno.inference import publish_checkpoints
```

```text
publish_checkpoints(pressure, temperature, output)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `pressure` | `未标注` | `必填` |
| `temperature` | `未标注` | `必填` |
| `output` | `未标注` | `必填` |

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
from ai4e_contrib.application.geothermal.pcno.inference import publish_checkpoints

print(signature(publish_checkpoints))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`pcno`, `pcno_cylinder`
- 案例：`geothermal.pcno`, `pcno.double_cylinder`

### 源码位置

- 模块：`ai4e_contrib.application.geothermal.pcno.inference`
- 仓库相对路径：`packages/ai4e-contrib/application/geothermal/pcno/inference.py:17`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.geothermal.pcno.inference')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
