# ai4e-contrib

可安装的共享能力。当前提供 application/datasets/shapenet_car 的 manifest、官方分片、参考统计和按需 adapter。使用 `from ai4e_contrib.application.datasets import shapenet_car`，调用 open_dataset 后不立即读取网格。用户可复制数据集目录并修改 manifest/adapter；仅依赖 core/spec 公开接口。平台上传不在本切片。

WDNO Burgers 基础预测已提供可安装的小波变换、二维去噪网络、条件损失与采样，以及`application/spatiotemporal_pde/wdno`连接。依赖选择`ai4e-contrib[wdno]`；实际可复制入口和本机隔离环境见[WDNO recipe](../../recipes/wdno/README.md)，函数替换示例见[WDNO变体](../../examples/recipe_extensions/wdno/README.md)。当前为原三小时账本内的基础预测缩小迁移，完整论文、超分、控制与Smoke另行验收，不开放平台目录。
