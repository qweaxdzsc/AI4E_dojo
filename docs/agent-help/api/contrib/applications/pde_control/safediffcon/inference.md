<!-- dojo-help: {"domain": "ai4e_contrib.application.pde_control.safediffcon.inference", "kind": "api", "layer": "contrib.application", "summary": "ai4e_contrib.application.pde_control.safediffcon.inference 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.application.pde_control.safediffcon.inference", "topic_id": "module:ai4e_contrib.application.pde_control.safediffcon.inference"} -->
# `ai4e_contrib.application.pde_control.safediffcon.inference` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-application-pde-control-safediffcon-inference-adapt"></a>
## `ai4e_contrib.application.pde_control.safediffcon.inference.adapt`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`adapt(cfg: dict, prepared: dict, checkpoint: str, values: dict, *, construct, guide, session) -> tuple[torch.nn.Module, str, float]`
- **规范定义名**：`ai4e_contrib.application.pde_control.safediffcon.inference.adapt`

### 用途

明确更新参数并写入本次有效权重，普通采样不调用此函数。

### 导入与签名

```python
from ai4e_contrib.application.pde_control.safediffcon.inference import adapt
```

```text
adapt(cfg: dict, prepared: dict, checkpoint: str, values: dict, *, construct, guide, session) -> tuple[torch.nn.Module, str, float]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cfg` | `dict` | `必填` |
| `prepared` | `dict` | `必填` |
| `checkpoint` | `str` | `必填` |
| `values` | `dict` | `必填` |
| `construct` | `未标注` | `必填关键字参数` |
| `guide` | `未标注` | `必填关键字参数` |
| `session` | `未标注` | `必填关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`tuple[torch.nn.Module, str, float]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.application.pde_control.safediffcon.inference import adapt

print(signature(adapt))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`safediffcon`
- 案例：`safediffcon.burgers`, `safediffcon.tokamak`

### 源码位置

- 模块：`ai4e_contrib.application.pde_control.safediffcon.inference`
- 仓库相对路径：`packages/ai4e-contrib/application/pde_control/safediffcon/inference.py:34`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.pde_control.safediffcon.inference')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-pde-control-safediffcon-inference-generate"></a>
## `ai4e_contrib.application.pde_control.safediffcon.inference.generate`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`generate(cfg: dict, model: torch.nn.Module, values: dict, *, q: float, guide) -> tuple[np.ndarray, np.ndarray]`
- **规范定义名**：`ai4e_contrib.application.pde_control.safediffcon.inference.generate`

### 用途

普通生成不更新参数，逐批保留模型预测与物理控制。

### 导入与签名

```python
from ai4e_contrib.application.pde_control.safediffcon.inference import generate
```

```text
generate(cfg: dict, model: torch.nn.Module, values: dict, *, q: float, guide) -> tuple[np.ndarray, np.ndarray]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cfg` | `dict` | `必填` |
| `model` | `torch.nn.Module` | `必填` |
| `values` | `dict` | `必填` |
| `q` | `float` | `必填关键字参数` |
| `guide` | `未标注` | `必填关键字参数` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`tuple[np.ndarray, np.ndarray]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.application.pde_control.safediffcon.inference import generate

print(signature(generate))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`parametric_pde`, `safediffcon`
- 案例：`parametric_pde.advection`, `parametric_pde.burgers`, `parametric_pde.convection_diffusion`, `parametric_pde.diffusion_trapezoid`, `parametric_pde.neumann_diffusion`, `safediffcon.burgers`, `safediffcon.tokamak`

### 源码位置

- 模块：`ai4e_contrib.application.pde_control.safediffcon.inference`
- 仓库相对路径：`packages/ai4e-contrib/application/pde_control/safediffcon/inference.py:106`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.pde_control.safediffcon.inference')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-pde-control-safediffcon-inference-inputs"></a>
## `ai4e_contrib.application.pde_control.safediffcon.inference.inputs`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`inputs(cfg: dict, prepared: dict) -> dict`
- **规范定义名**：`ai4e_contrib.application.pde_control.safediffcon.inference.inputs`

### 用途

只从显式测试分片选固定前缀，返回模型空间和物理空间两种输入。

### 导入与签名

```python
from ai4e_contrib.application.pde_control.safediffcon.inference import inputs
```

```text
inputs(cfg: dict, prepared: dict) -> dict
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `cfg` | `dict` | `必填` |
| `prepared` | `dict` | `必填` |

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
from ai4e_contrib.application.pde_control.safediffcon.inference import inputs

print(signature(inputs))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `gencp`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `geotransolver/nasa_crm`, `geotransolver/shapenet_car`, `parametric_pde`, `pcno`, `pcno_cylinder`, `safediffcon`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.nasa_crm_geotransolver`, `aero_cfd.nasa_crm_meshgraphnet`, `aero_cfd.nasa_crm_transolver3`, `aero_cfd.shapenet_car_abupt`, `aero_cfd.shapenet_car_geotransolver`, `aero_cfd.shapenet_car_meshgraphnet`, `aero_cfd.shapenet_car_transolver3_surface`, `aero_cfd.shapenet_car_transolver3_volume`, `extension.pcno_cylinder`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `geothermal.pcno`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `parametric_pde.advection`, `parametric_pde.burgers`, `parametric_pde.convection_diffusion`, `parametric_pde.diffusion_trapezoid`, `parametric_pde.neumann_diffusion`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.gencp`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.inference_fields`, `recipe_extensions.sampling`, `recipe_extensions.wdno`, `safediffcon.burgers`, `safediffcon.tokamak`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.application.pde_control.safediffcon.inference`
- 仓库相对路径：`packages/ai4e-contrib/application/pde_control/safediffcon/inference.py:19`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.pde_control.safediffcon.inference')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
