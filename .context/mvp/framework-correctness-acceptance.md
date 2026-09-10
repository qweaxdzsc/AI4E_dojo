# 框架正确性修正验收（2026-09-09）

框架功能验收：本轮受影响范围通过。Noether 产物契约比较通过；数值一致性尚未确认，不能合并宣称“全部等价”。

## 实施内容与边界

- ability：模型输入按非张量、形状、类型、设备、非有限值分别报错，保留异常类型；通用搬运保持整数、布尔和浮点 dtype。
- application：在实际模型设备交接输入；异常附带阶段、操作及真实样本/批次身份，退出恢复上下文。评估、预测、网格分别记录状态和成功交付，首错停止。
- run：writer 写入 post-progress.json；异常收尾保留部分报告，写报告失败不覆盖原始计算异常，summary 使用同一状态快照。
- verification：区分契约、同权重推理、独立训练。校验数据、分片、归一化、结构、初始化、采样、实际输入、设备精度及源码入口；缺证据拒绝数值结论，不放宽容差。条件文件内容纳入数据身份。
- recipe：配置保持输入与实验选择；明确物理特征由 trainprep.use_physics_features 控制，已有检查点可只补网格，覆盖保护继续有效。

未改变训练算法、默认超参数、采样次数、随机流次序及既定数值容差；未新增进程分离架构。

## 回归证据

证据文件均在 [framework-correctness-results](framework-correctness-results/)：

- [相关回归](framework-correctness-results/final-tests.log)：104 passed、6 skipped；覆盖新增诊断/失败注入及既有后处理、训练恢复、配置快照、多域和参考算术。
- [日志与复制入口](framework-correctness-results/logging-tests.log)：8 passed。
- [真实 Apple GPU 用例](framework-correctness-results/device-tests.log)：7 passed，包含上述硬件跳过用例及一个重复 CPU 用例；CPU 检索和 MPS 回退邻域索引一致。
- [条件文件与协议回归](framework-correctness-results/conditions-tests.log)：20 passed，包含两项最后补充的外部条件内容变更用例；与其他回归存在重叠，不累计为独立测试总数。
- [相关 Python 格式与静态检查](framework-correctness-results/lint.json)：21 个变更 Python 文件通过 Ruff check 和 format --check。

故障注入覆盖评估、预测张量、点云、表面网格、体积网格及报告写入；检查原异常、提交路径、未完成计数、pending 状态、上下文恢复和仅网格补跑。

## 真实复制 recipe 验收

[复制配置](framework-correctness-results/copied-config.yaml)只修改原始数据、数据产物、运行目录及设备为 MPS。保留 seed 42、dim 192、depth 6、512 超节点、每域 256 锚点、双域、两轮和查询块长 16384；默认网格样本下标为 [0]。

889 个样本（789 train / 100 test），正式训练两轮共 1578 次更新，同进程进入后处理并成功结束：评估 100、预测 100、完整网格 1 个样本（表面和体积两个文件）。查询表面 3682 点、体积 29498 点；输出表面 3586 点/3584 面、体积 29498 点/26112 单元。短训证明此规模流程可执行，不证明收敛、泛化或论文精度。

[运行摘要](framework-correctness-results/summary.json)的 reports.post 与 [进度记录](framework-correctness-results/post-progress.json)一致。另保存[完整日志](framework-correctness-results/full-mps.log)、training-protocol.json、comparison-protocol.json、baseline.json 和 source-final.json。

原运行及检查点保留在 `/tmp/dojo-correctness-20260909/runs/2026-09-09T14-44-55_bfe5b9`，原始源码归档为 `/tmp/dojo-correctness-20260909/source-before.tar.gz`。大体积数据与权重不复制进仓库；临时目录可能被系统清理。仓库无 Git，基线与运行内源码快照用于追踪。最终额外补充的条件文件哈希仅影响使用外部条件文件的证据记录；正式案例无外部条件，训练行为不受影响，其源码指纹仍按实跑原样保存。

## Noether 对照结论

[契约比较](framework-correctness-results/noether-contract.json)通过：100 个样本的已比较锚点坐标、VTK 坐标/拓扑/身份与真值一致，所记录差值为零。此模式不比较预测数值或指标。

[数值门禁](framework-correctness-results/noether-numerical-gate.json)返回 not_comparable：历史 Noether 运行缺少必要协议，且为历史 CPU 参考，不能证明同一初始化、模型输入和执行条件。此结论表示数值可比性未确认，不表示模型性能差异，也不以设备差异排除代码问题。

本轮未建立新的同条件 Noether 数值基线，因此数值一致性验收未完成。后续必须获取可核验的参考协议及映射后权重/实际输入，再按既定容差比较；不得用契约通过替代数值通过。
