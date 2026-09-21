<!-- dojo-help: {"domain": "ai4e_contrib.ability.model.abupt.sampling", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.model.abupt.sampling 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.model.abupt.sampling", "topic_id": "module:ai4e_contrib.ability.model.abupt.sampling"} -->
# `ai4e_contrib.ability.model.abupt.sampling` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-model-abupt-sampling-prepare-inputs"></a>
## `ai4e_contrib.ability.model.abupt.sampling.prepare_inputs`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`prepare_inputs(fields, config, *, sample, data_specs, bindings, normalization=None, geometry_conditioning_dims=None, epoch=0, evaluation=False, repeat=None, indices=None, sample_index=0)`
- **规范定义名**：`ai4e_contrib.ability.model.abupt.sampling.prepare_inputs`

### 用途

输入为归一化点场；固定下标可用于参考对齐，生产默认独立随机流。

### 导入与签名

```python
from ai4e_contrib.ability.model.abupt.sampling import prepare_inputs
```

```text
prepare_inputs(fields, config, *, sample, data_specs, bindings, normalization=None, geometry_conditioning_dims=None, epoch=0, evaluation=False, repeat=None, indices=None, sample_index=0)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `fields` | `未标注` | `必填` |
| `config` | `未标注` | `必填` |
| `sample` | `未标注` | `必填关键字参数` |
| `data_specs` | `未标注` | `必填关键字参数` |
| `bindings` | `未标注` | `必填关键字参数` |
| `normalization` | `未标注` | `None` |
| `geometry_conditioning_dims` | `未标注` | `None` |
| `epoch` | `未标注` | `0` |
| `evaluation` | `未标注` | `False` |
| `repeat` | `未标注` | `None` |
| `indices` | `未标注` | `None` |
| `sample_index` | `未标注` | `0` |

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
from ai4e_contrib.ability.model.abupt.sampling import prepare_inputs

print(signature(prepare_inputs))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `pcno`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `geothermal.pcno`, `recipe_extensions.field_mapping`, `recipe_extensions.sampling`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.ability.model.abupt.sampling`
- 仓库相对路径：`packages/ai4e-contrib/ability/model/abupt/sampling.py:13`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.model.abupt.sampling')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
