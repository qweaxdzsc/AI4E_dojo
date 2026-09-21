<!-- dojo-help: {"case_ids": ["parametric_pde.neumann_diffusion"], "domain": "parametric-pde", "kind": "workflow", "layer": "workflow", "summary": "从 parametric_pde.neumann_diffusion 完成 direct-core、组件变体、Task 和证据读回。", "tasks": ["选择案例", "直接运行", "组件变体", "Task 托管", "证据读回"], "title": "参数化 PDE 研究流程", "topic_id": "workflow:parametric-pde"} -->
# 参数化 PDE 研究流程

本流程以 `parametric_pde.neumann_diffusion` 为可执行起点，适用于网络、方程损失、初边值约束、物理采样和训练策略研究。smoke 数据只证明接线和恢复，不证明 PDE 精度。

## 1. 搜索并选择案例

```python
import ai4e_task as task
case_id = 'parametric_pde.neumann_diffusion'
print(task.search_help("Neumann PDE sampling recovery", limit=10))
print(task.read_help_topic("case:" + case_id)["content"])
assert task.check_example(case_id)["ok"]
task.copy_example(case_id, "./neumann-study")
```

阶段顺序是 `generate → rawprep → trainprep → train → infer → post`。逐个阅读 README、`config.yaml`、`configuration.py`、`pipeline.py` 和阶段脚本。

## 2. 生成或绑定输入

最小数据可显式生成：

```python
from pathlib import Path
import ai4e_task as task

data = task.create_smoke_data(Path("./neumann-study/data/neumann-smoke"))
print(data["manifest"])
```

把生成的 manifest 写入 `inputs.rawprep.manifest`、`inputs.trainprep.dataset`、`inputs.train.dataset` 和 `inputs.infer.dataset`。同时把 `run_root` 与 `data_root` 指向研究目录外或案例自己的受控输出目录。

## 3. direct-core 建立基线

从案例目录外执行，证明入口不依赖 cwd：

```text
python /absolute/neumann-study/pipeline.py --config /absolute/neumann-study/config.yaml
```

也可以用 `--set train.max_epochs=2 --set train.device=cpu` 缩小工程预算。运行后检查 `runs/.../inputs/config.yaml`、`summary.json`、阶段报告、`checkpoints/`、`data_root/infer/results/predictions.json` 和 `data_root/post/metrics.json`。

## 4. 固定 preparation 后运行独立阶段

`trainprep` 报告返回 `preparation.json`。独立训练必须显式设置：

```yaml
pipeline: {stages: [train]}
inputs:
  train:
    dataset: /absolute/data/manifest.json
    preparation: /absolute/data/trainprep/preparation.json
    resume: null
```

独立 infer 绑定相同 dataset/preparation 和固定 checkpoint；独立 post 只绑定 `inputs.post.results`。不要让 train 或 infer 隐式重新生成 preparation。

## 5. 替换真实组件

可修改 `components.model`、`train.step`、`model.constraints`、`model.sampling`、优化参数或 `post.py`。先用 `describe_help_symbol` 核对实际接口：

```python
for symbol in (
    "ai4e_contrib.ability.model.pibsnet.component.step",
    "ai4e_core.abilities.constraint.physical.residual_loss",
    "ai4e_core.abilities.sampling.physical.sample_points",
):
    print(task.describe_help_symbol(symbol))
```

用户 `train.step` 接收 model 与一个已准备实例，返回包含标量 `loss` 的字典。改变采样、字段或模型语义后重新执行 trainprep，并从头训练不兼容检查点。

## 6. 证明组件调用

读取最终配置中的组件路径和权重；从 preparation contract 读取模型与采样身份；从训练报告读取命名损失、epoch/update 和参数变化；从检查点 contract 读取 preparation content ID 和训练协议；从预测清单读取 checkpoint 摘要和数据身份。

## 7. Task 托管同一目录


```python
from pathlib import Path
import ai4e_task as task

project = task.create_project("./study-project")
record = task.new_task(project, "neumann", source=Path("./neumann-study"))
run = task.wait_run(project, task.submit_run(project, record["id"])["id"], timeout=120)
if run["status"] != "succeeded":
    raise RuntimeError(task.read_log(project, run["id"]))
```

Task 捕获同一 `pipeline.py`、配置和外部输入，不生成另一套研究流程。

## 8. 正确恢复

恢复必须消费固定 preparation。先把 Task 配置改为 `[train]`，明确写入 preparation；训练检查点中的 preparation content ID 必须一致。`resume_run` 重放来源运行的代码和配置并注入 checkpoint：

```python
resumed = task.resume_run(project, train_run_id, checkpoint="latest.pt")
resumed = task.wait_run(project, resumed["id"], timeout=120)
```

目标轮次必须大于检查点 epoch。若来源运行配置会重新执行 trainprep，生成了不同 content ID，检查点应拒绝恢复；不要放宽该门禁。

## 9. 推理、post 与比较

把恢复运行的固定 `last.pt` 写入 `inputs.infer.checkpoint`，提交 `[infer]`；再把完整 `predictions.json` 写入 `inputs.post.results`，提交 `[post]`。读回逐样本张量、预测摘要、relative L2、time-relative L2 和 metrics 资产。建立变体时用 `fork_task`，只比较语义相同且已登记的指标。

## 10. 结论边界

短训证明参数进入运行、组件被调用、状态可保存恢复、预测和 post 可交接。学习效果需要预先声明的指标和多轮结果；论文级结论还需要论文数据、协议、预算和统计对照。
