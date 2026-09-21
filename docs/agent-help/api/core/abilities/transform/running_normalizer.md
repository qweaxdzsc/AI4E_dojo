<!-- dojo-help: {"domain": "ai4e_core.abilities.transform.running_normalizer", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.transform.running_normalizer 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.transform.running_normalizer", "topic_id": "module:ai4e_core.abilities.transform.running_normalizer"} -->
# `ai4e_core.abilities.transform.running_normalizer` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-transform-running-normalizer-runningnormalizer"></a>
## `ai4e_core.abilities.transform.running_normalizer.RunningNormalizer`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`RunningNormalizer(size: int, *, epsilon: float=1e-08, max_accumulations: int=1000000)`
- **规范定义名**：`ai4e_core.abilities.transform.running_normalizer.RunningNormalizer`

### 用途

按最后一维累计有限样本，并支持可恢复正反变换。

### 导入与签名

```python
from ai4e_core.abilities.transform.running_normalizer import RunningNormalizer
```

```text
RunningNormalizer(size: int, *, epsilon: float=1e-08, max_accumulations: int=1000000)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `size` | `int` | `必填` |
| `epsilon` | `float` | `1e-08` |
| `max_accumulations` | `int` | `1000000` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`RunningNormalizer`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.transform.running_normalizer import RunningNormalizer

print(signature(RunningNormalizer))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.transform.running_normalizer`
- 仓库相对路径：`packages/ai4e-core/abilities/transform/running_normalizer.py:9`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.transform.running_normalizer')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-transform-running-normalizer-runningnormalizer-accumulate"></a>
## `ai4e_core.abilities.transform.running_normalizer.RunningNormalizer.accumulate`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`accumulate(self, value: torch.Tensor) -> None`
- **规范定义名**：`ai4e_core.abilities.transform.running_normalizer.RunningNormalizer.accumulate`

### 用途

累计一批样本；达到上限后保持冻结统计。

### 导入与签名

```python
from ai4e_core.abilities.transform.running_normalizer import RunningNormalizer
```

```text
accumulate(self, value: torch.Tensor) -> None
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `value` | `torch.Tensor` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`None`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.transform.running_normalizer import RunningNormalizer

print(signature(RunningNormalizer.accumulate))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `recipe_extensions.field_mapping`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.abilities.transform.running_normalizer`
- 仓库相对路径：`packages/ai4e-core/abilities/transform/running_normalizer.py:24`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.transform.running_normalizer')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-transform-running-normalizer-runningnormalizer-forward"></a>
## `ai4e_core.abilities.transform.running_normalizer.RunningNormalizer.forward`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`forward(self, value: torch.Tensor, *, accumulate: bool=False) -> torch.Tensor`
- **规范定义名**：`ai4e_core.abilities.transform.running_normalizer.RunningNormalizer.forward`

### 用途

按当前统计归一化，并可先累计本批输入。

### 导入与签名

```python
from ai4e_core.abilities.transform.running_normalizer import RunningNormalizer
```

```text
forward(self, value: torch.Tensor, *, accumulate: bool=False) -> torch.Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `value` | `torch.Tensor` | `必填` |
| `accumulate` | `bool` | `False` |

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
from ai4e_core.abilities.transform.running_normalizer import RunningNormalizer

print(signature(RunningNormalizer.forward))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.transform.running_normalizer`
- 仓库相对路径：`packages/ai4e-core/abilities/transform/running_normalizer.py:46`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.transform.running_normalizer')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-transform-running-normalizer-runningnormalizer-inverse"></a>
## `ai4e_core.abilities.transform.running_normalizer.RunningNormalizer.inverse`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`inverse(self, value: torch.Tensor) -> torch.Tensor`
- **规范定义名**：`ai4e_core.abilities.transform.running_normalizer.RunningNormalizer.inverse`

### 用途

使用当前统计把归一化值还原到原空间。

### 导入与签名

```python
from ai4e_core.abilities.transform.running_normalizer import RunningNormalizer
```

```text
inverse(self, value: torch.Tensor) -> torch.Tensor
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `value` | `torch.Tensor` | `必填` |

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
from ai4e_core.abilities.transform.running_normalizer import RunningNormalizer

print(signature(RunningNormalizer.inverse))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.transform.running_normalizer`
- 仓库相对路径：`packages/ai4e-core/abilities/transform/running_normalizer.py:53`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.transform.running_normalizer')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-transform-running-normalizer-runningnormalizer-statistics"></a>
## `ai4e_core.abilities.transform.running_normalizer.RunningNormalizer.statistics`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`statistics(self, value: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]`
- **规范定义名**：`ai4e_core.abilities.transform.running_normalizer.RunningNormalizer.statistics`

### 用途

返回匹配输入设备和精度的均值与标准差。

### 导入与签名

```python
from ai4e_core.abilities.transform.running_normalizer import RunningNormalizer
```

```text
statistics(self, value: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `value` | `torch.Tensor` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`tuple[torch.Tensor, torch.Tensor]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.transform.running_normalizer import RunningNormalizer

print(signature(RunningNormalizer.statistics))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.abilities.transform.running_normalizer`
- 仓库相对路径：`packages/ai4e-core/abilities/transform/running_normalizer.py:38`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.transform.running_normalizer')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
