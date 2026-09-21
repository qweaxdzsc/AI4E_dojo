<!-- dojo-help: {"domain": "ai4e_contrib.application.datasets.diffusion_trapezoid.generate", "kind": "api", "layer": "contrib.application", "summary": "ai4e_contrib.application.datasets.diffusion_trapezoid.generate 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.application.datasets.diffusion_trapezoid.generate", "topic_id": "module:ai4e_contrib.application.datasets.diffusion_trapezoid.generate"} -->
# `ai4e_contrib.application.datasets.diffusion_trapezoid.generate` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-application-datasets-diffusion-trapezoid-generate-generate"></a>
## `ai4e_contrib.application.datasets.diffusion_trapezoid.generate.generate`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`generate(config)`
- **规范定义名**：`ai4e_contrib.application.datasets.diffusion_trapezoid.generate.generate`

### 用途

独立生产选定的主文十实例梯形数据，不启动训练。

### 导入与签名

```python
from ai4e_contrib.application.datasets.diffusion_trapezoid.generate import generate
```

```text
generate(config)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `未标注` | `必填` |

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
from ai4e_contrib.application.datasets.diffusion_trapezoid.generate import generate

print(signature(generate))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`parametric_pde`, `safediffcon`
- 案例：`parametric_pde.advection`, `parametric_pde.burgers`, `parametric_pde.convection_diffusion`, `parametric_pde.diffusion_trapezoid`, `parametric_pde.neumann_diffusion`, `safediffcon.burgers`, `safediffcon.tokamak`

### 源码位置

- 模块：`ai4e_contrib.application.datasets.diffusion_trapezoid.generate`
- 仓库相对路径：`packages/ai4e-contrib/application/datasets/diffusion_trapezoid/generate.py:58`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.datasets.diffusion_trapezoid.generate')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-datasets-diffusion-trapezoid-generate-make-sample"></a>
## `ai4e_contrib.application.datasets.diffusion_trapezoid.generate.make_sample`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`make_sample(rng, config, *, index, split)`
- **规范定义名**：`ai4e_contrib.application.datasets.diffusion_trapezoid.generate.make_sample`

### 用途

生成独立实例，显式记录数值协议；场布局始终为 t、eta、xi。

### 导入与签名

```python
from ai4e_contrib.application.datasets.diffusion_trapezoid.generate import make_sample
```

```text
make_sample(rng, config, *, index, split)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `rng` | `未标注` | `必填` |
| `config` | `未标注` | `必填` |
| `index` | `未标注` | `必填关键字参数` |
| `split` | `未标注` | `必填关键字参数` |

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
from ai4e_contrib.application.datasets.diffusion_trapezoid.generate import make_sample

print(signature(make_sample))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.datasets.diffusion_trapezoid.generate`
- 仓库相对路径：`packages/ai4e-contrib/application/datasets/diffusion_trapezoid/generate.py:43`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.datasets.diffusion_trapezoid.generate')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-datasets-diffusion-trapezoid-generate-parameter-streams"></a>
## `ai4e_contrib.application.datasets.diffusion_trapezoid.generate.parameter_streams`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`parameter_streams(config)`
- **规范定义名**：`ai4e_contrib.application.datasets.diffusion_trapezoid.generate.parameter_streams`

### 用途

重现原连续 MT19937 流；保留单例演示消耗，随后生成正式测试名单。

### 导入与签名

```python
from ai4e_contrib.application.datasets.diffusion_trapezoid.generate import parameter_streams
```

```text
parameter_streams(config)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `未标注` | `必填` |

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
from ai4e_contrib.application.datasets.diffusion_trapezoid.generate import parameter_streams

print(signature(parameter_streams))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.datasets.diffusion_trapezoid.generate`
- 仓库相对路径：`packages/ai4e-contrib/application/datasets/diffusion_trapezoid/generate.py:10`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.datasets.diffusion_trapezoid.generate')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-datasets-diffusion-trapezoid-generate-solve"></a>
## `ai4e_contrib.application.datasets.diffusion_trapezoid.generate.solve`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`solve(*, nx, ny, nt, a)`
- **规范定义名**：`ai4e_contrib.application.datasets.diffusion_trapezoid.generate.solve`

### 用途

原近似空间模板的 Euler 解，返回 xi、eta、FP32 时间和场。

每一步存回 FP32，差分中间量用 FP64，保留原 NumPy 1.x 标量提升。
数组运算替代相互独立的空间循环；不引入子步、混合导数或隐式积分。
超出显式稳定界时拒绝生成，不能自动改步长冒充同一个实验。

### 导入与签名

```python
from ai4e_contrib.application.datasets.diffusion_trapezoid.generate import solve
```

```text
solve(*, nx, ny, nt, a)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `nx` | `未标注` | `必填关键字参数` |
| `ny` | `未标注` | `必填关键字参数` |
| `nt` | `未标注` | `必填关键字参数` |
| `a` | `未标注` | `必填关键字参数` |

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
from ai4e_contrib.application.datasets.diffusion_trapezoid.generate import solve

print(signature(solve))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`safediffcon`
- 案例：`safediffcon.burgers`, `safediffcon.tokamak`

### 源码位置

- 模块：`ai4e_contrib.application.datasets.diffusion_trapezoid.generate`
- 仓库相对路径：`packages/ai4e-contrib/application/datasets/diffusion_trapezoid/generate.py:18`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.datasets.diffusion_trapezoid.generate')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
