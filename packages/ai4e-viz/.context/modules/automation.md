# automation 文件索引

职责：脚本校验、脚本化用例与未来持久化边界；当前无前端模块。PRD：[`automation.md`](../../docs/PRD/automation.md)。

## 模块设计

`automation`以脚本定义和执行请求为聚合边界，只通过其他一级模块公开用例编排能力，不绕过领域校验访问Repository或`visEngine`。脚本持久化一旦启用由本模块Repository拥有；尚未实现的保存/执行必须明确返回未就绪，不用目录或占位接口伪装完成。

| 后端文件 | 作用 |
| --- | --- |
| [`__init__.py`](../../backend/modules/automation/__init__.py) | 脚本化公开门面 |
| [`api.py`](../../backend/modules/automation/api.py) | 预留协议入口与未就绪错误映射 |
| [`application.py`](../../backend/modules/automation/application.py) | 脚本校验/保存/执行用例边界 |
| [`domain.py`](../../backend/modules/automation/domain.py) | 脚本模型、安全约束和校验规则 |
| [`repository.py`](../../backend/modules/automation/repository.py) | 模块未来脚本持久化所有权；未实现能力不假成功 |

测试：[`test_automation.py`](../../backend/tests/modules/test_automation.py)。Excel逐功能矩阵将当前能力标记为`demo_only`，因为只校验脚本文本，不执行、保存或生成提取结果。新增执行能力必须从所属业务模块公开用例编排，不能绕过校验。


## Dojo 当前实现文件

- `backend/modules/automation/__init__.py`：脚本化一级模块公开门面。
- `backend/modules/automation/api.py`：脚本保存和执行的HTTP适配层。
- `backend/modules/automation/application.py`：脚本化提取、校验和保存用例。
- `backend/modules/automation/domain.py`：脚本化领域对象。
- `backend/modules/automation/repository.py`：脚本持久化边界。
