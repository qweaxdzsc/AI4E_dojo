<!-- dojo-help: {"artifacts": ["checkpoint", "summary.json"], "domain": "managed-run", "errors": ["运行失败", "恢复不兼容"], "kind": "tutorial", "layer": "task", "summary": "direct-core 通过后使用 Task 管理版本、运行、停止、恢复和比较。", "tasks": ["Task 托管", "恢复训练"], "title": "用 Task 托管同一研究目录", "topic_id": "getting-started:manage-with-task"} -->
# 用 Task 托管同一研究目录

```python
from pathlib import Path
import ai4e_task as task

project_root = Path("./study")
case_root = Path("./neumann-study")
task.create_project(project_root, name="Neumann research")
record = task.new_task(project_root, "baseline", source=case_root)
submitted = task.submit_run(project_root, record["id"], overrides=["train.max_epochs=2"])
finished = task.wait_run(project_root, submitted["id"], timeout=120)
if finished["status"] != "succeeded":
    raise RuntimeError(task.read_log(project_root, submitted["id"]))
resumed = task.resume_run(project_root, finished["id"], checkpoint="latest.pt")
```

Task 捕获同一份代码、配置和输入，管理外围生命周期。提交成功只说明进程已经登记；必须等待终态并核对 core summary、阶段报告和资产索引。恢复创建新的运行记录并保留来源，不覆盖失败运行。
