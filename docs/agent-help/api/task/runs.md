<!-- dojo-help: {"domain": "task", "kind": "api-guide", "layer": "task", "summary": "`submit_run` 捕获当前代码、配置和输入；`wait_run`、`get_run`、`stop_run` 读取或控制真实运行。", "tasks": ["运行 API"], "title": "运行 API", "topic_id": "task-guide:runs"} -->
# 运行 API

## 适用操作

`submit_run` 捕获当前代码、配置和输入；`wait_run`、`get_run`、`stop_run` 读取或控制真实运行。

## 调用方式

从 `ai4e_task` 包根导入：`submit_run、wait_run、get_run、list_runs、stop_run、read_log`。精确签名、参数、返回值、显式异常和源码位置用下列方式查询：

```python
import ai4e_task as task
for name in ['submit_run', 'wait_run', 'get_run', 'list_runs', 'stop_run', 'read_log']:
    info = task.describe_help_symbol("ai4e_task." + name)
    print(info["signature"], info["source_path"])
```

## 失败与证据

Task 返回字典中的身份和状态用于继续查询；提交成功不等于研究成功。最终判断必须结合终态、core summary、阶段报告和固定产物。逐函数参考见 `api/task/public-api.md`。
