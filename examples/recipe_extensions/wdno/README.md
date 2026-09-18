# WDNO 研究变体

先复制完整 `recipes/wdno/` 到自己的研究目录，再用本目录的 `config.yaml`、`pipeline.py`、`audit.py`、`variants.py` 覆盖或补充同名文件。保留模板的配置加载器和五个阶段文件。本目录是扩展覆盖文件集，不能单独当作完整模板。

完整配置使用本机冻结来源与名单，外部机器须替换 `inputs.rawprep`。默认宽度8、两次更新是使用验收变体，不代表原正式网络或论文精度；较小数据验收需显式选择原名单的子集，不能擅自把完整轨迹截成时间片。执行前设置自己的 `run_root` 和 `data_root`，已有运行和原数据不覆盖。

## 修改与交接

- 参数在 `config.yaml`；Python决定步骤顺序，`pipeline.stages`只选原五阶段范围。
- `variants.custom_network`替换网络层级；`variants.custom_loss`替换目标；均为普通函数，无需框架登记。模型或损失变化应从头训练，不续用不相容权重。
- `variants.energy`保存空间平均平方，单位`u^2`，轴`sample/time`；`energy.npy`和预测共用样本身份。
- `pipeline.py`在真实推理后插入`audit`，由领域评价步骤读回固定结果，核对能量并生成`wdno-energy-readback.json`。缺字段、非有限值或数值不符会失败；检查模式不计算也不写报告。
- 单独post只消费固定预测。`audit`随infer执行，并非可独立选择的第六阶段；需要独立选择时，在复制目录明确扩展加载器和输入约定。

连续五阶段通过返回值交接，外部输入留null。只执行train/infer/post时，训练与推理各填同一组准备和验证/测试物理清单，推理权重留null接训练返回值。独立infer必须填`inputs.infer.checkpoint`；独立post必须填`inputs.post`。从2步恢复到总目标3只再更新1步。

## Task与实验预算

直接脚本与Task执行同一份pipeline；Task复制研究目录后，后续修改应在任务副本进行。新建项目/任务后分别提交准备、训练、推理和post即可；公开使用说明见[主模板](../../../recipes/wdno/README.md)，实际验证工具见[WDNO验证入口](../../../tools/verification/wdno/README.md)。

本次WDNO实验所有训练、采样和验收都用原累计账本监督。`train.seconds`仅限制训练阶段，不能替代总账本。见验证入口中的“续接预算”；不得另建账本或按变体重置预算。变体精度与官方复现分开报告。

## 可执行的本地配置示例

完成上面的完整模板复制和扩展文件覆盖后，将下面代码保存为复制目录中的 `configure_variant.py`。通过 `uv run --no-project --python "$wdno_python" python "$case/configure_variant.py" "$protocol" "$indices"` 执行，两个参数分别是现有来源协议和固定轨迹名单的文件路径。本机验收名单为 8/2/2 条完整轨迹。输入文件不在本脚本中生成，原名单不改写。

<!-- wdno-configure-example -->
```python
import sys
from pathlib import Path

import yaml

case = Path(__file__).resolve().parent
path = case / "config.yaml"
cfg = yaml.safe_load(path.read_text())
cfg["run_root"] = "../runs/wdno-variant"
cfg["data_root"] = "../data/wdno-variant"
cfg["inputs"]["rawprep"] = {
    "source": str(Path(sys.argv[1]).resolve()),
    "indices": str(Path(sys.argv[2]).resolve()),
}
cfg["model"].update(dim=8, dim_mults=[1, 1], ddim_steps=2)
cfg["train"].update(updates=2, batch_size=2, device="cpu", seconds=120)
cfg["infer"].update(device="cpu", batch_size=2)
cfg["components"].update(
    network="variants.custom_network",
    objective="variants.custom_loss",
    derived="variants.energy",
)
path.write_text(yaml.safe_dump(cfg, sort_keys=False))
```

上述接口均已存在。随后执行同目录 `pipeline.py`，或用该目录新建 Task。网络/损失变化从零训练，`audit` 在推理保存后实际读取 `energy.npy`；独立 post 无需构造网络。新指标登记清单和全部数组依赖，固定数组改动后 Task 比较不可用；重新评价会生成新运行记录，不修改历史报告。


## 只替换训练策略

先复制当前完整 `recipes/wdno/`，再覆盖本目录文件。新增 `variant_training.py` 提供普通优化器、调度器和更新函数；默认配置不启用这些变化。在完整 config.yaml 中按需增加：

```yaml
components:
  optimizer: variant_training.optimizer
  scheduler: variant_training.scheduler
  update: variant_training.update
```

以上只是新增键片段，不能替代完整 components。仅换优化器只增加 optimizer 一项；学习率仍来自 train.lr。省略选择继续使用原 Adam、余弦调度和原更新方式。原基础案例脚本无需同步修改，模型专属装配也会消费显式选择。

局部 update 示例缩放梯度，限单优化器、完整精度、无额外持久状态，不与框架累积/混合精度叠加。数据流、记录、取消和检查点继续复用框架。改动策略后从头训练；同一策略可增大 updates 续训，策略文件来源变化则完整恢复拒绝。预测和 post 不调用训练策略。

也可将本目录现成的 `configure_variant.py` 复制到研究目录后执行：它保留已有 inputs.rawprep，设为四次更新并显式启用网络、损失、能量和三个训练变体。先填写输入来源；脚本会修改复制目录的配置，执行前可直接编辑脚本中的参数。上面的带协议/名单参数代码是另一份数据路径配置示范，勿混用参数约定。
