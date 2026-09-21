<!-- dojo-help: {"domain": "ai4e_contrib.ability.postproc.safediffcon.burgers", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.postproc.safediffcon.burgers 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.postproc.safediffcon.burgers", "topic_id": "module:ai4e_contrib.ability.postproc.safediffcon.burgers"} -->
# `ai4e_contrib.ability.postproc.safediffcon.burgers` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-burgers-diff-mat-1d"></a>
## `ai4e_contrib.ability.postproc.safediffcon.burgers.Diff_mat_1D`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`Diff_mat_1D(Nx, device='cpu')`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.burgers.Diff_mat_1D`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.burgers import Diff_mat_1D
```

```text
Diff_mat_1D(Nx, device='cpu')
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `Nx` | `未标注` | `必填` |
| `device` | `未标注` | `'cpu'` |

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
from ai4e_contrib.ability.postproc.safediffcon.burgers import Diff_mat_1D

print(signature(Diff_mat_1D))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.burgers`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/burgers.py:9`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.burgers')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-burgers-burgers-numeric-solve-free"></a>
## `ai4e_contrib.ability.postproc.safediffcon.burgers.burgers_numeric_solve_free`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`burgers_numeric_solve_free(u0, f, visc, T, dt=0.0001, num_t=10, mode=None)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.burgers.burgers_numeric_solve_free`

### 用途

Simulates trajectories based on u0 and f. Trajectory i is based on u0[i, :]
and f[i, :, :]

Args:
    u0: (N,s), N is the number of samples (every sample has different u0 and f)
    f: (N,Nt,s)
    T: physical simulation time
    dt: physical simulation stepsize
    num_t: 
        number of sampling of times
        num of controllable forces (forces f_[i: i + T / dt] are the same)
Returns:
    simulated u: (N_{u0 and f}, num_t, n_spatial_grids)

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.burgers import burgers_numeric_solve_free
```

```text
burgers_numeric_solve_free(u0, f, visc, T, dt=0.0001, num_t=10, mode=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `u0` | `未标注` | `必填` |
| `f` | `未标注` | `必填` |
| `visc` | `未标注` | `必填` |
| `T` | `未标注` | `必填` |
| `dt` | `未标注` | `0.0001` |
| `num_t` | `未标注` | `10` |
| `mode` | `未标注` | `None` |

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
from ai4e_contrib.ability.postproc.safediffcon.burgers import burgers_numeric_solve_free

print(signature(burgers_numeric_solve_free))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.burgers`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/burgers.py:26`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.burgers')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
