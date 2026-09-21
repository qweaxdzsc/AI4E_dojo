<!-- dojo-help: {"domain": "ai4e_core.applications.aero_cfd.infer.mesh", "kind": "api", "layer": "core.application", "summary": "ai4e_core.applications.aero_cfd.infer.mesh 的完整源码参考与公开符号索引。", "title": "ai4e_core.applications.aero_cfd.infer.mesh", "topic_id": "module:ai4e_core.applications.aero_cfd.infer.mesh"} -->
# `ai4e_core.applications.aero_cfd.infer.mesh` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-applications-aero-cfd-infer-mesh-prepare-fixed-inputs"></a>
## `ai4e_core.applications.aero_cfd.infer.mesh.prepare_fixed_inputs`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`prepare_fixed_inputs(config, restored, *, prepare_inputs, collate, split: str, item: int)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.infer.mesh.prepare_fixed_inputs`

### 用途

用训练评估同一入口准备几何和锚点，去掉预填充不允许的查询坐标。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.infer.mesh import prepare_fixed_inputs
```

```text
prepare_fixed_inputs(config, restored, *, prepare_inputs, collate, split: str, item: int)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `未标注` | `必填` |
| `restored` | `未标注` | `必填` |
| `prepare_inputs` | `未标注` | `必填关键字参数` |
| `collate` | `未标注` | `必填关键字参数` |
| `split` | `str` | `必填关键字参数` |
| `item` | `int` | `必填关键字参数` |

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
from ai4e_core.applications.aero_cfd.infer.mesh import prepare_fixed_inputs

print(signature(prepare_fixed_inputs))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.infer.mesh`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/infer/mesh.py:183`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.infer.mesh')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-infer-mesh-query-meshes"></a>
## `ai4e_core.applications.aero_cfd.infer.mesh.query_meshes`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`query_meshes(config, run, restored, *, prepare_inputs, collate, context_factory, progress=None, protocol=None)`
- **规范定义名**：`ai4e_core.applications.aero_cfd.infer.mesh.query_meshes`

### 用途

按测试下标查询原始顶点并提交表面/体积网格。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.infer.mesh import query_meshes
```

```text
query_meshes(config, run, restored, *, prepare_inputs, collate, context_factory, progress=None, protocol=None)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `未标注` | `必填` |
| `run` | `未标注` | `必填` |
| `restored` | `未标注` | `必填` |
| `prepare_inputs` | `未标注` | `必填关键字参数` |
| `collate` | `未标注` | `必填关键字参数` |
| `context_factory` | `未标注` | `必填关键字参数` |
| `progress` | `未标注` | `None` |
| `protocol` | `未标注` | `None` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`未标注`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FileNotFoundError`, `IndexError`, `ValueError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.infer.mesh import query_meshes

print(signature(query_meshes))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.infer.mesh`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/infer/mesh.py:37`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.infer.mesh')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-applications-aero-cfd-infer-mesh-raw-mesh-paths"></a>
## `ai4e_core.applications.aero_cfd.infer.mesh.raw_mesh_paths`

- **层级**：`core.application`
- **稳定性**：`extension`
- **定义**：`raw_mesh_paths(config, sample_id: str) -> tuple[Path, Path]`
- **规范定义名**：`ai4e_core.applications.aero_cfd.infer.mesh.raw_mesh_paths`

### 用途

按原始数据根和设计号拼表面、体积文件；平台路径可来自绑定来源。

### 导入与签名

```python
from ai4e_core.applications.aero_cfd.infer.mesh import raw_mesh_paths
```

```text
raw_mesh_paths(config, sample_id: str) -> tuple[Path, Path]
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `config` | `未标注` | `必填` |
| `sample_id` | `str` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`tuple[Path, Path]`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FileNotFoundError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.applications.aero_cfd.infer.mesh import raw_mesh_paths

print(signature(raw_mesh_paths))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.applications.aero_cfd.infer.mesh`
- 仓库相对路径：`packages/ai4e-core/applications/aero_cfd/infer/mesh.py:209`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.applications.aero_cfd.infer.mesh')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
