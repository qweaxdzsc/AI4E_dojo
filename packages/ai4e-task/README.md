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

项目下 `tasks/<task_id>/recipe` 可编辑；`runs/<run_id>` 保存运行证据；`data/<run_id>` 保存数据输出；`assets/<名称>` 保存显式复制资产。项目 `shared/<名称>/asset.json` 随内容记录来源，datasets 可以再按数据集名称分组。

fork 默认当前代码，`source="version"` 选择创建记录，`source="run", run_id=...` 选择固定执行快照。`copy_datasets/copy_preparation/copy_checkpoints` 独立且默认 False。不复制历史 runs，不因复制检查点自动续训。勾选准备／检查点复制时，还会读取父任务最近完整成功运行的 `produced_assets` 声明；指定 run_id 可固定来源，复制结果单列在 copied_outputs 中，不自动绑定到训练输入。`resume_run` 使用原运行的捕获代码及配置和检查点，仍需核心检查点契约校验。

## 普通模板声明

`task-entry.json` 声明脚本、配置、输入资产类别、输出路径绑定和可选恢复键。输出仅可绑定 `{data_dir}` 下路径，`run_root` 绑定 `{run_root}`；不能通过命令覆盖逃逸。已有路径型输入需完整登记，自定义代码仍应通过 core 公共会话执行。

```json
{
  "script": "pipeline.py",
  "config": "config.yaml",
  "inputs": {"dataset.root": "dataset"},
  "outputs": {"run_root": "{run_root}", "data_root": "{data_dir}"}
}
```

`produced_assets` 可按资产类型声明运行目录内的相对文件模式，例如 `{"preparation":["artifacts/preparation.json"],"checkpoint":["checkpoints/*.pt"]}`。准备记录的原数据依赖会随引用登记，单独复制不会重写其内部路径。

指标声明使用 summary 中的键路径列表与 field/domain/unit/split/statistic 语义；可从最终配置补充分片和采样定义。没有完整语义的指标不判可比。完整例子见仓库 aero_cfd 模板。

## 完整性与限制

new/fork 先暂存后发布并支持幂等键；相同键不同请求报冲突。运行完成需 core 摘要与 worker 收据一致。无法核对进程时保留 unknown，不自动重启。`recover_project` 显式清理未登记任务及 task 暂存目录；数据库仍须备份。

复制拒绝符号链接；大数据摘要会产生读取开销。准备文件内部的依赖仍保留显式引用，单独复制准备文件不代表依赖已搬迁。项目路径作为配置的一部分保存，移动项目后外部绝对引用需要重新配置。首期本地进程适用于 macOS/Linux，不包含 Windows 进程适配、远程调度、Web/Server 或 PyPI 发布。

## Web 复用公开管理能力

`read_configuration` 返回未展开配置与内容修订；`save_configuration(..., revision=...)` 原子合并任务副本，旧修订拒绝。`update_project`、`update_task` 提供名称、描述、归档和恢复，归档不删除文件。编辑不增加正式版本。

从默认模板创建时允许尚未绑定数据路径；已有继承资产继续验证，实际执行仍严格捕获输入。服务仅调用原 submit_run 的阶段与样本覆盖，不新增调度器。相关测试：test_task_configuration.py、test_web_project_task.py、test_web_runtime.py。
