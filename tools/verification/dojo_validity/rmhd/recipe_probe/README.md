# JOREK recipe 主控工程验证

此工具验证“复制完整案例→改写阶段→注入用户组件→框架训练”的可行性，不是正式实验执行器，不提供隐藏评价。

- `setup.py --root <dojo_train下新证明目录> --source <旧实验目录>`：实际调用copy_example物化wdno.burgers_base，再覆盖overlay；保留base-example与来源回执。目标网络/初始权重来自已冻结来源，非Dojo原有算法。仅对新目录执行，不覆盖研究中的修改。
- `overlay/`：阶段正文和局部组件；pipeline来自原完整example。rawprep只消费source下train/validation原始归档；trainprep自行拟合统计与物化。
- `verify.py --help`：独立原始科学更新、统计与新进程恢复验证。需要MPS与原始训练/验证材料，失败日志保留。
- `audit_blocks.py --study <旧主控study> --proof <本证明目录>`：按旧审计器原口径统计293行，输出新/旧/完整复制案例；包含用户组件，不将自写组件追认为已有Dojo源码。
- `implementation_coverage.py`：`ImplementationCoverage(产品包根映射)` 的 start/stop/save 采集当前进程实际调用函数及执行行，按文件行号去重。排除未调用工具、模块/类导入声明和第三方实现；完整函数体包含未走分支，不可将结果当最短重写量或插桩性能。

所有Python入口通过`uv run --no-sync python`运行。物化后从case/pipeline.py执行；用`--set pipeline.stages=[rawprep,trainprep]`准备，再以显式`inputs.train.preparation`连接；独立infer用`inputs.infer.preparation`与`inputs.infer.checkpoint`，post只读固定结果。运行与数据根显式落dojo_train，配置不写入安装包。

这不是新的官方可安装JOREK案例，未重做原五轮选优或可信隐藏裁判。实际完整500epoch、恢复、变体与资源交付证据见[验收记录](../../../../../.context/mvp/jorek-rmhd-recipe-proof-acceptance.md)。
