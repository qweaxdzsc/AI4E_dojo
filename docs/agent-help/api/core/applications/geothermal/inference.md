<!-- dojo-help: {"domain": "ai4e_core.applications.geothermal.inference", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.geothermal.inference 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.geothermal.inference", "topic_id": "module:ai4e_core.applications.geothermal.inference"} -->
# `ai4e_core.applications.geothermal.inference` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-geothermal-inference-predict-fields"></a>
## `ai4e_core.applications.geothermal.inference.predict_fields`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`predict_fields(networks, spatial, global_parameters, statistics)`
- **规范定义名**：`ai4e_core.applications.geothermal.inference.predict_fields`

### 用途

只使用两个网络的预测；反归一化在监督裁剪之前，与原物理输入一致。

### 导入与签名

```python
from ai4e_core.applications.geothermal.inference import predict_fields
```

```text
predict_fields(networks, spatial, global_parameters, statistics)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `networks` | `未标注` | `必填` |
| `spatial` | `未标注` | `必填` |
| `global_parameters` | `未标注` | `必填` |
| `statistics` | `未标注` | `必填` |

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
from ai4e_core.applications.geothermal.inference import predict_fields

print(signature(predict_fields))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `geotransolver/darcy`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`
- 案例：`classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `geotransolver.darcy`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`

### 源码位置

- 模块：`ai4e_core.applications.geothermal.inference`
- 仓库相对路径：`packages/ai4e-core/applications/geothermal/inference.py:9`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.geothermal.inference')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-geothermal-inference-predict-wells"></a>
## `ai4e_core.applications.geothermal.inference.predict_wells`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`predict_wells(fields, physical_parameters)`
- **规范定义名**：`ai4e_core.applications.geothermal.inference.predict_wells`

### 用途

以预测压力和温度求解物理残差与井级量，不读取真实标签。

### 导入与签名

```python
from ai4e_core.applications.geothermal.inference import predict_wells
```

```text
predict_wells(fields, physical_parameters)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `fields` | `未标注` | `必填` |
| `physical_parameters` | `未标注` | `必填` |

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
from ai4e_core.applications.geothermal.inference import predict_wells

print(signature(predict_wells))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.geothermal.inference`
- 仓库相对路径：`packages/ai4e-core/applications/geothermal/inference.py:23`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.geothermal.inference')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-geothermal-inference-save-sample"></a>
## `ai4e_core.applications.geothermal.inference.save_sample`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`save_sample(path, result)`
- **规范定义名**：`ai4e_core.applications.geothermal.inference.save_sample`

### 用途

保存自包含单例，切断来源整批storage；拒绝非有限预测。

### 导入与签名

```python
from ai4e_core.applications.geothermal.inference import save_sample
```

```text
save_sample(path, result)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `未标注` | `必填` |
| `result` | `未标注` | `必填` |

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
from ai4e_core.applications.geothermal.inference import save_sample

print(signature(save_sample))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.physical_visualization`, `recipe_extensions.sampling`

### 源码位置

- 模块：`ai4e_core.applications.geothermal.inference`
- 仓库相对路径：`packages/ai4e-core/applications/geothermal/inference.py:35`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.geothermal.inference')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
