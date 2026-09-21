<!-- dojo-help: {"domain": "recipes.safediffcon.configuration", "kind": "recipe", "layer": "recipe", "summary": "recipes.safediffcon.configuration 的完整源码参考与公开符号索引。", "title": "recipes.safediffcon.configuration", "topic_id": "module:recipes.safediffcon.configuration"} -->
# `recipes.safediffcon.configuration` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-recipes-safediffcon-configuration-plain"></a>
## `recipes.safediffcon.configuration.plain`

- **层级**：`recipe`
- **稳定性**：`extension`
- **定义**：`plain(cfg, *, stage='train')`
- **规范定义名**：`recipes.safediffcon.configuration.plain`

### 用途

程序入口也执行与文件加载相同的参数校验。

### 导入与签名

```python
from recipes.safediffcon.configuration import plain
```

```text
plain(cfg, *, stage='train')
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cfg` | `未标注` | `必填` |
| `stage` | `未标注` | `'train'` |

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
from recipes.safediffcon.configuration import plain

print(signature(plain))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`safediffcon`
- 案例：`safediffcon.burgers`, `safediffcon.tokamak`

### 源码位置

- 模块：`recipes.safediffcon.configuration`
- 仓库相对路径：`recipes/safediffcon/configuration.py:12`
- 安装源码：先调用 `ai4e_task.source_location('recipes')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('recipes.safediffcon.configuration')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-recipes-safediffcon-infer-infer"></a>
## `recipes.safediffcon.infer.infer`

- **层级**：`recipe`
- **稳定性**：`extension`
- **定义**：`infer(cfg, prepared=None, checkpoint=None)`
- **规范定义名**：`recipes.safediffcon.infer.infer`

### 用途

显式适配、生成控制、求解响应、评价和保存。

### 导入与签名

```python
from recipes.safediffcon.infer import infer
```

```text
infer(cfg, prepared=None, checkpoint=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cfg` | `未标注` | `必填` |
| `prepared` | `未标注` | `None` |
| `checkpoint` | `未标注` | `None` |

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
from recipes.safediffcon.infer import infer

print(signature(infer))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`safediffcon`
- 案例：`safediffcon.burgers`, `safediffcon.tokamak`

### 源码位置

- 模块：`recipes.safediffcon.infer`
- 仓库相对路径：`recipes/safediffcon/infer.py:18`
- 安装源码：先调用 `ai4e_task.source_location('recipes')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('recipes.safediffcon.infer')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-recipes-safediffcon-pipeline-pipeline"></a>
## `recipes.safediffcon.pipeline.pipeline`

- **层级**：`recipe`
- **稳定性**：`extension`
- **定义**：`pipeline(cfg)`
- **规范定义名**：`recipes.safediffcon.pipeline.pipeline`

### 用途

Python 是实际研究顺序的唯一来源。

### 导入与签名

```python
from recipes.safediffcon.pipeline import pipeline
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
from recipes.safediffcon.pipeline import pipeline

print(signature(pipeline))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`safediffcon`
- 案例：`safediffcon.burgers`, `safediffcon.tokamak`

### 源码位置

- 模块：`recipes.safediffcon.pipeline`
- 仓库相对路径：`recipes/safediffcon/pipeline.py:14`
- 安装源码：先调用 `ai4e_task.source_location('recipes')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('recipes.safediffcon.pipeline')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-recipes-safediffcon-post-post"></a>
## `recipes.safediffcon.post.post`

- **层级**：`recipe`
- **稳定性**：`extension`
- **定义**：`post(cfg, results=None)`
- **规范定义名**：`recipes.safediffcon.post.post`

### 用途

仅消费固定数组，重复评价不更新网络或调用响应求解器。

### 导入与签名

```python
from recipes.safediffcon.post import post
```

```text
post(cfg, results=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cfg` | `未标注` | `必填` |
| `results` | `未标注` | `None` |

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
from recipes.safediffcon.post import post

print(signature(post))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`safediffcon`
- 案例：`safediffcon.burgers`, `safediffcon.tokamak`

### 源码位置

- 模块：`recipes.safediffcon.post`
- 仓库相对路径：`recipes/safediffcon/post.py:14`
- 安装源码：先调用 `ai4e_task.source_location('recipes')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('recipes.safediffcon.post')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-recipes-safediffcon-posttrain-posttrain"></a>
## `recipes.safediffcon.posttrain.posttrain`

- **层级**：`recipe`
- **稳定性**：`extension`
- **定义**：`posttrain(cfg, prepared=None, checkpoint=None)`
- **规范定义名**：`recipes.safediffcon.posttrain.posttrain`

### 用途

显式两轮校准及重加权更新；下轮使用上轮输出。

### 导入与签名

```python
from recipes.safediffcon.posttrain import posttrain
```

```text
posttrain(cfg, prepared=None, checkpoint=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cfg` | `未标注` | `必填` |
| `prepared` | `未标注` | `None` |
| `checkpoint` | `未标注` | `None` |

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
from recipes.safediffcon.posttrain import posttrain

print(signature(posttrain))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`safediffcon`
- 案例：`safediffcon.burgers`, `safediffcon.tokamak`

### 源码位置

- 模块：`recipes.safediffcon.posttrain`
- 仓库相对路径：`recipes/safediffcon/posttrain.py:14`
- 安装源码：先调用 `ai4e_task.source_location('recipes')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('recipes.safediffcon.posttrain')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-recipes-safediffcon-rawprep-rawprep"></a>
## `recipes.safediffcon.rawprep.rawprep`

- **层级**：`recipe`
- **稳定性**：`extension`
- **定义**：`rawprep(cfg)`
- **规范定义名**：`recipes.safediffcon.rawprep.rawprep`

### 用途

读取原数据，独立发布三个物理分片。

### 导入与签名

```python
from recipes.safediffcon.rawprep import rawprep
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
from recipes.safediffcon.rawprep import rawprep

print(signature(rawprep))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`safediffcon`
- 案例：`safediffcon.burgers`, `safediffcon.tokamak`

### 源码位置

- 模块：`recipes.safediffcon.rawprep`
- 仓库相对路径：`recipes/safediffcon/rawprep.py:10`
- 安装源码：先调用 `ai4e_task.source_location('recipes')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('recipes.safediffcon.rawprep')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-recipes-safediffcon-train-train"></a>
## `recipes.safediffcon.train.train`

- **层级**：`recipe`
- **稳定性**：`extension`
- **定义**：`train(cfg, prepared=None)`
- **规范定义名**：`recipes.safediffcon.train.train`

### 用途

从明确准备开始预训练，恢复权重只影响本次调用。

### 导入与签名

```python
from recipes.safediffcon.train import train
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
from recipes.safediffcon.train import train

print(signature(train))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`safediffcon`
- 案例：`safediffcon.burgers`, `safediffcon.tokamak`

### 源码位置

- 模块：`recipes.safediffcon.train`
- 仓库相对路径：`recipes/safediffcon/train.py:13`
- 安装源码：先调用 `ai4e_task.source_location('recipes')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('recipes.safediffcon.train')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-recipes-safediffcon-trainprep-trainprep"></a>
## `recipes.safediffcon.trainprep.trainprep`

- **层级**：`recipe`
- **稳定性**：`extension`
- **定义**：`trainprep(cfg, physical=None)`
- **规范定义名**：`recipes.safediffcon.trainprep.trainprep`

### 用途

物理分片转换为模型准备，保留物理目标。

### 导入与签名

```python
from recipes.safediffcon.trainprep import trainprep
```

```text
trainprep(cfg, physical=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cfg` | `未标注` | `必填` |
| `physical` | `未标注` | `None` |

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
from recipes.safediffcon.trainprep import trainprep

print(signature(trainprep))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`safediffcon`
- 案例：`safediffcon.burgers`, `safediffcon.tokamak`

### 源码位置

- 模块：`recipes.safediffcon.trainprep`
- 仓库相对路径：`recipes/safediffcon/trainprep.py:10`
- 安装源码：先调用 `ai4e_task.source_location('recipes')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('recipes.safediffcon.trainprep')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
