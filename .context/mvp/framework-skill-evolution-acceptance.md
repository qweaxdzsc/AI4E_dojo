# 框架承接与案例发现验收

日期：2026-09-22。已实施[第一计划](../../.cursor/plans/dojo-framework-skill-evolution.plan.md)，并复核[第二计划](foundational-capabilities-minimal-acceptance.md)。源码、配套安装包、受控小规模联合流程及正式8000/5173现有训练消费链兼容性验收通过。未开展新一轮Agent采用率对照，不能声称Skill已使采用率提高。

## 本轮实现与上下游

- `fit_iterations`增加可选`checkpoint_every`；未传时保持跟随评价周期的旧行为。`train_model`分别交付两个周期。同一步先执行评价，再保存已经更新的用户状态；最终、中断和零更新保持既有保存语义。
- `train_model/capture_iteration/restore_iteration`新增可选`state_bindings`。每个名称绑定普通save/validate/load函数，无基类要求；可变状态与静态algorithm_state/contract分开。检查名称、版本及全部用户状态后再加载；异常时恢复模型、优化器、随机流、输入流与用户内存状态。某项回滚失败仍尝试其余连接，最终显式报告失败。不承诺任意用户函数的外部副作用可回滚。
- 旧自定义iterate没有新参数时，等周期按旧接口执行；不同周期在训练前明确拒绝。未使用状态连接的旧检查点继续可用；含用户状态的检查点不能由无绑定调用静默丢弃。
- 案例清单增加`research`摘要、数据形态、训练机制、替换点和限制。`list_examples`支持可选文本/标签交集筛选，保留清单顺序；旧清单不伪造新标签。
- 已维护案例补充README改写说明。`copy_example`保留原脚本及根README字节，另外生成`.dojo-docs`及来源摘要；extension同时交付基案例和变体正文。保留目录冲突提前拒绝，未交付的外部本机参考显式标明。返回值和provenance增加`documentation`，原字段保留。
- Help生成器将真实README正文与摘要纳入案例主题，导出后能读详细说明；源摘要/渲染摘要可追溯。GUIDE只描述能力与入口；本轮Skill增量仅是列表摘要→正文→复制说明的导航，没有新增下一轮优化、选优或调度决策规则。既有框架/Web→能力替换→复核三步保持。
- 两个extension均基于`geotransolver.darcy`：`tail_batch`替换有限有序输入流；`research_state`留出独立验证、连接raw/EMA选优和用户状态。沿用完整recipe、共享训练、writer及独立infer/post，不新增Trainer或正式JOREK案例。

公开变更均为可选关键字或返回对象附加字段。新拒绝行为仅针对无法兑现的独立周期、无效绑定或不相容用户状态。固定外部用户源码基线与摘要未改。完整API签名见生成帮助；职责与长期行为写入core abilities/applications、task templates/cli及参数化PDE现有PRD。

## 测试与安装证据

证据根：`/Users/zonghui/work/project_simulation/dojo_train/framework-skill-evolution/3cbdc67f-bb6c-4786-bcb6-2b2d3b07654f/`。

最终圈定集合按pytest完整用例名去重，共**162项通过，0失败、0跳过**。不以全仓测试代替本切片验收；嵌套安装进程中的重复执行不重复计入162。

- `acceptance.xml`：107项。周期、用户状态、两个基础能力、案例筛选/复制/导出、资源/帮助、固定公开用户基线，以及最终框架安装用例。
- `final-state.xml`：13项，其中12项用户状态与上述重复；另1项基础能力真实安装验收在独立环境复跑54项行为。缺失字段、版本类型、坏状态、加载失败和逐项回滚均覆盖。
- `final-joint.xml`：31项。现有训练策略、外流扩展、epoch检查点回归，以及两个新extension的配套四包wheel完整链路；在最终检查点强化后重跑。WDNO可选依赖仅使用证据目录的独立解释器，不改变主环境。
- `navigation-final.xml`：23项。案例/recipe共享文件、可携带入口、阶段产物契约及研究导航。README补充没有通过删除共享声明逃避一致性测试。
- `final-docs.xml`：在最后一次帮助生成后补验Help与框架安装，属于上述162的重复；安装命令、源码摘要、离线正文及12项状态复跑结果保存在`final-docs/test_installed_state_hooks_and0/`。
- 修改的训练/能力/扩展、文档助手与新测试经圈定ruff检查。共享resources模块的其他并发改动不据此宣称全文件lint通过。

两例实际在仓库外物化，修改批量、替换loss、新增带轴与单位说明的误差输出并由post消费。direct-core、Task的4→6恢复与连续6更新逐值一致；核对模型/优化器/调度/随机流/历史及启用的EMA和用户状态。research_state最佳来自更新4、最终更新6，移走旧best文件后仍从完整状态恢复此前受评权重；独立infer及不加载模型的固定post成功。详细收据在`final-joint/test_external_copy_direct_task{0,1}/acceptance.json`。

数值输入是小型合成流程夹具，不是Darcy科学复现。第二计划另有静态索引/随机时间窗两种任务的梯度和参数独立参考，以及EMA早于末轮获胜的writer验证，见其验收记录。

安装测试分别构建配套spec/core/task或spec/core/contrib/task wheel，在仓库外导入并核对来源；GUIDE、Skill、训练源码及案例文档与安装内容核对摘要。第三方依赖可只读复用已有环境，不声称第三方依赖完全重新安装或OS隔离。

## 首轮失败及修复

- 新测试最初引用了README没有的标题，改为核对实际正文；后续正文与来源摘要测试通过。
- 首轮WDNO回归因主环境缺可选wavelets失败；转到已记录的独立依赖环境后完整重跑通过。
- 隔离安装曾误以为site-packages路径会递归处理另一个venv的`.pth`，缺omegaconf；从主项目解释器运行该隔离安装测试后通过。未因此同步主环境。
- 两个GeoTransolver README声明与recipe共享，首次只改example导致一致性失败；已同步两个源正文，保留原契约，23项复验通过。
- Help在其他并行任务修改公开源码后漂移，保留检查输出，收尾重新生成和检验。生成通过仅对应该次源码快照，不作为其他并发项目整体验收。
- 扩展曾使用不支持的writer名称、比较时未区分writer附加来源字段；修复与历史失败详见第二计划联合记录。以上已核实错误追加根`error.log`，早期失败XML保留。

## 正式入口兼容性验收（用户授权后续接）

此前只读预检`formal-runtime-preflight.json`确认源码与主环境安装副本不同，因此当时保留未验收状态。用户随后明确授权重装、重启和验证。新证据保存在上述证据根的`formal-release/`，不覆盖此前证据。

本计划没有新增或修改Web页面功能。共享epoch训练通过`abilities/training/loop.py`消费`checkpoint.restore`；本轮提取共享内部恢复函数，因此已有Web→server→Task→core链需要兼容性验证。工作区另有并发Web/server改动，不归入本计划成果；本次没有为验证而增加前端功能。

已备份安装副本和进程信息，按规定带dev及visualization重装spec/core/contrib/task四包；9个目标文件的源码与安装内容摘要一致。停止旧8000进程90789并启动85596，5173进程93327保持不变。期间85596被外部并发工作优雅停止并替换为93467（同平台根，附加data-root）；最终验收记录实际93467，不将其启动归为本任务操作。服务切换期间页面曾短暂请求失败，重载后恢复；最终8000项目接口与5173均200。

正式页面派生新任务“框架状态恢复正式验收0922”（`c0163e939c7a446d8c62de6e4c1ed5ad`），不修改原任务。只读使用已有有效冻结准备中的2条真实ShapeNet-Car训练样本，AB-UPT缩小为50,020参数、CPU FP32、每域16个采样锚点：

- 页面实际启动`f4e5f98e61814bbfbf1ee847847f9ad3`，完成2轮/4更新，保存曲线、检查点和两份预测。
- 公共Task接口从该检查点恢复，目标改为3轮，`bfe57a3d3c9e4ed59d2002668dde5f7b`完成3轮/6更新。正式页面真实读回成功状态、完整1～3轮损失曲线和日志，证据为`resumed-browser-dom.txt`、`resumed-browser.png`。
- 连续3轮参考`b888371c8cb14aac80c5aa02756581de`成功。恢复与连续运行的模型、优化器、调度器、随机状态、历史（排除墙钟耗时）及曲线逐值一致；两样本保存的预测、真值、位置和身份张量读回有限且逐值一致。`verify_formal.py`和`acceptance.json`保存可复核过程及收据。
- 页面“继续训练”是加载权重重新训练，不将其当作完整状态恢复。完整恢复本次通过公共Task接口提交，再由页面读回；现有固定配置恢复API对已完成2轮且目标仍为2轮的请求正确拒绝（`10842c5c89174b78a459cb7448fe0dea`），保留失败证据。
- 首次冒烟配置dim12/head3不满足3D RoPE有效维度要求（`e9ca226a78e4449f98eeef162a816bed`）；仅纠正新任务为已验证的dim24，不修改模型源码。失败不计通过。

独立周期和用户状态扩展由前述Python/安装测试证明；正式Web只证明已有消费者兼容。本次不是完整点场精度、生产规模、MPS性能或可视化工作台验收。

未做新的隔离Agent选择/改写行为试验，故只声明案例入口、说明交付与可执行扩展有效；不声称Agent工具采用率或科学效果提高。
