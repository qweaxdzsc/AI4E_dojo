# ai4e-contrib

可安装的共享能力。当前提供 application/datasets/shapenet_car 的 manifest、官方分片、参考统计和按需 adapter。使用 `from ai4e_contrib.application.datasets import shapenet_car`，调用 open_dataset 后不立即读取网格。用户可复制数据集目录并修改 manifest/adapter；仅依赖 core/spec 公开接口。平台上传不在本切片。
