<!-- dojo-help: {"case_ids": ["wdno.burgers_base"], "domain": "spatiotemporal-pde", "kind": "workflow", "layer": "workflow", "summary": "从 wdno.burgers_base 完成 direct-core、组件变体、Task 和证据读回。", "tasks": ["选择案例", "直接运行", "组件变体", "Task 托管", "证据读回"], "title": "时空预测研究流程", "topic_id": "workflow:spatiotemporal-pde"} -->
# 时空预测研究流程

本流程以 WDNO Burgers 为起点，适用于小波表示、扩散目标、DDPM/DDIM 采样、轨迹派生量和时空评价研究。MeshGraphNet 轨迹预测有独立 recipe/API 说明，数据与训练合同不同。

## 1. 选择案例

```python
import ai4e_task as task
case_id = 'wdno.burgers_base'
print(task.search_help("WDNO Burgers wavelet diffusion", limit=10))
print(task.read_help_topic("case:" + case_id)["content"])
assert task.check_example(case_id)["ok"]
task.copy_example(case_id, "./study-case")
```

## 2. 核对轨迹合同

阶段顺序是 `rawprep → trainprep → train → infer → post`。核对完整轨迹长度、空间/时间轴、训练/验证/测试名单、归一化、小波层级和条件窗口。小样本必须选完整轨迹子集，不能把时间截断冒充同一数据集。

## 3. 阅读真实调用点

`trainprep` 生成可恢复的物理/变换清单；`train` 构造网络、目标、optimizer、scheduler 和 EMA；`infer` 加载固定权重并执行声明采样器；`post` 只读 validation/test 预测。配置中的随机流、seed、更新数和采样步数必须实际进入这些函数。

## 4. direct-core 基线

从案例目录外运行 pipeline。缩小 dim、更新数和 DDIM 步数只用于工程 smoke。读回 preparation、训练更新/EMA、checkpoint、validation/test 预测、样本与时间身份、能量等派生数组、指标和 post 报告。

## 5. 修改组件

物化 `recipe_extensions.wdno`，可以替换 `components.network`、`objective`、`derived`、`optimizer`、`scheduler` 和 `update`。也可修改小波变换或 DDPM/DDIM sampler，但需要同步 checkpoint 和推理合同。默认基础案例不启用这些变体。

## 6. 证明调用

读取配置和来源摘要；对网络/目标核对参数更新与命名损失；对 optimizer/scheduler 核对 step 和学习率；对 EMA 核对保存/恢复状态；对 sampler 核对随机流、步数和输出；对派生量核对保存与独立 audit 读回。

## 7. 固定预测与 post

独立 infer 必须绑定 validation/test preparation 和固定 checkpoint；结果清单同时记录预测、真值、样本 ID、时间轴及派生数组摘要。post 只重算固定结果。修改数组字节后依赖摘要应让 Task 比较不可用。

## 8. Task 托管


把同一目录传给 `new_task`。推荐分阶段提交 preparation、train、infer、post，并把前次报告路径写入当前输入。Task 运行与恢复不创建版本；研究分支使用 `fork_task`。

## 9. 恢复与对照

恢复总目标应在原总训练计划内继续剩余更新；不能先用目标 2 完成，再把目标改 3 并宣称与原目标 3 完整等价，除非调度合同明确允许。固定 preparation、网络、目标、optimizer、scheduler、EMA 和随机状态后，比较连续与恢复预测。

## 10. 结论边界

短训证明参数进入运行、组件被调用、状态可保存恢复、预测和 post 可交接。学习效果需要预先声明的指标和多轮结果；论文级结论还需要论文数据、协议、预算和统计对照。
