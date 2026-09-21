<!-- dojo-help: {"domain": "ai4e_contrib.application.datasets.nasa_crm.adapter", "kind": "api", "layer": "contrib.application", "summary": "ai4e_contrib.application.datasets.nasa_crm.adapter 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.application.datasets.nasa_crm.adapter", "topic_id": "module:ai4e_contrib.application.datasets.nasa_crm.adapter"} -->
# `ai4e_contrib.application.datasets.nasa_crm.adapter` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-application-datasets-nasa-crm-adapter-rawdataset"></a>
## `ai4e_contrib.application.datasets.nasa_crm.adapter.RawDataset`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`RawDataset(settings)`
- **规范定义名**：`ai4e_contrib.application.datasets.nasa_crm.adapter.RawDataset`

### 用途

原始数据只在单样本读取期间打开；分片含明确的来源文件。

### 导入与签名

```python
from ai4e_contrib.application.datasets.nasa_crm.adapter import RawDataset
```

```text
RawDataset(settings)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `settings` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`RawDataset`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.application.datasets.nasa_crm.adapter import RawDataset

print(signature(RawDataset))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.datasets.nasa_crm.adapter`
- 仓库相对路径：`packages/ai4e-contrib/application/datasets/nasa_crm/adapter.py:74`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.datasets.nasa_crm.adapter')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-datasets-nasa-crm-adapter-rawdataset-content-digest"></a>
## `ai4e_contrib.application.datasets.nasa_crm.adapter.RawDataset.content_digest`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`content_digest(self)`
- **规范定义名**：`ai4e_contrib.application.datasets.nasa_crm.adapter.RawDataset.content_digest`

### 用途

源内容与分片声明共同决定身份。

### 导入与签名

```python
from ai4e_contrib.application.datasets.nasa_crm.adapter import RawDataset
```

```text
content_digest(self)
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

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
from ai4e_contrib.application.datasets.nasa_crm.adapter import RawDataset

print(signature(RawDataset.content_digest))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.datasets.nasa_crm.adapter`
- 仓库相对路径：`packages/ai4e-contrib/application/datasets/nasa_crm/adapter.py:174`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.datasets.nasa_crm.adapter')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-datasets-nasa-crm-adapter-rawdataset-describe"></a>
## `ai4e_contrib.application.datasets.nasa_crm.adapter.RawDataset.describe`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`describe(self)`
- **规范定义名**：`ai4e_contrib.application.datasets.nasa_crm.adapter.RawDataset.describe`

### 用途

提供参考兼容数据清单的业务声明，不包含统计结果。

### 导入与签名

```python
from ai4e_contrib.application.datasets.nasa_crm.adapter import RawDataset
```

```text
describe(self)
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

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
from ai4e_contrib.application.datasets.nasa_crm.adapter import RawDataset

print(signature(RawDataset.describe))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`pcno_cylinder`
- 案例：`pcno.double_cylinder`, `recipe_extensions.model_block`

### 源码位置

- 模块：`ai4e_contrib.application.datasets.nasa_crm.adapter`
- 仓库相对路径：`packages/ai4e-contrib/application/datasets/nasa_crm/adapter.py:149`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.datasets.nasa_crm.adapter')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-datasets-nasa-crm-adapter-rawdataset-read"></a>
## `ai4e_contrib.application.datasets.nasa_crm.adapter.RawDataset.read`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`read(self, partition, index=0, *, fields=None, selection=None)`
- **规范定义名**：`ai4e_contrib.application.datasets.nasa_crm.adapter.RawDataset.read`

### 用途

按稳定字段顺序读出点字段和样本工况。

### 导入与签名

```python
from ai4e_contrib.application.datasets.nasa_crm.adapter import RawDataset
```

```text
read(self, partition, index=0, *, fields=None, selection=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `partition` | `未标注` | `必填` |
| `index` | `未标注` | `0` |
| `fields` | `未标注` | `None` |
| `selection` | `未标注` | `None` |

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
from ai4e_contrib.application.datasets.nasa_crm.adapter import RawDataset

print(signature(RawDataset.read))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `geotransolver/shapenet_car`, `pcno_cylinder`, `wdno`
- 案例：`aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.free_wiring`, `recipe_extensions.physical_visualization`, `recipe_extensions.sampling`, `recipe_extensions.wdno`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.application.datasets.nasa_crm.adapter`
- 仓库相对路径：`packages/ai4e-contrib/application/datasets/nasa_crm/adapter.py:122`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.datasets.nasa_crm.adapter')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-datasets-nasa-crm-adapter-view"></a>
## `ai4e_contrib.application.datasets.nasa_crm.adapter.View`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`View(path)`
- **规范定义名**：`ai4e_contrib.application.datasets.nasa_crm.adapter.View`

### 用途

参考 NPY 分块的只读视图，支持已有合法产物而不重写它。

### 导入与签名

```python
from ai4e_contrib.application.datasets.nasa_crm.adapter import View
```

```text
View(path)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`View`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.application.datasets.nasa_crm.adapter import View

print(signature(View))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.datasets.nasa_crm.adapter`
- 仓库相对路径：`packages/ai4e-contrib/application/datasets/nasa_crm/adapter.py:184`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.datasets.nasa_crm.adapter')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-datasets-nasa-crm-adapter-view-content-digest"></a>
## `ai4e_contrib.application.datasets.nasa_crm.adapter.View.content_digest`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`content_digest(self)`
- **规范定义名**：`ai4e_contrib.application.datasets.nasa_crm.adapter.View.content_digest`

### 用途

逐文件内容摘要，包含工况、元数据和全部块。

### 导入与签名

```python
from ai4e_contrib.application.datasets.nasa_crm.adapter import View
```

```text
content_digest(self)
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

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
from ai4e_contrib.application.datasets.nasa_crm.adapter import View

print(signature(View.content_digest))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.datasets.nasa_crm.adapter`
- 仓库相对路径：`packages/ai4e-contrib/application/datasets/nasa_crm/adapter.py:268`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.datasets.nasa_crm.adapter')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-datasets-nasa-crm-adapter-view-describe"></a>
## `ai4e_contrib.application.datasets.nasa_crm.adapter.View.describe`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`describe(self)`
- **规范定义名**：`ai4e_contrib.application.datasets.nasa_crm.adapter.View.describe`

### 用途

返回完整数据声明，调用者不需要识别 NPY 文件名。

### 导入与签名

```python
from ai4e_contrib.application.datasets.nasa_crm.adapter import View
```

```text
describe(self)
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

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
from ai4e_contrib.application.datasets.nasa_crm.adapter import View

print(signature(View.describe))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`pcno_cylinder`
- 案例：`pcno.double_cylinder`, `recipe_extensions.model_block`

### 源码位置

- 模块：`ai4e_contrib.application.datasets.nasa_crm.adapter`
- 仓库相对路径：`packages/ai4e-contrib/application/datasets/nasa_crm/adapter.py:264`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.datasets.nasa_crm.adapter')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-datasets-nasa-crm-adapter-view-read"></a>
## `ai4e_contrib.application.datasets.nasa_crm.adapter.View.read`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`read(self, partition, index=0, *, fields=None, selection=None)`
- **规范定义名**：`ai4e_contrib.application.datasets.nasa_crm.adapter.View.read`

### 用途

selection 是块下标；点字段携带原始点 ID，工况保持样本级。

### 导入与签名

```python
from ai4e_contrib.application.datasets.nasa_crm.adapter import View
```

```text
read(self, partition, index=0, *, fields=None, selection=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `partition` | `未标注` | `必填` |
| `index` | `未标注` | `0` |
| `fields` | `未标注` | `None` |
| `selection` | `未标注` | `None` |

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
from ai4e_contrib.application.datasets.nasa_crm.adapter import View

print(signature(View.read))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `geotransolver/shapenet_car`, `pcno_cylinder`, `wdno`
- 案例：`aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.free_wiring`, `recipe_extensions.physical_visualization`, `recipe_extensions.sampling`, `recipe_extensions.wdno`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.application.datasets.nasa_crm.adapter`
- 仓库相对路径：`packages/ai4e-contrib/application/datasets/nasa_crm/adapter.py:224`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.datasets.nasa_crm.adapter')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-datasets-nasa-crm-adapter-inspect"></a>
## `ai4e_contrib.application.datasets.nasa_crm.adapter.inspect`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`inspect(path)`
- **规范定义名**：`ai4e_contrib.application.datasets.nasa_crm.adapter.inspect`

### 用途

检查全部 group 的必需字段和共同点数，不读取场数组。

### 导入与签名

```python
from ai4e_contrib.application.datasets.nasa_crm.adapter import inspect
```

```text
inspect(path)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `未标注` | `必填` |

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
from ai4e_contrib.application.datasets.nasa_crm.adapter import inspect

print(signature(inspect))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`pcno`
- 案例：`geothermal.pcno`

### 源码位置

- 模块：`ai4e_contrib.application.datasets.nasa_crm.adapter`
- 仓库相对路径：`packages/ai4e-contrib/application/datasets/nasa_crm/adapter.py:34`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.datasets.nasa_crm.adapter')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-datasets-nasa-crm-adapter-manifest-digest"></a>
## `ai4e_contrib.application.datasets.nasa_crm.adapter.manifest_digest`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`manifest_digest(manifest)`
- **规范定义名**：`ai4e_contrib.application.datasets.nasa_crm.adapter.manifest_digest`

### 用途

保持参考 manifest 的稳定 JSON 摘要算法。

### 导入与签名

```python
from ai4e_contrib.application.datasets.nasa_crm.adapter import manifest_digest
```

```text
manifest_digest(manifest)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `manifest` | `未标注` | `必填` |

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
from ai4e_contrib.application.datasets.nasa_crm.adapter import manifest_digest

print(signature(manifest_digest))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.datasets.nasa_crm.adapter`
- 仓库相对路径：`packages/ai4e-contrib/application/datasets/nasa_crm/adapter.py:26`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.datasets.nasa_crm.adapter')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
