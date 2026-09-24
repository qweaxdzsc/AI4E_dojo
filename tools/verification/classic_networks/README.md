# 经典网络统一校验

本工具验证已批准的场网络变体，不是论文复现框架。来源与变体见 `sources.json`，功能边界见仓库 `.context/mvp/classic-networks-acceptance.md`。Dojo训练使用recipe和共享train_model；仅独立参考有自己的Adam循环。

先运行真实rawprep/trainprep，把三案例的physical/prepared路径登记到外部实验根 `evidence/preparation.json`。`run_matrix.py --root <实验根> --device <cpu或mps>` 按十三组合固定顺序运行；`--only <family-case>` 可补验明确受影响项。已经passed的组合不重复训练。每组测速20更新，预算选择100/50/20，同组所有尝试持续计费。设备切换须写明诊断原因，不因设备差异放宽固定容差。

`run_installed.py --root <实验根>` 要求独立wheel已装到 `<实验根>/installed`，逐个复制三完整案例和三组合扩展，实际direct训练/恢复、Task后台执行、搬移准备/权重/结果、独立post。外层统一BudgetLedger持锁计时，子进程按剩余预算终止并清理本次worker；不操作用户正式平台。

验证工具从仓库用 `uv run --no-sync python ...` 执行。生产包使用源码映射或隔离wheel环境，不能以旧主环境可编辑副本冒充当前代码。安装重放自身只从指定wheel环境读包和案例资源，模块路径及worker PID写入报告。

真实证据检查设置 `DOJO_CLASSIC_EVIDENCE=<实验根>` 后运行 `uv run --no-sync pytest tests/integration/test_classic_network_acceptance.py tests/integration/test_classic_network_installation.py`。未给真实目录时跳过只表示没有运行证据，不能计入本批完成。其他组件/数据/边界测试均使用各自明确fixture，不依赖真实源目录。
