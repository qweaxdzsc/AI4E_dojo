<!-- dojo-help: {"domain": "task", "kind": "api-guide", "layer": "task", "summary": "`create_project` 和 `open_project` 管理本地研究项目根；共享数据操作保持项目级身份。", "tasks": ["项目 API"], "title": "项目 API", "topic_id": "task-guide:projects"} -->
# 项目 API

## 适用操作

`create_project` 和 `open_project` 管理本地研究项目根；共享数据操作保持项目级身份。

## 调用方式

从 `ai4e_task` 包根导入：`create_project、open_project、list_shared_datasets、bind_shared_dataset`。精确签名、参数、返回值、显式异常和源码位置用下列方式查询：

```python
import ai4e_task as task
for name in ['create_project', 'open_project', 'list_shared_datasets', 'bind_shared_dataset']:
    info = task.describe_help_symbol("ai4e_task." + name)
    print(info["signature"], info["source_path"])
```

## 失败与证据

Task 返回字典中的身份和状态用于继续查询；提交成功不等于研究成功。最终判断必须结合终态、core summary、阶段报告和固定产物。逐函数参考见 `api/task/public-api.md`。
