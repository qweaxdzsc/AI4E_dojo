# 模型设置先选模型验收

实施与验收日期：2026-09-14。已完成本切片，日常平台已重启加载新接口。

## 行为与边界

- 模型页第一项选择同数据集登记模型，参数草稿和能力一起刷新；当前结构只有案例默认档，不虚构版本。采样跟随当前模型字段：AB-UPT 为点/锚点/查询，Transolver-3 为种子/步长/分块，步长只读，切片数量在主干参数；损失不可配时仍展示固定项。换模不沿用上一模型采样字段。模型设置不展示权重加载。圈定 `test_model_sampling_capability_follows_component`、换模回读与 `model-picker`/`stage-consistency` 页面断言。
- 显式换模完整替换模型、训练和准备段，模型组件从登记案例取得；普通保存保留未编辑字段和用户扩展。
- 全部训练默认重置，物理清单、原数据绑定、原始处理配置、数据/运行目录与研究版本保持。
- 旧准备与权重选择解除，历史文件与创建来源保留；旧准备不能用于新模型。物理清单缺目标字段时仍拒绝准备。
- 清单/准备输入与相关告警放在右侧，模型页不显示检查点告警。last/best/latest 保持运行时标签语义。结构跟踪消费现行 version=2 准备记录，与训练同一条读盘链；旧物理接口不再对现行准备抛 `KeyError('dataset')`。
- 保存失败不提交后续操作；选项失败可重试，任务切换后的迟到响应不覆盖新任务。

## 圈定验证

共 91 个不同 Python 用例通过，重复验证不重复计数：

- 70 项配置、阶段一致性、任务创建/绑定、recipe 兼容及仓库外真实扩展回归；`regression.xml`：70 passed，无 skip。
- 2 项新增受控绑定保持回归，覆盖 ShapeNet 目录及 NASA 三文件。
- 1 项新增候选配置不能执行的限制用例；task 最终文件共 3 passed，其中另两项已计入 70 项。
- 16 项文档、依赖边界、前端微领域与冻结准备契约；`docs-contract.xml`：16 passed。
- 2 项显式真实换模交接；最终 `real-field.xml`：2 passed，无 skip，含缺失法向字段清单拒绝。

浏览器共 10 个不同流程通过：`model-picker.spec.ts` 5 项、`stage-consistency.spec.ts` 3 项、`model-inspection.spec.ts` 本次真实换模 2 项。最终截图在 1920×1080 视口采集，已查看真实两栏与结构图；1280 视口沿用既有响应式上下排列，不声称逐状态像素一致。

前端构建、微领域检查、修改范围 Ruff 与差异空白检查通过。构建仍有既有大包提示，测试仍有 FastAPI/Starlette 弃用提示，均非失败。

## 真实规模与产物

- ShapeNet：一份真实 CFD 训练样本，原始处理 → AB-UPT 准备 → 切换 Transolver-3 表面 → 新准备 → CPU 正式网络结构生成；保留 256 隐藏宽度、24 层。
- NASA：真实 8 训练 / 1 验证 / 1 测试样本，每例 454404 个表面点；同样完成原始处理、旧准备拒绝、新准备及 CPU 正式 Transolver-3 结构生成，保留 256 隐藏宽度、24 层。
- 不以本次准备/结构检查声称训练精度、网络数值等价或生产规模训练通过。

新输出与缓存统一在 `/Users/zonghui/work/project_simulation/dojo_train/model-picker/`：

- `regression.xml`、`docs-contract.xml`：圈定用例结果。
- `real-field.xml`、`real-field-evidence/`：含缺字段拒绝的最终真实交接及任务/运行/准备记录。
- `real-evidence/`：浏览器结构生成使用的实际任务和准备身份。
- `browser-final/`、`browser-real-final/`：最终浏览器结果及两数据集结构截图。
- `installed-source.json`：真实 wheel 重装后四个关键源码文件与安装副本逐字节一致。
- `live-service.json`：日常平台重启后的健康状态与既有任务模型选项读取。

历史验收路径有已失效项，本次另用实际存在的本机 CFD 原始数据生成新产物，未改写历史证据。安装环境下的仓库外复制 recipe 与用户能力已由 `test_recipe_extensions.py` 实跑，包含新增场保存、读回、归一化及训练消费。

## 重跑入口

Python 使用 `uv run pytest`，可加 `--no-sync` 保留已核验安装环境。圈定文件：`test_web_stage_consistency.py`、`test_task_configuration.py`、`test_web_dataset_binding.py`、`test_web_recipe_compatibility.py`、`test_web_project_task.py`、`test_recipe_extensions.py`，以及上述文档/契约用例。

真实 CFD 用例在 `test_web_stage_consistency.py::test_model_switch_real_preparation_handoff`；设置 `DOJO_MODEL_PICKER_REAL=1` 与 `DOJO_MODEL_PICKER_EVIDENCE=<本次证据目录>`。未启用时明确 skip，不能计为真实验收。`--basetemp`、pytest/uv 缓存需指向本次 dojo_train 目录。

真实浏览器使用 `DOJO_MODEL_PICKER_EVIDENCE=<证据目录>`，以两个证据文件中的 platform_root/data_roots 启动独立服务；端口从 `DOJO_MODEL_PICKER_PORT` 起连续两个，默认 8017/8018。运行 model-inspection.spec.ts 中“换模后真实”两项，不依赖旧平台任务。

## 文档与部署

同步 AGENTS、总索引、Web/Server/Task 模块索引、相应 PRD、Task 开发规则及生成的请求契约。task 候选描述是 describe_case 的只读配置覆盖，不能用于执行；核心算法与案例脚本未修改。

日常服务重启前已核对无进行中的研究运行或辅助检查；使用原 root、template、三组授权 data-root 和 8000 端口启动新进程。既有项目与任务未改写，浏览器刷新即可调用新模型选项接口。
