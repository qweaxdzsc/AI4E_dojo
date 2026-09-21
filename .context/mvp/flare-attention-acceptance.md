# FLARE++ 可选注意力组件验收

完成时间：2026-09-21T11:20:32.501053+08:00。HEAD：477c47bc4cba83fd1e903800034d7d58286ee6d8；工作区含用户既有未提交修改，HEAD 不代表完整交付源码。

## 范围与公开入口

用户授权仅加入 core 可选注意力能力。`ai4e_core.abilities.modeling.modules.flare_attention.FLAREPlusPlus` 是普通 nn.Module，处理 `(B,N,C)` 浮点张量；不是完整模型或强制流程，不改变默认 GALE、recipe、GeoTransolver 构造器或平台选择。

来源锁定 PhysicsNeMo `94dbdf829d1a4e93e3f31ecb77713392c471388e`。先独立运行上游类 CPU float64 前向/反向，再迁入组件。测试 fixture 的原文件先核 SHA-256，再只提取原类，延后注解解析，数值方法 AST 原样执行；没有安装 PhysicsNeMo。

本地保持参数名、布局和三次 SDPA 算术；用 Torch reshape/transpose 替代 einops，去除框架/注解依赖，增加中文公开说明和输入校验。来源及修改记录在 `packages/ai4e-core/Notice/physicsnemo/flare_plus_plus.json`，沿用同目录 Apache-2.0 LICENSE，不修改已有 GeoTransolver 来源身份。

长期行为见 core abilities PRD 第十章；使用示例在 `docs/agent-help/user-components/network.md`，自动 API 在 `docs/agent-help/api/core/abilities/modeling/modules/flare_attention.md`。

## 验收

```bash
uv run --no-sync pytest tests/integration/test_flare_attention.py tests/integration/test_flare_attention_installation.py tests/integration/test_public_api_stability.py tests/integration/test_agent_help.py tests/integration/test_geotransolver_core.py --basetemp=/Users/zonghui/work/project_simulation/dojo_train/flare_plus_plus/pytest-final -q
```

**43 passed，0 failed，0 skipped，15.71 秒。** 新组件与两份测试 ruff check 通过。

- float32/float64 上游前向、输入/参数梯度、Adam 更新逐值一致；覆盖不同 token 长度/内部宽度/路由数/scale 及相同布局的非连续输入。
- 独立 matmul/softmax 三段公式验证 float64 前向与梯度，排列等变、输入条件路由、eval RNG 不变。
- 带 dropout 四次更新与两次保存后恢复两次更新的参数逐值一致，固定预测保存读回一致；CPU bfloat16 autocast 前向一致，梯度有限。
- 非法构造参数/形状/空 token/整数输入拒绝；TE、token 分片拒绝。
- 实际 core wheel 安装到实验目录，仓库外公开 import 组合 LayerNorm→FLARE++→Linear，真实更新、权重恢复和预测读回成功；安装源码字节、Notice/许可交付通过；未加载 contrib/Task/server/PhysicsNeMo/einops/jaxtyping。
- 固定用户源码基线及安装测试通过，未改基线摘要。Agent Help 全量生成校验与 GALE 现有能力回归通过。

初次测试 25 passed、2 failed、4 errors：比较夹具一侧非连续切片、一侧连续 clone，产生微小内核舍入差；实验父目录未创建。保持两侧相同布局、预建目录后 31 passed，没有放宽逐值容差。测试 lint 修正后最终43项通过，原始事实见 error.log。

帮助生成同时刷新四份当前源码对应的既有漂移生成页（sampling/graph、trainprep/physical、trainprep/topology、contrib aero_cfd/operations）及总索引；不修改这些源码或手写功能说明。

## 安装与证据边界

- [验收 wheel](/Users/zonghui/work/project_simulation/dojo_train/flare_plus_plus/pytest-final/test_installed_flare_optional_0/wheels/ai4e_core-0.1.0-py3-none-any.whl)，SHA-256 `e28c3890d38891d31734f50cef6c318fcbda357baee3ad5e4b5c3d344a0841cf`。
- 新源码 SHA-256 `303a84d1fa5eb09d382d1e5d7fdf7cec66230ae4fa1e0dabb314fec3d41993d0`。
- 测试与实验产物位于 `/Users/zonghui/work/project_simulation/dojo_train/flare_plus_plus`，未新建到 tmp。
- 主 `.venv` 未 sync/重装，8000/5173/Vis 未重启；交付为源码和隔离 wheel 可用，正式环境尚未发布新增文件。
- 无 mask/因果/token 分片/TE 支持；本轮CPU测试，不声明 CUDA/MPS/compile 或完整模型精度/性能收益。

## 调研口径

N-001 改为可选能力候选，架构建议数为0；原日期周报保留，latest/去重账本注明纠正及后续实施。dojo-4 提示词已更新，时间、模型、工作目录和只读调研边界不变；架构建议须有跨模型/应用完整流程、状态所有权、恢复/评价及Agent使用证据，单组件新增不能冒充架构改进。


## 文档补齐（2026-09-21）

补充此前遗漏的 core README、能力简表、源码明细 A163 与合并主表 M13/O12 映射；PRD、网络指南、生成 API、AGENTS 和模块索引沿用现行可选组件边界。该增量不新增业务阶段，不扩大默认模型或平台支持；全局架构分层未变化，不向架构正文复制组件功能说明。

文档圈定验收：能力清单链接/导航、合并映射/五阶段/简表及 Agent Help 共 **12 passed，0 skipped**。另静态核对 FLARE++ 类及公开方法在 A163 中逐项可发现、五份用户入口文档相对链接有效；未把历史能力快照当作本轮全仓完整盘点。未重复运行数值训练。
