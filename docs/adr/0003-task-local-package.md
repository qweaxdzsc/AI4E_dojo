# ADR 0003：Task 本地 Python 包与正式版本

状态：已按用户确认方案实施，验收范围见 `.context/mvp/task-acceptance.md`。

## 决策与原因

Task 的业务是本地目录、资产、版本与执行，采用六类功能模块足够；取消与 Server 共同强制 DDD 的要求。Python API 和 CLI 复用实现，Hatchling 单层映射支持 wheel 安装。SQLite 保存管理事实，实际运行来源由 core writer 保存。

只有 new/fork 创建正式版本，工作目录可编辑，运行只是版本下的测试。不可变创建快照、当前代码和运行快照分别承担来源、编辑及执行证据职责，不要求 Git。版本树是单父、多根，基线可以独立选择。

runs/data/recipe 都位于 tasks/<task_id> 内，保持兄弟目录。shared 按资产名称存放并附来源，复制开关默认关闭，显式分享不覆盖已有资产。路径及指标通过模板声明，不在 task 硬编码 aero_cfd。

## 影响

更新架构第 19 节、AGENTS、task/server 规则及 Web 设计语义。旧独立 recipe 保持兼容；不承诺从 runs 恢复未执行任务的管理事实。未知执行状态需核对，不自动重启。远程队列与 Web/Server 不在本期。
