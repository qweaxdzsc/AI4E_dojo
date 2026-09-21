# GeoTransolver bumper_beam

可复制的五阶段 Python 研究案例。设置 `inputs.rawprep.source`、`run_root` 和 `data_root` 后，以 `uv run --no-sync python pipeline.py --config config.yaml` 执行。原始数据只读，所有输出使用独立数据根。

保险杠124训练/7验证；共同11帧，预测10帧全部节点；6层基础256宽，多尺度后320宽。

默认20更新及120秒用于短检查，超过阶段预算会保存检查点并失败；恢复设置 `inputs.train.resume` 和累计目标 `train.updates`。调度沿原实验总轮次，短训不压缩日程。论文精度未复现。

独立 post 仅设置 `inputs.post.results` 并选择 `[post]`，无需原数据或网络；可在 `components.loss/derived/consume` 替换普通函数。安装依赖选择 `ai4e-contrib[geotransolver]`，运行不依赖 PhysicsNeMo。
