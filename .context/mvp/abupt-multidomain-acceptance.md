# AB-UPT 多域输入与推理缓存验收

日期：2026-09-08。状态：A1–F3 相关门禁全部通过。

参考 Noether：313e6c5c2ff31f283a3e5935b4d85888aac6b025。夹具来自实际归一化处理器和原样包装 forward，在骨干边界捕获输入；不使用手写参考数据替代，不比较 Noether 网络预测。正式包不导入 Noether。

范围：CPU/FP32 的合法小网络；B=2/B=3 不同几何点数、不同域点数，输出和梯度容差 rtol=1e-5/atol=1e-6。输入夹具浮点 rtol=1e-6/atol=1e-6，索引精确相等。默认规模只构造，不做生产规模训练；local_data 两项不属于本轮门禁。CUDA/设备迁移无硬件实测，不声称 GPU 性能或精度复现。

## 功能节点

- **A1**：`tests/integration/test_abupt_domains.py::test_order_changes_signature_and_output_slices`。
- **A2**：`tests/integration/test_abupt_domains.py::test_default_scale_constructs_only`。
- **A3**：`tests/integration/test_abupt_domains.py::test_invalid_input_rejected`。
- **B1**：`tests/integration/test_abupt_input_alignment.py::test_reference_values_and_field_binding`。
- **B2**：`tests/integration/test_abupt_input_alignment.py::test_fixed_indices_and_target_identity`。
- **B3**：`tests/integration/test_abupt_input_alignment.py::test_query_subsets_and_condition_files`。
- **B4**：`tests/integration/test_train_batch_model.py::test_contribution_batch_keeps_targets_outside_inputs`。
- **C1**：`tests/integration/test_abupt_multidomain.py::test_real_domains_forward_backward`。
- **C2**：`tests/integration/test_abupt_multidomain.py::test_features_and_geometry_conditions`。
- **C3**：`tests/integration/test_abupt_multidomain.py::test_real_batch_matches_individual_outputs_and_gradients`。
- **D1**：`tests/integration/test_abupt_inference_cache.py::test_full_geometry_cache_and_chunks`。
- **D2**：`tests/integration/test_abupt_inference_cache.py::test_cache_skips_all_kv_projections_and_reports_cost`。
- **D3**：`tests/integration/test_abupt_inference_cache.py::test_invalid_cache_rejected`。
- **D4**：`tests/integration/test_abupt_recipe.py::test_real_recipe_cached_query`。
- **E1**：`tests/integration/test_abupt_training_contract.py::test_query_supervision_and_declared_evaluation`。
- **E2**：`tests/integration/test_abupt_training_contract.py::test_relative_loss_is_mean_of_samples`。
- **E3**：`tests/integration/test_abupt_recipe.py::test_batch_two_recipe_resume`。
- **F1**：`tests/integration/test_abupt_input_alignment.py::test_reference_values_and_field_binding`。
- **F2**：`tests/integration/test_abupt_recipe.py::test_new_recipe_defaults`。
- **F3**：`tests/integration/test_train_abupt_real.py::test_real_network_fit`。

E3 另由 test_layout_conflict_rejected_before_restore 覆盖域顺序/特征/条件冲突和旧格式拒绝。C2 另验条件初始恒等及调制启用后的输入梯度。D3 另验 train→eval 后仍失效、额外查询特征拒绝、上下文释放。F3 真实固定采样单样本最多 1000 更新，损失须降至初值 10% 以下。

## 复验命令

```sh
uv sync --locked --all-packages --all-extras --reinstall-package ai4e-core --reinstall-package ai4e-contrib --reinstall-package ai4e-spec
OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 UV_CACHE_DIR=/tmp/dojo-uv-cache uv run --no-sync pytest tests/integration/test_abupt*.py tests/integration/test_train*.py tests/integration/test_normalized_dataset.py tests/integration/test_model_evaluation.py tests/integration/test_constraint_losses.py tests/integration/test_dataset_recipe.py tests/integration/test_rawprep_dataset.py tests/contract/test_model_components.py -m 'not local_data' -q -o junit_family=xunit1 --junitxml=/tmp/dojo-multidomain-acceptance.xml
```

最终相关回归：179 passed、2 deselected，27.67 秒。排除的两项是本机官方数据约束及生产规模两轮训练（local_data），未作为本轮通过项。唯一警告来自第三方 torch.jit.script 弃用提示。

缓存观测（单次 CPU 小模型，仅作记录）：{"uncached_seconds": "0.0009495420381426811", "cached_query_seconds": "0.0020565829472616315", "cache_tensor_bytes": "5312"}。时间受运行环境影响，不用于推断生产性能。缓存性能只记录测量值，不设倍数门槛。依赖重新按锁定 workspace 安装；未使用替身替代正式网络。
