# JOREK RMHD 双组实验工具

这是主控工具，不是交给实验 Agent 的训练模板。Neumann 旧入口与结果保持原样。

2026-09-22 的 [recipe 工程验证](recipe_probe/README.md) 独立于正式比较：主控实际复制 example，用公开用户组件实现 JOREK，核对完整训练、恢复和代码复用。它不启动实验会话，也不读取隐藏测试。

顺序为 `prepare → preflight → materials → probe → run → evaluate → summarize`。所有命令使用：

```bash
uv run --no-sync python -m tools.verification.dojo_validity.rmhd <命令> --comparison <主控比较目录>
```

`prepare` 改用 `--base <dojo_train> --data-root <原始JOREK目录>`，返回独立比较目录。preflight只消费训练/验证，固定500epoch；失败不启动正式组。materials只交网络、初始化、协议、原始分片和通用安装材料，组内环境和派生数据仍由Agent实际创建。

probe验证实际组工作根、独立临时MPS诊断环境及公网代理；诊断环境随后删除。还必须保存 `evidence/worker-check.json` 与 `evidence/cli-capability.json` 的实际通过证据，验证冻结预测、无真值/断网边界、CLI工具/原session续接及请求usage。不能手写passed绕过验收。

run为单组创建新CLI并串行调度双方round00和五轮，组内保留session。失败继续原session，开发验证可反馈，隐藏评价不能进入run。两组最终选择锁定后，evaluate独立复制环境，以只读冻结提交、当前历史输入和无网络worker预测，主控FP64复算。summarize只写比较目录。

统一提交接口、抽样序列摘要和baseline证据要求由materials交付的SUBMISSION.md定义。逐组第一条提示仅增加Dojo组的GUIDE入口。Dojo使用可选，学习计编码成本。

Seatbelt仅允许明确系统运行时、组根或冻结候选；系统GPU驱动是只读前提。公网经每次CLI专用代理，拒绝本机/内网/保留地址；VPN合成DNS地址通过固定公共HTTPS DNS解析为核过的公网数值IP。TLS内容不检查，不能把域名记录当作无污染证明。

隐藏推理采用父进程计时和固定数值数组交换，50ms包含同口径通信拷贝开销。加载与归档另计。共享数组不包含未来真值，评分器不import候选。候选跨请求缓存预测、查表或干预计时属于协议违规。

圈定测试：`uv run --no-sync pytest tests/integration/test_dojo_validity_rmhd.py tests/integration/test_dojo_validity.py tests/integration/test_dojo_validity_cli.py`。工具验收、预实验和正式五轮须分开陈述。

每次CLI新建/续接的权限取自主控比较配置，并核验组内protocol初始摘要。组内改写路径不能增加授权。评价时钟与窗口起点分开保存；保持最后帧及逐场改善只作诊断，主指标不变。

隐藏评价器本身也检查双方最终锁定，然后重核测试来源摘要；不只依赖命令行门禁。冷启动与预测归档单列。`scientific_runs_complete` 与 `cost_evidence_complete` 分开；估计区间、训练内未分离验证、未知重试usage不能追认为完整成本。已完成的实际两条轨迹及报告入口见仓库 `.context/mvp/jorek-rmhd-validity-acceptance.md`。

## 单组 Skill 改进研究

`uv run --no-sync python -m tools.verification.dojo_validity.rmhd.skill_study` 提供 `prepare/probe/deliver/round/select/hidden`。`prepare --source <已有主控科学材料> --base <dojo_train>` 仅继承网络初始化、科学设置、原始 train/validation 包及通用安装材料；创建全新组级根与独立主控根，不读取旧研究代码来准备新组。它复用原隐藏分片，因此报告必须注明重复使用 holdout。Dojo wheel 重新构建，框架在本次五轮中冻结。

每轮通过 `deliver --root <主控根> --number N --rationale <依据>` 冻结 Skill；`round` 执行本轮后暂停。继续下一轮前主会话填写 `reviews/round-NN.json`，用固定 13 类职责审查 Dojo、Web 参考和实际调用证据，区分直接复用、框架变体、有理由自写、可复用却自写、不适用和未知。计量的是职责覆盖，不是 import 次数。Skill 只在轮间更新，Guide/帮助及框架 API 保持初始版本。

`select` 要求六个候选和六份主会话审查齐备，锁定最终选择与独立环境；`hidden` 检查单组最终锁与来源摘要，无隐藏反馈或重选通路。此研究评估一条连续、适应性指导的轨迹，不能据此作 Skill 的因果对照结论。

隐藏评价完成后，`uv run --no-sync python -m tools.verification.dojo_validity.rmhd.skill_report --root <主控根>` 输出报告、逐轮数据及科学曲线。训练进程区间与内部验证补充时钟分开，后者必须落在主控观察到的训练区间内，仍不冒充独立计量。未报告的重试 usage 与未采集的主会话开发成本保留未知。

## 固定Skill四会话对照

`factorial` 是独立协议入口，BP/BD提供同一U-Net，NP/ND不提供模型建议；两Dojo组使用同版冻结Skill和wheel。不会在轮间升级Skill。主控先建立私有分片与完整真实预实验，再执行 `python -m tools.verification.dojo_validity.rmhd.factorial materials --root <比较目录>`，为四组交付独立原始副本；此命令不覆盖已有材料。所有Python入口以 `uv run --no-sync` 启动。

随后 `factorial probe` 验证四组权限与MPS；`factorial_precheck.check_cli(root)` 实测新建/恢复及原始usage，`check_inference(root)` 实测无真值/断网隔离预测。全量初始摘要复核并保留真实门禁收据后才设为ready。`factorial run` 串行完成四组六轮并锁最终选择；启动失败不能通过手填passed解决。运行中断使用原根再次run，保留同组session和已冻结轮次。

`factorial hidden` 在四份最终选择全部锁定后才评分24份冻结候选，各轮依赖环境独立冻结。`factorial_report --root <比较目录>` 只在隐藏评分完成后汇总；缺成本或复用审计仍明确partial。`factorial_audit`按有证据的源码位置并集计量；`trace_replay`供主控在副本重放训练/验证，函数体与本地顶层执行分开保存，不用于计时、不执行隐藏输入。复用审计和报告不自动回写实验组。

逐轮审计写入主控`reuse-audit/<组>/round-NN/summary.json`：`responsibilities`保存职责分子、分母与未知上下界；`whole_pipeline`、`prediction`分别保存`reuse_sets`返回的代码量与位置集合。`trace_positions`核源码摘要、排除纯import/原样给定模型并去重重复路径；复制来源必须另有逐块来源映射，不能靠语义相似自动认定。报告同时交付逐轮/累计编码成本、验证/隐藏六场图、双范围复用与代码体积图及`detail-series.csv`；缺审计的点为缺口。

`trace_replay`另记录并排除处于CPython frozen importlib调用栈中的导入副作用；同一函数之后由科学流程实际调用仍计入。该过滤不等于证明所有动态加载器行为均已覆盖，运行线程/子进程范围仍按实际追踪声明。

圈定 `test_dojo_factorial.py`、`test_dojo_validity_rmhd.py`、`test_dojo_validity_cli.py`、`test_dojo_implementation_coverage.py`、`test_dojo_skill_study.py`；四组真实执行状态见仓库 `.context/mvp/rmhd-factorial-acceptance.md`。

计账列出已结束CLI尝试内只有started、没有completed收据的活动，保持终点与退出码未知并将账本标为partial。后续恢复成功或token总量对账成功不能补齐被中断的阶段；尚在运行的CLI活动不提前判为中断。历史原始证据不改写。

有事件流但缺少整个CLI进程收据的尝试另列`unclosed_cli_attempts`，标为仍运行或已中断、无法仅凭文件判断；最后事件时间仅为观察锚点，不是退出时间。即使后续续接已找回请求usage，也不能把这个时间证据缺口标成完整。

续接CLI的`turn.completed.usage`可能累计历史请求，不逐轮相加。`usage_reconciliation`按各快照末端连续请求核对汇总，输出每份摘要覆盖的request IDs及其并集`cli_covered_request_total`；无法匹配或覆盖的请求显式列出。旧`cli_turn_total`求和字段撤除，原始历史报告保留，当前报告可由原始流重新生成。

主控可用`runtime.clone_verified_file`优化已冻结环境中完全相同的运行库：仅当内容摘要和扩展属性相同，才原子替换为独立inode的写时复制副本，保留原模式与时间并记录收据。它不改研究工作区、候选或权限；失败保留原文件，不能把逻辑字节量当实测回收空间。主控代码调整、预实验和已作废尝试的成本单列，未完成对账保留未知。
