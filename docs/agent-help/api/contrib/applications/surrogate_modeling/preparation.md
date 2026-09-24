<!-- dojo-help: {"domain": "ai4e_contrib.application.surrogate_modeling.preparation", "kind": "api", "layer": "contrib.application", "summary": "ai4e_contrib.application.surrogate_modeling.preparation 的完整源码参考与公开符号索引。", "title": "ai4e_contrib.application.surrogate_modeling.preparation", "topic_id": "module:ai4e_contrib.application.surrogate_modeling.preparation"} -->
# `ai4e_contrib.application.surrogate_modeling.preparation` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-contrib-application-surrogate-modeling-preparation-preparation-identity"></a>
## `ai4e_contrib.application.surrogate_modeling.preparation.preparation_identity`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`preparation_identity(path)`
- **规范定义名**：`ai4e_contrib.application.surrogate_modeling.preparation.preparation_identity`

### 用途

绑定准备及其子清单内容，移动整个目录不改变身份。

子清单自身记录数组摘要，实际读入仍由 read_arrays 校验数组内容。
这里不只摘要顶层索引，避免同名分片或 POD 被替换后仍误认为原准备。

### 导入与签名

```python
from ai4e_contrib.application.surrogate_modeling.preparation import preparation_identity
```

```text
preparation_identity(path)
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
from ai4e_contrib.application.surrogate_modeling.preparation import preparation_identity

print(signature(preparation_identity))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`surrogate_modeling/double_cylinder`, `surrogate_modeling/nasa_crm`
- 案例：`surrogate_modeling.double_cylinder`, `surrogate_modeling.nasa_crm`

### 源码位置

- 模块：`ai4e_contrib.application.surrogate_modeling.preparation`
- 仓库相对路径：`packages/ai4e-contrib/application/surrogate_modeling/preparation.py:340`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.surrogate_modeling.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-surrogate-modeling-preparation-prepare-nasa"></a>
## `ai4e_contrib.application.surrogate_modeling.preparation.prepare_nasa`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`prepare_nasa(train_h5, test_h5, output)`
- **规范定义名**：`ai4e_contrib.application.surrogate_modeling.preparation.prepare_nasa`

### 用途

读取全局属性表，训练独立拟合统计，保存自包含准备清单。

不读取或复制百万点网格；本产物不是平台物理网格准备。不同来源文件中的
同名 Sample 保留 source_id 与 split，不因为组名相同合并实体。

### 导入与签名

```python
from ai4e_contrib.application.surrogate_modeling.preparation import prepare_nasa
```

```text
prepare_nasa(train_h5, test_h5, output)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `train_h5` | `未标注` | `必填` |
| `test_h5` | `未标注` | `必填` |
| `output` | `未标注` | `必填` |

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
from ai4e_contrib.application.surrogate_modeling.preparation import prepare_nasa

print(signature(prepare_nasa))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`surrogate_modeling/nasa_crm`
- 案例：`surrogate_modeling.nasa_crm`

### 源码位置

- 模块：`ai4e_contrib.application.surrogate_modeling.preparation`
- 仓库相对路径：`packages/ai4e-contrib/application/surrogate_modeling/preparation.py:74`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.surrogate_modeling.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-surrogate-modeling-preparation-prepare-pod-data"></a>
## `ai4e_contrib.application.surrogate_modeling.preparation.prepare_pod_data`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`prepare_pod_data(classic_manifest, output, rank=2)`
- **规范定义名**：`ai4e_contrib.application.surrogate_modeling.preparation.prepare_pod_data`

### 用途

一次拟合训练快照 POD 并物化系数；真实调用由主控串行调度。

历史和未来都使用训练 target 通道统计，绝不使用 classic 的 input 统计。
每个 trajectory/time 只进入 POD 一次；重复引用若数值不同则拒绝。
输出包含独立基状态及物理目标/身份，无需旧准备目录即可恢复推理和后处理。

### 导入与签名

```python
from ai4e_contrib.application.surrogate_modeling.preparation import prepare_pod_data
```

```text
prepare_pod_data(classic_manifest, output, rank=2)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `classic_manifest` | `未标注` | `必填` |
| `output` | `未标注` | `必填` |
| `rank` | `未标注` | `2` |

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
from ai4e_contrib.application.surrogate_modeling.preparation import prepare_pod_data

print(signature(prepare_pod_data))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`surrogate_modeling/double_cylinder`
- 案例：`surrogate_modeling.double_cylinder`

### 源码位置

- 模块：`ai4e_contrib.application.surrogate_modeling.preparation`
- 仓库相对路径：`packages/ai4e-contrib/application/surrogate_modeling/preparation.py:185`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.surrogate_modeling.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-surrogate-modeling-preparation-read-pod"></a>
## `ai4e_contrib.application.surrogate_modeling.preparation.read_pod`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`read_pod(path)`
- **规范定义名**：`ai4e_contrib.application.surrogate_modeling.preparation.read_pod`

### 用途

从准备目录内部读取同一次冻结 POD 状态及其语义。

### 导入与签名

```python
from ai4e_contrib.application.surrogate_modeling.preparation import read_pod
```

```text
read_pod(path)
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
from ai4e_contrib.application.surrogate_modeling.preparation import read_pod

print(signature(read_pod))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_contrib.application.surrogate_modeling.preparation`
- 仓库相对路径：`packages/ai4e-contrib/application/surrogate_modeling/preparation.py:330`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.surrogate_modeling.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-contrib-application-surrogate-modeling-preparation-read-prepared"></a>
## `ai4e_contrib.application.surrogate_modeling.preparation.read_prepared`

- **层级**：`contrib.application`
- **稳定性**：`extension`
- **定义**：`read_prepared(path, split)`
- **规范定义名**：`ai4e_contrib.application.surrogate_modeling.preparation.read_prepared`

### 用途

读取自包含拟合输入，不返回旧来源的可执行引用。

### 导入与签名

```python
from ai4e_contrib.application.surrogate_modeling.preparation import read_prepared
```

```text
read_prepared(path, split)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `未标注` | `必填` |
| `split` | `未标注` | `必填` |

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
from ai4e_contrib.application.surrogate_modeling.preparation import read_prepared

print(signature(read_prepared))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：`classic_networks/darcy`, `classic_networks/double_cylinder`, `classic_networks/shapenet_volume`, `operator_learning/darcy`, `operator_learning/double_cylinder`, `operator_learning/shapenet_volume`, `surrogate_modeling/double_cylinder`, `surrogate_modeling/nasa_crm`
- 案例：`classic_networks.darcy`, `classic_networks.double_cylinder`, `classic_networks.shapenet_volume`, `operator_learning.darcy`, `operator_learning.double_cylinder`, `operator_learning.shapenet_volume`, `surrogate_modeling.double_cylinder`, `surrogate_modeling.nasa_crm`

### 源码位置

- 模块：`ai4e_contrib.application.surrogate_modeling.preparation`
- 仓库相对路径：`packages/ai4e-contrib/application/surrogate_modeling/preparation.py:316`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_contrib')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_contrib.application.surrogate_modeling.preparation')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
