<!-- dojo-help: {"domain": "task", "kind": "api-guide", "layer": "task", "summary": "`new_task` 从完整研究目录创建根任务；`fork_task` 从现有任务或运行派生分支，保留来源。", "tasks": ["任务 API"], "title": "任务 API", "topic_id": "task-guide:tasks"} -->
# 任务 API

## 适用操作

`new_task` 从完整研究目录创建根任务；`fork_task` 从现有任务或运行派生分支，保留来源。

## 调用方式

从 `ai4e_task` 包根导入：`new_task、fork_task、get_task、list_tasks`。精确签名、参数、返回值、显式异常和源码位置用下列方式查询：

```python
import ai4e_task as task
for name in ['new_task', 'fork_task', 'get_task', 'list_tasks']:
    info = task.describe_help_symbol("ai4e_task." + name)
    print(info["signature"], info["source_path"])
```

## 失败与证据

Task 返回字典中的身份和状态用于继续查询；提交成功不等于研究成功。最终判断必须结合终态、core summary、阶段报告和固定产物。逐函数参考见 `api/task/public-api.md`。
