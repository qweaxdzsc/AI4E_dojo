# Neumann 双组有效性实验实施与验收

日期：2026-09-20。**当前：两个正式 Codex CLI 会话各五轮及独立最终评价、成本封账已完成。** 最终结果见文末「正式完成与结论边界」。下文准备期的 0/5、桌面接口阻塞与进行中记录保留为历史，不代表当前状态。

## 本次实际目录

- 白板会话工作根：`/Users/zonghui/work/project_simulation/dojo_train/neumann-plain/`。
- 白板实验：`experiment-f5ca61e8-a73a-4529-9e8f-c75475a378a0/`。
- Dojo 会话工作根：`/Users/zonghui/work/project_simulation/dojo_train/neumann-dojo/`。
- Dojo 实验：`experiment-f35d54c0-e65b-4fa9-a35c-0e02cce6ef66/`。
- 比较目录：`/Users/zonghui/work/project_simulation/dojo_train/neumann-comparison/comparison-34372a43-7329-45fd-aa58-829bc0d6460b/`。
- 用户完整计划：`/Users/zonghui/work/project_simulation/dojo_train/dojo_validity/PLAN.md`，保留原指标、证据和验收细节，已改为组级根加各自 experiment UUID。

两个 protocol 只包含本组路径，配对仅在比较目录。各自独立 baseline、环境和缓存；初始材料摘要一致。未覆盖既有实验，首次材料封存前的旧摘要保存在 `evidence/preparation-before-seal.json`。没有修改固定公共 API 测试基线或已完成历史数值证据。

## 科学起点及完整 round-00

普通 Python baseline 从锁定 PI-BSNet `40ffb623...` 的 `src/neumann_bc.py` 抽取数值定义，保留参数坐标导数和原初始化消耗。未修改正式模型、recipe 或训练语义。

`evidence/baseline-parity.json`：60 个数据实例、223168 参数初始权重、样条矩阵、整轮损失、梯度和一次 Adam 更新与已安装 Neumann 路径逐值一致（rtol=atol=0）。

两组分别在独立 Python 3.12.14、Torch 2.14.0、NumPy 2.5.3 环境完成 5000 次更新，使用相同普通 baseline 入口，均生成十个 128×128 场：

- 白板 round-00 训练进程内计时：101.270351 秒。
- Dojo round-00 训练进程内计时：124.104677 秒。
- 两组 FP64 平均完整场相对 L2：`0.018813866272418954`。
- 两组最终 checkpoint 文件 SHA-256 相同：`a09ef88ff69a6735777d47e421129e81a6873d5a5f52d20259e4558fcdaa0878`。
- 十个预测文件及清单逐文件摘要相同。

详见比较目录 `evidence/baseline-comparison.json` 和各组 `round-00/result.json`、对应尝试下的 `events.json`、训练日志、history、checkpoint、预测和指标。

既有 708–709 秒是完整 recipe 的历史耗时。本轮普通 Python baseline 复用已准备数据/样条矩阵；预算、更新、最终权重和精度一致，但执行范围与开销不同。不能把 101/124 秒与 709 秒直接解释为框架效果，也不能继续保证当前入口接近十分钟。两组 baseline 尚未采用不同开发策略，不是正式效果结果。

## 环境与 Dojo 入口

分别复制公共依赖，site-packages 不共享；解释器系统运行库作为只读工具前提登记，不复制主环境的 AI4E 包到白板组。setuptools 的 distutils 启动 `.pth` 明确不复制，其余隐式 `.pth` 拒绝。Dojo 组额外在本组安装从当前源码构建的 spec/core/contrib/task wheel，无 editable 外部项目引用。未 sync 主环境或重启服务。

Dojo 组有完整 `DOJO_AGENT_GUIDE.md`、dojo-research、Agent Help Center、索引、案例、recipe、公开源码及 wheel 副本。`evidence/dojo-help.json` 验证帮助入口、manifest、`ai4e_core.run.launch` 的安装源码与 Neumann standalone 都位于本组工作根；案例 check 成功。首次正式 agent 学习仍须计入开发成本，当前准备检查不算 agent 学习或调用证据。

## 隔离验证与正式阻塞

两个本组 `evidence/command-isolation.json`：真实 Codex 命令 sandbox 的本组读写、父目录列举拒绝、跨组/比较目录/开发仓库读取与写入拒绝、软链接越界拒绝、公共网络可用，均通过。比较目录 `evidence/environment-sandbox.json` 另验证两个独立 Python/Torch 环境在各自命令 sandbox 中成功启动且 cwd 为组级根。

上述仅证明**命令执行边界**。OpenAI 权限文档明确此类 profile 不自动控制 MCP、连接器、浏览器、Computer Use 和初始上下文注入：<https://learn.chatgpt.com/docs/permissions#scope-and-enforcement>。

当前桌面 `create_thread` 没有任意绝对 cwd、全工具读取白名单、初始注入审计以及逐请求 usage/活动时间流参数；本次项目列表无两个新工作根。Docker daemon 未运行。CLI 的命令隔离可用，但整个会话覆盖及计量 adapter 尚未实现/验收。没有以提示词或 fake 证据代替该要求。

实际调用两组 `run` 均在创建会话前进入 blocked，本组 `evidence/execution.json` 保存原因和 `session_id: null`。比较 `results/comparison.json` 为 incomplete，正式 accuracy/efficiency 排名为空，token 为缺失值；没有伪造两组十轮结果。

尚需完成：全工具隔离的真实会话 adapter、同一模型设置及初始上下文验收、原始请求 usage 和完整活动流、任意候选的冻结推理重放、完整失败/评价成本封账，随后创建两组会话并运行五轮。不能把目前工具代码和 baseline 验收称为全计划完成。

## 圈定检查

- `tests/integration/test_dojo_validity.py`：20 passed，无 skip。覆盖组级/实验根分离、baseline 独立、白板提示无 Dojo 注入、路径/软链接、指标坏样本整批拒绝、时间并集/等待重叠、usage 去重/缓存/缺失/混合、首轮失败保存会话、后续失败同会话续接、指定最终轮次及冻结篡改拒绝、fake 两组五轮汇总、正式启动 fail-closed。
- `uv run --no-sync ruff check tools/verification/dojo_validity tests/integration/test_dojo_validity.py`：通过。
- 同范围 `ruff format --check`：通过。
- 两组独立 5000 update round-00、十样本 FP64 复算、实际 wheel 帮助定位及命令 sandbox：如上实测通过。

Fake runner 不调用模型、不训练；其输出固定标 simulation。正式 run 仍依赖未完成 adapter。只新增验证工具与相关文档，未涉及正式 Web 消费链，不需要正式服务发布。

## 2026-09-20 正式 CLI 续接（进行中）

用户要求用真实 CLI/Multica 创建正式会话后，已实现 Codex CLI 适配。旧桌面接口阻塞记录保留为历史。采用整进程 Seatbelt 而不是只隔离单条 shell；关闭内部重复沙箱。全局规则、宿主 skills、记忆、插件、MCP 均不注入；每组独立 Codex 状态保存认证、会话与用量。两组只读系统运行库和通用工具，组级根独占可写。公共 HTTPS、Python/Torch、本组读写通过；父目录列举、另一组/比较/仓库读写、外部软链接、存活的 loopback 与本机 LAN 测试监听均被拒绝，详见各组 `evidence/whole-process-isolation.json`。

正式模型均为 `gpt-6-astra`，reasoning `high`。白板会话 `01a0bea8-c4eb-79e3-9fb9-6f57f6db3f0d`；Dojo 会话 `01a0bea8-fe05-7b00-ab13-5afd1d9ae9c6`。会话均为新建，未 fork，不以子 agent 替代。白板第一轮发现环境 PATH 无 uv，主控给两组复制独立 uv/rg 后，保留全部失败证据并在同一轮同一会话续接；这是实验组织问题，不能解释为框架差异。

新增 CLI 圈定后合计 25 passed（含真实 macOS 文件边界测试），无 skip。两组五轮正在执行；完成、精度排名与编码成本封账尚不能宣布。


## 2026-09-20 正式完成与结论边界

两个既有正式 CLI 会话均完成 round-01 至 round-05，并由本组选择第五轮作为最终提交；未创建替代会话、未重跑共同 baseline、未中断研究预算。组级工作根、独立 UUID 和会话 ID 如上。最终 `evidence/execution.json` 均为 `complete`、`simulation=false`；比较目录 `results/comparison.json` 已封账。

- 白板逐轮主指标：`7.904580156842328e-08`、`6.408242370690761e-09`、`1.9615965053520154e-08`、`1.9013016885440543e-08`、`0`。最终重放为 `0`。
- Dojo 可用组逐轮主指标：`7.919589346717726e-08`、`2.5555461172970204e-08`、`1.901301688544054e-08`、`1.901301688544054e-08`、`1.901301688544054e-08`。最终重放与后三轮一致。
- 编码时间：白板 `3038.947` 秒、Dojo 可用组 `2213.694` 秒。五轮训练活动分别 `2.881` 秒和 `0.945` 秒，评价分别 `1.824` 秒和 `1.800` 秒。模型已变成紧凑解析/数值模型，不能将极短训练时间解释为 Dojo 加速。
- 全部去重 token：白板 `4171906`（57 请求），Dojo 可用组 `2653695`（38 请求）。每个供应商 response ID 的用量与 CLI 完成回合总量一致，缓存/推理子计数不重复相加。
- 编码 token 区间：白板 `1768594–3631650`，Dojo 可用组 `973101–2549941`。混合请求不任意分摊，区间重叠，因此编码 token 排名不确定。
- 正式会话初始化至最终评价的端到端分别 `3398.352` 秒和 `5639.854` 秒；其中执行器排队分别 `14.815` 秒和 `3102.089` 秒。排队单列，不用后运行一组的原始墙钟声称框架较慢。
- 白板首轮 1 次工具路径故障保留在尝试、日志和账本中；Dojo 无命令失败尝试。供应商未提供的 retry_count 保持 null。公共准备/主控开发成本没有完整请求级账本，明确为未测，不填零；round-00 成本另列。

Dojo 组第一轮读取本地 `DOJO_AGENT_GUIDE.md`、帮助首页与参数化 PDE 工作流，五轮均声明并经冻结源码/实际命令核对未使用 Dojo API、Task 或组件。实际条件是“知道且可用”，没有擅自改成必须采用。**本次不能证明或否定实际使用 Dojo 训练框架的效率**。

白板第五轮使用固定十例分数选择并细化候选，alpha=0.53125；最终推理源码只用权重、配置、参数和坐标，没有读取真值生成预测，也无测试场查表。独立重放确认十例零误差，但仅表示对给定 float32 场的匹配，不代表未参与优化的泛化或连续 PDE 零误差。Dojo 最终 checkpoint 为 185 字节，预测与第三/四轮相同。结论只覆盖两条连续轨迹。

`finish.py` 已核所有冻结摘要、原始起点与完整十例评价；实际模型输出与真值由 FP64 evaluator 重算。主会话保护副本位于比较目录 `evidence/groups/{plain,dojo}/`，各含正式原始 rollout、CLI 事件、隔离证明、最终冻结提交、重新生成的十个预测及摘要清单，不复制认证。组内 REPORT 只含自己的结果。`evidence/scientific-review.json` 保存实际使用与精度解释核查。

最终圈定：`uv run --no-sync pytest tests/integration/test_dojo_validity.py tests/integration/test_dojo_validity_cli.py -q`，**31 passed，无 skip**。真实 macOS 文件拒绝、混合工具子命令计时、串行排队并集、缺失重试字段和缓存去重均覆盖；同范围 Ruff 检查与格式检查通过。未 sync 主环境、未修改正式服务或公共数学实现。
