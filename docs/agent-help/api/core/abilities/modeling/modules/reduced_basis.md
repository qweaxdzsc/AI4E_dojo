<!-- dojo-help: {"domain": "ai4e_core.abilities.modeling.modules.reduced_basis", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.modeling.modules.reduced_basis 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.modeling.modules.reduced_basis", "topic_id": "module:ai4e_core.abilities.modeling.modules.reduced_basis"} -->
# `ai4e_core.abilities.modeling.modules.reduced_basis` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-modeling-modules-reduced-basis-frozenbasisdecoder"></a>
## `ai4e_core.abilities.modeling.modules.reduced_basis.FrozenBasisDecoder`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`FrozenBasisDecoder(representation: ReducedBasis)`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.reduced_basis.FrozenBasisDecoder`

### 用途

系数可微，基底和均值为冻结缓冲区，支持普通模块保存及设备迁移。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.reduced_basis import FrozenBasisDecoder
```

```text
FrozenBasisDecoder(representation: ReducedBasis)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `representation` | `ReducedBasis` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`FrozenBasisDecoder`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.reduced_basis import FrozenBasisDecoder

print(signature(FrozenBasisDecoder))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.reduced_basis`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/reduced_basis.py:84`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.reduced_basis')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-reduced-basis-frozenbasisdecoder-forward"></a>
## `ai4e_core.abilities.modeling.modules.reduced_basis.FrozenBasisDecoder.forward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, coefficients: torch.Tensor) -> torch.Tensor`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.reduced_basis.FrozenBasisDecoder.forward`

### 用途

执行 [...,r]→[...,D]，不剥离系数计算图。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.reduced_basis import FrozenBasisDecoder
```

```text
forward(self, coefficients: torch.Tensor) -> torch.Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `coefficients` | `torch.Tensor` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`torch.Tensor`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.reduced_basis import FrozenBasisDecoder

print(signature(FrozenBasisDecoder.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：`recipe_extensions.network_composition.cnn_rnn`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.operator_branch_replacement`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.reduced_basis`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/reduced_basis.py:93`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.reduced_basis')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-reduced-basis-reducedbasis"></a>
## `ai4e_core.abilities.modeling.modules.reduced_basis.ReducedBasis`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`ReducedBasis(state: dict)`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.reduced_basis.ReducedBasis`

### 用途

使用固定均值与正度量投影；basis 为 [D,r]，快照末轴为 D。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.reduced_basis import ReducedBasis
```

```text
ReducedBasis(state: dict)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `state` | `dict` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`ReducedBasis`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.reduced_basis import ReducedBasis

print(signature(ReducedBasis))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.reduced_basis`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/reduced_basis.py:10`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.reduced_basis')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-reduced-basis-reducedbasis-decode"></a>
## `ai4e_core.abilities.modeling.modules.reduced_basis.ReducedBasis.decode`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`decode(self, coefficients: np.ndarray) -> np.ndarray`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.reduced_basis.ReducedBasis.decode`

### 用途

将 [...,r] 重建为 [...,D]；不会重拟合均值或基底。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.reduced_basis import ReducedBasis
```

```text
decode(self, coefficients: np.ndarray) -> np.ndarray
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `coefficients` | `np.ndarray` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`np.ndarray`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.reduced_basis import ReducedBasis

print(signature(ReducedBasis.decode))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`geotransolver/bumper_beam`, `geotransolver/darcy`
- 案例：`geotransolver.bumper_beam`, `geotransolver.darcy`, `recipe_extensions.research_state`, `recipe_extensions.tail_batch`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.reduced_basis`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/reduced_basis.py:65`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.reduced_basis')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-reduced-basis-reducedbasis-encode"></a>
## `ai4e_core.abilities.modeling.modules.reduced_basis.ReducedBasis.encode`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`encode(self, value: np.ndarray) -> np.ndarray`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.reduced_basis.ReducedBasis.encode`

### 用途

按冻结正度量将 [...,D] 投影到 [...,r]。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.reduced_basis import ReducedBasis
```

```text
encode(self, value: np.ndarray) -> np.ndarray
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `value` | `np.ndarray` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`np.ndarray`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.reduced_basis import ReducedBasis

print(signature(ReducedBasis.encode))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.free_wiring`, `recipe_extensions.operator_branch_replacement`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.reduced_basis`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/reduced_basis.py:59`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.reduced_basis')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-reduced-basis-reducedbasis-from-state"></a>
## `ai4e_core.abilities.modeling.modules.reduced_basis.ReducedBasis.from_state`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`from_state(cls, state: dict) -> 'ReducedBasis'`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.reduced_basis.ReducedBasis.from_state`

### 用途

校验后恢复冻结基。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.reduced_basis import ReducedBasis
```

```text
from_state(cls, state: dict) -> 'ReducedBasis'
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `state` | `dict` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`'ReducedBasis'`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.reduced_basis import ReducedBasis

print(signature(ReducedBasis.from_state))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.reduced_basis`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/reduced_basis.py:75`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.reduced_basis')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-reduced-basis-reducedbasis-to-state"></a>
## `ai4e_core.abilities.modeling.modules.reduced_basis.ReducedBasis.to_state`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`to_state(self) -> dict`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.reduced_basis.ReducedBasis.to_state`

### 用途

返回完全独立的状态副本，保存由调用方承担。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.reduced_basis import ReducedBasis
```

```text
to_state(self) -> dict
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.reduced_basis import ReducedBasis

print(signature(ReducedBasis.to_state))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.reduced_basis`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/reduced_basis.py:70`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.reduced_basis')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-modeling-modules-reduced-basis-reducedbasis-torch-decoder"></a>
## `ai4e_core.abilities.modeling.modules.reduced_basis.ReducedBasis.torch_decoder`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`torch_decoder(self, *, dtype=torch.float64, device=None) -> 'FrozenBasisDecoder'`
- **规范定义名**：`ai4e_core.abilities.modeling.modules.reduced_basis.ReducedBasis.torch_decoder`

### 用途

用同一数值状态创建可微系数解码器；只注册缓冲区。

### 导入与签名

```python
from ai4e_core.abilities.modeling.modules.reduced_basis import ReducedBasis
```

```text
torch_decoder(self, *, dtype=torch.float64, device=None) -> 'FrozenBasisDecoder'
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `dtype` | `未标注` | `torch.float64` |
| `device` | `未标注` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`'FrozenBasisDecoder'`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.modeling.modules.reduced_basis import ReducedBasis

print(signature(ReducedBasis.torch_decoder))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.modeling.modules.reduced_basis`
- 仓库相对路径：`packages/ai4e-core/abilities/modeling/modules/reduced_basis.py:79`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.modeling.modules.reduced_basis')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
