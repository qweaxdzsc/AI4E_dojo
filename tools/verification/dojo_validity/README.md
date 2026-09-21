# Neumann 双组五轮验证工具

长期行为及指标见 [参数化 PDE PRD](../../../docs/PRD/recipes/parametric_pde/PRD.md#二独立双组研究实验)。当前实测与未完事项见 [验收记录](../../../.context/mvp/dojo-validity-acceptance.md)。

## 当前可用范围

- 生成两个组级工作根及不同 experiment UUID，独立复制原始数据、权重和普通 Python baseline。
- 构建独立环境；Dojo 组增加本次源码 wheel、Agent 启动指南、帮助索引、案例与公开源码副本。
- 逐值核对原数据、初始化、基矩阵、损失、梯度和一次 Adam 更新；独立执行完整 round-00。
- NPY 预测/真值清单的 FP64 独立评价、区间时间账本、去重供应商 usage、五轮调度与失败续接。
- Codex 命令沙箱真实探针；fake runner 验证两条五轮控制流。

正式 CLI 入口位于 `formal.py`，每组使用独立 Codex 状态、相同模型设置和同一会话续接五轮。`cli.py` 在 macOS Seatbelt 整进程隔离内启动 CLI，禁用内部重复沙箱（macOS 不支持叠加），不表示解除外层权限。全局配置、项目规则、记忆、插件、MCP 和宿主 skill 注入关闭；系统运行库只读，其他组和父目录不可读，所有后代进程继承边界，本机网络服务被拒绝。公网 HTTP/HTTPS 可用。

`evidence/whole-process-isolation.json` 必须先由主控实际预检生成；正式会话 ID、每轮 JSONL、stderr 和本组原始 rollout 都保留。`activity.py` 分开记录训练、评价、环境与数据处理进程。逐请求原始 usage 取真实 response ID；自动分类与完整封账仍须核对，不以请求总量冒充编码 token。
## 入口

在仓库根执行 `uv run --no-sync python -m tools.verification.dojo_validity --help`。

```text
prepare --base <dojo_train> --reference-source <原仓库/src/neumann_bc.py>
environment --experiment <组级根/experiment-UUID>
verify-baseline --baseline <比较目录/baseline> --output <比较目录/evidence/parity.json>
baseline --experiment <组级根/experiment-UUID> --truth <比较目录/baseline/truth/manifest.json>
probe --experiment <组级根/experiment-UUID> --codex <Codex二进制> --forbidden <已存在目录> ...
run --experiment <组级根/experiment-UUID> --truth <主控可信真值清单>
evaluate --predictions <predictions.json> --truth <可信manifest.json> --output <metrics.json>
summarize --comparison <比较目录>
```

组级根非空时 `prepare` 拒绝，不覆盖历史实验。`prepare_pair` 返回主会话比较目录；该目录的 `comparison-protocol.json` 是唯一双组路径映射。两组各自的 `protocol.json` 不含对方路径。

`session_workspace_root` 固定是 `neumann-plain/` 或 `neumann-dojo/`；`experiment_root` 是该根下的 `experiment-UUID/`。会话绑定前者，运行与计量使用后者，不能互换。

准备期若工具仍在修改，全部材料就绪后调用 `prepare.seal_preparation(comparison)` 封存并保留准备前摘要。它只能执行一次，round-00 或正式执行开始后禁止刷新起点。Baseline 运行前用 `verify-baseline` 核科学一致性；不是以修改摘要掩盖数值差异。

`baseline --epochs 2` 仅产生 smoke 记录，不能写正式 `round-00/result.json`；默认 5000。训练和推理分别在本组解释器运行并单独计时。运行失败保留 UUID 尝试目录。

## 组内提交与执行器连接

`runner.run(experiment, runner, evaluator)` 的执行器需要实现：

1. `simulation`：真实执行必须为 false。
2. `preflight(protocol)`：验证实际会话根、全工具文件隔离、网络旁路、初始上下文、usage 与时间流，返回 `workspace` 和 `all_tools_isolated`；命令探针不能自行填 true。
3. `create_session(protocol)`：创建全新会话并立即返回 ID；先保存 ID，再执行任何优化请求。
4. `turn(protocol, session_id, round_number, prompt, attempt_directory)`：续用同一会话，将原始响应、命令和 usage 持久化在 attempt 目录；返回同一 `session_id`、统一单调时钟的 `started/ended`、活动 `events`、规范化 `usage` 和 `submission`。

`submission` 的 `source/config/checkpoint/predictions/training/summary/diff` 均为本组实验内相对路径。预测目录包含 `predictions.json`，其 `samples` 每项为 `{id, path, sha256}`，path 是相对该清单的 NPY。官方目标为十个 `test-00000` 至 `test-00009`、128×128 网格。

evaluator 在主会话执行，须在受控执行环境中恢复冻结模型、运行其明确推理入口后评价；不能直接相信 agent 自报的 metrics 或真值。通用 `evaluate` 只复算固定预测；正式执行器另启动冻结 `source/infer.py`，传入 checkpoint/config/inputs/output，独立生成十个预测后再复算。推理输入不含真值；沙箱不允许读取原始 baseline 和工作区。

每个优化轮结束会冻结候选并独立评价；失败保留 attempt，续接跳过已完成轮次。完成五轮后状态为 `five_rounds_completed_final_selection_pending`，不会自行标记正式完成。`runner.finalize(experiment, selected_round, evaluator)` 核对历史冻结内容，复制指定轮候选并重新评价，状态进入 `final_evaluated_accounting_pending`；不得自动替 agent 选择最佳轮。完整失败成本、编码阶段分类与评价成本仍须封账。`summarize` 不将缺失成本当零，不将这类未完成状态当完整正式结果。

## 计量约定

时间事件为 `{event_id, phase, start, end}`，start/end 使用同一单调时钟；不同进程时钟需要 adapter 统一。阶段并集、进程累计、重叠和未记账时间分别保存。等待与其他活动重叠时扣除重叠部分。

usage 保留原始供应商内容，规范字段包括 `request_id/phase/input_tokens/output_tokens/cache_read_tokens/cache_write_tokens/tool_calls/retry_count`。adapter 明确 `input_includes_cache=true` 和 `output_includes_reasoning=true` 后才可汇总。总 token 是去重输入加输出，缓存及推理子项不再相加。阶段为空或计量缺失输出 null；混合请求保留 mixed。后台训练存在时，编码仍归 coding。

## 圈定测试

```bash
uv run --no-sync pytest tests/integration/test_dojo_validity.py --basetemp=<dojo_train下已建父目录>/pytest
uv run --no-sync ruff check tools/verification/dojo_validity tests/integration/test_dojo_validity.py
```

所有产物放在显式指定的 dojo_train 根，不在框架默认值中硬编码本机路径。不更改正式 8000/5173，不 sync 主环境。

## 主控正式调度

`uv run --no-sync python -m tools.verification.dojo_validity.formal --comparison <主会话比较目录>` 串行调度两组，各自连续五轮；已有完成轮次跳过，失败保留原会话。整进程策略来源及许可见 `policies/NOTICE.md`。身份、准备修复与实际进行中的状态以验收记录为准。

`telemetry.py` 从正式会话原始请求与工具输出重建活动，不用总墙钟减训练估算编码。`finish.py --comparison ...` 只在两组五轮和最终评价齐全时封账；`summarize` 在最终候选齐全时调用同一封账逻辑，否则输出明确的进行中状态。供应商未给重试计数保留 null，混合请求独立列出。

混合工具调用按实际子命令区间核对编码与训练；混合请求 token 保留编码上下界，区间重叠则不判定编码 token 胜负。比较账本单列另一组执行期间的串行排队与全部调用间等待。主控可在 `evidence/scientific-review.json` 的 `findings` 中记录冻结源码、框架实际使用与固定测试集选择的核查结论；封账将该核查纳入最终报告。不得以阅读文档或源码中存在框架名就宣称实际调用过框架。
# JOREK RMHD 新协议

独立前处理、隐藏测试、MPS与50ms推理门槛使用 [rmhd/README.md](rmhd/README.md)。以下Neumann命令和历史定义继续保留，不用于新RMHD实验。
