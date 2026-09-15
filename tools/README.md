# 仓库工具

工具用于维护与验收，不承载正式 recipe 的运行逻辑。

- `ssh-git-remote.conf`：远程 Git SSH 主机与 `git push server` 连接说明；不含私钥。

- `generate_abupt_inputs.py`：用锁定 Noether 实际处理器生成多域输入夹具，版本和摘要写入 `tests/fixtures/abupt_inputs/source.json`。
- `verification/reference_env.py`：保留当前 Dojo 数值依赖，加载指定 Noether 源码及缺少的纯 Python 依赖，仅用于对照。
- `verification/compare_datapre.py`、`compare_trainprep.py`：真实数据的前处理和模型输入差分。
- `verification/compare_abupt.py`：小网络快速定位；`compare_full_updates.py`：正式网络真实采样输入的逐更新对照。
- `verification/run_noether_reference.py`：官方预设完整两轮训练。
- `verification/compare_training.py`：先冻结官方重复运行容差，再核对全部最终参数、训练轮次和逐轮指标。
- `verification/state_mapping.py`：验收专用参数名称映射，不能当作产品检查点交换接口。

命令、参考源码和最终差异报告见 [三阶段参考验收](../.context/mvp/abupt-reference-acceptance.md)。正式 `packages/` 和 recipe 不依赖 Noether。

- `verification/run_noether_post.py`：调用本地锁定 Noether user_project 的真实锚点和网格后处理，只统一 CPU、seed=42、零读取子进程。
- `verification/compare_post.py`：测试身份、兼容张量包、点云、网格字段/拓扑/类型及评估指标对照。证据见 [端到端验收](../.context/mvp/abupt-end-to-end-acceptance.md)。

Recipe 显式流程验收：`verification/transolver3/dojo.py` 继续通过历史 NPY 兼容入口作原仓库数值对照；当前五例物理步骤由 `tests/integration/test_recipe_explicit_equivalence.py` 与冻结源码逐值比较。参考 `.context/mvp/recipe-explicit-acceptance.md`。
