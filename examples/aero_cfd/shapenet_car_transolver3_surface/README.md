# shapenet_car_transolver3_surface

一个独立模型实例，使用唯一 aero_cfd recipe 的共享阶段入口。复制本目录，修改数据与运行路径后运行。

- 已有物理 PT：配置 `train.manifest` 后执行 `uv run python pipeline.py`。
- 独立训练消费 `train.preparation`；独立后处理指定 `post.checkpoint`，沿用对应准备。
- 一轮完整训练，最后检查点；固定五个测试样本全点评价。前三个样本用于跨运行图表。
- NASA 只有表面场。汽车 Transolver 表面与体积各使用独立 example，复用同一物理数据。

本期交叉实跑已交付；结果与验收边界见仓库 `.context/mvp/cross-model-acceptance.md`。
