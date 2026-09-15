# 独立推理验收记录

本次外流推理切片已完成，正式 Web 服务已接入。架构正文仍以 `docs/AI4E_Dojo_ARCHITECTURE (1).md` 第 5、9、19.11 节为准；本文件记录实际验收及范围。

## 分项结论

- **原子能力：通过。** `abilities/inference` 提供预测与执行原语，模型缓存和查询保留原数值行为。CORE 最终圈定38项通过、0失败、0跳过，包括五案例原生 infer 与旧 post 逐值对齐、扩展字段、旧网格输出和 MPS 回归。
- **业务步骤与脚本：通过。** 六套模板提供显式 infer；新 post 消费固定结果，独立 post 在 checkpoint 不可用时仍可读取既有结果。实际 core wheel、仓库外 recipe 训练/推理/读回通过。已核验旧模板保持原目录，未知修改不自动执行；旧锚点报告缺完整比较协议时显示 insufficient。
- **批次与权重固定：通过。** 当前任务多训练运行检查点 × 有序样本；完整字节固定到任务私有 assets，同任务串行，独立子运行和数据目录。最终任务/HTTP/契约18项通过，覆盖旧停止收据回归、权重更新后副本保持、串行收据、失败重试、幂等、启动前取消、协调器终态提交前中断后恢复且不重跑子运行。任务配置与版本不变。
- **工作台与结果交接：通过。** 九步稳定 slug，旧数字6→post、7→report保持。13项浏览器契约/HTTP测试通过，终态刷新与默认名称追加1项通过。真实2×2 CFD浏览器两轮均通过，结果可下载并进入后处理 Trame。

## 实际计算规模与结果

真实源为三辆 ShapeNet-Car 的原始 CFD 数据：1个训练样本，2个测试样本；CPU 小型 Transolver-3，分别2轮和1轮训练得到不同权重。该预算验收处理、推理、完整表面输出和平台交接，不代表生产精度或正式大模型吞吐。

- 项目与数据身份：`/Users/zonghui/work/project_simulation/dojo_train/infer-acceptance/real-cfd/context.json`。
- 检查点：`aaa67502710444d99e47375359aa176f:last.pt`、`77d0647fc97246149fa09200fe247db7:last.pt`。
- 测试样本：`param1/1dc757e77f3cfad0253c03b7df20edd5`、`param1/1e2f9cb6b33c92ea82381b04bbe0ce6d`。
- 两轮实际浏览器批次：`a5c67eb106d5437f94e4a8223f151329`、`b3e6104a3e2f41f1b793fd5423806c4a`，均 succeeded，4/4结果。各批次另存输出，不覆盖之前结果。
- 首轮浏览器通过25秒；终态通知与截图修正后的补验23.6秒。确认两行总体指标、四组文件、有效下载，以及嵌入 Trame 的基础显示对象。
- 证据目录：`dojo_train/infer-acceptance/browser-real/`、`browser-real-followup/`。后者分别包含 `inference-batch.png`、`inference-results.png`、`inference-metrics.png`、`inference-trame.png`，均已查看。前者结果截图只展示顶部选择区，不作为结果表视觉证据。

## 圈定测试与证据

所有 Python 验证使用 `uv run --no-sync pytest`，避免无关 workspace 依赖同步；运行前重新安装受影响包并核对安装副本。下列分组可能重叠，不相加声称独立总覆盖数。

1. CORE最终38通过：`test_infer_abilities.py test_infer_compatibility.py test_infer_extensions.py test_infer_stage.py test_post_mesh.py`。报告：`/Users/zonghui/work/project_simulation/dojo_train/infer-core-acceptance/corrections.xml`。此前网格与安装失败已修正后纳入这组，不用早期失败报告验收。
2. Task/Server/Spec最终18通过：`test_task_infer_batches.py test_task_infer_checkpoints.py test_task_execution.py test_web_inference.py test_infer_results.py test_infer_devices.py`。报告：`/Users/zonghui/work/project_simulation/dojo_train/infer-acceptance/parent-final.xml`；产物目录 `parent-final/`。
3. 实际五包wheel安装1通过：`test_infer_installation.py`。目录 `dojo_train/infer-acceptance/install-task-server/`。安装位置为该用例下 `installed/`；子进程校验 spec/core/task/server 从该安装目录加载，排队执行和HTTP启动通过，安装目录文件摘要不变。CORE独立wheel外部训练/infer/post另由第1组覆盖。
4. 旧脚本兼容11通过：`test_web_recipe_compatibility.py`，目录 `dojo_train/infer-acceptance/legacy-final/`。36份旧脚本固定清单在 `recipes/aero_cfd/legacy-profile.json`；通用模板6份Python正文的AST与未改写历史计划逐项一致。实际AS任务只读核对兼容通过。
5. 平台集成回归：`test_web_integrated_pipeline.py test_web_platform_operations.py test_task_contracts.py test_task_configuration.py test_web_architecture.py` 共28项通过；与旧profile同次初跑35通过/4个旧profile失败，4项已在第4组全部修复重跑。
6. 阶段与配置回归：`test_web_stage_consistency.py test_task_configuration.py`，28通过、2跳过、1个旧阶段枚举断言需同步。已把断言更新为包含infer的现行能力，并单独重跑该项通过。两项跳过为另需显式真实模型选择环境的专项，不能计作该专项验收；本次真实CFD推理由独立证据覆盖。
7. 文档19通过：`test_task_documents.py test_recipe_documents.py test_aero_cfd_documents.py test_web_design_documents.py`。历史计划按迁移前AST核对，不要求把历史计划改写为当前源码。
8. Web：`inference.spec.ts http-errors.spec.ts` 13通过；修改终态通知/默认名称后 `inference.spec.ts --grep '多检查点批次'` 1通过；`inference-real.spec.ts` 两次实际CFD均通过。证据 `dojo_train/inference-web/final/`、`terminal-followup/` 和上述真实目录。构建与 `check:architecture` 通过，已有包体积提示不等于性能验收。
9. 新增任务/服务/契约与相关测试的圈定 Ruff 检查通过。未跑全仓测试冒充专项验收。

## 正式服务与使用

- 用户入口 `http://127.0.0.1:5173`，正式后端8000已安装更新并重启；最新进程记录 `dojo_train/infer-acceptance/live-service.json`。
- 主任务通过应用内浏览器实际打开原AS任务的 `/infer`：九步导航、推理选择和批次区域正常；原任务未训练，因此检查点为空，设备可选择MPS。这不是对AS执行MPS推理的证明。
- 独立真实验收服务8010保留上述CFD项目供检查；不把它的训练结果写入AS任务。
- 程序入口顺序：读取候选与样本 → check_inference → submit_inference → 查询批次/结果 → 按固定文件引用打开Trame。新配置不创建任务版本；checkpoint字节固定与结果输出各自归属明确。
- 重开页面仅查询结果。恢复中断批次核对已有子运行收据；失败重试创建新批次/子运行，复用原固定权重而不覆盖原输出。

## 范围边界

本期支持同一任务不同训练运行的兼容权重和既有准备样本，不扩展跨任务权重或未登记新几何。默认避开当前项目已知Dojo运行占用的加速设备；外部进程占用不保证发现。CPU真实CFD与既有MPS数值回归已验收，未执行CUDA生产预算。历史锚点结果缺完整协议时不进行数值排名。两项无关模型选择专项跳过已单独披露。

## 可复现入口

`tools/verification/inference_acceptance.py --root <独立验收目录> --source <真实ShapeNet根>` 准备1训练/2测试样本与两份权重。输出context供 `e2e/inference-real.spec.ts` 使用，设置 `DOJO_WEB_URL`、`DOJO_INFER_PROJECT`、`DOJO_INFER_TASK`、`DOJO_INFER_CHECKPOINTS`、`DOJO_INFER_SAMPLES`；缺失环境导致skip不算验收。产物统一放用户指定的 `dojo_train` 目录。

## 治理与前端文件导航

本次涉及的治理与前端入口如下；算法、任务与服务的完整文件导航见对应模块索引。

治理与文档：

- `AGENTS.md`
- `.context/index.md`
- `.context/modules/ai4e-task.md`
- `.context/modules/ai4e-server.md`
- `.context/modules/ai4e-spec.md`
- `.context/modules/ai4e-web.md`
- `.context/mvp/inference-acceptance.md`
- `.cursor/rules/ai4e-algorithm-architecture.mdc`
- `.cursor/rules/ai4e-recipe-authoring.mdc`
- `.cursor/rules/ai4e-task-architecture.mdc`
- `docs/AI4E_Dojo_ARCHITECTURE (1).md`
- `docs/PRD/ai4e-task/tasks/PRD.md`
- `docs/PRD/ai4e-task/storage/PRD.md`
- `docs/PRD/ai4e-server/modules/PRD.md`
- `docs/PRD/ai4e-spec/artifacts/PRD.md`
- `docs/PRD/ai4e-web/src/PRD.md`

本轮 Web 收尾（此前完整 Web 切片目录见模块索引）：

- `packages/ai4e-web/src/modules/inference/useInference.ts`：终态通知、默认名称。
- `packages/ai4e-web/src/modules/inference/InferenceWorkspace.tsx`：名称默认提示。
- `packages/ai4e-web/e2e/inference.spec.ts`：实际请求默认名称断言。
- `packages/ai4e-web/e2e/inference-real.spec.ts`：终态刷新、进度/文件/指标进入视口及分别截图。

`tools/verification/inference_acceptance.py` 及后端各圈定测试由主任务编写，本轮只补导航与实际进度，不改这些代码或服务生命周期。
