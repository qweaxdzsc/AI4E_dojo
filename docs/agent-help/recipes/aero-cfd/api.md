<!-- dojo-help: {"domain": "recipes.aero_cfd.configuration", "kind": "recipe", "layer": "recipe", "summary": "recipes.aero_cfd.configuration 的完整源码参考与公开符号索引。", "title": "recipes.aero_cfd.configuration", "topic_id": "module:recipes.aero_cfd.configuration"} -->
# `recipes.aero_cfd.configuration` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-recipes-aero-cfd-configuration-application-parameters"></a>
## `recipes.aero_cfd.configuration.application_parameters`

- **层级**：`recipe`
- **稳定性**：`extension`
- **定义**：`application_parameters(config, *, session=None)`
- **规范定义名**：`recipes.aero_cfd.configuration.application_parameters`

### 用途

纯配置转换；执行正文可显式传入会话以分配本次输出。

### 导入与签名

```python
from recipes.aero_cfd.configuration import application_parameters
```

```text
application_parameters(config, *, session=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `未标注` | `必填` |
| `session` | `未标注` | `None` |

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
from recipes.aero_cfd.configuration import application_parameters

print(signature(application_parameters))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`

### 源码位置

- 模块：`recipes.aero_cfd.configuration`
- 仓库相对路径：`recipes/aero_cfd/configuration.py:8`
- 安装源码：先调用 `ai4e_task.source_location('recipes')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('recipes.aero_cfd.configuration')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-recipes-aero-cfd-configuration-load-configuration"></a>
## `recipes.aero_cfd.configuration.load_configuration`

- **层级**：`recipe`
- **稳定性**：`extension`
- **定义**：`load_configuration(path, overrides=None)`
- **规范定义名**：`recipes.aero_cfd.configuration.load_configuration`

### 用途

以配置文件位置解析参数；不在复制目录维护平台内部键转换。

### 导入与签名

```python
from recipes.aero_cfd.configuration import load_configuration
```

```text
load_configuration(path, overrides=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `未标注` | `必填` |
| `overrides` | `未标注` | `None` |

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
from recipes.aero_cfd.configuration import load_configuration

print(signature(load_configuration))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`

### 源码位置

- 模块：`recipes.aero_cfd.configuration`
- 仓库相对路径：`recipes/aero_cfd/configuration.py:17`
- 安装源码：先调用 `ai4e_task.source_location('recipes')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('recipes.aero_cfd.configuration')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-recipes-aero-cfd-infer-infer"></a>
## `recipes.aero_cfd.infer.infer`

- **层级**：`recipe`
- **稳定性**：`extension`
- **定义**：`infer(cfg, trained=None)`
- **规范定义名**：`recipes.aero_cfd.infer.infer`

### 用途

连续运行消费训练引用，独立运行消费指定检查点。

### 导入与签名

```python
from recipes.aero_cfd.infer import infer
```

```text
infer(cfg, trained=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cfg` | `未标注` | `必填` |
| `trained` | `未标注` | `None` |

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
from recipes.aero_cfd.infer import infer

print(signature(infer))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`

### 源码位置

- 模块：`recipes.aero_cfd.infer`
- 仓库相对路径：`recipes/aero_cfd/infer.py:12`
- 安装源码：先调用 `ai4e_task.source_location('recipes')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('recipes.aero_cfd.infer')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-recipes-aero-cfd-pipeline-pipeline"></a>
## `recipes.aero_cfd.pipeline.pipeline`

- **层级**：`recipe`
- **稳定性**：`extension`
- **定义**：`pipeline(cfg)`
- **规范定义名**：`recipes.aero_cfd.pipeline.pipeline`

### 用途

按声明顺序执行阶段；已有数据或准备产物允许省略上游。

### 导入与签名

```python
from recipes.aero_cfd.pipeline import pipeline
```

```text
pipeline(cfg)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cfg` | `未标注` | `必填` |

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
from recipes.aero_cfd.pipeline import pipeline

print(signature(pipeline))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`

### 源码位置

- 模块：`recipes.aero_cfd.pipeline`
- 仓库相对路径：`recipes/aero_cfd/pipeline.py:18`
- 安装源码：先调用 `ai4e_task.source_location('recipes')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('recipes.aero_cfd.pipeline')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-recipes-aero-cfd-post-analyze-sample"></a>
## `recipes.aero_cfd.post.analyze_sample`

- **层级**：`recipe`
- **稳定性**：`extension`
- **定义**：`analyze_sample(reference, *, cfg, output)`
- **规范定义名**：`recipes.aero_cfd.post.analyze_sample`

### 用途

一次只处理一个样本，研究者可在正文插入或替换公开步骤。

### 导入与签名

```python
from recipes.aero_cfd.post import analyze_sample
```

```text
analyze_sample(reference, *, cfg, output)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `reference` | `未标注` | `必填` |
| `cfg` | `未标注` | `必填关键字参数` |
| `output` | `未标注` | `必填关键字参数` |

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
from recipes.aero_cfd.post import analyze_sample

print(signature(analyze_sample))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`

### 源码位置

- 模块：`recipes.aero_cfd.post`
- 仓库相对路径：`recipes/aero_cfd/post.py:16`
- 安装源码：先调用 `ai4e_task.source_location('recipes')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('recipes.aero_cfd.post')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-recipes-aero-cfd-post-post"></a>
## `recipes.aero_cfd.post.post`

- **层级**：`recipe`
- **稳定性**：`extension`
- **定义**：`post(cfg, trained=None)`
- **规范定义名**：`recipes.aero_cfd.post.post`

### 用途

连续或独立运行都消费固定结果；没有启用分析时保留原接口。

### 导入与签名

```python
from recipes.aero_cfd.post import post
```

```text
post(cfg, trained=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cfg` | `未标注` | `必填` |
| `trained` | `未标注` | `None` |

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
from recipes.aero_cfd.post import post

print(signature(post))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`

### 源码位置

- 模块：`recipes.aero_cfd.post`
- 仓库相对路径：`recipes/aero_cfd/post.py:119`
- 安装源码：先调用 `ai4e_task.source_location('recipes')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('recipes.aero_cfd.post')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-recipes-aero-cfd-rawprep-rawprep"></a>
## `recipes.aero_cfd.rawprep.rawprep`

- **层级**：`recipe`
- **稳定性**：`extension`
- **定义**：`rawprep(cfg)`
- **规范定义名**：`recipes.aero_cfd.rawprep.rawprep`

### 用途

交付本次成功处理的数据清单，检查模式不发布数据。

### 导入与签名

```python
from recipes.aero_cfd.rawprep import rawprep
```

```text
rawprep(cfg)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cfg` | `未标注` | `必填` |

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
from recipes.aero_cfd.rawprep import rawprep

print(signature(rawprep))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`

### 源码位置

- 模块：`recipes.aero_cfd.rawprep`
- 仓库相对路径：`recipes/aero_cfd/rawprep.py:12`
- 安装源码：先调用 `ai4e_task.source_location('recipes')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('recipes.aero_cfd.rawprep')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-recipes-aero-cfd-train-observe-epoch"></a>
## `recipes.aero_cfd.train.observe_epoch`

- **层级**：`recipe`
- **稳定性**：`extension`
- **定义**：`observe_epoch(context, *, cfg)`
- **规范定义名**：`recipes.aero_cfd.train.observe_epoch`

### 用途

在指定轮次生成当前模型快照，再执行与独立推理相同的分析正文。

### 导入与签名

```python
from recipes.aero_cfd.train import observe_epoch
```

```text
observe_epoch(context, *, cfg)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `context` | `未标注` | `必填` |
| `cfg` | `未标注` | `必填关键字参数` |

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
from recipes.aero_cfd.train import observe_epoch

print(signature(observe_epoch))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`

### 源码位置

- 模块：`recipes.aero_cfd.train`
- 仓库相对路径：`recipes/aero_cfd/train.py:72`
- 安装源码：先调用 `ai4e_task.source_location('recipes')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('recipes.aero_cfd.train')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-recipes-aero-cfd-train-train"></a>
## `recipes.aero_cfd.train.train`

- **层级**：`recipe`
- **稳定性**：`extension`
- **定义**：`train(cfg, prepared=None)`
- **规范定义名**：`recipes.aero_cfd.train.train`

### 用途

缺少准备引用时显式调用同一准备阶段，不隐藏另一套准备链。

### 导入与签名

```python
from recipes.aero_cfd.train import train
```

```text
train(cfg, prepared=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cfg` | `未标注` | `必填` |
| `prepared` | `未标注` | `None` |

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
from recipes.aero_cfd.train import train

print(signature(train))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`

### 源码位置

- 模块：`recipes.aero_cfd.train`
- 仓库相对路径：`recipes/aero_cfd/train.py:14`
- 安装源码：先调用 `ai4e_task.source_location('recipes')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('recipes.aero_cfd.train')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-recipes-aero-cfd-trainprep-trainprep"></a>
## `recipes.aero_cfd.trainprep.trainprep`

- **层级**：`recipe`
- **稳定性**：`extension`
- **定义**：`trainprep(cfg, dataset=None)`
- **规范定义名**：`recipes.aero_cfd.trainprep.trainprep`

### 用途

返回可被训练和独立后处理消费的准备引用。

### 导入与签名

```python
from recipes.aero_cfd.trainprep import trainprep
```

```text
trainprep(cfg, dataset=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cfg` | `未标注` | `必填` |
| `dataset` | `未标注` | `None` |

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
from recipes.aero_cfd.trainprep import trainprep

print(signature(trainprep))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`

### 源码位置

- 模块：`recipes.aero_cfd.trainprep`
- 仓库相对路径：`recipes/aero_cfd/trainprep.py:12`
- 安装源码：先调用 `ai4e_task.source_location('recipes')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('recipes.aero_cfd.trainprep')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
