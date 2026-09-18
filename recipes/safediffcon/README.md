# SafeDiffCon 可复制研究模板

长期说明见[模板 PRD](../../docs/PRD/recipes/safediffcon/PRD.md)，实际范围见[验收记录](../../.context/mvp/safediffcon-acceptance.md)。这是代码研究入口，短训练不代表论文精度。

## 复制与环境

可复制本目录，或直接复制 `examples/safediffcon/burgers` / `tokamak` 完整目录；两例都包含可编辑的六阶段脚本与配置。`config.yaml` 是默认入口；`quick.yaml` 保留相同科学默认值作为旧命令兼容，名字不保证耗时。每例仍需原累计账本监督。

使用同一套实际安装的 spec/core/contrib/task，安装 contrib 的 safediffcon 可选依赖。研究隔离环境与正式平台分开；直接脚本和 Task 必须使用同一解释器和安装副本。当前已交付启动器及实际包摘要见专项记录。

## 公共配置

`inputs.rawprep.source` 指原始数据目录；`inputs.trainprep.dataset_train/cal/test` 是物理清单；训练、后训练、推理各自绑定 `inputs.<stage>.preparation_train/cal/test`。`run_root` 放运行记录，`data_root` 放阶段数据，相对路径以配置文件为准。

恢复使用 `inputs.train.resume`；两轮后训练和推理分别使用 `inputs.posttrain.checkpoint`、`inputs.infer.checkpoint`。Tokamak 使用 `inputs.infer.solver_assets` 捕获 KSTAR 资源，`solver.python` 保留隔离虚拟环境解释器路径，不能替换为解析符号链接后的基础 Python。Burgers 不需要 KSTAR，两项设为空。

完整流程将前序返回值交给后序；同次生产的下游外部输入应为空。独立阶段则必须填写明确引用。上游结果与外部引用冲突会失败，不搜索最近权重。Python决定步骤顺序；配置只选范围，未知未执行阶段会留下未完成研究状态。

```bash
uv run --no-project --python <研究Python> python pipeline.py --config config.yaml
uv run --no-project --python <研究Python> python train.py --config config.yaml --set train.updates=3 --set inputs.train.resume=<完整预训练权重>
uv run --no-project --python <研究Python> python post.py --config config.yaml --set inputs.post.results=<固定结果manifest.json>
```

在仓库中将计算命令包在原累计监督器外层：

```bash
uv run --no-sync python -m tools.verification.safediffcon.budget --ledger <原账本> --seconds <本阶段秒数> --reserve <评价预留秒数> -- <计算命令>
```

`train.updates` 是含恢复历史的总目标，默认4000、上限20000；上限不替代每例累计180分钟。失败和重试同样计账。后训练轮内任意恢复不属于当前保证范围。

## Task 运行

Task 从 `pipeline.py/config.yaml` 自动发现；无需第二份声明。直接运行与Task执行同一正文。

```python
from pathlib import Path
import ai4e_task as task

project = Path("/你的实验目录/control-project")
task.create_project(project)
item = task.new_task(project, "SafeDiffCon", source="/你的完整案例目录")
job = task.submit_run(project, item["id"])
result = task.wait_run(project, job["id"], timeout=30)
# 超时只结束等待；get_run查询状态，stop_run才请求停止。
```

独立执行可覆盖 `pipeline.stages=[train]`，但须先绑定准备。CLI使用同一实现：`python -m ai4e_task run TASK_ID --project PROJECT --set 'pipeline.stages=[post]' --set inputs.post.results=PATH --wait`。执行不增加版本；fork才增加。平台模型选择和专用批量推理未接入。

## 旧配置与冻结产物

```bash
uv run --no-project --python <研究Python> python configuration.py --migrate old.yaml --output new.yaml
```

转换只写新文件，按原目录展开路径；拒绝新旧输入混用。旧准备、检查点和结果保持原字节，按原科学合同读取。旧自定义Task用离线候选审阅与备份迁移，不自动覆盖脚本。

## 扩展与交付

编辑复制目录中的步骤正文可插入普通函数；`components.model/guide/derived` 可替换构造、安全引导与派生量。现有扩展示例位于 `examples/recipe_extensions/safediffcon/variants.py`。派生量声明 values/valid/units/axes，保存后由独立post消费。

物理、准备和推理结果登记自包含数组目录；共享/复制原样保留科学文件。后处理指标登记固定真值、样本、单位与统计口径，不因预测变化误判不可比；自定义指标缺少科学语义则不冒充可比较指标。后处理不重新训练、不更新权重、不调用求解器；这不免除正常训练与推理的验收。
