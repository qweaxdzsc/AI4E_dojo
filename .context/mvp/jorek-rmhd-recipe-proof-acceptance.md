# JOREK recipe 实跑与复用审计验收

2026-09-22，主控工程验证。只用训练/验证，未读隐藏测试、未新建正式会话、未修改历史冻结结果或正式服务；未声称官方JOREK模型集成或论文复现。

## 交付与结果

Skill改为完整新任务先复制最接近standalone，按Dojo recipe/训练框架改写，差异通过公开用户组件表达；GUIDE负责能力地图，Help负责详细签名。补齐原已有HDF5、矩统计、数组保存入口，去除只有网络即可跳过案例的旧教程指引。CLI PRD与导航同步。

实际复制wdno.burgers_base，pipeline原字节保留。JOREK六场U-Net通过rawprep/trainprep/train/infer/post；独立准备27.055秒；MPS完整500 epoch、2500更新，训练阶段464.011秒，验证0.4686577902553746，与旧baseline一致。完整40帧数组进出P95为5.899742ms。初次infer资产kind错误保留，纠正后用原checkpoint续做infer/post，独立FP64复算相同。

归一化、前向、梯度及单步权重最大差0；10更新连续与5+新进程恢复到10的模型、优化器、stream、history及四类RNG全部一致。原最终权重复放0.1927037472804363。复制新原型仅改YAML的5更新变体成功，新增Python为0；不是完整旧第五轮训练复现，短训未改善精度。

原49/342=14.33%是调用/导入占比。新原型同规则201/579=34.72%，两者功能分母不同，不能作为严格开发成本对照。完全复制WDNO的调用占比62.94%、来源复用100%；新原型变体Python来源复用100%只证明本次原型支持范围，不能追认为旧版框架已有JOREK。完整293行对照、缺失边界及框架建议见[报告](/Users/zonghui/work/project_simulation/dojo_train/jorek-rmhd-recipe-proof/proof-f6163918-c577-4c22-9ebc-5e8a3f1816b7/REPORT.md)。

## 验证

- `uv run --no-sync pytest tests/integration/test_dojo_recipe_probe.py tests/integration/test_example_contract.py tests/integration/test_agent_help.py -q`：19通过。覆盖配置容器、窗口尾批及恢复、八块梯度、真实writer的infer/post资产交接、帮助导航与导出合同。
- `uv run --no-sync pytest tests/integration/test_task_installation.py -q`：1通过，实际wheel独立安装；新Skill/GUIDE/教程与wheel内容摘要一致。
- 帮助生成器481文件检查、Skill格式校验与新增源码ruff通过。
- 证据根：`/Users/zonghui/work/project_simulation/dojo_train/jorek-rmhd-recipe-proof/proof-f6163918-c577-4c22-9ebc-5e8a3f1816b7`；保留初次失败、重试与科学训练记录。`verification.json`、`final-receipt.json`、`wheel-resource-proof.json`、`code-gap-analysis.json`可核对。

## 范围

没有发现baseline的框架表达硬障碍；尚缺官方JOREK来源/窗口/滚动/模型装配模板。Net2Wider、原raw/EMA选优和余弦策略未完整重做；本次不使用额外框架API实现来掩盖缺失。尚未证明新版Skill对新Agent的因果改进。

## 2026-09-22：共享实现量展开与Skill顺序修订

Skill按“框架+Web形成初案→按初案查工具更新→复核计划和代码的框架写法”更新，统计为可选附属能力。CLI PRD、AGENTS和研究导航同步；GUIDE仍只说明能力，不复制决策流程。

主控插桩实跑70/15原始准备、5更新后恢复到10、验证推理与固定post，追踪29个产品源文件：被调用函数1348有效行，实际走到821行，按文件行号去重，排除未用工具/导入类声明/第三方代码。当地原型579行，展开1927行；加原样pipeline30行后既有Dojo提供1378行（71.51%）。这是同实现源码体积，不是证明无Dojo最短手写量。337行候选充分产品化的固定分母情景为约89%，正式迁移尚未执行。

证据：[展开报告](/Users/zonghui/work/project_simulation/dojo_train/jorek-rmhd-recipe-proof/proof-f6163918-c577-4c22-9ebc-5e8a3f1816b7/implementation-audit/REPORT.md)、coverage.json、comparison.json与reused-source.txt。最初计入导入类声明的版本已明确废弃并保留，回归覆盖该错误。16项圈定测试与1项真实wheel外部安装通过，Skill/GUIDE wheel字节与源一致；未改变正式环境。仓库落点与未来验收见[实施方案](../../.cursor/plans/jorek-reuse-capacity.plan.md)。

## 范围更正：后续优化面向未知任务

用户明确不以JOREK专用集成为下一步目标。上述运行和计数仍是历史事实；337行产品化、89%覆盖仅为先前特定源码情景，已撤出实施目标。后续按[通用复用方案](../../.cursor/plans/dojo-general-reuse-capacity.plan.md)分开处理框架扩展/恢复与基础能力族成组集成，先核实已有能力与真实缺口，再验证跨任务组合。此次只改计划与导航，没有新增框架能力或训练。
