<!-- dojo-help: {"domain": "task", "kind": "api-guide", "layer": "task", "summary": "搜索帮助、定位源码、读取清单、复制案例和导出离线帮助；这些操作不加载训练栈。", "tasks": ["帮助与案例资源 API"], "title": "帮助与案例资源 API", "topic_id": "task-guide:help-resources"} -->
# 帮助与案例资源 API

## 适用操作

搜索帮助、定位源码、读取清单、复制案例和导出离线帮助；这些操作不加载训练栈。

## 调用方式

从 `ai4e_task` 包根导入：`help_info、search_help、read_help_topic、describe_help_symbol、export_help、list_examples、copy_example`。精确签名、参数、返回值、显式异常和源码位置用下列方式查询：

```python
import ai4e_task as task
for name in ['help_info', 'search_help', 'read_help_topic', 'describe_help_symbol', 'export_help', 'list_examples', 'copy_example']:
    info = task.describe_help_symbol("ai4e_task." + name)
    print(info["signature"], info["source_path"])
```

## 失败与证据

Task 返回字典中的身份和状态用于继续查询；提交成功不等于研究成功。最终判断必须结合终态、core summary、阶段报告和固定产物。逐函数参考见 `api/task/public-api.md`。
