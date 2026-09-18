# 数据集声明驱动原始处理验收

实施日期：2026-09-14。覆盖 ShapeNet-Car 与 NASA CRM；全部官方名单发现和真实转换规模分别报告。

## 当前实现

数据组件 `describe_rawprep()` 从 manifest 交付默认配置、绑定槽位、输出字段、功能依赖与几何数值参数。未绑定即可读取。默认优先级为数据集声明、案例配置、当前任务值；显式空映射/空列表保留。恢复案例默认读取创建快照中的案例参数，普通编辑不新增版本。

`inspect_dataset()` 提供真实字段、稳定样本身份与依赖。页面默认按全部声明样本执行，可切分片或指定样本；文件树仅浏览。代表检查标明覆盖范围，执行前核验所选样本。旧文件选择请求保留原范围。

PT 逐场布局保存张量，向量保持多分量；历史容器保持字典语义。NASA 直接从 HDF5 转换，清单只发布实际输出及物理布局。缺少模型字段时准备明确报缺项。ShapeNet 原七字段及几何/清洗数值不变；点到表面距离为可选能力，与最近顶点方式互斥。

## 证据位置

本次根目录：`/Users/zonghui/work/project_simulation/dojo_train/manifest_rawprep/20260914/`。

- `source-before.tgz`、`baseline.py`、`baseline/`：修改前源码和真实处理基线。
- `inputs.json`：实际原始来源与训练/测试样本身份。
- `real/*/*/evidence.json`：服务创建的任务、运行、完整物理清单和逐字段精确对照结果。没有 evidence.json 的目录为失败尝试，不作为成功证据。
- `browser-completed/`：首次两个数据集真实页面执行与 PT 预览截图。
- `browser-audited/`：最终指定样本及显式小名单全部执行的截图、任务与运行身份。
- `downstream/`：复制案例消费新清单的准备记录和日志。
- `wheels/`、`wheel-check/`、`wheel.log`：真实 wheel 安装与仓库外扩展运行。

## 已核验的真实规模

ShapeNet 与 NASA 各使用训练和测试各一个真实样本，全点处理。分别运行默认保存与修改保存/重命名，共四次服务运行。每个 PT 重新读取为 torch.Tensor，与修改前基线按逻辑来源逐元素比较，rtol=0、atol=0；清单没有虚报取消字段。ShapeNet 默认七字段，NASA 默认八字段（坐标、法向、Cp、Cf、面积、工况、全局目标、身份）。

两个数据集的新默认清单均生成真实准备记录。NASA 仅一个训练样本导致工况 zscore 标准差为零；本次准备验收将工况设为 identity，其他准备设置保留。该显式验收配置不改变框架默认值，也不代表生产统计精度。

浏览器从首页进入项目和任务，修改保存名单，选择训练/测试两样本执行，刷新保留修改并预览真实 PT。官方发现 ShapeNet 889（train 789/test 100）、NASA 149（train 84/validation 21/test 44），依赖分别 1778 和 3，代表样本分别检查 2 和 3 个，依赖缺失为 0。`official-catalog.json` 保存发现结果，不能据此声称整库全部字段检查。小名单全部执行两套均实际处理 train 1/test 1，不受文件树勾选影响。

## 圈定检查

- A1/A2：`test_dataset_rawprep_descriptor.py`、`test_task_configuration.py`，无绑定描述、创建默认、保存、空值及版本。
- A3：`test_rawprep_manifest_configuration.py`，依赖、互斥、格式和参数类型。
- B1：`test_rawprep_field_catalog.py`、`test_nasa_crm_data.py`，缺场、类型、形状与真实覆盖。
- B2/B3：`test_rawprep_field_selection.py`、`test_physical_dataset_contract.py`，逐场、旧容器及身份。
- C1/C3：`test_rawprep_sample_selection.py`、`test_manifest_rawprep_real.py`、`test_rawprep_dataset.py`，全名单/子集、过期检查、空选、异常和完整清单门禁。
- C2/C4：`test_manifest_rawprep_real.py`、`test_web_rawprep_handoff.py`，精确数值、VTKHDF预览、物理读回与真实准备。
- D1/D2：`test_recipe_explicit_equivalence.py`、`test_recipe_extensions.py`、`test_task_installation.py`、`test_web_recipe_compatibility.py`，五例短训/恢复/预测等价、用户能力和实际 wheel。
- E1：`test_web_design_documents.py`、`test_recipe_documents.py`、`test_aero_cfd_documents.py` 与相关架构测试。
- E2：`e2e/manifest-rawprep-real.spec.ts`，真实页面执行；字段提取改为每个 `.pt` 一张卡片，不再用声明清单勾选。最终 2 项真实流程与 1 项完成状态核对通过。

## 验收结果

最终结论：ShapeNet 跑通；NASA 跑通；前端修改/保存/刷新生效；PT 全部为独立张量且数值正确；新清单可读回并生成下游准备记录。以下是圈定结果，不合并重复用例冒充独立测试总数。

- `regression.log`：51 passed（描述、配置、字段、样本、真实 ShapeNet/VTKHDF 交接、失败门禁和物理契约）。
- `final-contracts.log` 首轮 55 passed/1 failed，发现创建后默认注入导致工作树变化；修复后 `creation-final.log` 28 passed，`defaults-final.log` 21 passed，覆盖该失败及配置插值保留。
- `real-gates.log`：2 passed，两个数据集默认/修改共四次真实运行，另拒绝过期检查和名单外样本。逐场 PT 与修改前基线精确一致。
- `doc-final.log`：19 passed；六节结构、功能清单和实际源码正文一致。新可视化章节纳入逐章校验，没有删掉旧断言。
- 显式流程/扩展回归：17 passed，包含五例小规模 CPU 训练、恢复、预测及用户扩展。`wheel-delivery.log`：1 passed，安装本次最终 wheel 后复制案例，速度模长保存、统计、准备和下游运行通过；wheel 已核验包含两个 manifest/descriptor/inspection。
- `browser-audited.log`：2 passed，两种数据集分别指定两样本执行及显式两样本名单全部执行，共四次页面提交。`browser-output-verification.json` 对四次运行全部 PT 再做独立复读与精确对照。
- `browser-state-verified.log`：1 passed，重新进入两任务核对页面日志 succeeded 与服务成功一致。最终状态截图在 `browser-state-verified/`；早期截图捕获页面轮询更新前的 running，不作为最终状态证据。
- 前端构建、微领域边界检查及本次新增 Python 相关静态检查通过；这些检查不替代真实处理。

浏览器执行记录：

- ShapeNet：任务 `e7cb45d4490e41469337028a9b6f0fc4`；指定样本运行 `ac6f8920a8b04b72bdf88ded6a7cb0c2`；全部小名单运行 `66794a1399d747908f1b79717e5c502b`。每次两个完整样本，路径详见 `browser-output-verification.json`。

- NASA：任务 `980b965fcc654811a489178dfdbb72c3`；指定样本运行 `6ef835055d0f402f9acfa31e3c33d793`；全部小名单运行 `e6d73695431b40a2b67086afe550be5f`。每次两个完整样本，路径详见 `browser-output-verification.json`。

## 已发现并修复的问题与边界

Ant Select 自动化操作需先展开/聚焦并等待选项，本次补了逐次样本数断言；某次旧 NASA 浏览器尝试只选择到测试样本，已从正式证据排除并重跑。默认参数在创建快照前展开，保留配置插值；恢复案例默认与当前编辑互不覆盖。新建任务不因默认注入显示为已修改。

NASA 小样本准备使用显式工况 identity，原因见上文。这里验证真实全点转换、读回、字段依赖和下游准备；不声明整库转换、完整训练精度或所有页面状态逐像素一致。旧准备、检查点、历史数值证据保留原样。

机器可复核汇总：`/Users/zonghui/work/project_simulation/dojo_train/manifest_rawprep/20260914/acceptance.json`。输出复读脚本为同目录 `verify_browser_outputs.py`，使用 `uv run --no-sync python` 执行。


## 后续修复：旧任务 recipe_profile_changed

用户原任务 `as`（项目 `34f74688805f4d4e815885da04a081d2`、任务 `f9fca9f6c4414c17abae50f8713fd86b`）创建于旧显式入口版本。当前模板增加默认展开和格式整理，原逐字节门禁误报。现按 Python 语法/入口 JSON 判断同义性，仅对已审定的历史配置加载入口登记有限兼容关系；新逻辑、语法错误、缺文件、额外脚本与入口变化仍拒绝并列出文件。提交给旧入口的配置是页面显示的完整有效默认值。

- `profile-fix.log`：14 passed，覆盖默认和两个注册案例的旧配置保存、格式/注释、真正逻辑改动拒绝、真实旧加载入口的一样本七 PT 输出、原配置未写回，以及原始处理/架构回归。
- 文档圈定：15 passed；相关静态检查通过。
- 实际 8000 服务已刷新。`profile-live.json` 记录用户原任务的真实样本检查返回 200，样本 1、依赖文件 2。任务原脚本、配置修订和版本保留；没有启动该用户任务的整库转换。
- 历史加载源码固定在 `tests/fixtures/rawprep_legacy/configuration.py`；兼容关系绑定当前入口和旧入口的语法摘要，未来逻辑变化须重新核验。

后续原任务产物复核：恢复 8000 服务后发现 `as` 已有成功运行 `b8517271de324a96aa2c32a8fbff9090`，本轮直接复读该运行，没有重复提交。实际转换一个训练样本 `param1/1dc58be25e1b6e5675cad724c63e222e`，清洗后表面 3586 点、体积 28504 点。七个 PT 均为 float32 张量，与修改前基线逐值、形状、类型一致，两个域的来源实体 ID 也完全一致；物理视图及准备字段接口读回通过。旧基线清单没有物理布局，复核时显式提供七字段布局，未改写历史清单。原任务脚本及配置与该运行快照摘要一致。证据为同批次 `profile-live-run.json`，其中包含实际数据清单和运行日志路径。本轮没有重新执行浏览器操作、完整数据准备或训练，也没有扩大为整库转换。

当前服务重新检查原任务也通过：官方目录发现 889 样本，指定上述单样本的执行预检返回 200，依赖文件 2 个，没有再次触发 `recipe_profile_changed`。文档圈定 `test_web_design_documents.py`：12 passed。

## 全部样本读绑定宇宙（2026-09-17）

页面「全部」只读绑定数据集的官方或自身分片，回传 `sample_universe=bound_dataset`，不吃任务配置里看不见的 `dataset.partitions` 子集。当次执行或发布的名单只属于该次输出，不得写回下次 catalog。2026-09-17 23:50 正式 8000 重装并重启后，对照任务 catalog/页面「全部」为 **889** 样本、1778 来源文件，`sample_universe=bound_dataset`。圈定 `test_web_rawprep.py`、`test_web_dataset_binding.py`、`test_web_rawprep_handoff.py`。正式五页证据见后处理专项验收。

## VTKHDF 默认勾选（2026-09-18）

ShapeNet 新任务与缺键按清单/案例默认勾选 VTKHDF；NASA 仍不显示。对照任务当时已保存为关，已用正式 8000 写回 `rawprep.vtkhdf: true`。页面缺键回退 `profile.defaults.vtkhdf`。圈定 `packages/ai4e-web/e2e/rawprep-consistency.spec.ts`（7 passed）。正式 5173 原始处理页 VTKHDF 已勾选，未重装、未重启。证据 `official-20260918-vtkhdf/`。
