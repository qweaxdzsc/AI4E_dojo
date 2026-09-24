# 基础模型 Agent 帮助同步（2026-09-24）

## 缺口与交付

此前经典网络、算子网络与传统代理的源码 API 已进入生成帮助，但 Guide 与能力教程主要仍描述神经网络路线；API 页存在未覆盖 Agent 的能力发现与正确连接需求。

本轮补齐 `DOJO_AGENT_GUIDE.md` 与 `docs/agent-help/capabilities/{model,training,inference,data,loss}.md`。模型教程连接计算 block、可复用阶段、完整架构的实际 API 和案例；补充 MLP/CNN/ResNet/U-Net/Transformer/GNN/RNN、DeepONet/FNO、POD/RSM/RBF/Kriging/LightGBM 的形状、替换点及主要边界。传统拟合、普通对象批次预测、安全状态读回与独立物理约束分别归入原有能力页。元数据同步到 Guide、研究 Skill 和帮助首页菜单；API/主题/案例索引由现有生成器维护。

AGENTS、集成 Skill、算法规则和 recipe 规则现要求每次变更评估 Agent 使用影响；涉及公开用法则同步 Docstring、API 与教程，按需改 Guide，并验证受影响的安装/离线资源。内部实现未改变用法可说明不适用。未建立新的框架层级或统一组件协议。

## 验证范围

圈定 `test_agent_capabilities.py`、`test_agent_help.py`、`test_task_resources.py`、`test_research_navigation.py`。覆盖所有能力/应用/recipe 公开符号与源码索引、14 类模型名称检索、教程声明符号查询、离线链接和真实 Task wheel 构建/安装/导出。九个文档例子实跑，新增 MLP 作为 DeepONet branch 的反传、FNO 前向，以及 RSM 拟合→状态保存→重建→含尾批预测数值核对。

独立 Task wheel 使用当前环境已有的第三方/core 依赖；这证明本轮帮助资源交付，不是干净依赖安装或重新验收全部模型训练。未重装主环境，未操作正式 8000/5173；仅 Python/离线文档消费，无 Web 功能变更。

最终 **31 passed in 29.64s**，无失败/跳过/警告；JUnit 为 `final-results.xml`，真实 wheel、独立安装环境和离线资料在 `final-pytest/test_capabilities_in_real_whee0/`。生成器覆盖 572 份生成帮助文件且 `--check` 通过；受影响测试的 ruff 与集成 Skill 校验通过。证据根：`/Users/zonghui/work/project_simulation/dojo_train/foundational-agent-help-20260924/`。
