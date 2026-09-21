<!-- dojo-help: {"domain": "task", "kind": "api-guide", "layer": "task", "summary": "读取 revision 后合并保存或完整替换；运行临时覆盖仍由 submit_run.overrides 表达。", "tasks": ["配置 API"], "title": "配置 API", "topic_id": "task-guide:configuration"} -->
# 配置 API

## 适用操作

读取 revision 后合并保存或完整替换；运行临时覆盖仍由 submit_run.overrides 表达。

## 调用方式

从 `ai4e_task` 包根导入：`read_configuration、save_configuration、replace_configuration`。精确签名、参数、返回值、显式异常和源码位置用下列方式查询：

```python
import ai4e_task as task
for name in ['read_configuration', 'save_configuration', 'replace_configuration']:
    info = task.describe_help_symbol("ai4e_task." + name)
    print(info["signature"], info["source_path"])
```

## 失败与证据

Task 返回字典中的身份和状态用于继续查询；提交成功不等于研究成功。最终判断必须结合终态、core summary、阶段报告和固定产物。逐函数参考见 `api/task/public-api.md`。
