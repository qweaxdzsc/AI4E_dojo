<!-- dojo-help: {"domain": "ai4e_core.abilities.data.save.mesh_dataset", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.data.save.mesh_dataset 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.data.save.mesh_dataset", "topic_id": "module:ai4e_core.abilities.data.save.mesh_dataset"} -->
# `ai4e_core.abilities.data.save.mesh_dataset` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-data-save-mesh-dataset-read-mesh-dataset"></a>
## `ai4e_core.abilities.data.save.mesh_dataset.read_mesh_dataset`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`read_mesh_dataset(path)`
- **规范定义名**：`ai4e_core.abilities.data.save.mesh_dataset.read_mesh_dataset`

### 用途

解析相对样本引用并校验清单摘要，禁止跨目录引用。

### 导入与签名

```python
from ai4e_core.abilities.data.save.mesh_dataset import read_mesh_dataset
```

```text
read_mesh_dataset(path)
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
from ai4e_core.abilities.data.save.mesh_dataset import read_mesh_dataset

print(signature(read_mesh_dataset))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.save.mesh_dataset`
- 仓库相对路径：`packages/ai4e-core/abilities/data/save/mesh_dataset.py:107`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.save.mesh_dataset')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-save-mesh-dataset-read-mesh-sample"></a>
## `ai4e_core.abilities.data.save.mesh_dataset.read_mesh_sample`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`read_mesh_sample(path, *, mesh=False)`
- **规范定义名**：`ai4e_core.abilities.data.save.mesh_dataset.read_mesh_sample`

### 用途

核验逐场摘要与实体数量，返回原物理字段；需要时读网格。

### 导入与签名

```python
from ai4e_core.abilities.data.save.mesh_dataset import read_mesh_sample
```

```text
read_mesh_sample(path, *, mesh=False)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `path` | `未标注` | `必填` |
| `mesh` | `未标注` | `False` |

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
from ai4e_core.abilities.data.save.mesh_dataset import read_mesh_sample

print(signature(read_mesh_sample))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.save.mesh_dataset`
- 仓库相对路径：`packages/ai4e-core/abilities/data/save/mesh_dataset.py:67`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.save.mesh_dataset')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-save-mesh-dataset-save-mesh-sample"></a>
## `ai4e_core.abilities.data.save.mesh_dataset.save_mesh_sample`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`save_mesh_sample(directory, mesh, *, metadata: dict)`
- **规范定义名**：`ai4e_core.abilities.data.save.mesh_dataset.save_mesh_sample`

### 用途

原子提交完整网格与原始 point/cell 字段；不转换字段关联。

### 导入与签名

```python
from ai4e_core.abilities.data.save.mesh_dataset import save_mesh_sample
```

```text
save_mesh_sample(directory, mesh, *, metadata: dict)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `directory` | `未标注` | `必填` |
| `mesh` | `未标注` | `必填` |
| `metadata` | `dict` | `必填关键字参数` |

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
from ai4e_core.abilities.data.save.mesh_dataset import save_mesh_sample

print(signature(save_mesh_sample))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.save.mesh_dataset`
- 仓库相对路径：`packages/ai4e-core/abilities/data/save/mesh_dataset.py:15`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.save.mesh_dataset')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
