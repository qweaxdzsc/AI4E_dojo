# recipes 模板索引

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
