<!-- dojo-help: {"domain": "ai4e_core.abilities.modeling.modules.patch_embedding", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.modeling.modules.patch_embedding 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.modeling.modules.patch_embedding", "topic_id": "module:ai4e_core.abilities.modeling.modules.patch_embedding"} -->
# `ai4e_core.abilities.modeling.modules.patch_embedding` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-modeling-modules-patch-embedding-patchembedding"></a>
## `ai4e_core.abilities.modeling.modules.patch_embedding.PatchEmbedding`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`PatchEmbedding(in_channels: int, dim: int, patch_shape: Sequence[int])`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.patch_embedding.PatchEmbedding`

### 用途

把二维或三维规则格分块后线性投影；仅在高索引侧补零。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.patch_embedding import PatchEmbedding
```

```text
PatchEmbedding(in_channels: int, dim: int, patch_shape: Sequence[int])
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `in_channels` | `int` | `必填` |
| `dim` | `int` | `必填` |
| `patch_shape` | `Sequence[int]` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`PatchEmbedding`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.patch_embedding import PatchEmbedding

print(signature(PatchEmbedding))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.unet_transformer`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.patch_embedding`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/patch_embedding.py:32`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.patch_embedding')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-patch-embedding-patchembedding-forward"></a>
## `ai4e_core.abilities.modeling.modules.patch_embedding.PatchEmbedding.forward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, value: torch.Tensor, valid_mask: torch.Tensor | None=None) -> tuple[torch.Tensor, torch.Tensor, dict]`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.patch_embedding.PatchEmbedding.forward`

### 用途

返回 tokens、真为忽略的键掩码，以及可搬移的纯形状字典。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.patch_embedding import PatchEmbedding
```

```text
forward(self, value: torch.Tensor, valid_mask: torch.Tensor | None=None) -> tuple[torch.Tensor, torch.Tensor, dict]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `value` | `torch.Tensor` | `必填` |
| `valid_mask` | `torch.Tensor | None` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`tuple[torch.Tensor, torch.Tensor, dict]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.patch_embedding import PatchEmbedding

print(signature(PatchEmbedding.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.patch_embedding`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/patch_embedding.py:47`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.patch_embedding')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-patch-embedding-partition-patches"></a>
## `ai4e_core.abilities.modeling.modules.patch_embedding.partition_patches`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`partition_patches(value: torch.Tensor, patch_shape: Sequence[int]) -> torch.Tensor`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.patch_embedding.partition_patches`

### 用途

将已整除的 [B,*spatial,C] 转为 [B,N,patch_volume*C]，末轴最快。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.patch_embedding import partition_patches
```

```text
partition_patches(value: torch.Tensor, patch_shape: Sequence[int]) -> torch.Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `value` | `torch.Tensor` | `必填` |
| `patch_shape` | `Sequence[int]` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`torch.Tensor`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.patch_embedding import partition_patches

print(signature(partition_patches))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.patch_embedding`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/patch_embedding.py:20`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.patch_embedding')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-patch-embedding-patch-centers"></a>
## `ai4e_core.abilities.modeling.modules.patch_embedding.patch_centers`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`patch_centers(spatial_info: dict, *, device=None, dtype=torch.float32) -> torch.Tensor`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.patch_embedding.patch_centers`

### 用途

返回 [N,ndim] 归一化块格中心；它是索引位置而非物理坐标。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.patch_embedding import patch_centers
```

```text
patch_centers(spatial_info: dict, *, device=None, dtype=torch.float32) -> torch.Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `spatial_info` | `dict` | `必填` |
| `device` | `未标注` | `None` |
| `dtype` | `未标注` | `torch.float32` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`torch.Tensor`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.patch_embedding import patch_centers

print(signature(patch_centers))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.unet_transformer`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.patch_embedding`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/patch_embedding.py:13`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.patch_embedding')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
