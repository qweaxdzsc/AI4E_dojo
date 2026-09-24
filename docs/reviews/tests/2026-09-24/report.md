# 2026-09-24 Dojo 增量测试报告

## 结论

- 状态：**上轮 16 个源码失败已恢复，但发现 1 个新的测试合同漂移，仍需行动**。
- 本轮按上次快照后的源码、Task、recipe、RMHD 与帮助文档变化圈定，去重结果为 `289 passed / 1 failed / 2 skipped`。单节点复测为 `8 passed / 1 failed`，仅作失败稳定性确认，不重复计数。
- 新失败是 `test_declared_legacy_provider_and_actual_training_capabilities`：现行 Transolver-3 能力描述发布 `evaluation_split.allowed=["eval"]`，测试仍期望旧公开值 `["validation"]`。contrib 实现继续接受 `eval` 与旧名 `validation`，模块索引也明确“平台约束发布 eval”，因此是测试期望过时，不是训练实现回归。
- 最小建议：把该断言更新为 `["eval"]`，保留 `test_transolver_training.py` 对旧 `validation` 别名与现行 `eval` 的兼容覆盖；不要把平台能力描述退回旧名。
- 上轮的 `data_specs`、准备 v2、AB-UPT 权重等价、资源直接加载、案例说明、RMHD recipe probe 和 Task wheel `ema_pytorch` 共 16 个失败均未复现。旧失败/recipe 组 `50 passed`。
- 正式 8000 的 `/docs`、`/openapi.json` 只读返回 200；5173 未监听。8000 进程早于本轮源码/安装更新，且本轮涉及 Task/Server/Web 消费链，因此正式 Web 仍未验收；如要发布验收，需要用户另行授权更新并重启正式服务后再做浏览器冒烟。

## 源码与环境身份

- 开始：2026-09-24 07:13 CST；结束：2026-09-24 09:39 CST（周四增量轮次）。本轮超过默认 90 分钟窗口，未再扩展测试；后续应优先拆分 Task 来源依赖长节点或在到限时保存续查清单。
- Git HEAD：`9b53fc4cc4e38c128b18489f0b95f85055ceafaf`，与上轮相同。
- 开始时排除 `docs/reviews/tests` 后为 499 个已跟踪修改、516 个未跟踪文件。结束时为 497 个已跟踪修改、540 个未跟踪文件；内容身份 SHA-256：`6fae7a67e32166ca95843c650637a1fbcb92b1016a0c1b47cca0c28857b5dd50`。
- 测试期间另一个工作流写入 `.context/mvp/rmhd-factorial-acceptance.md` 和 `docs/reviews/archreview/` 证据；未检测到本轮受测产品源码或测试文件在运行中变化。
- Python 3.12.14；uv 0.12.5；pytest 9.1.1；Apple M5 Pro。
- `ai4e_core`、`ai4e_contrib`、`ai4e_task`、`ai4e_server` 从主 `.venv/site-packages` 导入。抽查 core/contrib/task/server 六个本轮关键文件，安装副本与源码 SHA-256 一致；当前主环境仍无 `ema_pytorch`，但当前源码的独立 wheel 测试已通过，说明控制案例不再被该未声明依赖提前阻断。

## 测试结果

| 分组 | 结果 | 时间 | 证据 |
| --- | --- | ---: | --- |
| 上轮失败、recipe、资源与 wheel 复测 | 50 pass | 407.76 s | `prior-failures-and-recipes.xml` |
| Task/Web/算法平台上下游合同 | 183 pass, 1 fail, 2 skip | 1938.73 s | `task-web-contracts.xml` |
| RMHD factorial/ledger、dojo-compare、Agent Help | 56 pass | 12.93 s | `rmhd-help-public.xml` |
| 失败单节点与 Transolver 兼容复测 | 8 pass, 1 fail | 2.68 s | `evaluation-split-rerun.xml` |

去重结果为 `289 passed / 1 failed / 2 skipped`。两个 skip 是 `test_model_switch_real_preparation_handoff` 的 ShapeNet-Car AB-UPT 与 NASA CRM AB-UPT 真实模型换模入口，要求显式 `DOJO_MODEL_PICKER_REAL=1`；不计通过。

## 趋势与发现

1. **已恢复：上轮 16 个源码失败全部终止。**
   - 五例显式 recipe、独立 infer、外部 wheel、准备 v2 与 AB-UPT 逐值等价均通过。
   - Agent 能力导出、案例 README、RMHD recipe probe 与 Task wheel 外部运行均通过。
   - `test_task_resources.py::test_resource_manifest_and_checks` 也通过；主安装资源漂移在本轮抽查范围内已恢复。

2. **新可行动问题：Transolver-3 能力描述测试仍断言旧切片名。**
   - 症状：实现返回 `allowed=["eval"]`，测试期望 `["validation"]`，全组和单节点复测均稳定失败。
   - 根因证据：`packages/ai4e-contrib/application/aero_cfd/transolver3.py` 接受 `eval`/`validation` 两个输入；`.context/modules/ai4e-contrib.md` 明确平台约束发布 `eval`；`test_transolver_training.py` 的 8 个节点通过。
   - 后果：圈定回归无法全绿，并会把现行平台能力合同误报成训练退化。
   - 最小修复：只更新该能力描述断言并保留旧名兼容测试，不改实现或历史证据。

3. **安装副本已更新，但正式服务证据仍不完整。**
   - 主 `.venv` 抽查文件与源码一致，代表性 wheel/仓库外复制测试通过。
   - 8000 进程已运行约 15 小时，早于本轮变化；Python 已加载模块不能由磁盘文件更新证明刷新。5173 未运行，未执行浏览器页面验收。
   - 本轮未 sync、未重装、未杀进程、未重启 8000/5173/Vis，也未提交正式任务。

4. **资源风险较昨日缓解。**
   - `dojo_train` 约 320 GiB，数据盘可用约 139 GiB；未发现 pytest、torchrun、accelerate 或 RMHD 训练进程。
   - 保留现有 8000、8011 与 Vis 进程，未干预用户工作。

## Not run

- 周四不执行周日全量；根 pytest、Vis backend、Web/Vis 前端架构/类型/构建/浏览器全量未运行。
- 两个真实模型换模节点因缺显式 `DOJO_MODEL_PICKER_REAL=1` 跳过。
- 5173 未监听；正式 8000 只做只读 HTTP 检查。没有当前安装副本→重启服务→浏览器页面的完整证据链。
- 未启动完整论文训练、大下载或 GPU 任务。

## 执行命令

- `uv run --no-sync pytest <上轮失败、recipe、资源与 wheel 七个文件>`
- `uv run --no-sync pytest <算法平台、Task 来源依赖/执行/推理、Transolver、Web 配置十四个文件>`
- `uv run --no-sync pytest tests/integration/test_dojo_factorial.py tests/integration/test_dojo_validity.py tests/integration/test_dojo_compare_skill.py tests/integration/test_agent_help.py`
- `uv run --no-sync pytest <失败单节点> tests/integration/test_transolver_training.py`
- 只读检查 `127.0.0.1:8000/docs`、`127.0.0.1:8000/openapi.json`、端口、磁盘、训练进程与安装文件摘要。
