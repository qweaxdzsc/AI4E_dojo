<!-- dojo-help: {"domain": "ai4e_core.abilities.constraint.geothermal", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.constraint.geothermal 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.constraint.geothermal", "topic_id": "module:ai4e_core.abilities.constraint.geothermal"} -->
# `ai4e_core.abilities.constraint.geothermal` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-constraint-geothermal-pde-f"></a>
## `ai4e_core.abilities.constraint.geothermal.PDE_F`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`class PDE_F`
- **规范定义名**：`ai4e_core.abilities.constraint.geothermal.PDE_F`

### 用途

五层地热网格的水物性、上风通量、质量与能量残差；压力输入 MPa、温度摄氏度：PDE_F；保留来源算法、参数与权重布局。

### 导入与签名

```python
from ai4e_core.abilities.constraint.geothermal import PDE_F
```

```text
class PDE_F
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`PDE_F`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.constraint.geothermal import PDE_F

print(signature(PDE_F))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.constraint.geothermal`
- 仓库相对路径：`packages/ai4e-core/abilities/constraint/geothermal.py:12`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.constraint.geothermal')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-constraint-geothermal-pde-f-den"></a>
## `ai4e_core.abilities.constraint.geothermal.PDE_F.den`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`den(p, T)`
- **规范定义名**：`ai4e_core.abilities.constraint.geothermal.PDE_F.den`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_core.abilities.constraint.geothermal import PDE_F
```

```text
den(p, T)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `p` | `未标注` | `必填` |
| `T` | `未标注` | `必填` |

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
from ai4e_core.abilities.constraint.geothermal import PDE_F

print(signature(PDE_F.den))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.constraint.geothermal`
- 仓库相对路径：`packages/ai4e-core/abilities/constraint/geothermal.py:16`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.constraint.geothermal')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-constraint-geothermal-pde-f-ent"></a>
## `ai4e_core.abilities.constraint.geothermal.PDE_F.ent`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`ent(T)`
- **规范定义名**：`ai4e_core.abilities.constraint.geothermal.PDE_F.ent`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_core.abilities.constraint.geothermal import PDE_F
```

```text
ent(T)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `T` | `未标注` | `必填` |

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
from ai4e_core.abilities.constraint.geothermal import PDE_F

print(signature(PDE_F.ent))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.constraint.geothermal`
- 仓库相对路径：`packages/ai4e-core/abilities/constraint/geothermal.py:40`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.constraint.geothermal')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-constraint-geothermal-pde-f-harmonic-mean-v"></a>
## `ai4e_core.abilities.constraint.geothermal.PDE_F.harmonic_mean_v`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`harmonic_mean_v(k)`
- **规范定义名**：`ai4e_core.abilities.constraint.geothermal.PDE_F.harmonic_mean_v`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_core.abilities.constraint.geothermal import PDE_F
```

```text
harmonic_mean_v(k)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `k` | `未标注` | `必填` |

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
from ai4e_core.abilities.constraint.geothermal import PDE_F

print(signature(PDE_F.harmonic_mean_v))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.constraint.geothermal`
- 仓库相对路径：`packages/ai4e-core/abilities/constraint/geothermal.py:87`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.constraint.geothermal')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-constraint-geothermal-pde-f-harmonic-mean-x"></a>
## `ai4e_core.abilities.constraint.geothermal.PDE_F.harmonic_mean_x`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`harmonic_mean_x(k, eps=1e-30)`
- **规范定义名**：`ai4e_core.abilities.constraint.geothermal.PDE_F.harmonic_mean_x`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_core.abilities.constraint.geothermal import PDE_F
```

```text
harmonic_mean_x(k, eps=1e-30)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `k` | `未标注` | `必填` |
| `eps` | `未标注` | `1e-30` |

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
from ai4e_core.abilities.constraint.geothermal import PDE_F

print(signature(PDE_F.harmonic_mean_x))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.constraint.geothermal`
- 仓库相对路径：`packages/ai4e-core/abilities/constraint/geothermal.py:54`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.constraint.geothermal')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-constraint-geothermal-pde-f-harmonic-mean-y"></a>
## `ai4e_core.abilities.constraint.geothermal.PDE_F.harmonic_mean_y`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`harmonic_mean_y(k, eps=1e-30)`
- **规范定义名**：`ai4e_core.abilities.constraint.geothermal.PDE_F.harmonic_mean_y`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_core.abilities.constraint.geothermal import PDE_F
```

```text
harmonic_mean_y(k, eps=1e-30)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `k` | `未标注` | `必填` |
| `eps` | `未标注` | `1e-30` |

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
from ai4e_core.abilities.constraint.geothermal import PDE_F

print(signature(PDE_F.harmonic_mean_y))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.constraint.geothermal`
- 仓库相对路径：`packages/ai4e-core/abilities/constraint/geothermal.py:65`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.constraint.geothermal')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-constraint-geothermal-pde-f-harmonic-mean-z"></a>
## `ai4e_core.abilities.constraint.geothermal.PDE_F.harmonic_mean_z`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`harmonic_mean_z(k, eps=1e-30)`
- **规范定义名**：`ai4e_core.abilities.constraint.geothermal.PDE_F.harmonic_mean_z`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_core.abilities.constraint.geothermal import PDE_F
```

```text
harmonic_mean_z(k, eps=1e-30)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `k` | `未标注` | `必填` |
| `eps` | `未标注` | `1e-30` |

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
from ai4e_core.abilities.constraint.geothermal import PDE_F

print(signature(PDE_F.harmonic_mean_z))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.constraint.geothermal`
- 仓库相对路径：`packages/ai4e-core/abilities/constraint/geothermal.py:76`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.constraint.geothermal')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-constraint-geothermal-pde-f-upstream-x"></a>
## `ai4e_core.abilities.constraint.geothermal.PDE_F.upstream_x`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`upstream_x(x, p)`
- **规范定义名**：`ai4e_core.abilities.constraint.geothermal.PDE_F.upstream_x`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_core.abilities.constraint.geothermal import PDE_F
```

```text
upstream_x(x, p)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `p` | `未标注` | `必填` |

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
from ai4e_core.abilities.constraint.geothermal import PDE_F

print(signature(PDE_F.upstream_x))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.constraint.geothermal`
- 仓库相对路径：`packages/ai4e-core/abilities/constraint/geothermal.py:98`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.constraint.geothermal')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-constraint-geothermal-pde-f-upstream-y"></a>
## `ai4e_core.abilities.constraint.geothermal.PDE_F.upstream_y`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`upstream_y(x, p)`
- **规范定义名**：`ai4e_core.abilities.constraint.geothermal.PDE_F.upstream_y`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_core.abilities.constraint.geothermal import PDE_F
```

```text
upstream_y(x, p)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `p` | `未标注` | `必填` |

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
from ai4e_core.abilities.constraint.geothermal import PDE_F

print(signature(PDE_F.upstream_y))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.constraint.geothermal`
- 仓库相对路径：`packages/ai4e-core/abilities/constraint/geothermal.py:113`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.constraint.geothermal')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-constraint-geothermal-pde-f-upstream-z"></a>
## `ai4e_core.abilities.constraint.geothermal.PDE_F.upstream_z`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`upstream_z(x, p)`
- **规范定义名**：`ai4e_core.abilities.constraint.geothermal.PDE_F.upstream_z`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_core.abilities.constraint.geothermal import PDE_F
```

```text
upstream_z(x, p)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `p` | `未标注` | `必填` |

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
from ai4e_core.abilities.constraint.geothermal import PDE_F

print(signature(PDE_F.upstream_z))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.constraint.geothermal`
- 仓库相对路径：`packages/ai4e-core/abilities/constraint/geothermal.py:128`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.constraint.geothermal')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-constraint-geothermal-pde-f-vis"></a>
## `ai4e_core.abilities.constraint.geothermal.PDE_F.vis`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`vis(T)`
- **规范定义名**：`ai4e_core.abilities.constraint.geothermal.PDE_F.vis`

### 用途

保留分段物性公式，仅屏蔽未选分支的非法自变量及梯度。

### 导入与签名

```python
from ai4e_core.abilities.constraint.geothermal import PDE_F
```

```text
vis(T)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `T` | `未标注` | `必填` |

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
from ai4e_core.abilities.constraint.geothermal import PDE_F

print(signature(PDE_F.vis))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.constraint.geothermal`
- 仓库相对路径：`packages/ai4e-core/abilities/constraint/geothermal.py:25`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.constraint.geothermal')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-constraint-geothermal-compute-loss"></a>
## `ai4e_core.abilities.constraint.geothermal.compute_loss`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`compute_loss(p_out, T_out, loss_func, Temp_wh_t, Heat_wh_t, P_inj_t)`
- **规范定义名**：`ai4e_core.abilities.constraint.geothermal.compute_loss`

### 用途

五层地热网格的水物性、上风通量、质量与能量残差；压力输入 MPa、温度摄氏度：compute_loss；保留来源算法、参数与权重布局。

### 导入与签名

```python
from ai4e_core.abilities.constraint.geothermal import compute_loss
```

```text
compute_loss(p_out, T_out, loss_func, Temp_wh_t, Heat_wh_t, P_inj_t)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `p_out` | `未标注` | `必填` |
| `T_out` | `未标注` | `必填` |
| `loss_func` | `未标注` | `必填` |
| `Temp_wh_t` | `未标注` | `必填` |
| `Heat_wh_t` | `未标注` | `必填` |
| `P_inj_t` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`TypeError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.constraint.geothermal import compute_loss

print(signature(compute_loss))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.constraint.geothermal`
- 仓库相对路径：`packages/ai4e-core/abilities/constraint/geothermal.py:268`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.constraint.geothermal')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-constraint-geothermal-physical-loss"></a>
## `ai4e_core.abilities.constraint.geothermal.physical_loss`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`physical_loss(T_i, p_i, Cp_r, lam_r, dz, q_inj, pwf, T_inj, k, phi, depth, dt=24 * 3600 * 365, dx=10.0, dy=10.0)`
- **规范定义名**：`ai4e_core.abilities.constraint.geothermal.physical_loss`

### 用途

五层地热网格的水物性、上风通量、质量与能量残差；压力输入 MPa、温度摄氏度：physical_loss；保留来源算法、参数与权重布局。

### 导入与签名

```python
from ai4e_core.abilities.constraint.geothermal import physical_loss
```

```text
physical_loss(T_i, p_i, Cp_r, lam_r, dz, q_inj, pwf, T_inj, k, phi, depth, dt=24 * 3600 * 365, dx=10.0, dy=10.0)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `T_i` | `未标注` | `必填` |
| `p_i` | `未标注` | `必填` |
| `Cp_r` | `未标注` | `必填` |
| `lam_r` | `未标注` | `必填` |
| `dz` | `未标注` | `必填` |
| `q_inj` | `未标注` | `必填` |
| `pwf` | `未标注` | `必填` |
| `T_inj` | `未标注` | `必填` |
| `k` | `未标注` | `必填` |
| `phi` | `未标注` | `必填` |
| `depth` | `未标注` | `必填` |
| `dt` | `未标注` | `24 * 3600 * 365` |
| `dx` | `未标注` | `10.0` |
| `dy` | `未标注` | `10.0` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`physical_loss`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.constraint.geothermal import physical_loss

print(signature(physical_loss))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.constraint.geothermal`
- 仓库相对路径：`packages/ai4e-core/abilities/constraint/geothermal.py:142`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.constraint.geothermal')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-constraint-geothermal-physical-loss-phy-loss"></a>
## `ai4e_core.abilities.constraint.geothermal.physical_loss.phy_loss`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`phy_loss(self, p_pred, T_pred)`
- **规范定义名**：`ai4e_core.abilities.constraint.geothermal.physical_loss.phy_loss`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_core.abilities.constraint.geothermal import physical_loss
```

```text
phy_loss(self, p_pred, T_pred)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `p_pred` | `未标注` | `必填` |
| `T_pred` | `未标注` | `必填` |

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
from ai4e_core.abilities.constraint.geothermal import physical_loss

print(signature(physical_loss.phy_loss))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.constraint.geothermal`
- 仓库相对路径：`packages/ai4e-core/abilities/constraint/geothermal.py:165`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.constraint.geothermal')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
