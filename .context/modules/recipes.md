# recipes 模板索引

- `docs/yaml-config-comparison.md`：五框架运行 YAML 的源码梳理与 Dojo 配置讨论；非实施决策，不替代 PRD 或架构正文。

平台原型映射：`docs/prototypes/dojo-web-wireframe.html` 通过配置快照展示 aero_cfd 四阶段及其产物交接，不执行或修改 recipe。参考图与字段来源见 web 模块索引。

普通文件集合，不是 workspace 成员或安装包。允许引用 core/spec/contrib；task 将来复制文件，不导入 recipe。

- `recipes/aero_cfd/README.md`：复制、安装依赖、执行和参数说明。
- `recipes/aero_cfd/config.yaml`：实验选择、路径插值与统计策略；归一化支持准备探测与可选物化。
- `recipes/aero_cfd/pipeline.py`：显式顺序串接 rawprep/trainprep/train/post。
- `docs/PRD/recipes/aero_cfd/PRD.md`：模板行为与迁移。
- `tests/integration/test_dataset_recipe.py`：复制脚本、路径、统计、失败与日志验收。
- `tests/recipe_assets.py`、`tests/legacy_pre.py`、`tests/fixtures/legacy_pre.yaml`：旧行为回归夹具，不是产品入口。

不包含 init/main、缓存、训练占位和用户组件目录；共享 manifest/adapter 在 contrib。

## 本次实施定位（2026-09-08）

- `aero_cfd/train.py`：probe/prepare/fit 单一会话入口。
- `aero_cfd/post.py`：薄入口，注入贡献组件后交给 post 装配。
- `aero_cfd/config.yaml`：公开采样预算、模型参数、损失权重、设备自动选择、Lion/调度/累积/`test_repeat`/快照与 VTKHDF 开关；post 含评估/保存/点云/完整网格回贴开关与 `sample_indices`。

## 多域模型变更

`recipes/aero_cfd/post.py`：贡献组件注入与唯一 session.launch；pipeline 登记 rawprep/trainprep/train/post。`config.yaml`：data_specs、trainprep、域采样、supervision，以及 post 评估/保存/点云/完整网格回贴开关。

验收导航：`.context/mvp/abupt-multidomain-acceptance.md`。

## 三阶段 recipe 与参考验收

- `recipes/aero_cfd/rawprep.py`：数据前处理显式业务流水线。
- `recipes/aero_cfd/trainprep.py`：独立准备、全分片校验与 preparation.json 引用。
- `recipes/aero_cfd/train.py`：消费准备引用、构建模型、目标、优化、评估与执行。
- `tests/integration/test_recipe_three_stage.py`：独立入口、完整流水线、干跑和数据冲突。
- `.context/mvp/abupt-reference-acceptance.md`：逐阶段官方对照及未完成门槛。

端到端样板默认包含 post；config 不预填未来准备引用或检查点。独立运行时可通过公开覆盖指向已有产物，连续运行自动交接。见 `.context/mvp/abupt-end-to-end-acceptance.md` 与 `tests/integration/test_post_reference.py`。

README 新增按 post-progress.json 检查部分交付、已有检查点仅补网格及自动比较协议说明；配置不增加未来输出输入项。

## Task 接入

- `aero_cfd/task-entry.json`：显式输入输出绑定、恢复键与标量比较定义；模板不导入 task。
- `.context/mvp/task-acceptance.md`：相关验收入口。

## 双模型组件入口

- `recipes/aero_cfd/`：共享阶段脚本。
- `examples/aero_cfd/shapenet_car_abupt/`、`nasa_crm_transolver3/`：复制案例、配置和使用说明。

验收状态与相关测试见 `.context/mvp/transolver3-acceptance.md`，正式规模数值对标已通过，旧公开配置兼容政策仍待确认。

## 五段配置与快照职责（2026-09-09）

configuration.py 为五段配置加载与业务参数映射；rawprep.py 调用库既有 datapre，不改库接口。test_recipe_configuration.py、test_run_config_snapshot.py、test_verification_config.py 覆盖本轮。

## 物理数据跨模型实验

- `docs/ai4s-framework-comparison.md`：Dojo 与五框架的能力比较；后续通过新模型、数据集和科研案例发现共同需求，相关建议按案例触发，不预设接入清单或前置重构。
- `tests/integration/test_framework_comparison_document.py`：比较文档的索引与仓内证据链接检查；本次只新增参考文档和演进约定，不改变案例执行行为。

examples/aero_cfd/ 下固定五个独立配置，阶段脚本来自唯一 recipes/aero_cfd；新增 nasa_crm_abupt、shapenet_car_transolver3_surface、shapenet_car_transolver3_volume。

状态与圈定测试见 `.context/mvp/cross-model-acceptance.md`。

- `docs/aero-cfd-server-runbook.md`：复制五例、CUDA预检、50轮配置、分阶段执行与报告交付操作手册。

- `.context/mvp/cross-model-50-acceptance.md`：沿用五例网络与共享入口的50轮实验；验收测试支持显式epoch/设备预算，历史默认不变。

## Web 复用

平台只复制现有 aero_cfd，经 task 的原 submit_run 覆盖原始处理阶段和固定样本。不修改模板或生成替代脚本。真实接入与输出交接见 `.context/mvp/web-rawprep-acceptance.md`。

- `aero_cfd/configuration.py`：规范模型采样写入 model.sampling；旧 trainprep.sampling 单键兼容，双键拒绝。字段容器和 PT/Zarr 格式保留于 rawprep。

## 本机实验存储位置

按 AGENTS.md 的本机约定，新训练输出使用 `/Users/zonghui/work/project_simulation/dojo_train/<实验名>/`，显式配置运行与预测路径。50轮运行已迁至 `dojo_train/dojo-cross-model-50`；七个用户指定的历史工具缓存/暂存目录已同名迁入 dojo_train，迁移记录为该目录下 `cache-relocation-20260910.json`。旧tmp位置仅保留兼容链接，未变更可复制模板的跨机器默认路径。
- `aero_cfd/task-entry.json`：当前比较量采样选择器使用 `model/sampling`，旧运行仍读取其代码快照中的历史 entry，不迁写冻结资产。
