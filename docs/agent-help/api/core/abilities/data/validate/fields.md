<!-- dojo-help: {"domain": "ai4e_core.abilities.data.validate.fields", "kind": "api", "layer": "core.ability", "summary": "ai4e_core.abilities.data.validate.fields 的完整源码参考与公开符号索引。", "title": "ai4e_core.abilities.data.validate.fields", "topic_id": "module:ai4e_core.abilities.data.validate.fields"} -->
# `ai4e_core.abilities.data.validate.fields` API 参考

> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，完整研究调用请继续阅读关联工作流和案例。

<a id="symbol-ai4e-core-abilities-data-validate-fields-fieldvalidationerror"></a>
## `ai4e_core.abilities.data.validate.fields.FieldValidationError`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`FieldValidationError(report: ValidationReport)`
- **规范定义名**：`ai4e_core.abilities.data.validate.fields.FieldValidationError`

### 用途

携带完整报告，供执行层序列化。

### 导入与签名

```python
from ai4e_core.abilities.data.validate.fields import FieldValidationError
```

```text
FieldValidationError(report: ValidationReport)
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `report` | `ValidationReport` | `必填` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`FieldValidationError`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.validate.fields import FieldValidationError

print(signature(FieldValidationError))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.validate.fields`
- 仓库相对路径：`packages/ai4e-core/abilities/data/validate/fields.py:32`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.validate.fields')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-validate-fields-validationissue"></a>
## `ai4e_core.abilities.data.validate.fields.ValidationIssue`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`class ValidationIssue`
- **规范定义名**：`ai4e_core.abilities.data.validate.fields.ValidationIssue`

### 用途

可定位到样本、组和字段的校验失败。

### 导入与签名

```python
from ai4e_core.abilities.data.validate.fields import ValidationIssue
```

```text
class ValidationIssue
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`ValidationIssue`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.validate.fields import ValidationIssue

print(signature(ValidationIssue))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.validate.fields`
- 仓库相对路径：`packages/ai4e-core/abilities/data/validate/fields.py:12`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.validate.fields')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-validate-fields-validationreport"></a>
## `ai4e_core.abilities.data.validate.fields.ValidationReport`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`class ValidationReport`
- **规范定义名**：`ai4e_core.abilities.data.validate.fields.ValidationReport`

### 用途

成功和失败使用同一个报告契约。

### 导入与签名

```python
from ai4e_core.abilities.data.validate.fields import ValidationReport
```

```text
class ValidationReport
```

### 参数

本符号没有公开构造参数，或源码未声明可提取的参数。

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`ValidationReport`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.validate.fields import ValidationReport

print(signature(ValidationReport))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.validate.fields`
- 仓库相对路径：`packages/ai4e-core/abilities/data/validate/fields.py:23`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.validate.fields')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-validate-fields-require-valid-records"></a>
## `ai4e_core.abilities.data.validate.fields.require_valid_records`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`require_valid_records(records: Sequence[FieldRecord], groups: Mapping[str, GroupContract], *, sample: str='') -> ValidationReport`
- **规范定义名**：`ai4e_core.abilities.data.validate.fields.require_valid_records`

### 用途

保留结构化结果；失败时抛出带报告的异常。

### 导入与签名

```python
from ai4e_core.abilities.data.validate.fields import require_valid_records
```

```text
require_valid_records(records: Sequence[FieldRecord], groups: Mapping[str, GroupContract], *, sample: str='') -> ValidationReport
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `records` | `Sequence[FieldRecord]` | `必填` |
| `groups` | `Mapping[str, GroupContract]` | `必填` |
| `sample` | `str` | `''` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`ValidationReport`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

`FieldValidationError`

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.validate.fields import require_valid_records

print(signature(require_valid_records))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.validate.fields`
- 仓库相对路径：`packages/ai4e-core/abilities/data/validate/fields.py:104`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.validate.fields')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。

<a id="symbol-ai4e-core-abilities-data-validate-fields-validate-records"></a>
## `ai4e_core.abilities.data.validate.fields.validate_records`

- **层级**：`core.ability`
- **稳定性**：`extension`
- **定义**：`validate_records(records: Sequence[FieldRecord], groups: Mapping[str, GroupContract], *, sample: str='') -> ValidationReport`
- **规范定义名**：`ai4e_core.abilities.data.validate.fields.validate_records`

### 用途

即使没有筛选也检查每行身份；不使用名称后缀推断归属。

### 导入与签名

```python
from ai4e_core.abilities.data.validate.fields import validate_records
```

```text
validate_records(records: Sequence[FieldRecord], groups: Mapping[str, GroupContract], *, sample: str='') -> ValidationReport
```

### 参数

| 参数 | 类型 | 默认值 |
| --- | --- | --- |
| `records` | `Sequence[FieldRecord]` | `必填` |
| `groups` | `Mapping[str, GroupContract]` | `必填` |
| `sample` | `str` | `''` |

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`ValidationReport`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。

### 最小可执行检查

```python
from inspect import signature
from ai4e_core.abilities.data.validate.fields import validate_records

print(signature(validate_records))
```

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：无直接 recipe 归属。
- 案例：机器索引未发现直接文本引用。

### 源码位置

- 模块：`ai4e_core.abilities.data.validate.fields`
- 仓库相对路径：`packages/ai4e-core/abilities/data/validate/fields.py:40`
- 安装源码：先调用 `ai4e_task.source_location('ai4e_core')`，再按模块相对路径定位。

### 相关 API

通过 `search_help('ai4e_core.abilities.data.validate.fields')` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
