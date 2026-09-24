<!-- dojo-help: {"domain": "ai4e_contrib.application.spatiotemporal_pde.wdno.model", "kind": "api", "layer": "contrib.application", "summary": "ai4e_contrib.application.spatiotemporal_pde.wdno.model 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.application.spatiotemporal_pde.wdno.model", "topic_id": "module:ai4e_contrib.application.spatiotemporal_pde.wdno.model"} -->
# `ai4e_contrib.application.spatiotemporal_pde.wdno.model` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-application-spatiotemporal-pde-wdno-model-diffusion"></a>
## `ai4e_contrib.application.spatiotemporal_pde.wdno.model.diffusion`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`diffusion(options: dict, construct=network)`
- **规范定义名**：`ai4e_contrib.application.spatiotemporal_pde.wdno.model.diffusion`

### 用途

小波/通道/条件语义在局部连接声明，不让训练循环解释。

### 导入与签名

```python
from ai4e_contrib.application.spatiotemporal_pde.wdno.model import diffusion
```

```text
diffusion(options: dict, construct=network)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `options` | `dict` | `必填` |
| `construct` | `未标注` | `network` |

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
from ai4e_contrib.application.spatiotemporal_pde.wdno.model import diffusion

print(signature(diffusion))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.spatiotemporal_pde.wdno.model`
- 仓库相对路径：`packages/ai4e-contrib/application/spatiotemporal_pde/wdno/model.py:19`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.spatiotemporal_pde.wdno.model')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-spatiotemporal-pde-wdno-model-network"></a>
## `ai4e_contrib.application.spatiotemporal_pde.wdno.model.network`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`network(options: dict)`
- **规范定义名**：`ai4e_contrib.application.spatiotemporal_pde.wdno.model.network`

### 用途

构造可替换去噪网络，参数名称沿用作者实现。

### 导入与签名

```python
from ai4e_contrib.application.spatiotemporal_pde.wdno.model import network
```

```text
network(options: dict)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `options` | `dict` | `必填` |

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
from ai4e_contrib.application.spatiotemporal_pde.wdno.model import network

print(signature(network))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`pcno`, `pcno_cylinder`, `wdno`
- 案例：`extension.pcno`, `extension.pcno_cylinder`, `geothermal.pcno`, `pcno.double_cylinder`, `recipe_extensions.network_composition.resunet`, `recipe_extensions.network_composition.unet_transformer`, `recipe_extensions.pod_surrogate_replacement`, `recipe_extensions.safediffcon`, `recipe_extensions.wdno`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.application.spatiotemporal_pde.wdno.model`
- 仓库相对路径：`packages/ai4e-contrib/application/spatiotemporal_pde/wdno/model.py:8`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.spatiotemporal_pde.wdno.model')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-spatiotemporal-pde-wdno-model-objective"></a>
## `ai4e_contrib.application.spatiotemporal_pde.wdno.model.objective`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`objective(model, values)`
- **规范定义名**：`ai4e_contrib.application.spatiotemporal_pde.wdno.model.objective`

### 用途

默认目标调用原条件扩散算术，允许 recipe 直接替换。

### 导入与签名

```python
from ai4e_contrib.application.spatiotemporal_pde.wdno.model import objective
```

```text
objective(model, values)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model` | `未标注` | `必填` |
| `values` | `未标注` | `必填` |

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
from ai4e_contrib.application.spatiotemporal_pde.wdno.model import objective

print(signature(objective))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `gencp`, `geotransolver/bumper_beam`, `geotransolver/darcy`, `pcno`, `safediffcon`, `wdno`
- 案例：`classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `gencp.double_cylinder_cno`, `gencp.double_cylinder_sit_fno`, `gencp.ntcouple_cno`, `gencp.ntcouple_sit_fno`, `gencp.turek_hron_cno`, `gencp.turek_hron_sit_fno`, `geothermal.pcno`, `geotransolver.bumper_beam`, `geotransolver.darcy`, `recipe_extensions.geotransolver`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.pod_surrogate_replacement`, `recipe_extensions.research_state`, `recipe_extensions.safediffcon`, `recipe_extensions.tail_batch`, `recipe_extensions.task_labels`, `recipe_extensions.wdno`, `safediffcon.burgers`, `safediffcon.tokamak`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.application.spatiotemporal_pde.wdno.model`
- 仓库相对路径：`packages/ai4e-contrib/application/spatiotemporal_pde/wdno/model.py:44`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.spatiotemporal_pde.wdno.model')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
