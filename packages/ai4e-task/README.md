# ai4e-task

本地项目、任务正式版本、共享资产与执行管理。功能模块为 cli/projects/tasks/versions/templates/storage，不使用 DDD。只有 new/fork 创建正式版本；编辑和运行不增加版本。

## 安装与入口

构建后的 `ai4e_task-0.1.0-py3-none-any.whl` 可用 pip 安装（同版本 spec/core 须可获取）；源码开发使用根 uv workspace。提供 `ai4e` 和 `python -m ai4e_task`。管理操作不提前导入训练栈，执行案例仍需要案例依赖。

```bash
ai4e project new ./study
ai4e new baseline --project ./study --from ./my_recipe
ai4e fork TASK_ID --project ./study --copy-datasets
ai4e run TASK_ID --project ./study --wait
ai4e tree --project ./study
ai4e compare runs RUN_A RUN_B --project ./study --save
```

命令支持 `--json`。完整 Python API 由包根导出，可创建、打开和恢复项目，登记模板及共享资产，new/fork、查询、执行、停止、恢复、导入和比较。

## 目录与资产

项目下 `tasks/<task_id>/recipe` 可编辑；任务内 `runs/<run_id>` 保存运行证据，`data/<run_id>` 保存准备副本与预测等任务专属数据，`assets/<名称>` 保存显式复制资产。正式物理数据存入项目 `shared/datasets/<名称>/content`，其父目录 `asset.json` 记录当前内容和来源；其他通用共享资产沿用 `shared/<名称>/asset.json`。

fork 默认当前代码，`source="version"` 选择创建记录，`source="run", run_id=...` 选择固定执行快照。`copy_datasets/copy_preparation/copy_checkpoints` 独立且默认 False。不复制历史 runs，不因复制检查点自动续训。勾选准备／检查点复制时，还会读取父任务最近完整成功运行的 公共资产索引；指定 run_id 可固定来源，复制结果单列在 copied_outputs 中，不自动绑定到训练输入。`resume_run` 使用原运行的捕获代码及配置和检查点，仍需核心检查点契约校验。

## 普通研究入口

Task 发现 `pipeline.py/config.yaml`，不需要 `task-entry.json`。公共输入放在 `inputs.<stage>.<name>`，值为路径或 null；参数和算法仍由 recipe/application 解释。`pipeline.stages` 只选择范围，Python 决定步骤顺序。

```yaml
run_root: ../runs
data_root: ../data
pipeline:
  stages: [post]
inputs:
  post:
    results: ../fixed/results.json
```

托管执行分配本次运行和数据目录。普通脚本可自由修改；缺运行记录时只能确认进程退出，缺资产或指标索引只使发现、比较不可用。显式选中的输入缺失或内容改变则拒绝。

使用 `TrainingRun.record_asset` 登记真实输出及依赖，使用 `record_metric` 交付字段、单位、分片、统计与数据身份明确的指标。writer独占运行索引。`components.application` 可选提供领域检查/评价/导出连接；未配置不猜测模型。历史配置与脚本使用离线迁移副本，保留冻结证据，正常运行不自动适配旧结构。

## 完整性与限制

new/fork 先暂存后发布并支持幂等键；相同键不同请求报冲突。运行完成需 core 摘要与 worker 收据一致。无法核对进程时保留 unknown，不自动重启。`recover_project` 显式清理未登记任务及 task 暂存目录；数据库仍须备份。

复制拒绝符号链接；大数据摘要会产生读取开销。准备文件内部的依赖仍保留显式引用，依赖闭包不支持便携复制时明确拒绝，仍可引用。项目路径作为配置的一部分保存，移动项目后外部绝对引用需要重新配置。首期本地进程适用于 macOS/Linux，不包含 Windows 进程适配、远程调度、Web/Server 或 PyPI 发布。

## Web 复用公开管理能力

`read_configuration` 返回未展开配置与内容修订；`save_configuration(..., revision=...)` 原子合并任务副本，旧修订拒绝。`update_project`、`update_task` 提供名称、描述、归档和恢复，归档不删除文件。编辑不增加正式版本。

从默认模板创建时允许尚未绑定数据路径；已有继承资产继续验证，实际执行仍严格捕获输入。服务仅调用原 submit_run 的阶段与样本覆盖，不新增调度器。相关测试：test_task_configuration.py、test_web_project_task.py、test_web_runtime.py。

## 项目共享物理数据

官方外流 Task 的正式 rawprep 默认写入 `shared/datasets/<dataset.processed_name>/content/`。运行配置与日志仍在任务 runs；准备副本及预测在任务 data。正式提交前填写名称，同名不自动复用，重做须显式 `submit_run(..., overwrite=True)` 或 `ai4e run <task> --overwrite`。覆盖不改旧任务、准备或检查点；新准备读取同名当前内容，旧冻结消费保留原校验。

```python
import ai4e_task as task
resources = task.list_shared_datasets(project)
current = task.read_configuration(project, consumer_id)
task.bind_shared_dataset(project, consumer_id, "cars", revision=current["revision"])
run = task.submit_run(project, consumer_id, overrides=["pipeline.stages=[trainprep]"])
```

`ai4e project datasets list --project <project>` 列出资源；`bind <task> <name> --revision <revision>` 显式绑定；`migrate --project <project>` 只预览，带 `--execute` 才复制历史正式成功数据。迁移保留原文件，试跑/失败不登记。Task 无需 Server，跨项目汇聚由平台完成。

入口可选 `shared_outputs` 声明生产阶段、名称键、清单与消费绑定；`stage_inputs` 声明输入的使用阶段及 `provided_by` 前序生产方。原 `outputs` 通过 `{shared_<group>_dir}` 取得受控目录。未知自定义入口不自动追加声明，显式空声明保持原意。

迁移已有登记条目时可用 `migrate_shared_datasets(project, sources={"登记名称": "正式运行ID"})` 精确预览；带 `dry_run=False` 才复制。省略 sources 沿用按配置名称选最新正式运行；空映射不迁移，试跑与失败来源拒绝。
