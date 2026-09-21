<!-- dojo-help: {"topic_id": "capability:run-task", "title": "运行记录与 Task 管理", "kind": "tutorial", "layer": "capability", "domain": "run-task", "summary": "direct-core 启动、报告、资产，以及可选版本、后台、停止、恢复和比较", "tasks": ["运行记录", "Task 管理", "后台训练", "案例复制"], "symbols": ["ai4e_core.run.launch", "ai4e_core.run.TrainingRun", "ai4e_task.create_project", "ai4e_task.new_task", "ai4e_task.submit_run", "ai4e_task.wait_run", "ai4e_task.compare_runs"], "navigation_order": 9} -->
# 运行记录与 Task 管理

需要日志、配置和检查点记录时，用公开 launch + TrainingRun，参见训练分支的可运行脚本。需要版本、资产、后台运行、停止、恢复或比较时，再把同一研究目录交给 Task。单个数学工具调用不要求先创建项目。

下面只演示完整案例复制与任务创建，不会启动训练。真实数据与配置准备完成、direct-core 验证后，再按 Task 教程 submit_run/wait_run；等待终态并读取 summary 和产物，提交成功不等于执行成功。

## 直接入口

- `ai4e_core.run.launch`
- `ai4e_core.run.TrainingRun`
- `ai4e_task.create_project`
- `ai4e_task.new_task`
- `ai4e_task.submit_run`
- `ai4e_task.wait_run`
- `ai4e_task.compare_runs`

使用 `ai4e_task.describe_help_symbol` 核对当前安装版本的签名和源码；这里的例子验证调用，不代表生产精度。

## 可执行小例子

将代码保存到独立研究目录的 `source/demo.py`，从研究目录启动；不同例子用不同工作目录。

```python
from pathlib import Path
import ai4e_task as task

case = Path("copied-case").resolve()
project = Path("managed-study").resolve()
task.copy_example("parametric_pde.neumann_diffusion", case)
task.create_project(project, name="research")
record = task.new_task(project, "baseline", source=case)
assert record["id"]
assert (case / "pipeline.py").is_file()
```

## 继续阅读

[接入细节](../getting-started/manage-with-task.md) · [帮助首页](../index.md)
