# PCNO 圆柱泛化实施结果

日期：2026-09-21。Double Cylinder 已完成代码集成及本轮短预算验证；CylinderFlow 因约束准入失败停止，整体双案例计划未全部完成。

## 已交付

- 核心二维时空谱/U-Net、交错散度/三角梯度、流式统计、固定窗口评价；贡献侧数据与分支连接。
- Double Cylinder：5条训练、1条留出验证，四谱块/宽度8/模态4，Adam 0.001，seed7，CPU4线程。
- 共同100次预热；监督与物理流体分支各达到500次更新，结构分支500次；源网格128×128，历史3、预测12、间隔10。
- 验证起点0/120/…/840，共8窗口、96个目标时刻。没有独立测试轨迹，不是全轨迹滚动预测。
- 实际wheel外部安装、direct/Task同正文10次短训权重最大差0；预测在约定容差内一致。替换构造器、8次预算、物理权重0.2及速度模长保存/消费已真实执行。
- 原网格恢复实验覆盖2/4/10更新，即预热及爬升边界；模型、优化器、损失历史与连续训练一致。
- 最终wheel从正式500次权重读回预测，并经Task独立后处理，对照通过rtol=1e-5、atol=1e-6。

## 学习效果

以下顺序均为速度u、速度v、压力，单位为发布数据单位，空间按有效网格点计权，先按轨迹汇总；本例只有一条留出验证轨迹。

- 末帧保持 RMSE：[0.12599578185973884, 0.156325627682057, 0.21219965049316555]。
- 监督模型 RMSE：[0.06100306990226201, 0.05126359539474273, 0.1042082130687815]。
- 物理模型 RMSE：[0.06156410126038898, 0.05126683233643421, 0.10523480956479019]。
- 监督/物理散度RMS：0.011622041 / 0.008911994，后者降低约23.32%。
- 结构分支SDF RMSE：0.007563118；末帧保持为0.008859307。SDF按来源除100后的单位。
- 物理项改善了相对监督模型的连续性，但三个流场分量RMSE略升；不声明提升预测精度。两组流场误差均低于初始化和末帧保持。
- 预测散度仍明显大于真实标签及末帧保持，不能称为满足精确不可压缩条件；单种子小数据不支持论文精度或显著性结论。

## CylinderFlow 未准入

官方8/2/2完整轨迹已下载并校验，保留600帧和原始字段/网格，总约155MiB。固定P1三角形梯度算子在8条训练、2条验证上的散度/梯度比5.57%—7.14%，超过预定1%。
因此没有执行网格映射、训练或物理收益验证，没有用测试标签调参，没有登记可训练standalone案例。该结论针对候选离散算子，不表示原CFD数据违反不可压缩方程。下一步需追溯COMSOL速度表示或考虑经验证的相容弱形式，不能事后放宽门槛。

## 时间与测试

正式配对续跑388.96秒；此前完成100次预热后因writer标签错误失败25.96秒，已从保存状态续接，没有丢弃失败记录。测速25次7.11秒，真实恢复17.28秒，首次安装/direct/Task/扩展85.69秒。
公共运行日志去重累计535.68秒，含失败和复跑；pytest、构建及下载等待另记，不把开发耗时称为训练时间。训练验证保持在三小时内。
最终圈定78通过、0失败、0跳过，见final-tests.log；新增及修改代码ruff通过。未跑全仓、全仓mypy/Sphinx或Web。
另轮扩大兼容检查的未通过项保留：WDNO缺pytorch_wavelets、GenCP缺timm；两项既有Agent帮助文字断言不符；外流默认输出位于代码目录的配置测试失败。这些不计通过，未改写并行功能或原基线。

## 清理与继续使用

按22项明确生成路径清理，回收1,164,503,510字节，约1.08GiB。原始六条HDF5及官方12条记录保留；最终三分支权重、当前完整恢复依赖、配置、完整指标、两个代表性预测窗口、wheel及可用研究环境保留。
清理后重新校验来源摘要、最终模型加载、恢复依赖与代表性固定结果后处理。完整8窗口指标在evidence；retained中的2窗口不能当成重新完成全量评价。

- 可用案例：`/Users/zonghui/work/project_simulation/dojo_train/pcno/cylinder-generalization/study/config.yaml`（默认使用已有权重执行infer/post）。
- 运行解释器：installed-env/bin/python，第三方依赖复用既有PCNO参考环境，产品包来自本轮实际wheel。
- 原始子集：raw/cylinder_flow；候选算子报告：cylinder-flow-admission.json。
- 完整指标/安装证据：evidence/；最终包摘要：environment.json。
- 清理范围和结果：cleanup-ledger.json、cleanup-result.json、post-cleanup.json。

复跑示例：

```bash
uv run --no-sync --no-project --python /Users/zonghui/work/project_simulation/dojo_train/pcno/cylinder-generalization/installed-env/bin/python python /Users/zonghui/work/project_simulation/dojo_train/pcno/cylinder-generalization/study/pipeline.py --config /Users/zonghui/work/project_simulation/dojo_train/pcno/cylinder-generalization/study/config.yaml
```

正式8000/5173与主环境未操作；论文完整复现不在本轮范围。

证据根：`/Users/zonghui/work/project_simulation/dojo_train/pcno/cylinder-generalization`。
