# Recipe 三阶段与锁定 Noether 的数值验收

本文件保留 2026-09-08 三阶段验收的历史范围；当前默认流程已包含 post，后处理修复与独立复跑见 [2026-09-09 端到端验收](abupt-end-to-end-acceptance.md)。

本记录对应 2026-09-08 的三阶段实现，替代“只有小网络可以训练”的判断；旧验收记录保留其历史范围。正式训练入口默认执行拟合，多域、条件、多样本和缓存仍保留。

## 参考与环境

- 参考仓库：`/Users/zonghui/work/new_code_project/noether`，HEAD 为 `313e6c5c2ff31f283a3e5935b4d85888aac6b025`。
- **参考是锁定的本地源码，不是干净的上游 checkout。** `ShapeNetCarPreset.excluded_properties` 已有一个本地修正：排除 ShapeNet 不提供的 `surface_area`，与官方 `train_shapenet.yaml` 一致。本次未修改 Noether。各源码文件 SHA256、依赖与平台记录在 `/tmp/dojo-three-stage-full/reference-environment.json`；源码树摘要 `94e7b11f354d0a814815a9c5a69a023178ec28caab7ee4aa9466d71f7179e7ae`。
- 双方共用 Python 3.12.14、Torch 2.14.0、NumPy 2.5.3、scikit-learn 1.9.0、VTK 9.7.0、PyG 2.6.1、torch-cluster 1.6.3；CPU FP32、1 线程、0 DataLoader workers、seed=42。
- 原始数据：`/Users/zonghui/work/datasets/shapenet_car_cfd/mlcfd_data/training_data`。官方资产：`/Users/zonghui/work/datasets/shapenet_car_cfd/preprocessed`。
- 正式规模：官方 train=789、test=100；dim=192、geometry_depth=6、物理块 `pscscscscsc`、每域 decoder=12、batch=1、2 epochs、1578 次更新，18.6M 参数。没有缩网或替身模型。

## 已完成证据

1. **datapre 全量数据对照**：实际调用官方 `load_simulation_data` 并运行 Dojo recipe，889 样本的 7 个字段对照通过；除 volume_normals 最大绝对误差 `5.960464477539063e-08` 外，其他字段为 0。报告 `/tmp/dojo-three-stage-full/datapre.json`，Dojo 数据清单 `/tmp/dojo-three-stage-full/data/manifest.json`。
2. **trainprep 全量输入对照**：使用实际 `MeanStdNormalization`/`PositionNormalizer` 与 `AeroMultistagePipeline`；889 样本的自然采样索引、坐标、目标和随机流推进精确一致。报告 `/tmp/dojo-three-stage-full/trainprep-v2.json`。此前 `trainprep.json` 使用旧 sample processor，不作为最终归一化证据。
3. **完整官方重复运行**：`reference-a` 与 `reference-b` 两次正式训练最终权重完全相同。在 Dojo 完整比较之前冻结 CPU FP32 `rtol=1e-5、atol=1e-6`，未按 Dojo 偏差放宽。报告 `/tmp/dojo-three-stage-full/tolerance.json`。
4. **完整训练对照**：`/tmp/dojo-three-stage-full/full-training-v4.json` 通过；全部最终参数与缓冲区最大绝对误差 **0**；两轮训练损失、测试分项及物理 MSE/MAE/相对 L2 共 20 个指标均通过冻结容差。正式检查点 `/tmp/dojo-three-stage-full/dojo-v4/2026-09-08T23-25-34_6f2600/checkpoints/last.pt`。
5. **逐更新定位**：实际官方训练器前 5 次更新与正式网络逐张量精确一致；正式网络真实数据 20 次 Lion 更新精确一致，报告 [full-updates.json](abupt-reference-results/full-updates.json)，对照工具为 `tools/verification/compare_full_updates.py`。小网络工具 `compare_abupt.py` 仅作为快速诊断，不能替代本条和完整训练。

6. **安装后的复制流水线**：普通 recipe 复制到 `/tmp/dojo-three-stage-full/copied-recipe`，无源码 PYTHONPATH、无 Noether 运行依赖，只修改路径和公开设备配置，完成 889 样本 datapre、trainprep 以及正式两轮 train；最终权重差异为 0，20 个指标全部通过。报告 [copied-pipeline.json](abupt-reference-results/copied-pipeline.json)，运行目录 `/tmp/dojo-three-stage-full/copied-runs/2026-09-08T23-31-56_36a721`。
7. **真实中断恢复**：独立 trainprep 发布引用，独立 train 在第 100 次更新后收到 SIGTERM，返回失败并保存轮次起始状态；同配置恢复后完整训练。模型、优化器、EMA、调度、Python/NumPy/Torch 随机状态及训练进度与连续训练精确一致，且通过官方最终权重和指标对照。报告 [recovery.json](abupt-reference-results/recovery.json)、[resumed-training.json](abupt-reference-results/resumed-training.json)。

最终小型证据已持久化到本仓库 `abupt-reference-results/`；其中 `datapre.json`、`trainprep.json`、`tolerance.json`、`full-training.json`、`reference-environment.json` 分别对应上述阶段和基准，不只依赖临时目录报告。

## 使用命令与产物

先安装：

```bash
uv sync --locked --all-packages --all-extras
```

复制 `recipes/aero_cfd` 整个目录，修改旁边 `config.yaml` 的 `dataset.root`、`data_root`、`run_root`；参考对照明确设 `train.device=cpu`。从已安装 Dojo 的环境运行：

```bash
uv run --no-sync python /path/to/recipe/datapre.py
uv run --no-sync python /path/to/recipe/trainprep.py
uv run --no-sync python /path/to/recipe/train.py --set train.preparation=/path/to/prep-run/artifacts/preparation.json
uv run --no-sync python /path/to/recipe/pipeline.py
```

- datapre：`${data_root}/manifest.json`、train/test 张量和统计来源。默认 reference 统计来自锁定参考参数，manifest 记录来源；选择 fit 时写出本次完整 train 的统计文件。
- trainprep：本次 `${run_root}/<run>/artifacts/preparation.json`，归一化记录在独立 normalize 数据路径；冻结数据内容、外部条件文件、组件源码、采样及拼批声明。训练期继续按迭代采样，不固化某一批。
- train：`artifacts/training.json`、`checkpoints/{latest,best,last}.pt`、`inputs/config.yaml`、`code.tar.gz`、运行日志。普通检查点包含 EMA 恢复状态，周期 EMA 权重单独发布到 `ema_latest.pt`。
- 续训：保持公开准备与训练配置，设置 `train.resume=/path/to/latest.pt`。预热余弦必须保持最初计划总轮数；恒定调度可增加总轮数。中断保存当前轮次开始状态，恢复重放该轮，防止重复更新已消费样本。
- 已有数据可配置 `pipeline.stages=[trainprep,train]`；已有准备引用可只运行 train。dry-run 不发布虚假的下游成功产物。

正式运行不需要 Noether。验收工具通过 `reference_env.py` 固定当前 Dojo 的数值依赖，再加载指定 Noether 源码；默认从该仓库 `.venv/lib/python3.12/site-packages` 补齐纯 Python 依赖，也可用 `--reference-site` 指定。下面四个参考工具均采用该入口；固定 `OMP_NUM_THREADS=1`、`VECLIB_MAXIMUM_THREADS=1`：

```bash
uv run --no-sync python tools/verification/reference_env.py --noether /path/to/noether compare_datapre.py --help
uv run --no-sync python tools/verification/reference_env.py --noether /path/to/noether compare_trainprep.py --config /path/to/config.yaml --output /path/to/trainprep-report.json
uv run --no-sync python tools/verification/reference_env.py --noether /path/to/noether compare_full_updates.py --config /path/to/config.yaml --output /path/to/update-report.json
uv run --no-sync python tools/verification/reference_env.py --noether /path/to/noether run_noether_reference.py --dataset /path/to/preprocessed --output /path/to/reference-runs --run-id reference-a
uv run --no-sync python tools/verification/compare_training.py freeze --reference /path/to/reference-a/checkpoints/ab_upt_cp=last_model.th --checkpoint /path/to/reference-b/checkpoints/ab_upt_cp=last_model.th --output /path/to/tolerance.json
uv run --no-sync python tools/verification/compare_training.py compare --reference /path/to/reference-a/checkpoints/ab_upt_cp=last_model.th --checkpoint /path/to/dojo/checkpoints/last.pt --tolerance /path/to/tolerance.json --output /path/to/full-report.json
```

## 版本迁移与已知边界

- 模型结构版本 3：RMSNorm、绝对位置编码器、联合投影、初始化与参数注册顺序。结构 2 权重不能直接续训。checkpoint 容器版本仍是 2，与模型版本不同。
- 准备引用版本 2：含组件源码与条件文件内容摘要。旧准备引用须重新 trainprep。
- 新归一化记录版本 2 采用官方实际 shift/scale 运算顺序，正反变换共用同一系数。旧版本 1 保留除法路径，不静默重解释旧归一化资产；官方复现使用新版本 2。
- 完整数值一致性仅指上述锁定 ShapeNet-Car 默认配置与环境。用户更换统计方式、特征、条件、监督方法、采样、网络规模或训练配置后，需为新实验重新对照；多域扩展的功能回归不等于所有配置的官方同轨迹证明。
- CUDA、AMP 和真实 MPS 硬件未在本机验收，不宣称硬件等价性。MPS 邻域检索与复数 RoPE 显式经 CPU 回退，保留梯度；设备功能验收与本次 CPU 完整训练结果分开记录。
- `test_repeat` 默认关闭，次数配置保留；开启后改变采样轨迹和评估开销，需使用对应官方回调配置重新比较。
- full mesh post、云图与报告不属于本次三阶段数值一致性门槛；保留现有 post 实现及固定锚点默认行为，`post.random_stream=independent` 与训练采样流分开配置。

## 最终相关回归

未以全仓测试替代验收。以下均使用 `uv run --no-sync pytest`；正式包已重新构建安装，训练入口组不设置源码 PYTHONPATH。

- 训练、引用交接、源码快照、恢复、调度、诊断、多域和缓存：55 passed。路径为 `test_reference_arithmetic.py`、`test_recipe_three_stage.py`、`test_train_recipe.py`、`test_train_optim_align.py`、`test_abupt_multidomain.py`、`test_abupt_inference_cache.py`、`test_train_boundary_alignment.py`、`test_train_resolved_config.py`、`test_train_code_snapshot.py`、`test_train_interrupt.py`、`test_train_diagnostics.py`、`test_train_entry_init.py`、`test_train_shapenet_contract.py`、`test_train_reference_stats.py`，均在 `tests/integration/`。
- 归一化、评估、物化和已有数据资产：`tests/integration/test_model_evaluation.py tests/integration/test_train_normalize_sample.py tests/integration/test_normalized_dataset.py tests/integration/test_pre_materialize.py`，59 passed。
- 保留原 post 固定锚点与网格行为：`tests/integration/test_post_inference.py tests/integration/test_post_mesh.py`，17 passed。
- 受影响 Python 文件的 Ruff 检查与格式检查通过；未以此替代数值对照。未运行全仓 mypy/Sphinx 门禁，不将它们记为通过。

计数和日志位置见 [test-summary.json](abupt-reference-results/test-summary.json)。
