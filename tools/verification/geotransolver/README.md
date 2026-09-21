# GeoTransolver 工程验收

本目录是验证工具，不是框架运行依赖。PhysicsNeMo固定aa19b58a129f8d1fabdcaa41c6ca85d5dc01aae1；参考定义独立加载，不从Dojo导入数值实现。普通运行仅依赖四个Dojo wheel及已声明第三方依赖。

- `budget.py`：持久累计账本，包含测速、准备、失败重试、两侧训练与评价；160分钟后禁止新训练，180分钟硬截止。单次进程提前预留Task收尾时间，孤儿记录需核实后才能继续。
- `vendor_sources.py`：锁定版本数值定义的初始迁移；重新生成前应核对现有本地修正，不得覆盖已维护实现。
- `reference.py`、`reference_patches.md`：独立原类/函数、CPU邻域执行和科学协议修正说明。
- `audit_preparation.py`：全部原始MAT/VTP与独立上游读取、统计对照。
- `compare.py`：完整结构的固定容差前向、逐层、梯度及单步更新对照。
- `benchmark.py`、`run_acceptance.py`：正式网格、完整网络两侧更新测速及准备审计。
- `train_pairs.py`、`reference_train.py`、`evaluate_pairs.py`：冻结预算、成对训练、全量物理评价和最终状态比较。`continue_pairs.py`是本次报告交接失败后的显式恢复记录，保留原失败目录，不重新执行已完成训练。
- `install.py`、`installed_replay.py`、`task_replay.py`、`asset_replay.py`：独立wheel安装，外部复制/direct-core/Task/恢复/派生能力及固定结果隔离消费；公开共享/派生API复制完整准备、权重及结果，隔离来源后继续执行。
- `write_recipes.py`：仅初次脚手架，已有目录拒绝覆盖；最终正文由recipes和examples显式维护。

本机原始数据位于用户datasets目录，所有生成数据和工具缓存位于dojo_train/geotransolver。所有数值命令通过同一预算入口串行执行。论文对标与工程一致性分别报告，短训不使用原Transolver 0.0057或135例保险杠论文成绩作通过结论。
