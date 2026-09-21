<!-- dojo-help: {"domain": "ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util", "topic_id": "module:ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util"} -->
# `ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-dnnlib-util-easydict"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.EasyDict`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`class EasyDict`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.EasyDict`

### 用途

Convenience class that behaves like a dict but allows access with the attribute syntax.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import EasyDict
```

```text
class EasyDict
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`EasyDict`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`AttributeError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import EasyDict

print(signature(EasyDict))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/dnnlib/util.py:41`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-dnnlib-util-logger"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.Logger`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`Logger(file_name: str=None, file_mode: str='w', should_flush: bool=True)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.Logger`

### 用途

Redirect stderr to stdout, optionally print stdout to a file, and optionally force flushing on both stdout and the file.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import Logger
```

```text
Logger(file_name: str=None, file_mode: str='w', should_flush: bool=True)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `file_name` | `str` | `None` |
| `file_mode` | `str` | `'w'` |
| `should_flush` | `bool` | `True` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Logger`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import Logger

print(signature(Logger))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/dnnlib/util.py:57`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-dnnlib-util-logger-close"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.Logger.close`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`close(self) -> None`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.Logger.close`

### 用途

Flush, close possible files, and remove stdout/stderr mirroring.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import Logger
```

```text
close(self) -> None
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`None`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import Logger

print(signature(Logger.close))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/dnnlib/util.py:101`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-dnnlib-util-logger-flush"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.Logger.flush`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`flush(self) -> None`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.Logger.flush`

### 用途

Flush written text to both stdout and a file, if open.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import Logger
```

```text
flush(self) -> None
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`None`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import Logger

print(signature(Logger.flush))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/dnnlib/util.py:94`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-dnnlib-util-logger-write"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.Logger.write`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`write(self, text: Union[str, bytes]) -> None`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.Logger.write`

### 用途

Write text to stdout (and a file) and optionally flush.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import Logger
```

```text
write(self, text: Union[str, bytes]) -> None
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `text` | `Union[str, bytes]` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`None`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import Logger

print(signature(Logger.write))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/dnnlib/util.py:79`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-dnnlib-util-ask-yes-no"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.ask_yes_no`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`ask_yes_no(question: str) -> bool`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.ask_yes_no`

### 用途

Ask the user the question until the user inputs a valid answer.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import ask_yes_no
```

```text
ask_yes_no(question: str) -> bool
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `question` | `str` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`bool`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import ask_yes_no

print(signature(ask_yes_no))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/dnnlib/util.py:168`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-dnnlib-util-call-func-by-name"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.call_func_by_name`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`call_func_by_name(*args, func_name: str=None, **kwargs) -> Any`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.call_func_by_name`

### 用途

Finds the python object with the given name and calls it as a function.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import call_func_by_name
```

```text
call_func_by_name(*args, func_name: str=None, **kwargs) -> Any
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `*args` | `未标注` | `可变位置参数` |
| `func_name` | `str` | `None` |
| `**kwargs` | `未标注` | `可变关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Any`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import call_func_by_name

print(signature(call_func_by_name))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/dnnlib/util.py:294`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-dnnlib-util-construct-class-by-name"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.construct_class_by_name`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`construct_class_by_name(*args, class_name: str=None, **kwargs) -> Any`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.construct_class_by_name`

### 用途

Finds the python class with the given name and constructs it with the given arguments.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import construct_class_by_name
```

```text
construct_class_by_name(*args, class_name: str=None, **kwargs) -> Any
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `*args` | `未标注` | `可变位置参数` |
| `class_name` | `str` | `None` |
| `**kwargs` | `未标注` | `可变关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Any`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import construct_class_by_name

print(signature(construct_class_by_name))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/dnnlib/util.py:302`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-dnnlib-util-copy-files-and-create-dirs"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.copy_files_and_create_dirs`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`copy_files_and_create_dirs(files: List[Tuple[str, str]]) -> None`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.copy_files_and_create_dirs`

### 用途

Takes in a list of tuples of (src, dst) paths and copies files.
Will create all necessary directories.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import copy_files_and_create_dirs
```

```text
copy_files_and_create_dirs(files: List[Tuple[str, str]]) -> None
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `files` | `List[Tuple[str, str]]` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`None`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import copy_files_and_create_dirs

print(signature(copy_files_and_create_dirs))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/dnnlib/util.py:363`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-dnnlib-util-format-time"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.format_time`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`format_time(seconds: Union[int, float]) -> str`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.format_time`

### 用途

Convert the seconds to human readable string with days, hours, minutes and seconds.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import format_time
```

```text
format_time(seconds: Union[int, float]) -> str
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `seconds` | `Union[int, float]` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`str`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import format_time

print(signature(format_time))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/dnnlib/util.py:140`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-dnnlib-util-format-time-brief"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.format_time_brief`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`format_time_brief(seconds: Union[int, float]) -> str`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.format_time_brief`

### 用途

Convert the seconds to human readable string with days, hours, minutes and seconds.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import format_time_brief
```

```text
format_time_brief(seconds: Union[int, float]) -> str
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `seconds` | `Union[int, float]` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`str`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import format_time_brief

print(signature(format_time_brief))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/dnnlib/util.py:154`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-dnnlib-util-get-dtype-and-ctype"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.get_dtype_and_ctype`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`get_dtype_and_ctype(type_obj: Any) -> Tuple[np.dtype, Any]`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.get_dtype_and_ctype`

### 用途

Given a type name string (or an object having a __name__ attribute), return matching Numpy and ctypes types that have the same size in bytes.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import get_dtype_and_ctype
```

```text
get_dtype_and_ctype(type_obj: Any) -> Tuple[np.dtype, Any]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `type_obj` | `Any` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Tuple[np.dtype, Any]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`RuntimeError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import get_dtype_and_ctype

print(signature(get_dtype_and_ctype))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/dnnlib/util.py:202`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-dnnlib-util-get-module-dir-by-obj-name"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.get_module_dir_by_obj_name`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`get_module_dir_by_obj_name(obj_name: str) -> str`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.get_module_dir_by_obj_name`

### 用途

Get the directory path of the module containing the given object name.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import get_module_dir_by_obj_name
```

```text
get_module_dir_by_obj_name(obj_name: str) -> str
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `obj_name` | `str` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`str`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import get_module_dir_by_obj_name

print(signature(get_module_dir_by_obj_name))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/dnnlib/util.py:307`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-dnnlib-util-get-module-from-obj-name"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.get_module_from_obj_name`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`get_module_from_obj_name(obj_name: str) -> Tuple[types.ModuleType, str]`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.get_module_from_obj_name`

### 用途

Searches for the underlying module behind the name to some python object.
Returns the module and the object name (original name with module part removed).

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import get_module_from_obj_name
```

```text
get_module_from_obj_name(obj_name: str) -> Tuple[types.ModuleType, str]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `obj_name` | `str` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Tuple[types.ModuleType, str]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ImportError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import get_module_from_obj_name

print(signature(get_module_from_obj_name))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/dnnlib/util.py:237`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-dnnlib-util-get-obj-by-name"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.get_obj_by_name`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`get_obj_by_name(name: str) -> Any`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.get_obj_by_name`

### 用途

Finds the python object with the given name.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import get_obj_by_name
```

```text
get_obj_by_name(name: str) -> Any
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `name` | `str` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Any`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import get_obj_by_name

print(signature(get_obj_by_name))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/dnnlib/util.py:288`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-dnnlib-util-get-obj-from-module"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.get_obj_from_module`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`get_obj_from_module(module: types.ModuleType, obj_name: str) -> Any`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.get_obj_from_module`

### 用途

Traverses the object name and returns the last (rightmost) python object.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import get_obj_from_module
```

```text
get_obj_from_module(module: types.ModuleType, obj_name: str) -> Any
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `module` | `types.ModuleType` | `必填` |
| `obj_name` | `str` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Any`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import get_obj_from_module

print(signature(get_obj_from_module))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/dnnlib/util.py:278`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-dnnlib-util-get-top-level-function-name"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.get_top_level_function_name`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`get_top_level_function_name(obj: Any) -> str`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.get_top_level_function_name`

### 用途

Return the fully-qualified name of a top-level function.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import get_top_level_function_name
```

```text
get_top_level_function_name(obj: Any) -> str
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `obj` | `Any` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`str`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import get_top_level_function_name

print(signature(get_top_level_function_name))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/dnnlib/util.py:318`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-dnnlib-util-is-pickleable"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.is_pickleable`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`is_pickleable(obj: Any) -> bool`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.is_pickleable`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import is_pickleable
```

```text
is_pickleable(obj: Any) -> bool
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `obj` | `Any` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`bool`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import is_pickleable

print(signature(is_pickleable))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/dnnlib/util.py:225`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-dnnlib-util-is-top-level-function"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.is_top_level_function`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`is_top_level_function(obj: Any) -> bool`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.is_top_level_function`

### 用途

Determine whether the given object is a top-level function, i.e., defined at module scope using 'def'.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import is_top_level_function
```

```text
is_top_level_function(obj: Any) -> bool
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `obj` | `Any` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`bool`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import is_top_level_function

print(signature(is_top_level_function))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/dnnlib/util.py:313`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-dnnlib-util-is-url"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.is_url`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`is_url(obj: Any, allow_file_urls: bool=False) -> bool`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.is_url`

### 用途

Determine whether the given object is a valid URL string.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import is_url
```

```text
is_url(obj: Any, allow_file_urls: bool=False) -> bool
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `obj` | `Any` | `必填` |
| `allow_file_urls` | `bool` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`bool`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import is_url

print(signature(is_url))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/dnnlib/util.py:379`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-dnnlib-util-list-dir-recursively-with-ignore"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.list_dir_recursively_with_ignore`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`list_dir_recursively_with_ignore(dir_path: str, ignores: List[str]=None, add_base_to_relative: bool=False) -> List[Tuple[str, str]]`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.list_dir_recursively_with_ignore`

### 用途

List all files recursively in a given directory while ignoring given file and directory names.
Returns list of tuples containing both absolute and relative paths.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import list_dir_recursively_with_ignore
```

```text
list_dir_recursively_with_ignore(dir_path: str, ignores: List[str]=None, add_base_to_relative: bool=False) -> List[Tuple[str, str]]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dir_path` | `str` | `必填` |
| `ignores` | `List[str]` | `None` |
| `add_base_to_relative` | `bool` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`List[Tuple[str, str]]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import list_dir_recursively_with_ignore

print(signature(list_dir_recursively_with_ignore))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/dnnlib/util.py:330`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-dnnlib-util-make-cache-dir-path"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.make_cache_dir_path`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`make_cache_dir_path(*paths: str) -> str`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.make_cache_dir_path`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import make_cache_dir_path
```

```text
make_cache_dir_path(*paths: str) -> str
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `*paths` | `str` | `可变位置参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`str`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import make_cache_dir_path

print(signature(make_cache_dir_path))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/dnnlib/util.py:125`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-dnnlib-util-open-url"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.open_url`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`open_url(url: str, cache_dir: str=None, num_attempts: int=10, verbose: bool=True, return_filename: bool=False, cache: bool=True) -> Any`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.open_url`

### 用途

Download the given URL and return a binary-mode file object to access the data.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import open_url
```

```text
open_url(url: str, cache_dir: str=None, num_attempts: int=10, verbose: bool=True, return_filename: bool=False, cache: bool=True) -> Any
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `url` | `str` | `必填` |
| `cache_dir` | `str` | `None` |
| `num_attempts` | `int` | `10` |
| `verbose` | `bool` | `True` |
| `return_filename` | `bool` | `False` |
| `cache` | `bool` | `True` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Any`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`IOError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import open_url

print(signature(open_url))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/dnnlib/util.py:397`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-dnnlib-util-set-cache-dir"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.set_cache_dir`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`set_cache_dir(path: str) -> None`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.set_cache_dir`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import set_cache_dir
```

```text
set_cache_dir(path: str) -> None
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `str` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`None`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import set_cache_dir

print(signature(set_cache_dir))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/dnnlib/util.py:121`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-dnnlib-util-tuple-product"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.tuple_product`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`tuple_product(t: Tuple) -> Any`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util.tuple_product`

### 用途

Calculate the product of the tuple elements.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import tuple_product
```

```text
tuple_product(t: Tuple) -> Any
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `t` | `Tuple` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Any`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util import tuple_product

print(signature(tuple_product))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/dnnlib/util.py:178`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.dnnlib.util')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
