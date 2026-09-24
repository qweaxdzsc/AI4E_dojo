<!-- dojo-help: {"domain": "ai4e_contrib.application.surrogate_modeling.prediction", "kind": "api", "layer": "contrib.application", "summary": "ai4e_contrib.application.surrogate_modeling.prediction 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.application.surrogate_modeling.prediction", "topic_id": "module:ai4e_contrib.application.surrogate_modeling.prediction"} -->
# `ai4e_contrib.application.surrogate_modeling.prediction` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-application-surrogate-modeling-prediction-independentkriging"></a>
## `ai4e_contrib.application.surrogate_modeling.prediction.IndependentKriging`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`IndependentKriging(state)`
- **规范定义名**：`ai4e_contrib.application.surrogate_modeling.prediction.IndependentKriging`

### 用途

局部多输出连接；每列独立后验，不构造虚假的目标间协方差。

### 导入与签名

```python
from ai4e_contrib.application.surrogate_modeling.prediction import IndependentKriging
```

```text
IndependentKriging(state)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `state` | `未标注` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`IndependentKriging`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_contrib.application.surrogate_modeling.prediction import IndependentKriging

print(signature(IndependentKriging))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.surrogate_modeling.prediction`
- 仓库相对路径：`packages/ai4e-contrib/application/surrogate_modeling/prediction.py:14`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.surrogate_modeling.prediction')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-surrogate-modeling-prediction-independentkriging-get-state"></a>
## `ai4e_contrib.application.surrogate_modeling.prediction.IndependentKriging.get_state`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`get_state(self)`
- **规范定义名**：`ai4e_contrib.application.surrogate_modeling.prediction.IndependentKriging.get_state`

### 用途

返回独立的完整多目标状态。

### 导入与签名

```python
from ai4e_contrib.application.surrogate_modeling.prediction import IndependentKriging
```

```text
get_state(self)
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
from ai4e_contrib.application.surrogate_modeling.prediction import IndependentKriging

print(signature(IndependentKriging.get_state))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.surrogate_modeling.prediction`
- 仓库相对路径：`packages/ai4e-contrib/application/surrogate_modeling/prediction.py:38`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.surrogate_modeling.prediction')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-surrogate-modeling-prediction-independentkriging-predict"></a>
## `ai4e_contrib.application.surrogate_modeling.prediction.IndependentKriging.predict`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`predict(self, x, *, return_variance=False)`
- **规范定义名**：`ai4e_contrib.application.surrogate_modeling.prediction.IndependentKriging.predict`

### 用途

输出 [N,q] 均值，按需附 [N,q] 独立边际方差。

### 导入与签名

```python
from ai4e_contrib.application.surrogate_modeling.prediction import IndependentKriging
```

```text
predict(self, x, *, return_variance=False)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `x` | `未标注` | `必填` |
| `return_variance` | `未标注` | `False` |

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
from ai4e_contrib.application.surrogate_modeling.prediction import IndependentKriging

print(signature(IndependentKriging.predict))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`aero_cfd`, `pcno_cylinder`, `surrogate_modeling/double_cylinder`, `surrogate_modeling/nasa_crm`, `wdno`
- 案例：`aero_cfd.nasa_crm_abupt`, `aero_cfd.shapenet_car_abupt`, `pcno.double_cylinder`, `recipe_extensions.field_mapping`, `recipe_extensions.geotransolver_aero`, `recipe_extensions.pod_surrogate_replacement`, `recipe_extensions.sampling`, `recipe_extensions.wdno`, `surrogate_modeling.double_cylinder`, `surrogate_modeling.nasa_crm`, `wdno.burgers_base`

### 源码位置

- 模块：`ai4e_contrib.application.surrogate_modeling.prediction`
- 仓库相对路径：`packages/ai4e-contrib/application/surrogate_modeling/prediction.py:29`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.surrogate_modeling.prediction')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-surrogate-modeling-prediction-predict-prepared"></a>
## `ai4e_contrib.application.surrogate_modeling.prediction.predict_prepared`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`predict_prepared(state, prepared, output, *, split='test', batch_size=256, predictor=None)`
- **规范定义名**：`ai4e_contrib.application.surrogate_modeling.prediction.predict_prepared`

### 用途

读取准备并预测，反变换后交付 classic-results-v1 供固定 post 评价。

普通批量入口只沿真实样本轴切分。POD 解码只读取准备自身的固定基，不回读
原 HDF5 或旧准备目录；本函数不拟合，也不调用神经模型 eval/to 等接口。
predictor 可为调用方由普通状态重建的对象，无需添加框架注册条目。

### 导入与签名

```python
from ai4e_contrib.application.surrogate_modeling.prediction import predict_prepared
```

```text
predict_prepared(state, prepared, output, *, split='test', batch_size=256, predictor=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `state` | `未标注` | `必填` |
| `prepared` | `未标注` | `必填` |
| `output` | `未标注` | `必填` |
| `split` | `未标注` | `'test'` |
| `batch_size` | `未标注` | `256` |
| `predictor` | `未标注` | `None` |

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
from ai4e_contrib.application.surrogate_modeling.prediction import predict_prepared

print(signature(predict_prepared))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`surrogate_modeling/double_cylinder`, `surrogate_modeling/nasa_crm`
- 案例：`surrogate_modeling.double_cylinder`, `surrogate_modeling.nasa_crm`

### 源码位置

- 模块：`ai4e_contrib.application.surrogate_modeling.prediction`
- 仓库相对路径：`packages/ai4e-contrib/application/surrogate_modeling/prediction.py:63`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.surrogate_modeling.prediction')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-surrogate-modeling-prediction-rebuild"></a>
## `ai4e_contrib.application.surrogate_modeling.prediction.rebuild`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`rebuild(state)`
- **规范定义名**：`ai4e_contrib.application.surrogate_modeling.prediction.rebuild`

### 用途

按本应用明确支持的状态重建普通对象，不动态执行任意类路径。

### 导入与签名

```python
from ai4e_contrib.application.surrogate_modeling.prediction import rebuild
```

```text
rebuild(state)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `state` | `未标注` | `必填` |

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
from ai4e_contrib.application.surrogate_modeling.prediction import rebuild

print(signature(rebuild))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`surrogate_modeling/double_cylinder`, `surrogate_modeling/nasa_crm`
- 案例：`recipe_extensions.pod_surrogate_replacement`, `surrogate_modeling.double_cylinder`, `surrogate_modeling.nasa_crm`

### 源码位置

- 模块：`ai4e_contrib.application.surrogate_modeling.prediction`
- 仓库相对路径：`packages/ai4e-contrib/application/surrogate_modeling/prediction.py:43`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.surrogate_modeling.prediction')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
