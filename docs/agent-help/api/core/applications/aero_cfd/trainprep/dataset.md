<!-- dojo-help: {"domain": "ai4e_core.applications.aero_cfd.trainprep.dataset", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.aero_cfd.trainprep.dataset 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.aero_cfd.trainprep.dataset", "topic_id": "module:ai4e_core.applications.aero_cfd.trainprep.dataset"} -->
# `ai4e_core.applications.aero_cfd.trainprep.dataset` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-dataset-iter-partition-batches"></a>
## `ai4e_core.applications.aero_cfd.trainprep.dataset.iter_partition_batches`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`iter_partition_batches(index, partition: str, *, prepare, collate, normalization, physical_prepare, normalized_input: bool, sampling: dict, config: dict, batch_size: int, device, epoch: int=0, evaluation: bool=False, repeat=None)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.dataset.iter_partition_batches`

### 用途

按分片准备并收批，训练评估与独立后处理共用同一采样入口。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.dataset import iter_partition_batches
```

```text
iter_partition_batches(index, partition: str, *, prepare, collate, normalization, physical_prepare, normalized_input: bool, sampling: dict, config: dict, batch_size: int, device, epoch: int=0, evaluation: bool=False, repeat=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `index` | `未标注` | `必填` |
| `partition` | `str` | `必填` |
| `prepare` | `未标注` | `必填关键字参数` |
| `collate` | `未标注` | `必填关键字参数` |
| `normalization` | `未标注` | `必填关键字参数` |
| `physical_prepare` | `未标注` | `必填关键字参数` |
| `normalized_input` | `bool` | `必填关键字参数` |
| `sampling` | `dict` | `必填关键字参数` |
| `config` | `dict` | `必填关键字参数` |
| `batch_size` | `int` | `必填关键字参数` |
| `device` | `未标注` | `必填关键字参数` |
| `epoch` | `int` | `0` |
| `evaluation` | `bool` | `False` |
| `repeat` | `未标注` | `None` |

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
from ai4e_core.applications.aero_cfd.trainprep.dataset import iter_partition_batches

print(signature(iter_partition_batches))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.dataset`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/dataset.py:261`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.dataset')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-dataset-open-manifest-sample"></a>
## `ai4e_core.applications.aero_cfd.trainprep.dataset.open_manifest_sample`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`open_manifest_sample(manifest_path: str | Path, *, partition: str, index: int=0) -> dict[str, torch.Tensor]`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.dataset.open_manifest_sample`

### 用途

按产物清单读回实际字段与路径；禁止把归一化数据当物理数据派生。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.dataset import open_manifest_sample
```

```text
open_manifest_sample(manifest_path: str | Path, *, partition: str, index: int=0) -> dict[str, torch.Tensor]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `manifest_path` | `str | Path` | `必填` |
| `partition` | `str` | `必填关键字参数` |
| `index` | `int` | `0` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, torch.Tensor]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.dataset import open_manifest_sample

print(signature(open_manifest_sample))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.dataset`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/dataset.py:96`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.dataset')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-dataset-open-preprocessed-sample"></a>
## `ai4e_core.applications.aero_cfd.trainprep.dataset.open_preprocessed_sample`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`open_preprocessed_sample(sample_dir: str | Path, filemap: Mapping[str, str]) -> dict[str, torch.Tensor]`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.dataset.open_preprocessed_sample`

### 用途

读对照表中的磁盘场，标量压力/体积距离收成单通道，并生成表面距离全零场。

不套归一化。对照表外的场不读；``cell`` 缺文件时跳过。

Args:
    sample_dir: 样本目录。
    filemap: 逻辑名到磁盘文件名。

Returns:
    逻辑名到张量，含 ``surface_sdf``。

Raises:
    RuntimeError: 必需文件缺失或加载失败，信息含完整路径。
    ValueError: 无法从表面坐标或法向得到点数。
    TypeError: 对照表或载荷类型错误。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.dataset import open_preprocessed_sample
```

```text
open_preprocessed_sample(sample_dir: str | Path, filemap: Mapping[str, str]) -> dict[str, torch.Tensor]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `sample_dir` | `str | Path` | `必填` |
| `filemap` | `Mapping[str, str]` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, torch.Tensor]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.dataset import open_preprocessed_sample

print(signature(open_preprocessed_sample))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.dataset`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/dataset.py:53`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.dataset')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-dataset-open-splits-step"></a>
## `ai4e_core.applications.aero_cfd.trainprep.dataset.open_splits_step`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`open_splits_step(ctx: dict[str, Any]) -> dict[str, Any]`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.dataset.open_splits_step`

### 用途

规范化预处理根目录，按名单列分片并校验人数。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.dataset import open_splits_step
```

```text
open_splits_step(ctx: dict[str, Any]) -> dict[str, Any]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `ctx` | `dict[str, Any]` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, Any]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.dataset import open_splits_step

print(signature(open_splits_step))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.dataset`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/dataset.py:374`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.dataset')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-dataset-prepare-partition-sample"></a>
## `ai4e_core.applications.aero_cfd.trainprep.dataset.prepare_partition_sample`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`prepare_partition_sample(index, partition: str, item: int, *, prepare, normalization, physical_prepare, normalized_input: bool, sampling: dict, config: dict, epoch: int=0, evaluation: bool=False, repeat=None)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.dataset.prepare_partition_sample`

### 用途

读一个分片样本，套冻结变换后交给注入的采样准备。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.dataset import prepare_partition_sample
```

```text
prepare_partition_sample(index, partition: str, item: int, *, prepare, normalization, physical_prepare, normalized_input: bool, sampling: dict, config: dict, epoch: int=0, evaluation: bool=False, repeat=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `index` | `未标注` | `必填` |
| `partition` | `str` | `必填` |
| `item` | `int` | `必填` |
| `prepare` | `未标注` | `必填关键字参数` |
| `normalization` | `未标注` | `必填关键字参数` |
| `physical_prepare` | `未标注` | `必填关键字参数` |
| `normalized_input` | `bool` | `必填关键字参数` |
| `sampling` | `dict` | `必填关键字参数` |
| `config` | `dict` | `必填关键字参数` |
| `epoch` | `int` | `0` |
| `evaluation` | `bool` | `False` |
| `repeat` | `未标注` | `None` |

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
from ai4e_core.applications.aero_cfd.trainprep.dataset import prepare_partition_sample

print(signature(prepare_partition_sample))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.dataset`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/dataset.py:224`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.dataset')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-dataset-prepare-physical-sample"></a>
## `ai4e_core.applications.aero_cfd.trainprep.dataset.prepare_physical_sample`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`prepare_physical_sample(fields: dict[str, torch.Tensor], *, rules=None) -> dict[str, torch.Tensor]`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.dataset.prepare_physical_sample`

### 用途

统一标量通道；零距离仅按显式项目规则在物理空间派生。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.dataset import prepare_physical_sample
```

```text
prepare_physical_sample(fields: dict[str, torch.Tensor], *, rules=None) -> dict[str, torch.Tensor]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `fields` | `dict[str, torch.Tensor]` | `必填` |
| `rules` | `未标注` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, torch.Tensor]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.dataset import prepare_physical_sample

print(signature(prepare_physical_sample))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.dataset`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/dataset.py:108`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.dataset')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-dataset-probe"></a>
## `ai4e_core.applications.aero_cfd.trainprep.dataset.probe`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`probe(config: dict, *, prepare=None, dry_run: bool=False) -> dict`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.dataset.probe`

### 用途

按项目配置执行只读或准备探测，贡献组件通过参数注入。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.dataset import probe
```

```text
probe(config: dict, *, prepare=None, dry_run: bool=False) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `dict` | `必填` |
| `prepare` | `未标注` | `None` |
| `dry_run` | `bool` | `False` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.dataset import probe

print(signature(probe))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.dataset`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/dataset.py:115`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.dataset')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-dataset-read-probe-sample-step"></a>
## `ai4e_core.applications.aero_cfd.trainprep.dataset.read_probe_sample_step`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`read_probe_sample_step(ctx: dict[str, Any]) -> dict[str, Any]`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.dataset.read_probe_sample_step`

### 用途

按对照表打开探测分片的一个样本，默认 test 第 0 个。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.dataset import read_probe_sample_step
```

```text
read_probe_sample_step(ctx: dict[str, Any]) -> dict[str, Any]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `ctx` | `dict[str, Any]` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, Any]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.dataset import read_probe_sample_step

print(signature(read_probe_sample_step))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.dataset`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/dataset.py:402`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.dataset')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-dataset-read-probe-stage"></a>
## `ai4e_core.applications.aero_cfd.trainprep.dataset.read_probe_stage`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`read_probe_stage(cfg: Mapping[str, Any]) -> Stage`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.dataset.read_probe_stage`

### 用途

按配置交出名为 ``train`` 的阶段。

步骤为：记下模型名称、打开分片、读取探测样本；不执行训练。
不读命令行，不建运行目录。

Args:
    cfg: 案例配置。本函数不读磁盘。

Returns:
    训练准备阶段盒子。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.dataset import read_probe_stage
```

```text
read_probe_stage(cfg: Mapping[str, Any]) -> Stage
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cfg` | `Mapping[str, Any]` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Stage`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.dataset import read_probe_stage

print(signature(read_probe_stage))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.dataset`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/dataset.py:340`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.dataset')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-dataset-repeat-seed-epoch"></a>
## `ai4e_core.applications.aero_cfd.trainprep.dataset.repeat_seed_epoch`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`repeat_seed_epoch(repeat: int) -> int`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.dataset.repeat_seed_epoch`

### 用途

由重复序号派生独立采样流，避免固定评估种子下重复无新信息。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.dataset import repeat_seed_epoch
```

```text
repeat_seed_epoch(repeat: int) -> int
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `repeat` | `int` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`int`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.dataset import repeat_seed_epoch

print(signature(repeat_seed_epoch))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.dataset`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/dataset.py:333`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.dataset')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-dataset-repeated-samples"></a>
## `ai4e_core.applications.aero_cfd.trainprep.dataset.repeated_samples`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`repeated_samples(samples: list[str], repeats: int)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.dataset.repeated_samples`

### 用途

官方评估名单各走多次，长度等于人数乘重复次数。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.dataset import repeated_samples
```

```text
repeated_samples(samples: list[str], repeats: int)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `samples` | `list[str]` | `必填` |
| `repeats` | `int` | `必填` |

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
from ai4e_core.applications.aero_cfd.trainprep.dataset import repeated_samples

print(signature(repeated_samples))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.dataset`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/dataset.py:215`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.dataset')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-dataset-resolve-preprocessed-root"></a>
## `ai4e_core.applications.aero_cfd.trainprep.dataset.resolve_preprocessed_root`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`resolve_preprocessed_root(root: str | Path, *, folder_name: str=DEFAULT_PREPROCESSED_FOLDER) -> Path`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.dataset.resolve_preprocessed_root`

### 用途

若根目录名不是预处理子目录则追加，并验证目录存在。

Args:
    root: 数据根或已经指向预处理子目录的路径。
    folder_name: 预处理子目录名，默认 ``preprocessed``。

Returns:
    存在的预处理根目录。

Raises:
    FileNotFoundError: 解析后的目录不存在。
    ValueError: 解析后的目录名仍不是预处理子目录。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.dataset import resolve_preprocessed_root
```

```text
resolve_preprocessed_root(root: str | Path, *, folder_name: str=DEFAULT_PREPROCESSED_FOLDER) -> Path
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `root` | `str | Path` | `必填` |
| `folder_name` | `str` | `DEFAULT_PREPROCESSED_FOLDER` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`Path`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FileNotFoundError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.dataset import resolve_preprocessed_root

print(signature(resolve_preprocessed_root))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.dataset`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/dataset.py:25`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.dataset')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-trainprep-dataset-select-abupt-step"></a>
## `ai4e_core.applications.aero_cfd.trainprep.dataset.select_abupt_step`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`select_abupt_step(ctx: dict[str, Any]) -> dict[str, Any]`
- **规范定义名**：`ai4e_core.applications.aero_cfd.trainprep.dataset.select_abupt_step`

### 用途

确认已有运行目录，并记下模型为 AB-UPT。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.trainprep.dataset import select_abupt_step
```

```text
select_abupt_step(ctx: dict[str, Any]) -> dict[str, Any]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `ctx` | `dict[str, Any]` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`dict[str, Any]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.trainprep.dataset import select_abupt_step

print(signature(select_abupt_step))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.trainprep.dataset`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/trainprep/dataset.py:363`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.trainprep.dataset')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
