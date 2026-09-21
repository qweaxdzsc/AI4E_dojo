# Agent 能力导航验收（2026-09-21）

本轮完成九类能力教程和三种接入深度：单工具、已有研究代码、完整案例。教程元数据生成 skill、GUIDE、帮助首页菜单；不再要求单工具调用复制 standalone。API 数值行为不变。帮助检索对 tasks 精确匹配加权，仍低于精确符号/主题/案例/标题，避免“归一化”等明确任务被无关 API 淹没。

## 实现和交接

- `docs/agent-help/capabilities/`：九个实际可运行小例子、输入输出、边界和继续阅读。
- `tools/docs/build_agent_help.py`：同步三个入口菜单及现有帮助索引；`--check` 检查漂移。
- `packages/ai4e-task/templates/resources.py`：任务关键词精确匹配排序。
- `tests/integration/test_agent_capabilities.py`：菜单/符号、九例实跑、中文查询、导出、独立 wheel 安装。
- 同步 AGENTS、研究路由、模块及总索引、Task templates PRD。

## 圈定证据

最终修改后重跑 `test_agent_capabilities.py`、`test_agent_help.py`、`test_task_resources.py`，合计 **27 passed in 16.54s**（含真实 wheel）。九例包含真实反传、2→4 更新完整状态恢复、预测与 FP64 误差复算、PNG 读回及 Task 创建。实际 wheel 在仓库外隔离环境安装，核对安装路径、九类资源、三个入口链接和离线导出；复用主环境已有第三方/core 依赖，不表示干净依赖安装或正式实验组。

Skill quick_validate 与三份受影响 Python 文件的 ruff check 通过。交付 wheel、离线资料及摘要见上述产物目录的 `delivery/`。测试产物在 `/Users/zonghui/work/project_simulation/dojo_train/agent-capabilities-20260921/`。首次 pytest 指定 basetemp 的父目录不存在产生 setup 错误，创建父目录后重新运行；中文“归一化”排名失败驱动了本轮明确任务加权修正。

## 范围

本轮交付源码、生成帮助及验证过的独立 wheel，不重装正式环境、不重启 8000/5173。本功能为 Python/离线 Agent 资源，无 Web 消费变更。主环境已有安装副本未更新；下次实验应从本轮构建 wheel 提供匹配的 guide/skill/帮助。没有启动正式训优实验，也没有证明新入口一定提高研究精度或开发效率。
