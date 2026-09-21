<!-- dojo-help: {"domain": "ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.persistence", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.persistence 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.persistence", "topic_id": "module:ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.persistence"} -->
# `ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.persistence` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-local-torch-utils-persistence-import-hook"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.persistence.import_hook`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`import_hook(hook)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.persistence.import_hook`

### 用途

Register an import hook that is called whenever a persistent object
is being unpickled. A typical use case is to patch the pickled source
code to avoid errors and inconsistencies when the API of some imported
module has changed.

The hook should have the following signature:

    hook(meta) -> modified meta

`meta` is an instance of `dnnlib.EasyDict` with the following fields:

    type:       Type of the persistent object, e.g. `'class'`.
    version:    Internal version number of `torch_utils.persistence`.
    module_src  Original source code of the Python module.
    class_name: Class name in the original Python module.
    state:      Internal state of the object.

Example:

    @persistence.import_hook
    def wreck_my_network(meta):
        if meta.class_name == 'MyNetwork':
            print('MyNetwork is being imported. I will wreck it!')
            meta.module_src = meta.module_src.replace("True", "False")
        return meta

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.persistence import import_hook
```

```text
import_hook(hook)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `hook` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.persistence import import_hook

print(signature(import_hook))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.persistence`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/local_torch_utils/persistence.py:148`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.persistence')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-local-torch-utils-persistence-is-persistent"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.persistence.is_persistent`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`is_persistent(obj)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.persistence.is_persistent`

### 用途

Test whether the given object or class is persistent, i.e.,
whether it will save its source code when pickled.

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.persistence import is_persistent
```

```text
is_persistent(obj)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `obj` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.persistence import is_persistent

print(signature(is_persistent))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.persistence`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/local_torch_utils/persistence.py:135`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.persistence')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-gencp-modules-cno-libs-local-torch-utils-persistence-persistent-class"></a>
## `ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.persistence.persistent_class`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`persistent_class(orig_class)`
- **规范定义名**：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.persistence.persistent_class`

### 用途

Class decorator that extends a given class to save its source code
when pickled.

Example:

    from torch_utils import persistence

    @persistence.persistent_class
    class MyNetwork(torch.nn.Module):
        def __init__(self, num_inputs, num_outputs):
            super().__init__()
            self.fc = MyLayer(num_inputs, num_outputs)
            ...

    @persistence.persistent_class
    class MyLayer(torch.nn.Module):
        ...

When pickled, any instance of `MyNetwork` and `MyLayer` will save its
source code alongside other internal state (e.g., parameters, buffers,
and submodules). This way, any previously exported pickle will remain
usable even if the class definitions have been modified or are no
longer available.

The decorator saves the source code of the entire Python module
containing the decorated class. It does *not* save the source code of
any imported modules. Thus, the imported modules must be available
during unpickling, also including `torch_utils.persistence` itself.

It is ok to call functions defined in the same module from the
decorated class. However, if the decorated class depends on other
classes defined in the same module, they must be decorated as well.
This is illustrated in the above example in the case of `MyLayer`.

It is also possible to employ the decorator just-in-time before
calling the constructor. For example:

    cls = MyLayer
    if want_to_make_it_persistent:
        cls = persistence.persistent_class(cls)
    layer = cls(num_inputs, num_outputs)

As an additional feature, the decorator also keeps track of the
arguments that were used to construct each instance of the decorated
class. The arguments can be queried via `obj.init_args` and
`obj.init_kwargs`, and they are automatically pickled alongside other
object state. A typical use case is to first unpickle a previous
instance of a persistent class, and then upgrade it to use the latest
version of the source code:

    with open('old_pickle.pkl', 'rb') as f:
        old_net = pickle.load(f)
    new_net = MyNetwork(*old_obj.init_args, **old_obj.init_kwargs)
    misc.copy_params_and_buffers(old_net, new_net, require_all=True)

### 导入与签名

```python
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.persistence import persistent_class
```

```text
persistent_class(orig_class)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `orig_class` | `未标注` | `必填` |

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
from ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.persistence import persistent_class

print(signature(persistent_class))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.persistence`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/gencp/modules/CNO_libs/local_torch_utils/persistence.py:36`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.gencp.modules.CNO_libs.local_torch_utils.persistence')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
