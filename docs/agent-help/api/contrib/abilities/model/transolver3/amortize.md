<!-- dojo-help: {"domain": "ai4e_contrib.ability.model.transolver3.amortize", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.model.transolver3.amortize 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.model.transolver3.amortize", "topic_id": "module:ai4e_contrib.ability.model.transolver3.amortize"} -->
# `ai4e_contrib.ability.model.transolver3.amortize` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-model-transolver3-amortize-fullmeshdecodingmodel"></a>
## `ai4e_contrib.ability.model.transolver3.amortize.FullMeshDecodingModel`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`FullMeshDecodingModel(space_dim=1, n_layers=5, n_hidden=256, dropout=0, n_head=8, act='gelu', mlp_ratio=1, fun_dim=1, out_dim=1, slice_num=32, ref=8, unified_pos=False)`
- **规范定义名**：`ai4e_contrib.ability.model.transolver3.amortize.FullMeshDecodingModel`

### 用途

Stage 2 of the decoupled inference framework: full mesh decoding.

Runs inference at arbitrary mesh coordinates using the precomputed
physical state cache from Stage 1. The same trained checkpoint as
Transolver_chunk_opt_matrix_mul.Model can be loaded into this class.

### 导入与签名

```python
from ai4e_contrib.ability.model.transolver3.amortize import FullMeshDecodingModel
```

```text
FullMeshDecodingModel(space_dim=1, n_layers=5, n_hidden=256, dropout=0, n_head=8, act='gelu', mlp_ratio=1, fun_dim=1, out_dim=1, slice_num=32, ref=8, unified_pos=False)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `space_dim` | `未标注` | `1` |
| `n_layers` | `未标注` | `5` |
| `n_hidden` | `未标注` | `256` |
| `dropout` | `未标注` | `0` |
| `n_head` | `未标注` | `8` |
| `act` | `未标注` | `'gelu'` |
| `mlp_ratio` | `未标注` | `1` |
| `fun_dim` | `未标注` | `1` |
| `out_dim` | `未标注` | `1` |
| `slice_num` | `未标注` | `32` |
| `ref` | `未标注` | `8` |
| `unified_pos` | `未标注` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`FullMeshDecodingModel`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.transolver3.amortize import FullMeshDecodingModel

print(signature(FullMeshDecodingModel))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.transolver3.amortize`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/transolver3/amortize.py:221`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.transolver3.amortize')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-transolver3-amortize-fullmeshdecodingmodel-forward"></a>
## `ai4e_contrib.ability.model.transolver3.amortize.FullMeshDecodingModel.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, data, state_cache, use_checkpoint=True)`
- **规范定义名**：`ai4e_contrib.ability.model.transolver3.amortize.FullMeshDecodingModel.forward`

### 用途

Run full inference using the precomputed physical state cache.

state_cache: list of normalized physical states, one per layer,
    built by PhysicalStateCachingModel.

Returns: list of per-chunk output tensors.

### 导入与签名

```python
from ai4e_contrib.ability.model.transolver3.amortize import FullMeshDecodingModel
```

```text
forward(self, data, state_cache, use_checkpoint=True)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `data` | `未标注` | `必填` |
| `state_cache` | `未标注` | `必填` |
| `use_checkpoint` | `未标注` | `True` |

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
from ai4e_contrib.ability.model.transolver3.amortize import FullMeshDecodingModel

print(signature(FullMeshDecodingModel.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_contrib.ability.model.transolver3.amortize`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/transolver3/amortize.py:288`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.transolver3.amortize')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-transolver3-amortize-physicalstatecachingmodel"></a>
## `ai4e_contrib.ability.model.transolver3.amortize.PhysicalStateCachingModel`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`PhysicalStateCachingModel(space_dim=1, n_layers=5, n_hidden=256, dropout=0, n_head=8, act='gelu', mlp_ratio=1, fun_dim=1, out_dim=1, slice_num=32, ref=8, unified_pos=False)`
- **规范定义名**：`ai4e_contrib.ability.model.transolver3.amortize.PhysicalStateCachingModel`

### 用途

Stage 1 of the decoupled inference framework: physical state caching.

Iterates the full mesh in memory-compatible chunks, one layer at a time,
to build the physical state cache s_cache = {s_out'(l)}_{l=1..L}.
The caller accumulates per-chunk unnormalized statistics across batches,
then normalizes to obtain each layer's physical state before proceeding
to the next layer.

### 导入与签名

```python
from ai4e_contrib.ability.model.transolver3.amortize import PhysicalStateCachingModel
```

```text
PhysicalStateCachingModel(space_dim=1, n_layers=5, n_hidden=256, dropout=0, n_head=8, act='gelu', mlp_ratio=1, fun_dim=1, out_dim=1, slice_num=32, ref=8, unified_pos=False)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `space_dim` | `未标注` | `1` |
| `n_layers` | `未标注` | `5` |
| `n_hidden` | `未标注` | `256` |
| `dropout` | `未标注` | `0` |
| `n_head` | `未标注` | `8` |
| `act` | `未标注` | `'gelu'` |
| `mlp_ratio` | `未标注` | `1` |
| `fun_dim` | `未标注` | `1` |
| `out_dim` | `未标注` | `1` |
| `slice_num` | `未标注` | `32` |
| `ref` | `未标注` | `8` |
| `unified_pos` | `未标注` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`PhysicalStateCachingModel`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.model.transolver3.amortize import PhysicalStateCachingModel

print(signature(PhysicalStateCachingModel))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.model.transolver3.amortize`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/transolver3/amortize.py:118`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.transolver3.amortize')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-model-transolver3-amortize-physicalstatecachingmodel-forward"></a>
## `ai4e_contrib.ability.model.transolver3.amortize.PhysicalStateCachingModel.forward`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, data, state_cache, layer, use_checkpoint=True)`
- **规范定义名**：`ai4e_contrib.ability.model.transolver3.amortize.PhysicalStateCachingModel.forward`

### 用途

Process one chunk batch up to `layer` and return unnormalized
physical-state accumulators at that layer.

state_cache: list of normalized physical states already computed
    for layers 0..(layer-1).
layer: index of the layer at which to extract new statistics.

Returns: (fx_list, slice_token_wo_norm, slice_norm)
    slice_token_wo_norm and slice_norm are unnormalized accumulators
    to be summed across chunk batches before normalization.

### 导入与签名

```python
from ai4e_contrib.ability.model.transolver3.amortize import PhysicalStateCachingModel
```

```text
forward(self, data, state_cache, layer, use_checkpoint=True)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `data` | `未标注` | `必填` |
| `state_cache` | `未标注` | `必填` |
| `layer` | `未标注` | `必填` |
| `use_checkpoint` | `未标注` | `True` |

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
from ai4e_contrib.ability.model.transolver3.amortize import PhysicalStateCachingModel

print(signature(PhysicalStateCachingModel.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_contrib.ability.model.transolver3.amortize`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/transolver3/amortize.py:187`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.transolver3.amortize')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
