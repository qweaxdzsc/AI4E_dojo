<!-- dojo-help: {"domain": "ai4e_contrib.ability.transform.wdno.multiscale", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.transform.wdno.multiscale 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.transform.wdno.multiscale", "topic_id": "module:ai4e_contrib.ability.transform.wdno.multiscale"} -->
# `ai4e_contrib.ability.transform.wdno.multiscale` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-transform-wdno-multiscale-get-wt-t"></a>
## `ai4e_contrib.ability.transform.wdno.multiscale.get_wt_T`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`get_wt_T(test_data, shape)`
- **规范定义名**：`ai4e_contrib.ability.transform.wdno.multiscale.get_wt_T`

### 用途

test_data: [batch_size, 1+3*len(shape) or 2*(1+3*len(shape)), nt, nx]
return: list [batch_size, 64], [batch_size, 3, 64] * 3 layers

### 导入与签名

```python
from ai4e_contrib.ability.transform.wdno.multiscale import get_wt_T
```

```text
get_wt_T(test_data, shape)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `test_data` | `未标注` | `必填` |
| `shape` | `未标注` | `必填` |

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
from ai4e_contrib.ability.transform.wdno.multiscale import get_wt_T

print(signature(get_wt_T))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.transform.wdno.multiscale`
- 仓库相对路径：`packages/ai4e-contrib/ability/transform/wdno/multiscale.py:18`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.transform.wdno.multiscale')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-transform-wdno-multiscale-upsample-coef"></a>
## `ai4e_contrib.ability.transform.wdno.multiscale.upsample_coef`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`upsample_coef(w_sub, shape)`
- **规范定义名**：`ai4e_contrib.ability.transform.wdno.multiscale.upsample_coef`

### 用途

upsample the wavelet coefficients to the target shape
(old) w_sub: [N, layer, nt(maybe padded), nx(maybe padded)]
(old) w: [N, layer, shape[-2], shape[-1]]
w_sub: [N, layer, nt, nx]
w: [N, layer, 2*nt, 2*nx]

### 导入与签名

```python
from ai4e_contrib.ability.transform.wdno.multiscale import upsample_coef
```

```text
upsample_coef(w_sub, shape)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `w_sub` | `未标注` | `必填` |
| `shape` | `未标注` | `必填` |

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
from ai4e_contrib.ability.transform.wdno.multiscale import upsample_coef

print(signature(upsample_coef))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.transform.wdno.multiscale`
- 仓库相对路径：`packages/ai4e-contrib/ability/transform/wdno/multiscale.py:5`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.transform.wdno.multiscale')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
