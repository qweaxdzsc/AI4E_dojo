<!-- dojo-help: {"domain": "task", "kind": "api-guide", "layer": "task", "summary": "固定共享数据、准备、检查点和结果来源；复制前验证自包含目录与依赖。", "tasks": ["资产 API"], "title": "资产 API", "topic_id": "task-guide:assets"} -->
# 资产 API

## 适用操作

固定共享数据、准备、检查点和结果来源；复制前验证自包含目录与依赖。

## 调用方式

从 `ai4e_task` 包根导入：`list_stage_artifacts、freeze_checkpoint、freeze_result_item`。精确签名、参数、返回值、显式异常和源码位置用下列方式查询：

```python
import ai4e_task as task
for name in ['list_stage_artifacts', 'freeze_checkpoint', 'freeze_result_item']:
    info = task.describe_help_symbol("ai4e_task." + name)
    print(info["signature"], info["source_path"])
```

## 失败与证据

Task 返回字典中的身份和状态用于继续查询；提交成功不等于研究成功。最终判断必须结合终态、core summary、阶段报告和固定产物。逐函数参考见 `api/task/public-api.md`。
