# WDNO Burgers 基础预测

同一份 `pipeline.py` 可直接运行或由 Task 托管。Python 决定 rawprep → trainprep → train → infer → post 顺序；`pipeline.stages` 只选择其中按顺序排列的非空子集。Task 按 `pipeline.py + config.yaml` 自动发现，不需要 `task.py` 或 `task-entry.json`。

[功能说明](../../docs/PRD/recipes/wdno/PRD.md) · [验收与当前隔离安装](../../.context/mvp/wdno-acceptance.md) · [组件变体](../../examples/recipe_extensions/wdno/README.md)。当前只完成 Burgers 基础切片迁移，论文精度、Smoke、超分和控制未完成。

## 输入、输出与独立阶段

`run_root` 保存运行记录；`data_root` 提供数据根目录，每次执行由运行器分配独立子目录，各阶段使用 `TrainingRun.output_dir`。Task 托管时使用任务自己的数据目录。数组、检查点和指标通过公共资产/指标索引交给 Task，不能把 recipe 代码目录当作输出目录。

外部输入统一放在 `inputs.<阶段>`，每个值是文件路径或 null；相对路径以配置文件位置解析。三个分片继续使用原有数组清单，不要求重算旧准备：

- `rawprep.source` 是原数据来源协议，`rawprep.indices` 是固定代表轨迹名单。
- `trainprep.dataset` 是训练物理清单，`validation/test` 是两份评价物理清单。
- `train.preparation` 是训练小波准备，`validation/test` 是两份评价物理清单；`train.resume` 是可选完整检查点。
- `infer.preparation/validation/test` 指定同一组准备，`infer.checkpoint` 指定预测权重。
- `post.validation/test` 是已保存预测清单；单独 post 只重算固定结果，不构造网络。

连续执行时，Python 直接交接前一阶段返回值，对应外部输入留 null。如果同时填写了不同的外部路径，会明确拒绝冲突；不猜测最近结果，也不偷偷优先选择某一份。单阶段执行时，将前次 `summary.json` 中 `reports.rawprep/trainprep/infer` 的对应分片填到上述位置。

`train.updates` 是含已完成更新的总目标；例如2步检查点恢复到3表示再执行1次更新。变更模型、损失、学习率、批量、种子或准备身份会拒绝续训；采样步数、总更新数和时间限制可调整。预算/取消未完成时保存完整更新边界并报告未完成。

原 Trainer 权重仅通过 `infer.checkpoint_format: source` 显式导入，不能当作精确续训状态。

## 直接运行与 Task

先将本目录复制到研究目录，在验收记录所列隔离解释器和安装集合下执行。本机已验证解释器为 `/Users/zonghui/work/project_simulation/dojo_train/wdno/environment/bin/python`，`PYTHONPATH` 指向 `/Users/zonghui/work/project_simulation/dojo_train/wdno/protocol-update-20260917/installed`；两种入口使用同一环境。Python环境需安装 `ai4e-contrib[wdno]`，Task运行另需 `ai4e-task`；主环境不要自动 sync 或重装。

```bash
uv run --no-project --python "$wdno_python" python "$wdno_recipe/pipeline.py" \
  --set 'pipeline.stages=[train,infer,post]' --set train.updates=3
```

这里的变量是你选定的解释器与复制目录。运行前先在配置中填对应外部准备和恢复权重；`--set` 与配置文件、程序入口采用相同检查。

```python
import ai4e_task as task

project = task.create_project("/absolute/research/project")
current = task.new_task("/absolute/research/project", "wdno", source="/absolute/research/recipe")
record = task.submit_run(
    "/absolute/research/project", current["id"], overrides=["pipeline.stages=[train,infer,post]"]
)
finished = task.wait_run("/absolute/research/project", record["id"], timeout=180)
```

Task使用调用者解释器与环境，直接脚本和worker必须看到同一安装集合。新建任务后改的是任务自己的recipe副本，原模板后续编辑不自动回写旧任务；运行和续训不创建新版本。MSE比较包含样本/真值身份、单位、初帧排除、样本等权以及评价函数身份，缺少或不同语义不能判为相同实验。

## 旧配置转换与历史证据

旧 `data.*`、`train.resume`、`infer.checkpoint`、`post.results` 不再作为新用户配置接受；新旧同时出现也拒绝。显式转换只生成新文件：

```bash
uv run --no-project --python "$wdno_python" python "$wdno_recipe/configuration.py" \
  --migrate /absolute/old-config.yaml --output /absolute/new-config.yaml
```

转换保留科学参数与原路径身份，输出文件已存在则失败。检查新配置中的阶段和输入再运行；从旧完整训练配置转换后，要运行新的连续阶段时需主动清除与本次前序输出冲突的历史输入。旧数组格式、准备声明和检查点合同保持原义；旧2000步报告、冻结recipe与installed-final继续作为历史证据，不覆盖它们。

## Agent 查找与组装

从 `pipeline.py` 看顺序与交接，从阶段导入定位 application，从 `components` 定位普通函数。支持 reader、transform、network、objective、predict、metrics、derived 替换，无需登记框架组件。网络签名不同时在研究目录写局部连接；可持久化函数须为模块级函数。

例如替换网络层级、损失权重，或在 infer 后显式插入自己的 `run.stage`，保存能量数组并用 `record_asset` 登记单位/轴和依赖。直接脚本与Task执行同一正文。默认MSE排除初始时刻、样本等权；初帧不硬覆盖，论文0.00014与本地切片不能混作同协议精度验收。

## 分阶段Task验收与扩展目录

新建WDNO任务后可依次提交 `rawprep`、`trainprep`、`train`、`infer`、`post`，续训再提交 `train`；每次设置 `pipeline.stages` 为所选阶段，并从前次报告明确填写该阶段的输入。运行和续训不创建版本。公开API分阶段真实验证入口为 `tools.verification.wdno.task_replay --staged`，会核对实际阶段、更新数、权重变化、固定预测读回、后处理独立性和缺输入失败。

[完整扩展覆盖文件集](../../examples/recipe_extensions/wdno/README.md)提供完整配置和流程、网络/损失替换与能量读回步骤。先复制本模板，再覆盖扩展文件；扩展目录自身不含原五阶段文件。

当前实验计算使用[累计预算监督](../../tools/verification/wdno/README.md#续接预算与独立阶段验收)。续接要求账本已存在；模板的 `train.seconds` 只是阶段限时，不自动限制所有任务的累计成本。

## 当前公共约定补验与恢复

当前交付安装集合为 `/Users/zonghui/work/project_simulation/dojo_train/wdno/protocol-update-20260917/installed`，解释器仍为上文WDNO隔离解释器。`PYTHONPATH` 指向此目录；主环境没有小波依赖，不能用主环境启动复制worker。交付报告与最终状态见验收记录。

增加训练量：把 `pipeline.stages` 设为 `[train]`，绑定已有 `inputs.train.preparation/validation/test/resume`，提高 `train.updates` 总目标，再调用 `submit_run`。中断恢复：使用公开 `resume_run(project, run_id, checkpoint="train/latest.pt")`，保留该独立训练运行的冻结代码和总目标；已完成两步的运行不会自动变成三步。CLI同义入口如下，返回收据后仍须查询终态：

```bash
uv run --no-project --python "$wdno_python" python -m ai4e_task resume "$run_id" \
  --project "$wdno_project" --checkpoint train/latest.pt --json
```

模板与 `examples/wdno/burgers_base` 均可作为 `new_task` 来源，验证工具分别原样复制，扩展示例才覆盖 `pipeline/audit/variants`。普通执行不要求平台可选操作；未声明的 inspect/infer/evaluate/export 管理接口保持不可用，不等于阶段脚本不能运行。

## 复制产物与指标完整性

使用 `fork_task(..., source="run", run_id=..., copy_preparation=True, copy_checkpoints=True)` 从明确运行复制已经登记的准备及检查点；需要物理数组时同时选择 `copy_datasets=True`。从返回的 `copied_outputs` 找到实际复制品，将项目内相对路径展开后明确写入 `inputs.train` 和 `inputs.infer`。复制输出不会自动绑定训练输入。验证/测试物理数组在 trainprep 中按准备资产登记，会随准备复制。

冻结准备中的历史来源路径只作出处记录，实际消费使用清单旁的相对数组；复制不重写科学文件。原始来源协议可能引用目录外大文件，复制协议不等于复制原数据；仅运行训练/推理时应解除未使用的原始输入引用。

新post指标同时绑定结果清单、预测、真值、样本ID及派生数组，缺失或变化时Task比较返回不可用。不同预测值不改变科学可比身份；样本、真值、单位或评价定义不同则不可比。旧指标索引不自动改写，要获得完整依赖保护，请对原固定结果执行独立post生成新记录。


## 局部优化与更新

默认训练无需改脚本。复制目录可通过 components.optimizer / scheduler / update 选择模块级普通函数，详见[训练策略示例](../../examples/recipe_extensions/wdno/README.md#只替换训练策略)。构造参数来自 train，新的选择参与完整恢复身份；未选时原合同不变。自定义更新不接管日志、保存或EMA/调度推进。
