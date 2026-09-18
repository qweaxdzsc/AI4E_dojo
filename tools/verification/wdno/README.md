# WDNO 参考与迁移验收入口

本目录保留P0/P1原仓库切片，并提供当前Burgers基础预测迁移的对照、原权重导入、报告和累计审计工具。原Trainer来自冻结工作树；Dojo从实际安装包与复制recipe执行。当前同环境基础切片迁移完成，论文复现仍未完成。

执行与证据见 [专项验收](../../../.context/mvp/wdno-acceptance.md)，后续范围见 [实施计划](../../../.cursor/plans/wdno-reproduction-and-agent-composition.plan.md)。长期数据准入边界归 [贡献应用 PRD](../../../docs/PRD/ai4e-contrib/application/PRD.md) 的共享数据集选择。

## 当前运行

根目录：`/Users/zonghui/work/project_simulation/dojo_train/wdno/burgers-local-v1-20260917/`。

- `frozen/`：原源码、HEAD 补丁、文件摘要、原数据身份与固定训练/验证/测试名单。
- `budget.json`：累计监督账本，初始计入两次历史测速共 105.672568625 秒；新增诊断和每次尝试均计账。
- `diagnostic-2/`：正式网络两次原 Trainer 更新与原检查点读回。
- `diagnostic-2-sampling/`：两次更新、验证/测试各两条完整原采样，仅作入口诊断。
- `main/`：18000 轨迹训练池、最多 2000 更新、64 验证/128 测试的主切片；状态以 progress/result 和账本为准。

## 可执行方式

先在 Dojo 仓库中执行协议冻结。现有协议不能覆盖；新协议必须明确对应的新授权范围，不得以换目录重置旧实验余额。

```python
from tools.verification.wdno.protocol import freeze

freeze(source_directory, approved_split_manifest, new_frozen_directory)
```

计算入口必须由原组账本监督。下列变量代表明确的本机路径，不存在自动下载、自动补数据或默认扩大预算。

```bash
uv run --no-sync python -m tools.verification.wdno.budget --ledger "$ledger" -- \
  uv run --no-project --python "$reference_python" python \
  tools/verification/wdno/reference.py --frozen "$frozen" --output "$new_output" --ledger "$ledger"
```

`reference_python` 指向已有 WDNO Python 3.8/Torch 2.4.1 隔离环境。内层 `--no-project` 只选择该解释器，不同步 Dojo 环境。`--diagnostic` 显式选择 64 条训练、两次更新及各两条评价；诊断仍计原账本，不进入主切片验收。正常入口固定完整规模网络及 2000 上限；在累计 135 分钟内保存并结束训练，165 分钟内结束评价，外部监督在 180 分钟之前终止进程组并留宽限。

训练后先通过同一预算入口调用 `replay.py --root "$experiment_root"`，在原隔离解释器中重放主检查点的首批16条测试样本；随后独立生成报告：

```bash
uv run --no-sync python -m tools.verification.wdno.report --root "$experiment_root"
```

报告核对完整名单、原始真值、初帧排除后的 MSE、检查点完成步数和已收尾账本。只读取固定数组，不重跑采样。测试入口见专项验收。

## 历史原版工具的差异与恢复限制

原数据不改写，准备按 CPU 分块调用原小波函数；单进程 DataLoader 避免 Mac 多进程复制。原循环通过安全批次边界观察截止，原保存方法只改变保留文件位置。原检查点周期保存的 step 为零起始编号，因此 `checkpoint.json` 另记完成更新次数。

本阶段保留原检查点字段，未增加可恢复批次游标；**不提供精确续训**。中断保留最后完整保存。新尝试仍计同一账本，不自动从缺少状态的权重假装精确恢复。完整数据流恢复属于正式迁移后的 B5 验收。

评价只替换原 get_target 的数据来源，原条件小波与 MSE 函数保持；使用本地基础真值，未冒用缺失的高分辨率测试。初态经独立条件通道提供，重建初帧并非原算法硬约束。不能因诊断初帧误差而私自把预测改成真值。

## 当前迁移工具

原版P0/P1证据保留；`migration.py`通过复制recipe执行Dojo准备、训练、预测和严格对照，`finish.py`只用于本轮原版结束后的串行衔接。Dojo使用实际`installed-final` wheel和独立Python3.12环境，同原三小时账本记账。`import_replay.py`验证原检查点的显式source导入，`delivery.py`只读固定结果生成报告。`vendor.py`保留原方法定义并记录来源，不复制作者Trainer。

长期使用入口为仓库`recipes/wdno/README.md`；当前进度与完整数值结果以`.context/mvp/wdno-acceptance.md`为准。原训练seed0与切片seed42分别声明，对照工具逐项核验冻结protocol后才运行。

`variant.py`实际验证原数据上的小网络/损失/能量组合；`audit.py`在持有原预算锁时检查已关闭账本，设置硬超时，并在退出后追加测试耗时。最终命令与结果见专项验收。

## 公共Task/recipe约定后的验证

`task_replay.py`使用当前安装包和同一pipeline，以原数据8/2/2切片直接/Task各训练2更新再恢复到3，并比较状态、全部预测、派生字段和固定指标；`legacy_replay.py`从历史2000步原checkpoint在旧/新隔离入口各续至2001，验证完整状态及各16条预测。二者必须由原budget.json监督。

当前migration.py/variant.py已消费inputs与data_root；import_replay.py显式转换历史配置，在新的source-import-current目录使用当前recipe。历史finish.py只保留当时已完成的串行驱动，不用于启动新实验；完整旧工具正文已保存在dojo-final/delivery-code。读取旧报告不等于新运行继续接受旧配置。

## 续接预算与独立阶段验收

当前WDNO累计账本固定为 `/Users/zonghui/work/project_simulation/dojo_train/wdno/burgers-local-v1-20260917/budget.json`。以下监督入口默认要求账本已经存在；拼错路径不会静默获得新预算。`--credit-seconds`仅用于首次明确建账，已有实验不要使用。所有子进程使用同一安装集合，失败和重试照常扣账。

```bash
uv run --no-sync python -m tools.verification.wdno.budget \
  --ledger /Users/zonghui/work/project_simulation/dojo_train/wdno/burgers-local-v1-20260917/budget.json \
  -- uv run --no-project --python "$wdno_python" python "$wdno_recipe/pipeline.py"
```

`wdno_python`选用WDNO隔离解释器，`PYTHONPATH`指向实际验收的四包安装目录；`wdno_recipe`为完整复制目录。不要重装主环境。

`task_replay --staged`使用真实原数组8训练/2验证/2测试，小网络和两步采样，公开API新建项目/任务后分别提交rawprep、trainprep、train、infer、post、resume；逐阶段与直接脚本对照。后处理另外让模型构造路径不可用，缺准备/权重/结果分别验证失败。输出目录必须未存在，保留失败重试目录。

```bash
uv run --no-sync python -m tools.verification.wdno.budget \
  --ledger /Users/zonghui/work/project_simulation/dojo_train/wdno/burgers-local-v1-20260917/budget.json \
  -- uv run --no-project --python "$wdno_python" python -m tools.verification.wdno.task_replay \
  --staged --root /Users/zonghui/work/project_simulation/dojo_train/wdno/burgers-local-v1-20260917 \
  --output /absolute/new-acceptance-directory
```

`acceptance.json`保存新任务和每个运行身份、完整状态对照、指标、失败边界和检查点；`summaries.json`保留双方每阶段摘要。小网络结果只能证明工程交接，不能作为论文精度。

## 当前公共约定：三个入口与管理补验

`task_replay --staged --case recipe|example|extension`：默认extension保留原工具行为；recipe原样复制模板，example原样复制基础案例，只有extension覆盖公开扩展。各次使用独立输出父目录，父目录的task-indices.json保留该次原数据8/2/2名单。

`task_management --staged-root <本次staged目录>`：复用该次输入，另跑完整产物生产、指定运行fork、显式绑定复制品，临时隔离仅该次原产物后继续训练和预测；恢复所有临时位置。随后CLI/Python分别新建真实中断训练，在第2次完整更新边界保存，公开resume到3次，与不中断状态逐值对照。停止函数只在测试研究目录，不改变正式算法。该工具有真实计算，必须放进同一budget/audit监督；同一staged目录只执行一次。

当前发布集合：`/Users/zonghui/work/project_simulation/dojo_train/wdno/protocol-update-20260917/installed`，解释器沿用wdno/environment/bin/python。主环境不sync，不操作8000/5173。测试必须由同一解释器启动worker；测试用例安装夹具构建spec/core/contrib/task四包。

圈定test_wdno_public_metrics、test_wdno_task_assets、test_wdno_documents，以及原task/recipe/extensions和固定公开基线。最终通过/失败/跳过与源码、安装摘要归本次REPORT及delivery.json；不要把历史2000步数值对照称为此次重训。
