# GeoTransolver — shapenet_car

普通 PyTorch GALE 的外流基础案例，4 层/128 宽/4 头/64 切片，无局部邻域编码；非论文精度复现。

将 inputs.trainprep.dataset 指向已有物理 manifest；或配置 rawprep 输入并在 pipeline.stages 前加入 rawprep。物理输入必须有逐场 PT、VTKHDF 和实体身份。run_root 与 data_root 指向研究目录，原始数据只读。

通过 `uv run --no-sync python pipeline.py --config config.yaml` 运行；独立阶段使用对应脚本。训练恢复设置 inputs.train.resume；独立 infer 设置 inputs.infer.preparation/checkpoint；post 只需 inputs.post.results。

默认完整分片；本机验收的 2 train/1 test 由外部配置固定。训练每域最多8192查询点，几何最多8192点，推理分块8192、种子42，全点回贴但不等价于全场一次前向。分块与几何预算属于实验设置。

修改 model.supervision 或在 train.py 注入损失；几何/查询配置位于 model.sampling。网络条件与输出顺序由 model.data_specs、trainprep 明确绑定。逐样本物理指标和固定网格由 infer 交付；post 只读结果生成报告和图片。

包入口 ai4e_contrib.application.aero_cfd.geotransolver。Python/Task 可运行，不表示平台模型页登记。
