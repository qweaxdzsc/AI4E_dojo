# 2026-09-23 Dojo 增量测试报告

## 结论

- 状态：**有新可行动发现，未通过**。
- 对当前源码构建的新鲜 wheel 去重后，圈定结果为 `589 passed / 16 failed / 57 skipped`；主 `.venv` 另有 `1 failed / 8 collection errors`，均由安装副本落后于源码造成，不重复计入源码功能结果。
- 已恢复：随机重划、9 个公开 aero 配置、PCNO `iapws` 阻断及上一轮 5 个 PCNO error 均通过；Agent Help 生成物继续通过。
- 新回归集中在四组：旧五例显式 recipe/推理链 11 项、Agent 能力/案例导航 2 项、RMHD recipe probe 2 项、Task 外部 wheel 控制案例 1 项。
- 正式 8000 正在监听且 `/docs`、`/openapi.json` 返回 200；5173 未监听。未重装、重启或向正式服务提交任务，正式 Web 仍未验收。
- 检测到用户的 RMHD 四组实验正在运行；本轮未干预。`dojo_train` 约 421 GiB，数据盘仅余约 53 GiB，资源风险较昨日显著上升。

## 源码与环境身份

- 开始：2026-09-23 10:46 CST；结束：2026-09-23 11:22 CST（周三增量轮次）。
- Git HEAD：`9b53fc4cc4e38c128b18489f0b95f85055ceafaf`，与上轮相同。
- 排除 `docs/reviews/tests` 后，工作区有 442 个已跟踪修改、250 个未跟踪文件；内容身份 SHA-256：`169117e43274cceb01e531c64da7e02795047b7c0fac0b95425c0a455b04c7df`。相对上轮 `703ab1d...` 已发生大规模变化。
- 测试期间 `test_dojo_factorial.py`、RMHD `accounting.py` 与 README 被并发修改；因此对当前版本单独复跑 `test_dojo_factorial.py`，结果 18 passed。其他结果只对应报告所列结束身份，不外推到后续改动。
- Python 3.12.14；uv 0.12.5；pytest 9.1.1；Apple M5 Pro。
- 主 `.venv` 的产品包从 `site-packages` 导入，但缺少本轮新增建模模块和新增 Task 案例。隔离复测使用 `/Users/zonghui/work/project_simulation/dojo_train/daily-tests/2026-09-23/run-1046/site`，由当前源码构建 spec/core/contrib/task/server wheel 后以 `--target --no-deps` 安装；未改主环境。

## 测试结果

| 分组 | 结果 | 时间 | 证据 |
| --- | --- | ---: | --- |
| 上轮失败 + PCNO 复测（主环境） | 12 pass, 1 fail | 6.45 s | `prior-regressions-pcno.xml` |
| 新建模、经典网络、算子/代理能力（新鲜 wheel） | 388 pass, 57 skip | 48.99 s | `new-modeling-fresh-wheel.xml` |
| 公共 API、recipe、Task、推理（新鲜 wheel） | 189 pass, 17 fail | 765.29 s | `public-recipe-task-fresh-wheel.xml` |
| 隔离安装消歧复测 | 1 pass, 2 fail | 30.34 s | `isolated-install-rerun.xml` |
| 并发修改后的 RMHD factorial 当前复测 | 18 pass | 0.59 s | `dojo-factorial-current.xml` |
| 主环境新增模块诊断 | 8 collection errors | 5.13 s | `new-modeling-capabilities.xml` |

去重规则：隔离安装复测覆盖公共组中的同名 3 项；factorial 当前复测覆盖公共组中的旧版本 18 项；主环境安装漂移只作环境诊断。最终源码结果为 `589 passed / 16 failed / 57 skipped`。

## 趋势与发现

1. **已恢复：随机重划回归终止。**
   - `test_open_dataset_applies_random_split` 本轮通过；首次失败 2026-09-21，持续 2 天后恢复。

2. **已恢复：公开 aero 配置加载回归终止。**
   - `test_aero_public_inputs_preserve_domain_defaults` 本轮通过；9 个公开配置现可加载并保留领域默认。

3. **已恢复：PCNO 环境阻断终止。**
   - `iapws` 当前可导入；PCNO inference/post/equivalence 合计 10 项通过。上一轮 5 个 error 不再复现。

4. **持续安装漂移：主 `.venv` 未包含当前源码资源与新增模块。**
   - 主环境 `test_resource_manifest_and_checks` 仍失败，当前少 5 个新案例：operator learning 3 个、surrogate modeling 2 个。
   - 8 个新增建模测试文件在主环境收集时报 `ModuleNotFoundError`；同一源码的新鲜 wheel 下相关 445 项为 388 pass / 57 skip，无失败。
   - 最小建议：源码功能修复完成后，再由用户授权按仓库规定重装受影响 force-include 包；有 Web 消费链时需更新正式 8000 并冒烟。当前不应把主环境结果当成新源码验收。

5. **新回归：旧五例显式 recipe / infer 基线与现行准备契约断裂（11 项）。**
   - 7 项在 trainprep 报 `KeyError: data_specs`：Transolver-3 的 NASA/ShapeNet 三个显式等价用例、三个 infer 用例及外部 wheel infer 用例。
   - 2 项 AB-UPT 的旧 post 路径被现行门禁拒绝：`现行准备记录需用 trainprep.preparation 消费，不能走旧物理准备接口`。
   - 2 项 AB-UPT 显式流程与冻结流程训练权重不再逐值一致，最大绝对差约 `1.02e-4` 和 `3.92e-4`。
   - 不解决会使“旧完整流程 ↔ 显式阶段”的既有等价声明失效，并使外部复制的 NASA Transolver-3 无法完成 trainprep。
   - 最小建议：先统一测试夹具与现行 `data_specs`/preparation v2 交接，再独立定位 AB-UPT 两轮训练随机状态或阶段调用差异；不要放宽逐值基线掩盖变化。

6. **新回归：研究资源和 RMHD recipe probe 合同漂移（4 项）。**
   - `resources.py` 新增相对导入后，源码按无包上下文直接加载失败；对应测试需改为包上下文，或公开模块需保留明确的直接加载边界。
   - `operator_learning.darcy` README 未满足现行案例目录要求的“改写”说明。
   - RMHD recipe probe 仍调用已不存在的 `configuration.validate` 与 `configuration.component`。
   - 不解决会让能力离线导出测试、案例发现合同和 JOREK recipe 工程探针失去可信入口。

7. **新回归：Task 外部 wheel 控制案例缺可选依赖。**
   - `test_wheel_install_outside_checkout` 在 task-labels 的 trainprep 子任务中报 `ModuleNotFoundError: ema_pytorch`。
   - 该用例已清除 `PYTHONPATH` 后复测，仍失败，不是本轮隔离 wheel 路径污染。
   - 最小建议：把控制案例所需 extra 明确纳入隔离验收输入，或确保该阶段不提前导入控制训练专属依赖；不要给主环境临时安装来掩盖 wheel 合同。

## Skip / Not run

- 57 个 skip 均为明确的真实证据、上游源码或设备门禁，包括经典网络真实十三组合、安装重放、部分上游参考及 CUDA/MPS 分支；不计通过。
- 因检测到正在运行的 RMHD 四组实验，本轮未继续扩展 Web、Vis、全量 pytest、长训练或大下载，避免争用资源。
- 5173 未监听；8000 只做 `/docs` 与 `/openapi.json` 只读检查。未操作用户任务、未重装或重启正式服务。
- 全量测试未完成，本报告仅代表上述圈定集合。

## 执行命令

- `uv run --no-sync pytest <上轮失败与 PCNO 圈定节点>`
- 当前源码分别构建 `ai4e-spec/core/contrib/task/server` wheel，隔离 `--target --no-deps` 安装到 `dojo_train/daily-tests/2026-09-23/run-1046/site`。
- `PYTHONPATH=<新鲜 wheel site> uv run --no-sync pytest <新增建模/经典网络/算子代理集合>`
- `PYTHONPATH=<新鲜 wheel site> uv run --no-sync pytest <公共 API/recipe/Task/infer 集合>`
- 清除外层 `PYTHONPATH` 后复测 3 个独立安装节点；随后复测当前 `test_dojo_factorial.py`。
