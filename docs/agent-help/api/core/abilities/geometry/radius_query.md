<!-- dojo-help: {"domain": "ai4e_core.abilities.geometry.radius_query", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.geometry.radius_query 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.geometry.radius_query", "topic_id": "module:ai4e_core.abilities.geometry.radius_query"} -->
# `ai4e_core.abilities.geometry.radius_query` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-geometry-radius-query-ballquery"></a>
## `ai4e_core.abilities.geometry.radius_query.BallQuery`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`BallQuery(radius: float=0.25, neighbors_in_radius: int=10, *, chunk_size: int=256)`
- **规范定义名**：`ai4e_core.abilities.geometry.radius_query.BallQuery`

### 用途

按参考方向查询；缓存由调用方按身份校验后显式注入，不进入权重。

### 导入与签名

```python
from ai4e_core.abilities.geometry.radius_query import BallQuery
```

```text
BallQuery(radius: float=0.25, neighbors_in_radius: int=10, *, chunk_size: int=256)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `radius` | `float` | `0.25` |
| `neighbors_in_radius` | `int` | `10` |
| `chunk_size` | `int` | `256` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`BallQuery`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.geometry.radius_query import BallQuery

print(signature(BallQuery))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.geometry.radius_query`
- 仓库相对路径：`packages/ai4e-core/abilities/geometry/radius_query.py:58`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.geometry.radius_query')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-geometry-radius-query-ballquery-forward"></a>
## `ai4e_core.abilities.geometry.radius_query.BallQuery.forward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, x: torch.Tensor, p_grid: torch.Tensor, reverse_mapping: bool=True)`
- **规范定义名**：`ai4e_core.abilities.geometry.radius_query.BallQuery.forward`

### 用途

返回索引和邻域坐标；reverse_mapping=True 时从 x 查 p_grid。

### 导入与签名

```python
from ai4e_core.abilities.geometry.radius_query import BallQuery
```

```text
forward(self, x: torch.Tensor, p_grid: torch.Tensor, reverse_mapping: bool=True)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `torch.Tensor` | `必填` |
| `p_grid` | `torch.Tensor` | `必填` |
| `reverse_mapping` | `bool` | `True` |

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
from ai4e_core.abilities.geometry.radius_query import BallQuery

print(signature(BallQuery.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.geometry.radius_query`
- 仓库相对路径：`packages/ai4e-core/abilities/geometry/radius_query.py:69`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.geometry.radius_query')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-geometry-radius-query-build-radius-cache-arrays"></a>
## `ai4e_core.abilities.geometry.radius_query.build_radius_cache_arrays`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`build_radius_cache_arrays(coordinates, *, radii, neighbors)`
- **规范定义名**：`ai4e_core.abilities.geometry.radius_query.build_radius_cache_arrays`

### 用途

对每个来源点集预计算自查询索引与有效性，缓存不含学习特征。

### 导入与签名

```python
from ai4e_core.abilities.geometry.radius_query import build_radius_cache_arrays
```

```text
build_radius_cache_arrays(coordinates, *, radii, neighbors)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `coordinates` | `未标注` | `必填` |
| `radii` | `未标注` | `必填关键字参数` |
| `neighbors` | `未标注` | `必填关键字参数` |

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
from ai4e_core.abilities.geometry.radius_query import build_radius_cache_arrays

print(signature(build_radius_cache_arrays))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`geotransolver/bumper_beam`, `geotransolver/darcy`
- 案例：`geotransolver.bumper_beam`, `geotransolver.darcy`

### 源码位置

- 模块：`ai4e_core.abilities.geometry.radius_query`
- 仓库相对路径：`packages/ai4e-core/abilities/geometry/radius_query.py:96`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.geometry.radius_query')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-geometry-radius-query-coordinate-digest"></a>
## `ai4e_core.abilities.geometry.radius_query.coordinate_digest`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`coordinate_digest(value)`
- **规范定义名**：`ai4e_core.abilities.geometry.radius_query.coordinate_digest`

### 用途

固定 float32 坐标身份，用于与可搬移邻域缓存匹配。

### 导入与签名

```python
from ai4e_core.abilities.geometry.radius_query import coordinate_digest
```

```text
coordinate_digest(value)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `value` | `未标注` | `必填` |

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
from ai4e_core.abilities.geometry.radius_query import coordinate_digest

print(signature(coordinate_digest))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.geometry.radius_query`
- 仓库相对路径：`packages/ai4e-core/abilities/geometry/radius_query.py:84`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.geometry.radius_query')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-geometry-radius-query-gather-neighbors"></a>
## `ai4e_core.abilities.geometry.radius_query.gather_neighbors`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`gather_neighbors(points: torch.Tensor, indices: torch.Tensor, valid: torch.Tensor)`
- **规范定义名**：`ai4e_core.abilities.geometry.radius_query.gather_neighbors`

### 用途

按索引取邻域坐标并屏蔽超界点；保留来源坐标的梯度。

### 导入与签名

```python
from ai4e_core.abilities.geometry.radius_query import gather_neighbors
```

```text
gather_neighbors(points: torch.Tensor, indices: torch.Tensor, valid: torch.Tensor)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `points` | `torch.Tensor` | `必填` |
| `indices` | `torch.Tensor` | `必填` |
| `valid` | `torch.Tensor` | `必填` |

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
from ai4e_core.abilities.geometry.radius_query import gather_neighbors

print(signature(gather_neighbors))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.geometry.radius_query`
- 仓库相对路径：`packages/ai4e-core/abilities/geometry/radius_query.py:52`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.geometry.radius_query')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-geometry-radius-query-install-prepared-queries"></a>
## `ai4e_core.abilities.geometry.radius_query.install_prepared_queries`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`install_prepared_queries(model, arrays, *, radii, neighbors, cache_spec)`
- **规范定义名**：`ai4e_core.abilities.geometry.radius_query.install_prepared_queries`

### 用途

给普通 BallQuery 注入具身份的准备索引；坐标或参数不匹配明确报错。

### 导入与签名

```python
from ai4e_core.abilities.geometry.radius_query import install_prepared_queries
```

```text
install_prepared_queries(model, arrays, *, radii, neighbors, cache_spec)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model` | `未标注` | `必填` |
| `arrays` | `未标注` | `必填` |
| `radii` | `未标注` | `必填关键字参数` |
| `neighbors` | `未标注` | `必填关键字参数` |
| `cache_spec` | `未标注` | `必填关键字参数` |

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
from ai4e_core.abilities.geometry.radius_query import install_prepared_queries

print(signature(install_prepared_queries))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`geotransolver/bumper_beam`, `geotransolver/darcy`
- 案例：`geotransolver.bumper_beam`, `geotransolver.darcy`

### 源码位置

- 模块：`ai4e_core.abilities.geometry.radius_query`
- 仓库相对路径：`packages/ai4e-core/abilities/geometry/radius_query.py:118`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.geometry.radius_query')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-geometry-radius-query-radius-indices"></a>
## `ai4e_core.abilities.geometry.radius_query.radius_indices`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`radius_indices(points: torch.Tensor, queries: torch.Tensor, radius: float, max_points: int, *, chunk_size: int=256)`
- **规范定义名**：`ai4e_core.abilities.geometry.radius_query.radius_indices`

### 用途

返回 [B,Q,K] 索引和有效性；MPS 查询显式在 CPU 执行。

为对照兼容，N<K 的补位与参考相同，索引零且距离零（视作有效）。
不把距离超界与有效的第零号点混淆。查询不参与坐标梯度。

### 导入与签名

```python
from ai4e_core.abilities.geometry.radius_query import radius_indices
```

```text
radius_indices(points: torch.Tensor, queries: torch.Tensor, radius: float, max_points: int, *, chunk_size: int=256)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `points` | `torch.Tensor` | `必填` |
| `queries` | `torch.Tensor` | `必填` |
| `radius` | `float` | `必填` |
| `max_points` | `int` | `必填` |
| `chunk_size` | `int` | `256` |

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
from ai4e_core.abilities.geometry.radius_query import radius_indices

print(signature(radius_indices))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.geometry.radius_query`
- 仓库相对路径：`packages/ai4e-core/abilities/geometry/radius_query.py:11`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.geometry.radius_query')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
