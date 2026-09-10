# Recipe 五段配置与运行快照职责验收（2026-09-09）

本轮配置与框架功能验收通过，真实 MPS 两轮与同进程后处理通过。Noether 产物契约比较通过；跨框架数值一致性未确认，不能将这三项合并为数值等价。

## 当前职责与接口

- recipe 的 configuration.py 解释 rawprep/trainprep/model/train/post 五段配置，合并覆盖、展开组件默认、解析路径；阶段调用提取原库参数副本。rawprep.py 仍调用库 datapre 方法。
- run.launch 的可选 config_loader 接收配置路径和覆盖；未提供时保留旧外流解析兼容入口。兼容路径解析位于 application，不认识五段布局。
- run 在开始阶段前复制冻结最终用户配置；检查点 effective_config 与 inputs/config.yaml 一致。record_config 仅允许同内容确认，业务装配不再写回内部参数。
- 实际来源、清单和分片进入 summary.reports.dataset。准备、训练和后处理的动态引用继续进入已有业务交付及比较协议。
- run.execute 的可选 settings 显式传递给保存预检；recipe 提供提取后的业务设置。预检不再误读新用户分组而回到拟合统计默认。
- task 的两个采样选择器和统计输入绑定改读新路径；任一已声明比较条件缺失即标 missing，不因双方空值相同而判可比。

不改变模型网络、原子计算、默认预算、采样次序及数值容差；不新增检查点版本或旧产物禁用规则。本轮使用新数据输出目录重新准备和训练。

## 相关测试

结果保存在 [config-regroup-results](config-regroup-results/)；不同组存在交叉，不累计为独立用例总数。

- [基线](config-regroup-results/baseline-tests.log)：3 passed，配置展开与代码快照。
- [主要相关回归](config-regroup-results/final-tests.log)：108 passed、6 skipped。覆盖新配置、快照、参考读取，以及案例、日志、准备恢复、后处理、框架正确性和归一化数据。
- [真实硬件补验](config-regroup-results/device-tests.log)：7 passed，包含上述 6 项硬件跳过用例以及一个 CPU 搬运用例；覆盖 MPS 搬运、邻域回退、随机状态和查询。
- [任务及入口](config-regroup-results/task-regressions.log)：20 passed，包括真实小案例 new/fork、任务资产、执行、比较及文档。
- [归一化及参考](config-regroup-results/normalization-reference-tests.log)：76 passed，包括物化、冻结记录、参考算术及协议门禁。
- [训练兼容](config-regroup-results/training-compatibility-tests.log)：8 passed，包括 Transolver 更新、恢复、训练中断与入口初始化。
- [独立安装](config-regroup-results/installation-tests.log)：1 passed。四个实际 wheel 安装到源码外环境，核对产品包加载位置并执行任务管理入口。
- [静态检查](config-regroup-results/lint.json)：本轮 31 个 Python 文件通过 Ruff check 与 format --check。

底层回归夹具继续使用原业务结构；测试辅助函数显式转换到新案例配置后才调用复制脚本。新增通用加载测试使用两种无 aero_cfd 字段的布局，证明 run 不判断五段业务键。新增仅测试分片配参考统计用例验证预检交接。

## 正式复制案例

[复制配置](config-regroup-results/copied-config.yaml)只改原始数据位置、数据输出位置、运行根和设备为 MPS。保留官方 889 个样本（789 train / 100 test）、seed 42、正式网络、双域默认采样预算、两轮及查询块长 16384；完整网格仍使用默认测试下标 [0]。

[完整日志](config-regroup-results/full-mps.log)显示原始处理、准备、训练及后处理同进程完成。训练 2 轮、1578 次更新；评估和预测各完成 100 个测试样本，完整网格完成 1 个样本的表面与体积两个文件。

[实跑检查](config-regroup-results/full-acceptance-checks.json)：表面 3586 点、3584 面；体积 29498 点、26112 单元。summary.reports.post 与 post-progress.json 相同。[快照检查](config-regroup-results/snapshot-check.json)确认五段输入快照与最终检查点 effective_config 完全一致。

[仅网格配置](config-regroup-results/mesh-only-config.yaml)使用本轮检查点，关闭评估、锚点预测与兼容点云，输出到独立位置。[补跑摘要](config-regroup-results/mesh-only-summary.json)仅含 post，没有启动训练或产生新检查点。原来 900 个锚点文件的内容哈希未改变。随后再次运行同一配置，[覆盖保护](config-regroup-results/overwrite-rejected-summary.json)按预期失败，定位到表面网格保存，未将已存在文件冒充本次成功交付。

短训证明本轮正式规模配置的流程与交接可执行，不代表收敛、泛化或论文精度。耗时仅是本机此次执行记录，不作为性能结论。

## 配置与对照证据

[业务参数比较](config-regroup-results/business-equivalence.json)：从修改前源码归档读取原配置，除外部阶段名改为 rawprep 外，新旧完整生效业务参数相等。

[实验条件比较](config-regroup-results/experiment-equivalence.json)：与前次 Dojo 正式 MPS 验收的数据、分片、归一化、模型、初始化、采样、绑定和训练声明全部一致。这是实验条件核验，不等于预测值或训练轨迹相等。

[Noether 契约比较](config-regroup-results/noether-contract.json)：100 个样本通过；已比较坐标、拓扑、身份及真值差异为零，不比较预测数值。[数值门禁](config-regroup-results/noether-numerical-gate.json)因历史参考缺少协议返回 not_comparable；本轮没有建立新的跨框架同条件数值基线，未声称数值等价，也未放宽容差。

## 来源与交付位置

[加载来源](config-regroup-results/loaded-source.json)核对本轮受影响的 core/task 模块与安装副本一致；[最终源码指纹](config-regroup-results/source-final.json)列出本轮修改文件。仓库无 Git，基线通过文件摘要与源码归档保存。并行的其他模型实施不属于本轮改动范围。

主运行：`/tmp/dojo-regroup-20260909/runs/2026-09-09T18-40-50_fb0006`。

仅网格运行：`/tmp/dojo-regroup-20260909/runs/2026-09-09T22-11-31_996a37`。

覆盖拒绝运行：`/tmp/dojo-regroup-20260909/runs/2026-09-09T22-12-41_26bac8`。

大型原始输出、检查点和源码归档保留在上述临时实验目录；本仓库保存配置、摘要、日志、协议及检查结果，未复制大体积权重。临时目录清理后，大型产物需按配置重跑生成。
