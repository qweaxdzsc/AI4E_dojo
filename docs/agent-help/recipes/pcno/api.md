<!-- dojo-help: {"domain": "recipes.pcno.infer", "kind": "recipe", "layer": "recipe", "summary": "recipes.pcno.infer 的完整源码参考与公开符号索引。", "title": "recipes.pcno.infer", "topic_id": "module:recipes.pcno.infer"} -->
# `recipes.pcno.infer` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-recipes-pcno-infer-infer"></a>
## `recipes.pcno.infer.infer`

- **层级**：`recipe`
- **稳定性**：`extension`
- **定义**：`infer(cfg, preparation=None, trained=None)`
- **规范定义名**：`recipes.pcno.infer.infer`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from recipes.pcno.infer import infer
```

```text
infer(cfg, preparation=None, trained=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cfg` | `未标注` | `必填` |
| `preparation` | `未标注` | `None` |
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
from recipes.pcno.infer import infer

print(signature(infer))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`pcno`
- 案例：`geothermal.pcno`

### 源码位置

- 模块：`recipes.pcno.infer`
- 仓库相对路径：`recipes/pcno/infer.py:10`
- 安装源码：先调用 `ai4e_task.source_location('recipes')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('recipes.pcno.infer')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-recipes-pcno-pipeline-pipeline"></a>
## `recipes.pcno.pipeline.pipeline`

- **层级**：`recipe`
- **稳定性**：`extension`
- **定义**：`pipeline(cfg)`
- **规范定义名**：`recipes.pcno.pipeline.pipeline`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from recipes.pcno.pipeline import pipeline
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
from recipes.pcno.pipeline import pipeline

print(signature(pipeline))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`pcno`
- 案例：`geothermal.pcno`

### 源码位置

- 模块：`recipes.pcno.pipeline`
- 仓库相对路径：`recipes/pcno/pipeline.py:13`
- 安装源码：先调用 `ai4e_task.source_location('recipes')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('recipes.pcno.pipeline')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-recipes-pcno-post-post"></a>
## `recipes.pcno.post.post`

- **层级**：`recipe`
- **稳定性**：`extension`
- **定义**：`post(cfg, results=None)`
- **规范定义名**：`recipes.pcno.post.post`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from recipes.pcno.post import post
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

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from recipes.pcno.post import post

print(signature(post))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`pcno`
- 案例：`geothermal.pcno`

### 源码位置

- 模块：`recipes.pcno.post`
- 仓库相对路径：`recipes/pcno/post.py:16`
- 安装源码：先调用 `ai4e_task.source_location('recipes')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('recipes.pcno.post')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-recipes-pcno-rawprep-rawprep"></a>
## `recipes.pcno.rawprep.rawprep`

- **层级**：`recipe`
- **稳定性**：`extension`
- **定义**：`rawprep(cfg)`
- **规范定义名**：`recipes.pcno.rawprep.rawprep`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from recipes.pcno.rawprep import rawprep
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

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from recipes.pcno.rawprep import rawprep

print(signature(rawprep))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`pcno`
- 案例：`geothermal.pcno`

### 源码位置

- 模块：`recipes.pcno.rawprep`
- 仓库相对路径：`recipes/pcno/rawprep.py:10`
- 安装源码：先调用 `ai4e_task.source_location('recipes')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('recipes.pcno.rawprep')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-recipes-pcno-train-train"></a>
## `recipes.pcno.train.train`

- **层级**：`recipe`
- **稳定性**：`extension`
- **定义**：`train(cfg, preparation=None)`
- **规范定义名**：`recipes.pcno.train.train`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from recipes.pcno.train import train
```

```text
train(cfg, preparation=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cfg` | `未标注` | `必填` |
| `preparation` | `未标注` | `None` |

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
from recipes.pcno.train import train

print(signature(train))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`pcno`
- 案例：`geothermal.pcno`

### 源码位置

- 模块：`recipes.pcno.train`
- 仓库相对路径：`recipes/pcno/train.py:14`
- 安装源码：先调用 `ai4e_task.source_location('recipes')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('recipes.pcno.train')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-recipes-pcno-trainprep-trainprep"></a>
## `recipes.pcno.trainprep.trainprep`

- **层级**：`recipe`
- **稳定性**：`extension`
- **定义**：`trainprep(cfg, dataset=None)`
- **规范定义名**：`recipes.pcno.trainprep.trainprep`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from recipes.pcno.trainprep import trainprep
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
from recipes.pcno.trainprep import trainprep

print(signature(trainprep))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`pcno`
- 案例：`geothermal.pcno`

### 源码位置

- 模块：`recipes.pcno.trainprep`
- 仓库相对路径：`recipes/pcno/trainprep.py:10`
- 安装源码：先调用 `ai4e_task.source_location('recipes')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('recipes.pcno.trainprep')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
