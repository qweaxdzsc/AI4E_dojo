<!-- dojo-help: {"domain": "ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure", "kind": "api", "layer": "contrib.ability", "summary": "ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure", "topic_id": "module:ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure"} -->
# `ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-common-model-structure-sb2-ensemble"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.SB2_ensemble`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`SB2_ensemble(model_list, low_state, high_state, low_action, high_action, activation='relu', last_actv='tanh', norm=True, bavg=0.0)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.SB2_ensemble`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import SB2_ensemble
```

```text
SB2_ensemble(model_list, low_state, high_state, low_action, high_action, activation='relu', last_actv='tanh', norm=True, bavg=0.0)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model_list` | `未标注` | `必填` |
| `low_state` | `未标注` | `必填` |
| `high_state` | `未标注` | `必填` |
| `low_action` | `未标注` | `必填` |
| `high_action` | `未标注` | `必填` |
| `activation` | `未标注` | `'relu'` |
| `last_actv` | `未标注` | `'tanh'` |
| `norm` | `未标注` | `True` |
| `bavg` | `未标注` | `0.0` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`SB2_ensemble`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import SB2_ensemble

print(signature(SB2_ensemble))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar_common/model_structure.py:207`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-common-model-structure-sb2-ensemble-predict"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.SB2_ensemble.predict`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`predict(self, x, yold=None)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.SB2_ensemble.predict`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import SB2_ensemble
```

```text
predict(self, x, yold=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `yold` | `未标注` | `None` |

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
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import SB2_ensemble

print(signature(SB2_ensemble.predict))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `pcno_cylinder`, `surrogate_modeling/double_cylinder`, `surrogate_modeling/nasa_crm`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.shapenet_car_abupt`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.pod_surrogate_replacement`, `recipe_extensions.sampling`, `recipe_extensions.wdno`, `surrogate_modeling.double_cylinder`, `surrogate_modeling.nasa_crm`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar_common/model_structure.py:211`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-common-model-structure-sb2-model"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.SB2_model`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`SB2_model(model_path, low_state, high_state, low_action, high_action, activation='relu', last_actv='tanh', norm=True, bavg=0.0)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.SB2_model`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import SB2_model
```

```text
SB2_model(model_path, low_state, high_state, low_action, high_action, activation='relu', last_actv='tanh', norm=True, bavg=0.0)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model_path` | `未标注` | `必填` |
| `low_state` | `未标注` | `必填` |
| `high_state` | `未标注` | `必填` |
| `low_action` | `未标注` | `必填` |
| `high_action` | `未标注` | `必填` |
| `activation` | `未标注` | `'relu'` |
| `last_actv` | `未标注` | `'tanh'` |
| `norm` | `未标注` | `True` |
| `bavg` | `未标注` | `0.0` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`SB2_model`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import SB2_model

print(signature(SB2_model))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar_common/model_structure.py:179`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-common-model-structure-sb2-model-predict"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.SB2_model.predict`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`predict(self, x, yold=None)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.SB2_model.predict`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import SB2_model
```

```text
predict(self, x, yold=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `yold` | `未标注` | `None` |

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
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import SB2_model

print(signature(SB2_model.predict))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `pcno_cylinder`, `surrogate_modeling/double_cylinder`, `surrogate_modeling/nasa_crm`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.shapenet_car_abupt`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.pod_surrogate_replacement`, `recipe_extensions.sampling`, `recipe_extensions.wdno`, `surrogate_modeling.double_cylinder`, `surrogate_modeling.nasa_crm`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar_common/model_structure.py:192`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-common-model-structure-actv"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.actv`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`actv(x, method)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.actv`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import actv
```

```text
actv(x, method)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `method` | `未标注` | `必填` |

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
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import actv

print(signature(actv))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar_common/model_structure.py:169`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-common-model-structure-bpw-nn"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.bpw_nn`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`bpw_nn(model_path, n_models=1)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.bpw_nn`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import bpw_nn
```

```text
bpw_nn(model_path, n_models=1)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model_path` | `未标注` | `必填` |
| `n_models` | `未标注` | `1` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`bpw_nn`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import bpw_nn

print(signature(bpw_nn))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar_common/model_structure.py:139`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-common-model-structure-bpw-nn-predict"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.bpw_nn.predict`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`predict(self, x=None)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.bpw_nn.predict`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import bpw_nn
```

```text
predict(self, x=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `None` |

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
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import bpw_nn

print(signature(bpw_nn.predict))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `pcno_cylinder`, `surrogate_modeling/double_cylinder`, `surrogate_modeling/nasa_crm`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.shapenet_car_abupt`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.pod_surrogate_replacement`, `recipe_extensions.sampling`, `recipe_extensions.wdno`, `surrogate_modeling.double_cylinder`, `surrogate_modeling.nasa_crm`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar_common/model_structure.py:149`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-common-model-structure-bpw-nn-set-inputs"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.bpw_nn.set_inputs`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`set_inputs(self, x)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.bpw_nn.set_inputs`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import bpw_nn
```

```text
set_inputs(self, x)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |

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
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import bpw_nn

print(signature(bpw_nn.set_inputs))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar_common/model_structure.py:146`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-common-model-structure-k2rz"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.k2rz`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`k2rz(model_path, n_models=1, ntheta=64, closed_surface=True, xpt_correction=True)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.k2rz`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import k2rz
```

```text
k2rz(model_path, n_models=1, ntheta=64, closed_surface=True, xpt_correction=True)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model_path` | `未标注` | `必填` |
| `n_models` | `未标注` | `1` |
| `ntheta` | `未标注` | `64` |
| `closed_surface` | `未标注` | `True` |
| `xpt_correction` | `未标注` | `True` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`k2rz`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import k2rz

print(signature(k2rz))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar_common/model_structure.py:6`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-common-model-structure-k2rz-predict"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.k2rz.predict`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`predict(self, post=True)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.k2rz.predict`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import k2rz
```

```text
predict(self, post=True)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `post` | `未标注` | `True` |

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
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import k2rz

print(signature(k2rz.predict))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `pcno_cylinder`, `surrogate_modeling/double_cylinder`, `surrogate_modeling/nasa_crm`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.shapenet_car_abupt`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.pod_surrogate_replacement`, `recipe_extensions.sampling`, `recipe_extensions.wdno`, `surrogate_modeling.double_cylinder`, `surrogate_modeling.nasa_crm`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar_common/model_structure.py:15`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-common-model-structure-k2rz-set-inputs"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.k2rz.set_inputs`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`set_inputs(self, ip, bt, βp, rin, rout, k, du, dl)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.k2rz.set_inputs`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import k2rz
```

```text
set_inputs(self, ip, bt, βp, rin, rout, k, du, dl)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `ip` | `未标注` | `必填` |
| `bt` | `未标注` | `必填` |
| `βp` | `未标注` | `必填` |
| `rin` | `未标注` | `必填` |
| `rout` | `未标注` | `必填` |
| `k` | `未标注` | `必填` |
| `du` | `未标注` | `必填` |
| `dl` | `未标注` | `必填` |

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
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import k2rz

print(signature(k2rz.set_inputs))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar_common/model_structure.py:12`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-common-model-structure-kstar-lstm"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.kstar_lstm`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`kstar_lstm(model_path, n_models=1, ymean=None, ystd=None)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.kstar_lstm`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import kstar_lstm
```

```text
kstar_lstm(model_path, n_models=1, ymean=None, ystd=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model_path` | `未标注` | `必填` |
| `n_models` | `未标注` | `1` |
| `ymean` | `未标注` | `None` |
| `ystd` | `未标注` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`kstar_lstm`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import kstar_lstm

print(signature(kstar_lstm))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar_common/model_structure.py:82`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-common-model-structure-kstar-lstm-predict"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.kstar_lstm.predict`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`predict(self, x=None)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.kstar_lstm.predict`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import kstar_lstm
```

```text
predict(self, x=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `None` |

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
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import kstar_lstm

print(signature(kstar_lstm.predict))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `pcno_cylinder`, `surrogate_modeling/double_cylinder`, `surrogate_modeling/nasa_crm`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.shapenet_car_abupt`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.pod_surrogate_replacement`, `recipe_extensions.sampling`, `recipe_extensions.wdno`, `surrogate_modeling.double_cylinder`, `surrogate_modeling.nasa_crm`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar_common/model_structure.py:95`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-common-model-structure-kstar-lstm-set-inputs"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.kstar_lstm.set_inputs`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`set_inputs(self, x)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.kstar_lstm.set_inputs`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import kstar_lstm
```

```text
set_inputs(self, x)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |

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
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import kstar_lstm

print(signature(kstar_lstm.set_inputs))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar_common/model_structure.py:92`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-common-model-structure-kstar-nn"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.kstar_nn`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`kstar_nn(model_path, n_models=1, ymean=None, ystd=None)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.kstar_nn`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import kstar_nn
```

```text
kstar_nn(model_path, n_models=1, ymean=None, ystd=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model_path` | `未标注` | `必填` |
| `n_models` | `未标注` | `1` |
| `ymean` | `未标注` | `None` |
| `ystd` | `未标注` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`kstar_nn`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import kstar_nn

print(signature(kstar_nn))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar_common/model_structure.py:120`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-common-model-structure-kstar-nn-predict"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.kstar_nn.predict`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`predict(self, x=None)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.kstar_nn.predict`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import kstar_nn
```

```text
predict(self, x=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `None` |

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
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import kstar_nn

print(signature(kstar_nn.predict))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `pcno_cylinder`, `surrogate_modeling/double_cylinder`, `surrogate_modeling/nasa_crm`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.shapenet_car_abupt`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.pod_surrogate_replacement`, `recipe_extensions.sampling`, `recipe_extensions.wdno`, `surrogate_modeling.double_cylinder`, `surrogate_modeling.nasa_crm`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar_common/model_structure.py:133`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-common-model-structure-kstar-nn-set-inputs"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.kstar_nn.set_inputs`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`set_inputs(self, x)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.kstar_nn.set_inputs`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import kstar_nn
```

```text
set_inputs(self, x)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |

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
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import kstar_nn

print(signature(kstar_nn.set_inputs))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar_common/model_structure.py:130`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-common-model-structure-kstar-v220505"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.kstar_v220505`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`kstar_v220505(model_path, n_models=1, ymean=None, ystd=None, length=10)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.kstar_v220505`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import kstar_v220505
```

```text
kstar_v220505(model_path, n_models=1, ymean=None, ystd=None, length=10)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model_path` | `未标注` | `必填` |
| `n_models` | `未标注` | `1` |
| `ymean` | `未标注` | `None` |
| `ystd` | `未标注` | `None` |
| `length` | `未标注` | `10` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`kstar_v220505`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import kstar_v220505

print(signature(kstar_v220505))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar_common/model_structure.py:101`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-common-model-structure-kstar-v220505-predict"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.kstar_v220505.predict`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`predict(self, x=None)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.kstar_v220505.predict`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import kstar_v220505
```

```text
predict(self, x=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `None` |

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
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import kstar_v220505

print(signature(kstar_v220505.predict))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `pcno_cylinder`, `surrogate_modeling/double_cylinder`, `surrogate_modeling/nasa_crm`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.shapenet_car_abupt`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.pod_surrogate_replacement`, `recipe_extensions.sampling`, `recipe_extensions.wdno`, `surrogate_modeling.double_cylinder`, `surrogate_modeling.nasa_crm`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar_common/model_structure.py:114`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-common-model-structure-kstar-v220505-set-inputs"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.kstar_v220505.set_inputs`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`set_inputs(self, x)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.kstar_v220505.set_inputs`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import kstar_v220505
```

```text
set_inputs(self, x)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |

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
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import kstar_v220505

print(signature(kstar_v220505.set_inputs))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar_common/model_structure.py:111`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-common-model-structure-load-custom-model"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.load_custom_model`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`load_custom_model(input_shape, lstms, denses, model_path)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.load_custom_model`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import load_custom_model
```

```text
load_custom_model(input_shape, lstms, denses, model_path)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `input_shape` | `未标注` | `必填` |
| `lstms` | `未标注` | `必填` |
| `denses` | `未标注` | `必填` |
| `model_path` | `未标注` | `必填` |

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
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import load_custom_model

print(signature(load_custom_model))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar_common/model_structure.py:68`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-common-model-structure-tf-dense-model"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.tf_dense_model`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`tf_dense_model(model_path, n_models=1, ymean=0, ystd=1)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.tf_dense_model`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import tf_dense_model
```

```text
tf_dense_model(model_path, n_models=1, ymean=0, ystd=1)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model_path` | `未标注` | `必填` |
| `n_models` | `未标注` | `1` |
| `ymean` | `未标注` | `0` |
| `ystd` | `未标注` | `1` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`tf_dense_model`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import tf_dense_model

print(signature(tf_dense_model))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar_common/model_structure.py:155`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-common-model-structure-tf-dense-model-predict"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.tf_dense_model.predict`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`predict(self, x)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.tf_dense_model.predict`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import tf_dense_model
```

```text
predict(self, x)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |

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
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import tf_dense_model

print(signature(tf_dense_model.predict))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `pcno_cylinder`, `surrogate_modeling/double_cylinder`, `surrogate_modeling/nasa_crm`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.shapenet_car_abupt`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.pod_surrogate_replacement`, `recipe_extensions.sampling`, `recipe_extensions.wdno`, `surrogate_modeling.double_cylinder`, `surrogate_modeling.nasa_crm`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar_common/model_structure.py:164`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-common-model-structure-tf-dense-model-set-inputs"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.tf_dense_model.set_inputs`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`set_inputs(self, x)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.tf_dense_model.set_inputs`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import tf_dense_model
```

```text
set_inputs(self, x)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |

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
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import tf_dense_model

print(signature(tf_dense_model.set_inputs))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar_common/model_structure.py:161`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-common-model-structure-x2rz"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.x2rz`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`x2rz(model_path, n_models=1, ntheta=64, closed_surface=True, xpt_correction=True)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.x2rz`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import x2rz
```

```text
x2rz(model_path, n_models=1, ntheta=64, closed_surface=True, xpt_correction=True)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `model_path` | `未标注` | `必填` |
| `n_models` | `未标注` | `1` |
| `ntheta` | `未标注` | `64` |
| `closed_surface` | `未标注` | `True` |
| `xpt_correction` | `未标注` | `True` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`x2rz`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import x2rz

print(signature(x2rz))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar_common/model_structure.py:41`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-common-model-structure-x2rz-predict"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.x2rz.predict`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`predict(self, post=True)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.x2rz.predict`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import x2rz
```

```text
predict(self, post=True)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `post` | `未标注` | `True` |

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
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import x2rz

print(signature(x2rz.predict))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `pcno_cylinder`, `surrogate_modeling/double_cylinder`, `surrogate_modeling/nasa_crm`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.shapenet_car_abupt`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.pod_surrogate_replacement`, `recipe_extensions.sampling`, `recipe_extensions.wdno`, `surrogate_modeling.double_cylinder`, `surrogate_modeling.nasa_crm`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar_common/model_structure.py:50`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-ability-postproc-safediffcon-kstar-common-model-structure-x2rz-set-inputs"></a>
## `ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.x2rz.set_inputs`

- **层级**：`contrib.ability`
- **稳定性**：`extension`
- **定义**：`set_inputs(self, ip, bt, βp, rx1, zx1, rx2, zx2, drsep, rin, rout)`
- **规范定义名**：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure.x2rz.set_inputs`

### 用途

源码未提供 Docstring。

### 导入与签名

```python
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import x2rz
```

```text
set_inputs(self, ip, bt, βp, rx1, zx1, rx2, zx2, drsep, rin, rout)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `ip` | `未标注` | `必填` |
| `bt` | `未标注` | `必填` |
| `βp` | `未标注` | `必填` |
| `rx1` | `未标注` | `必填` |
| `zx1` | `未标注` | `必填` |
| `rx2` | `未标注` | `必填` |
| `zx2` | `未标注` | `必填` |
| `drsep` | `未标注` | `必填` |
| `rin` | `未标注` | `必填` |
| `rout` | `未标注` | `必填` |

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
from ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure import x2rz

print(signature(x2rz.set_inputs))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure`
- 仓库相对路径：`packages/ai4e-contrib/ability/postproc/safediffcon/kstar_common/model_structure.py:47`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.ability.postproc.safediffcon.kstar_common.model_structure')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
