<!-- dojo-help: {"domain": "task", "kind": "api-guide", "layer": "task", "summary": "比较已经登记且语义兼容的指标，不从残留文件重新计算。", "tasks": ["比较 API"], "title": "比较 API", "topic_id": "task-guide:comparison"} -->
# 比较 API

## 适用操作

比较已经登记且语义兼容的指标，不从残留文件重新计算。

## 调用方式

从 `ai4e_task` 包根导入：`compare_runs、read_run_metrics`。精确签名、参数、返回值、显式异常和源码位置用下列方式查询：

```python
import ai4e_task as task
for name in ['compare_runs', 'read_run_metrics']:
    info = task.describe_help_symbol("ai4e_task." + name)
    print(info["signature"], info["source_path"])
```

## 失败与证据

Task 返回字典中的身份和状态用于继续查询；提交成功不等于研究成功。最终判断必须结合终态、core summary、阶段报告和固定产物。逐函数参考见 `api/task/public-api.md`。
