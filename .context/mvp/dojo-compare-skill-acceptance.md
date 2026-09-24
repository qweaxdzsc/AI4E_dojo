# 通用Dojo对照实验Skill交付

日期：2026-09-22。用户要求从既有实验中抽取通用主控技能。本次新增`dojo-compare`，未创建正式实验会话、启动训练、修改研究Skill或重装/重启服务。

## 交付范围

技能入口为`.agents/skills/dojo-compare/SKILL.md`；按需参考为方案骨架和计量/报告说明。发现元数据在`agents/openai.yaml`。不绑定数据集、网络、DOE方法、优化轮数、设备或数值门槛。

主控要求至少有白板与Dojo对照，按用户目标选择数据和起点，区分给定模型、自主选模与成熟工程；原始数据准备由各组完成，正式前安排真实训练/推理预实验。独立会话与整进程隔离需实际验证；冻结干预，最终选择后隐藏推理与可信评分分开。正式报告包含精度、编码时间、编码token曲线及Dojo适用职责、本地来源和实际展开实现量。

仅主控使用此技能，不注入被试会话；既有Task研究资料导出仍只交付dojo-research。未修改导出实现、安装资源或公开API。AGENTS、研究路由、仓库索引及现有CLI PRD同步说明该边界。

## 验证与证据

- skill-creator的quick_validate通过：名称、frontmatter和基本结构合法。
- `tests/integration/test_dojo_compare_skill.py`最终2项通过：整个技能复制到仓库外后所有必读Markdown引用仍在包内且可读；实际调用现有研究指南导出，只有研究Skill，不含主控技能或AGENTS。
- 新测试文件ruff检查与格式检查通过。
- 人工核对：只要设计不启动；没有指定模型时不夹带推荐；预算/设备/阈值待本次确定；缺usage不画零值；import展开去重且不声称最小手写节省；失败组和延迟不合格候选保留。此为正文审查，不是独立Agent行为实验。

最终测试收据：`/Users/zonghui/work/project_simulation/dojo_train/dojo-compare-skill-validation/20260922-final-v3.xml`。首次pytest因basetemp父目录不存在而在夹具阶段报错，创建证据父目录后重跑；初次lint/格式检查发现新测试的导入间隔和断行，已纠正。早期XML保留，不计为通过。

未开展新会话前向行为评测或真实对照训练，不能声称此Skill已提高实验质量或Dojo采用率。无需正式Web冒烟：本次只新增主控文档技能和边界测试，没有Web或训练执行消费链变更。

## 2026-09-23 存储归属修订

按用户要求补充组内保存实体、主控只存索引与摘要的规则；环境按精确依赖和源码修订记录，不逐轮复制实际环境。保留组内候选不可变、引用核验和隐藏评价隔离，明确独有评价产物的单份保存及旧评价器迁移先于清理。方案骨架、报告口径和导航同步。此次只改技能与说明，不改变运行中实验、评价器或磁盘数据。

本次验证：`uv run --no-sync pytest tests/integration/test_dojo_compare_skill.py -q` 为2 passed；本次文档范围 `git diff --check` 通过。现有测试验证技能携带与导出边界，不代表新存储规则已在运行中的评价器实现。
