# 准备切片选择与旧任务写回验收

日期：2026-09-18 17:23–17:33。对照任务 `测试09182`（逻辑项目 `179ed1fe447b415b8870c45b6a89a296`，磁盘项目 `8ef5b810780b4d50bc1311be0db90156`，任务 `01400e5e5b8a4bd88d43f658ddc2fb9f`）。正式入口 `http://127.0.0.1:5173` 代理 `http://127.0.0.1:8000`。隔离 `7999`/`5172` 不作为本切片验收。

产品规则：准备记录固定交出 train/test/eval；训练选其中一份，默认训练集；推理页签读准备切片，不回退源清单。历史准备文件不改字节。旧任务缺训练切片或仍写 `validation` 时，打开/检查/提交写回配置，不新建研究版本。

Experience 检索 `receipt_949bc33dee774d3fbe661982c3ee5d3c`：无覆盖本切片的条目。

## 发布

2026-09-18 17:23 按当次授权执行 `uv sync --group dev --group visualization --reinstall-package ai4e-core --reinstall-package ai4e-server`。冒烟中发现换模保存若整段替换 `train` 会丢掉训练切片键，随后 GET 写回改修订导致 409；17:40 补上保存时合并缺键，再重装 `ai4e-server` 并只重启 8000。现行安装摘要：`split.py` `ecd08e569abfbf59`，`stages/domain.py` `09ccf81ca91c2948`，`stages/application.py` `7315f5be9449ee28`，`inference/application.py` `959db9c1c42e5160`，`fitting.py` `252c435fbb0aa36a`。

正式 8000 现进程 **85161**（2026-09-18 17:40:22），参数与此前正式入口相同。5173 未动：Vite **23629**（2026-09-17 14:53:17）。回退：重装变更前包版本并再只重启 8000。

## 圈定 pytest

源码侧此前 36 通过 / 1 跳过（安装门禁）。浏览器：`e2e/stage-consistency.spec.ts` 训练设置（含空评价集不能开训）通过；`e2e/inference-selection.spec.ts` 7 项通过。

重装后圈定：`test_trainprep_split.py`、`test_web_recipe_compatibility.py`、`test_web_configuration_composition.py`、`test_web_stage_consistency.py`、`test_infer_inspect_contract.py`。换模保存补键后，`test_registered_model_switch_replaces_defaults_and_preserves_identity` 4 项通过。整组按修复后计数为 116 通过 / 2 跳过。

## 正式 Web 冒烟（5173→8000）

入口：`http://127.0.0.1:5173/projects/179ed1fe447b415b8870c45b6a89a296/tasks/01400e5e5b8a4bd88d43f658ddc2fb9f/training`（无阶段 slug 会落到项目列表，须带 `training` / `infer` / `trainprep`）。

写回前配置无 `training_split`，哈希 `28719021846c9205fb4b5b9064144833842ffce72520c4bb66c994048131a57f`。打开配置后写回 `train.training_split: train`，修订 `57ee715e92c7260c01432731697a265ee1f9db8c6600994c3cec6a0b4b5fb368`，不新建研究版本。`evaluation_split` / `infer.split` / `post.split` 本就为 `test`，无残留 `validation`。`trainprep.split.counts` 已有 `eval: 0`。

阶段输入绑定准备 `321151f000d648b9a40429f407307a4f` 的 slices：训练 789、测试 100、评价 0，方法 original，种子 0。推理样本接口（检查点 `08bbe33e8a7c4b628487fa7dd0c5b042:last.pt`）partitions 同为 train/test/eval = 789/100/0，无 `official` 键；preparation revision `6c2f3b5f3665416a4b5ae6aae68c4e0ba3dd53102ed6add1b15fe28e36286c8b`。

| 项 | 操作 | 结果 |
| --- | --- | --- |
| A 打开旧任务 | 打开对照任务训练设置 | **通过**。任务名 `测试09182` 可读，训练切片默认「训练集（789）」，评估/写出为「测试集（100）」。截图 `prepared-slices-training.png`、`prepared-slices-training-slice.png`。 |
| B 写回配置 | 打开配置后出现训练切片，旧 `validation` 改评价集 | **通过**。GET `/configuration` 写入 `training_split: train`，修订随 YAML 内容哈希更新。无 `validation` 残留。 |
| C 训练切片 | 能选训练集并看到人数；空评价集不能开训 | **通过**。下拉为训练集（789）/测试集（100）/评价集（0）。选评价集后「开始训练」禁用，提示「所选切片没有样本」。截图 `prepared-slices-empty-eval.png`。改回训练集后保存并重开仍是「训练集（789）」，开始训练可用。 |
| D 推理页签 | 三个页签来自准备，不出现源清单官方测试集冒充 | **通过（目录）/ 部分（页面人数）**。页签固定为训练集/测试集/评价集，无「验证集」。HTTP 目录 789/100/0 来自准备记录。页面人数停在 0：检查点标记「当前 trainprep 与检查点 effective_config 不兼容」，前端不把不兼容检查点并入共用目录。此兼容提示是既有检查点/当前准备不一致，不是源清单官方分片冒充。截图 `prepared-slices-infer.png`。 |

数据准备页方法为保持原划分，中栏 789/100/0，可见「中栏人数不会改发布名单」说明。截图 `prepared-slices-trainprep.png`。

未改：四份历史 `preparation.json` 字节与冒烟前哈希一致；绑定源分片名单未改写。用户未改过的缺键才写回默认训练集。

## 重装后圈定

首次重装后该组曾 3 失败：换模保存未带训练切片键，打开配置写回改修订，后续保存 409。保存路径合并缺键后，换模 4 组合通过。另 1 项 `nasa_crm_transolver3-abupt` 曾报 contrib 组件导入失败，重跑即过，不计入本切片缺陷。

## 2026-09-22 随机跨来源重划修复（源码与隔离 wheel）

`ManifestIndex.remap_partitions` 改为目标分片精确匹配、`eval`/`validation` 别名匹配、唯一候选跨分片移动；缺失和多来源歧义分别失败。新增用例逐值读回原 train/test/validation 张量，并核对原 manifest、记录路径和张量文件字节不变。

- 新 Core wheel 位于 `/Users/zonghui/work/project_simulation/dojo_train/random-split-pcno-20260922/wheels/`，隔离 Python 从该 wheel 加载；`test_trainprep_split.py` 连同公开配置/资源/PCNO 文档组共 38 项通过，其中切分文件 16 项全部通过。
- 下游 `test_trainprep_consume.py`、`test_train_resolved_config.py`、`test_web_stage_consistency.py`、`test_task_configuration.py` 在当前主环境为 90 通过、2 跳过。一个跳过明确是主安装副本尚未附带新切片目录，另一个要求 `DOJO_MODEL_PICKER_REAL=1` 的真实换模专项；两者不计为正式通过。
- Web 架构检查和生产构建通过。`stage-consistency.spec.ts` 的 16 项浏览器用例因 `127.0.0.1:5173` 未监听而全部在 `page.goto` 前失败，没有形成页面功能证据。

授权前状态：**源码与隔离 wheel 已验收，主安装副本和正式 8000/5173 尚未发布、未验收**。当时未触碰历史任务或 preparation 文件。

## 2026-09-22 正式发布与随机切分页面验收

用户随后明确授权正式发布测试。按仓库规则执行完整 `dev + visualization` 同步并重装 Spec/Core/Contrib/Task/Server；同步时目标树摘要为 `1f3d4381e0c0642f2621c13546f5e187cae3fd07b9058c831c809157af6ca4ba`。正式 8000 为 PID `90789`，5173 为 PID `93327`，两端健康检查均为 HTTP 200。Core 的 `manifest.py` 源码与安装副本 SHA256 均为 `e8414ada6c6e03d9dbc4e4e767a9604523daefdbeec81a728d2e3494af49930b`。

为避免修改历史任务，新建项目“随机切分正式验收 20260922”（逻辑项目 `e24cb10be16048fdbbdb48e66d3b2f14`，磁盘项目 `27ae9d53ada54cc48c734be306ac995f`）及任务“三样本随机切分正式验收” (`e06623e821564b2fa74c95fd4e82eb41`)。正式页面为 `http://127.0.0.1:5173/projects/e24cb10be16048fdbbdb48e66d3b2f14/tasks/e06623e821564b2fa74c95fd4e82eb41/trainprep`。

- 首次 300 点夹具在真实 AB-UPT 准备中因候选不足失败，运行 `cbcbbf65e728405183bbbb3152796962` 保留为失败证据；没有改小门禁或把失败算成通过。
- 随后另建每域 1024 点的三样本夹具 `random_split_formal_20260922_0707`。源清单原分片为 train=`train-a, train-b`、test=`test-c`，SHA256 为 `a5ba8c672f270298969d26c3650f00a9da7e83036d17fa41965547434b35d85c`。
- 页面选择全部 3 个样本、随机方法、seed 0、train/test/eval=`2/0/1` 后提交；页面显示 100% 和 `succeeded`，成功运行 `d0a870e55c5449f191ae7615c7b94042`，日志时间 2026-09-22 15:11:41。
- 准备记录实际保存 train=`train-a, test-c`、test=空、eval=`train-b`；原 test 样本确实移动到新 train。安装后的 `ManifestIndex` 从该记录逐样本读回全部 7 组张量，每组形状均为 1024 点；`test-c` 的 `surface_pressure` 均值为 11.5，证明不是只改状态或名称。
- 正式 `stage-inputs` 返回 train/test/eval 三切片人数 `2/0/1`，方法均为 random、seed 均为 0；运行摘要的 `research_status=completed` 且 trainprep 阶段为 `succeeded`。
- 发布后圈定随机切分、外流配置、Task 资源与 PCNO 文档共 38 项通过；`stage-consistency.spec.ts` 16 项通过。全部 19 个 PCNO 文件另计 63 通过、4 跳过，跳过不计通过。

验收后有其他 Agent 继续修改共享工作树。`manifest.py` 仍与正式安装副本一致；Task `resources.py` 源码已不同于安装快照。因此本节正式证据严格对应上述同步时树和 PID，不声称覆盖同步后并行改动，也未为追随并行树再次同步或重启。Mac 随后锁定，无法补录第二次截图；已有页面提交、正式 API、日志、准备记录及张量读回证据保持有效。
