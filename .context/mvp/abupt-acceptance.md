> 多域接口已替换本记录的旧双域接口；当前验收以 abupt-multidomain-acceptance.md 为准。本文件保留前一阶段的历史结果，不代表新结构已通过同样数量测试。

# 历史阶段记录：Aero CFD / AB-UPT 本期验收记录

日期：2026-09-08。范围为用户批准的五类业务与训练闭环计划 A1–I4，共 34 个功能叶子；不扩展此前明确排除的功能。

## 执行结果

最终统一执行：**273 passed，0 failed，0 skipped，20.91 秒**。覆盖下方 34 个功能叶子，所有映射节点均已与 JUnit 成功结果核对。一个上游 Torch JIT 弃用提示，不影响执行。不同轮次结果不累加。

修改范围内 ruff check、ruff format --check 通过；六份相关 PRD 的六节结构及功能列表/详解编号一致性检查通过。未以全仓测试替代相关集合，也未声明执行全仓 mypy/Sphinx 门禁。

环境：macOS ARM，Python 3.12.14，Torch 2.14.0，PyG 2.6.1。uv.lock 与已安装 workspace 已同步。JUnit 原始结果：`/tmp/dojo-abupt-acceptance.xml`（临时文件可能被系统清理，本记录保留摘要和可复跑命令）。

## 可复跑命令

在仓库根目录先执行 `uv sync --locked --all-packages --all-extras`。本地包若为构建安装副本，源码修改后需加 `--reinstall-package ai4e-core --reinstall-package ai4e-contrib` 再测试。

```bash
OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 uv run --locked --all-packages --all-extras pytest \
  tests/contract/test_model_components.py \
  tests/integration/test_source_read.py \
  tests/integration/test_extract_clean.py \
  tests/integration/test_geometry_domain.py \
  tests/integration/test_pre_materialize.py \
  tests/integration/test_dataset_recipe.py \
  tests/integration/test_train_dataset_read.py \
  tests/integration/test_shapenet_pre_recipe.py \
  tests/integration/test_recipe_logging.py \
  tests/integration/test_train_normalize_sample.py \
  tests/integration/test_normalized_dataset.py \
  tests/integration/test_abupt_components.py \
  tests/integration/test_train_batch_model.py \
  tests/integration/test_train_loop.py \
  tests/integration/test_model_evaluation.py \
  tests/integration/test_train_checkpoint.py \
  tests/integration/test_train_recipe.py \
  tests/integration/test_train_abupt_real.py \
  tests/integration/test_rawprep_dataset.py \
  -q --tb=short --show-capture=no --junitxml=/tmp/dojo-abupt-acceptance.xml
```

## 逐项验收映射

同一用例可以覆盖多个功能叶子；参数化场景在 JUnit 中单独计数。下面列出的节点均须实际通过，不能以收集成功代替执行。

- **A1** 原始处理迁移且 pre/pipeline 保持行为：`tests/integration/test_dataset_recipe.py::test_copy_pipeline_and_pre_are_equivalent`。
- **A2** 正式依赖方向与旧路径移除：`tests/contract/test_model_components.py::test_core_spec_dependency_direction_and_no_old_paths`。
- **A3** 提交失败保护旧样本、禁止完整清单：`tests/integration/test_pre_materialize.py::test_commit_failure_protects_old_data`；`tests/integration/test_dataset_recipe.py::test_failure_keeps_commits_without_complete_manifest`。
- **B1** 清单只解析一次，重复轮次逐样本加载：`tests/integration/test_train_dataset_read.py::test_manifest_index_parses_once_and_reads_on_demand`。
- **B2** 标量通道与表面物理零距离：`tests/integration/test_train_dataset_read.py::test_one_dimensional_pressure_becomes_column`；`tests/integration/test_train_dataset_read.py::test_surface_sdf_is_on_the_fly_zeros`。
- **B3** 缺必需文件、形状与状态错误失败：`tests/integration/test_train_dataset_read.py::test_missing_required_file_reports_full_path`；`tests/integration/test_dataset_recipe.py::test_reader_checks_manifest_shape_and_state`。
- **C1** 正反变换、梯度、容差、参数维度及法向保持：`tests/integration/test_train_normalize_sample.py::test_transform_roundtrip_and_gradient`；`tests/integration/test_train_normalize_sample.py::test_coordinate_tolerance_disable_and_gradient`；`tests/integration/test_train_normalize_sample.py::test_invalid_statistics_rejected`；`tests/integration/test_normalized_dataset.py::test_memory_record_and_three_probe_spaces`。
- **C2** 实际配置参数经准备入口生效：`tests/integration/test_train_recipe.py::test_prepare_uses_one_session_and_dry_run`；`tests/integration/test_train_normalize_sample.py::test_sampling_alignment_independence_and_target_copy`。
- **C3** 几何全选保序、无放回、候选不足拒绝：`tests/integration/test_train_normalize_sample.py::test_sampling_alignment_independence_and_target_copy`；`tests/integration/test_train_normalize_sample.py::test_uniform_sampling_has_no_replacement`。
- **C4** 同域联动与独立目标复制：`tests/integration/test_train_normalize_sample.py::test_sampling_alignment_independence_and_target_copy`。
- **C5** 轮次变化、验证固定、操作独立及三份探测：`tests/integration/test_train_normalize_sample.py::test_sampling_alignment_independence_and_target_copy`；`tests/integration/test_normalized_dataset.py::test_memory_record_and_three_probe_spaces`。
- **D1** 实际参数与来源记录，防外部篡改：`tests/integration/test_normalized_dataset.py::test_memory_record_and_three_probe_spaces`。
- **D2** 内存记录与全分辨率物化各自产物：`tests/integration/test_normalized_dataset.py::test_memory_record_and_three_probe_spaces`；`tests/integration/test_train_recipe.py::test_materialized_roundtrip_and_frozen_record`。
- **D3** 统计文件移走后读回、逆变换、不重复执行和冲突：`tests/integration/test_normalized_dataset.py::test_frozen_read_without_statistics_and_config_conflicts`；`tests/integration/test_train_recipe.py::test_materialized_roundtrip_and_frozen_record`。
- **D4** 部分失败不发布，新版本失败保留旧有效数据：`tests/integration/test_train_recipe.py::test_materialization_failure_does_not_publish`；`tests/integration/test_normalized_dataset.py::test_failed_new_version_preserves_old_asset`。
- **E1** 已安装贡献正式模型、资源、依赖和源码标识：`tests/contract/test_model_components.py::test_installed_component_resources_and_real_model`。
- **E2** 三个提炼组件输出、输入及参数梯度、状态键等价：`tests/integration/test_abupt_components.py::test_component_output_gradient_and_keys`。
- **E3** 正式前向与动态点数，非法批次/布局前置拒绝：`tests/integration/test_train_abupt_real.py::test_real_network_fit`；`tests/integration/test_train_batch_model.py::test_real_component_rejects_bad_inputs_before_forward`。
- **E4** 初始权重、冻结、两项加权监督及广播拒绝：`tests/integration/test_train_loop.py::test_initial_weights_freezing_and_two_weighted_losses`；`tests/integration/test_train_loop.py::test_loss_rejects_broadcast_and_weights`。
- **F1** 不等几何点数偏移、目标隔离与密集布局错误：`tests/integration/test_train_batch_model.py::test_sparse_offsets_and_dense_failure`；`tests/integration/test_train_batch_model.py::test_contribution_batch_keeps_targets_outside_inputs`。
- **F2** 真实参数更新、设备门禁、缩放与裁剪顺序：`tests/integration/test_train_abupt_real.py::test_real_network_fit`；`tests/integration/test_train_loop.py::test_device_and_clip_validation`；`tests/integration/test_train_loop.py::test_precision_update_order_and_overflow_counters`。
- **F3** 有效更新与溢出跳步计数、EMA：`tests/integration/test_train_loop.py::test_precision_update_order_and_overflow_counters`；`tests/integration/test_train_loop.py::test_epoch_resume_and_updates`。
- **F4** 自定义步骤调用次数、实际日志、读失败传播：`tests/integration/test_train_loop.py::test_epoch_resume_and_updates`；`tests/integration/test_recipe_logging.py::test_recipe_phases_and_console_summaries`；`tests/integration/test_train_loop.py::test_log_frequency_preserves_history_and_final_event`；`tests/integration/test_train_recipe.py::test_real_recipe_read_failure_is_run_failure`。
- **G1** 逐样本损失和六项物理指标、零范数计数：`tests/integration/test_model_evaluation.py::test_evaluation_is_per_sample_and_shared_with_post`；`tests/integration/test_model_evaluation.py::test_metrics_zero_target`。
- **G2** 训练/独立评估同口径，一次前向及成功/失败恢复：`tests/integration/test_model_evaluation.py::test_evaluation_is_per_sample_and_shared_with_post`；`tests/integration/test_model_evaluation.py::test_evaluation_restores_state_on_failure`。
- **G3** 严格 best/latest/last 和写失败旧文件保护：`tests/integration/test_train_checkpoint.py::test_best_requires_strict_improvement`；`tests/integration/test_train_loop.py::test_checkpoint_failure_preserves_old`；`tests/integration/test_train_loop.py::test_training_bridge_preserves_effective_config`。
- **G4** 正式网络和脚本轮次恢复、状态冻结及语义冲突：`tests/integration/test_train_abupt_real.py::test_real_network_epoch_resume`；`tests/integration/test_train_recipe.py::test_real_recipe_fit_and_epoch_resume`；`tests/integration/test_train_checkpoint.py::test_snapshot_is_frozen_and_restores_rng`；`tests/integration/test_train_checkpoint.py::test_semantic_conflict_rejected_before_model_load`；`tests/integration/test_train_checkpoint.py::test_ema_present_without_object_rejected`。
- **H1** 表面/体网格拓扑、point/cell 场与原 ID 重读：`tests/integration/test_rawprep_dataset.py::test_vtkhdf_topology_point_cell_and_original_identity`。
- **H2** PT 筛选结果按实体映射关联 VTKHDF：`tests/integration/test_rawprep_dataset.py::test_recipe_vtkhdf_mapping`。
- **H3** 非法身份、类型及写出失败，旧资产恢复：`tests/integration/test_rawprep_dataset.py::test_vtkhdf_rejects_invalid_identity`；`tests/integration/test_rawprep_dataset.py::test_auxiliary_failure_preserves_old_tensors`；`tests/integration/test_rawprep_dataset.py::test_vtk_writer_failure_does_not_publish_asset`。
- **I1** 五类职责、来源与依赖、文档和逐项索引一致：`tests/contract/test_model_components.py::test_acceptance_document_covers_all_plan_leaves`；`tests/contract/test_model_components.py::test_core_spec_dependency_direction_and_no_old_paths`。
- **I2** 复制案例准备、正式训练经现有启动：`tests/integration/test_train_recipe.py::test_prepare_uses_one_session_and_dry_run`；`tests/integration/test_train_recipe.py::test_real_recipe_fit_and_epoch_resume`。
- **I3** 直接脚本、pipeline、probe/dry-run 单会话与无更新：`tests/integration/test_train_recipe.py::test_real_recipe_fit_and_epoch_resume`；`tests/integration/test_train_recipe.py::test_script_probe_and_fit_check_have_no_training_artifacts`。
- **I4** 正式骨干小配置拟合与恢复，不用替身替代：`tests/integration/test_train_abupt_real.py::test_real_network_fit`；`tests/integration/test_train_abupt_real.py::test_real_network_epoch_resume`；`tests/integration/test_train_recipe.py::test_real_recipe_fit_and_epoch_resume`。

## 结果边界

- 正式 AB-UPT 测试使用贡献包实际网络：宽度 24、几何深度 1、三头、psc 交互、每域一层。单样本固定输入最多 1000 次更新，损失低于初始值 10%；恢复比较 rtol=1e-5、atol=1e-6。未运行默认宽度 192 的生产规模长训，不声明复现 Noether 训练轨迹。
- 前馈、连续正余弦编码、旋转频率与锁定来源比较输出、输入梯度、参数梯度和状态键。参考仓库只读，正式网络运行不依赖其路径。
- 训练、评估、恢复默认自动选择设备（CUDA、MPS，否则警告后回退 CPU）。混合精度用可控缩放器验证解除缩放/裁剪/更新顺序，以及跳步时计数和 EMA 不推进；这不是 CUDA 硬件验收。显式设备不可用时拒绝的路径已测。
- VTKHDF 验证表面和体网格拓扑、point/cell 身份、筛选回贴、PT 关联及写出失败；无需把它设为 PT 训练前置。
- 计划中的 iteration 仍聚合在 training/loop.py；诊断、调度与分流已拆为独立公开模块。旧只读 Stage 聚合在 trainprep/dataset.py；不保留九个占位。验收按行为而非文件数量。
- 完整 FieldSpec/Sample、全网格推理、云图和报告不属于五类闭环当次结果。Lion、调度、重复评估、梯度累积、源码快照与完整诊断由后续切片交付，见下方「训练闭环剩余对齐」。

## 训练闭环剩余对齐

日期：2026-09-08。范围是功能表第 32/35/59/61 项与对照缺口；不重做五类改名与 40–47 变换采样。

机制验收：

```bash
uv run pytest tests/integration/test_train_resolved_config.py tests/integration/test_train_test_repeat.py tests/integration/test_train_code_snapshot.py tests/integration/test_train_interrupt.py tests/integration/test_train_diagnostics.py tests/integration/test_train_optim_align.py tests/integration/test_train_entry_init.py tests/integration/test_train_shapenet_contract.py tests/integration/test_train_reference_stats.py
```

正式验收（必须；跳过视为本切片未完成）：

```bash
uv run pytest tests/integration/test_train_formal_two_epoch.py
```

2026-09-08 本机执行：官方 789/100 物理清单由已落盘张量现场生成；正式配置两轮约 323.5 秒完成，产物含 `resolved.yaml`、`code.tar.gz`、best/latest/last，轮次 2 的 last 无 EMA。机制九项与 recipe/正式网络相关用例同日通过。

- **第 32 项** 最终生效配置与联合校验：`tests/integration/test_train_resolved_config.py`。
- **第 32 项** test_repeat 1000 次且独立采样：`tests/integration/test_train_test_repeat.py`。
- **第 35 项** 当次源码快照：`tests/integration/test_train_code_snapshot.py`。
- **第 59 项** 信号与回调异常可恢复收尾：`tests/integration/test_train_interrupt.py`。
- **第 61 项** 规模、参数量、峰值内存与条件 ETA：`tests/integration/test_train_diagnostics.py`。
- **对照** 可换优化器、公开调度、累积、十轮 EMA、缺键警告：`tests/integration/test_train_optim_align.py`。
- **F1** 整链入口与设备映射：`tests/integration/test_train_entry_init.py`。
- **F2** ShapeNet 字段契约：`tests/integration/test_train_shapenet_contract.py`。
- **F3** 参考统计量数值对照：`tests/integration/test_train_reference_stats.py`。
- **F4** 正式两轮全量：`tests/integration/test_train_formal_two_epoch.py`。

contrib 网络与 Noether 领域封装接口对齐、权重与检查点不等价。

## 文档同步

AGENTS、根 README、架构和 ADR、算法规则、模块索引、MVP 索引、core 的 abilities/applications/run PRD、contrib ability 和 spec components PRD、recipe PRD/README、包 README 与 tests 导航共同核对。旧占位章节整体替换，不以追加状态段保留矛盾正文。
