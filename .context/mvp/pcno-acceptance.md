# PCNO 代码集成与短预算验收

2026-09-20。按用户最新授权，停止长训练，先集成再做验证性短训。PCNO代码闭环和本次短预算数值对照已通过；全仓兼容性不宣称全绿，圈定回归中的两项其他外流案例问题仍存在，详见下文。原250轮训练不再是本次前置，也不会自动恢复。

## 停止与范围

原运行在停止检查时已无存活进程，遗留running标记已修正；压力18完整轮次/最后392更新，温度17完整轮次/最后370更新。检查点保留，证据为 `/Users/zonghui/work/project_simulation/dojo_train/pcno/reference/stop-record.json`。旧验收文本保留为 `code-validation/acceptance-before-code-integration.md`，不再将旧“正在训练”当成现态。

源代码 `/Users/zonghui/work/new_code_project/PCNO/capsule-8000337-code/` 与数据 `/Users/zonghui/work/datasets/undergroundwater_CMG_24data/` 的科学文件未修改。Code Ocean capsule 8000337 v1，commit dc4cd4417ed7f97715ffb47496690ce60f7665a3，GPL-3.0。

当前每分支21次更新（一轮21训练/3轮换验证），四维模态均为1、宽度8、CPU4线程，保持80×80×5×21完整网格、作者统计量和250轮损失/学习率日程。物理权重阶段没有为短训压缩。Python3.12.14、torch2.8.0、numpy2.3.2、pandas2.3.2、iapws1.5.4。官方容器Python小版本不同，本次为同一本机环境内原实现/Dojo对照。

训练前依据首轮实测估算两侧双分支约12–15分钟，另留推理、恢复与扩展余量。未修正Dojo一轮双分支377.9秒；修正后复跑547.1秒，参考温度修正版373.2秒（并行负载不同）。本轮从首次准备17:51至收尾约18:30，含数值问题定位、失败重试、全部预测、Task和扩展，仍低于三小时；该窗口不包括此前已停止的长训练与前置评估。

## 原版数值问题与明确修正

未修正温度训练在第6次更新 `chunk_07/2` 首次出现NaN梯度，预测温度范围约−93.99至203.35℃。黏度的未选中分支对负底数做分数次幂，前向选择有效值但反向仍被NaN污染。源码 `nan_to_num` 随后使损失维持有限，因此仅看损失不能认定训练正常。

`temperature-diagnosis/invalid.json`、未修正版 `reference-temp/`、原Dojo运行 `2026-09-20T17-53-10_e234a2` 均保留；该温度检查点和从它产生的早期预测不作为有效模型结果。没有把两侧同时NaN判为一致。

当前仅在黏度未激活分支使用安全自变量，活跃分段公式和前向值保持不变。原源码文件不改，参考通过 `numerical_repair.py` 在内存显式修正，Dojo记录同一修正；额外检查非有限梯度与权重。前向与有效分支导数测试通过。本次温度结论为“与经过明确最小修正的参考一致”，不能称未经修正原版。

## 已交付能力与使用入口

- core：四维谱卷积、三维U-Net、全局融合、时空监督与物理损失、水物性/井筒/经济计算、可恢复轮换流、地热数据交接、联合预测和固定结果评价。
- contrib：PCNO原权重布局与构造、CMG发布数据适配、原统计与日程、分支目标、训练及结果连接。默认模型依赖为 `ai4e-contrib[pcno]`。
- `recipes/pcno/`、`examples/geothermal/pcno/`：处理、准备、两个分支训练、联合推理、独立post。默认21更新，原版权重仅导入权重，完整Dojo检查点才可精确恢复。
- `examples/recipe_extensions/pcno/`：兼容构造器替换、实际初值变化、插入温降计算、保存K单位数组、下游读回。Task与直接入口使用同一正文。
- core/contrib/spec/task实际wheel安装在隔离研究环境，正式主环境和8000/5173未重装、未重启。本次无Web范围。

## 实际证据

统一根 `/Users/zonghui/work/project_simulation/dojo_train/pcno/code-validation/`；汇总 `delivery.json` 保存环境、wheel摘要、状态与证据引用。

1. 原版压力与修正版温度分别21次更新，对照Dojo运行 `2026-09-20T18-06-28_59d0a4`。`repaired-pres-parity.json`、`repaired-temp-parity.json`：模型、AdamW、调度、Python/Torch随机流、分片顺序及逐次损失通过rtol=1e-5/atol=1e-6。`pres-gradient.json`、`temp-gradient.json`：完整网格首步各分项与裁剪前梯度通过同容差。
2. `recovery/comparison.json`：真实两个分支固定2次更新目标，第1次更新后中断再恢复，与连续运行的权重/优化器/调度/历史/游标/RNG逐值一致。分片边界及49→50、79→80、109→110轮状态交接为针对性状态测试；没有声称实训至这些轮次。
3. 24例固定预测：`data/2026-09-20T18-17-31_c6d16a/infer/results.json`；18例新预测：`data/2026-09-20T18-17-32_a5c2ff/infer/results.json`。全例均已读回校验，18例无精度。`prediction24-parity.json`、`prediction18-parity.json` 对每组首末案例用原模块同权重独立核对两场、物理残差及所有井级量，共4例，不扩大为42例逐一重算对照。
4. 作者18例回放 `data/2026-09-20T18-07-37_d2b5fd/post/technical_economic.csv` 与附带CSV逐字节一致，SHA256 `74564184caf628c4086ff56c0c49c5dd75125298d26829a0aa76d45dfe787357`。独立post修改capacity_factor=0.8后表格实际改变；没有重新运行网络。
5. `task-replay-status.json`、`task-training-status.json`：Task作者回放、双分支2更新/预测/post均成功。Task两次更新状态与direct连续两次更新逐值一致。`release-status.json`：最终安装包物化的扩展示例经Task执行infer→analysis→post成功，新单位字段与温降数组被实际消费。
6. `extension-runs/2026-09-20T18-18-25_9b2f92`：本地网络替换、各1次更新、2例新预测、温降保存读回及post；构造器身份和实际权重变化均有证据。

## 学习效果与未定义经济值

24例只是训练集合回算，不是独立测试。第1—20年先按例计算再等权：压力MAE约8.411MPa、RMSE8.745MPa、MARE0.2824；温度MAE约46.98℃、RMSE52.75℃、MARE0.5333。这说明短训尚未学好，不可用于生产预测。

未成熟预测可能有负焓，经济对数、零发电量除法或恒定评分会出现来源程序的警告/未定义值。保留原表计算，当前post另报告 `economic_undefined_cells`；中间警告不必然意味着最终表格缺值。不把这些结果称为有效经济预测。24例轮换验证也不是独立测试；18例发布场与预存预测相同，没有独立真值；9450例论文实验、论文精度及充分收敛均未验证。

## 测试与剩余限制

- `final-tests.xml`：60项PCNO、共享训练执行及固定公开用户代码/实际wheel用例通过，0失败、0跳过。圈定 `test_pcno_*.py`、`test_training_execution.py`、`test_public_api_stability.py`。
- 训练策略回归3项均通过：WDNO在PCNO隔离环境执行，AB-UPT两项在已有图依赖环境配合隔离wheel执行；不改变主环境依赖。缺依赖的首轮失败保留，不计为通过。
- 案例/资源/公共配置回归首轮25通过、3失败。其中Task安装因隔离环境无torch_geometric失败，改用现有图依赖环境与实际wheel复验通过，见 `task-install.xml`。
- 剩余2失败属于当前工作区其他案例：`test_aero_public_inputs_preserve_domain_defaults` 的外流配置将data_root放入recipe代码目录；`test_declared_recipe_stage_files_are_byte_identical` 的 `aero_cfd.nasa_crm_meshgraphnet/rawprep.py` 与所声明公共模板不同。未为PCNO改写这些并行工作，故不能宣称全仓验收通过。
- 未运行全仓测试、全仓mypy/Sphinx、Web冒烟或250轮训练。当前使用范围为本机Python/Task发布小数据代码集成验证。末次源码/文档/完整案例复验12项通过，见last-tests.xml。可直接使用的本机目录为 `/Users/zonghui/work/project_simulation/dojo_train/pcno/study/`，已绑定数据并通过公开入口dry-run；实际计算证据仍以以上运行记录为准。
