<!-- dojo-help: {"domain": "ai4e_contrib.application.datasets.darcy_flow.adapter", "kind": "api", "layer": "contrib.application", "summary": "ai4e_contrib.application.datasets.darcy_flow.adapter 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.application.datasets.darcy_flow.adapter", "topic_id": "module:ai4e_contrib.application.datasets.darcy_flow.adapter"} -->
# `ai4e_contrib.application.datasets.darcy_flow.adapter` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-application-datasets-darcy-flow-adapter-darcysource"></a>
## `ai4e_contrib.application.datasets.darcy_flow.adapter.DarcySource`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`DarcySource(root, *, train_count=1000, evaluation_count=200)`
- **规范定义名**：`ai4e_contrib.application.datasets.darcy_flow.adapter.DarcySource`

### 用途

读取 smooth1/smooth2；内存只保留当前来源 MAT。

### 导入与签名

```python
from ai4e_contrib.application.datasets.darcy_flow.adapter import DarcySource
```

```text
DarcySource(root, *, train_count=1000, evaluation_count=200)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `root` | `未标注` | `必填` |
| `train_count` | `未标注` | `1000` |
| `evaluation_count` | `未标注` | `200` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`DarcySource`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.application.datasets.darcy_flow.adapter import DarcySource

print(signature(DarcySource))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.datasets.darcy_flow.adapter`
- 仓库相对路径：`packages/ai4e-contrib/application/datasets/darcy_flow/adapter.py:10`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.datasets.darcy_flow.adapter')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-datasets-darcy-flow-adapter-darcysource-read"></a>
## `ai4e_contrib.application.datasets.darcy_flow.adapter.DarcySource.read`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`read(self, sample)`
- **规范定义名**：`ai4e_contrib.application.datasets.darcy_flow.adapter.DarcySource.read`

### 用途

读取原系数和解，不在物理准备中下采样。

### 导入与签名

```python
from ai4e_contrib.application.datasets.darcy_flow.adapter import DarcySource
```

```text
read(self, sample)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `sample` | `未标注` | `必填` |

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
from ai4e_contrib.application.datasets.darcy_flow.adapter import DarcySource

print(signature(DarcySource.read))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `geotransolver/shapenet_car`, `pcno_cylinder`, `wdno`
- 案例：`aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.free_wiring`, `recipe_extensions.physical_visualization`, `recipe_extensions.sampling`, `recipe_extensions.wdno`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.application.datasets.darcy_flow.adapter`
- 仓库相对路径：`packages/ai4e-contrib/application/datasets/darcy_flow/adapter.py:33`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.datasets.darcy_flow.adapter')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-datasets-darcy-flow-adapter-darcysource-samples"></a>
## `ai4e_contrib.application.datasets.darcy_flow.adapter.DarcySource.samples`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`samples(self)`
- **规范定义名**：`ai4e_contrib.application.datasets.darcy_flow.adapter.DarcySource.samples`

### 用途

保留来源行号与固定分片，计数可缩小用于接口测试。

### 导入与签名

```python
from ai4e_contrib.application.datasets.darcy_flow.adapter import DarcySource
```

```text
samples(self)
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
from ai4e_contrib.application.datasets.darcy_flow.adapter import DarcySource

print(signature(DarcySource.samples))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`, `pcno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `extension.pcno`, `geothermal.pcno`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_contrib.application.datasets.darcy_flow.adapter`
- 仓库相对路径：`packages/ai4e-contrib/application/datasets/darcy_flow/adapter.py:25`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.datasets.darcy_flow.adapter')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
