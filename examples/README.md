# 可复制示例

五个独立训练案例共享唯一 aero_cfd recipe，物理数据复用，训练准备和检查点独立：

- [汽车 AB-UPT 联合域](aero_cfd/shapenet_car_abupt/README.md)
- [NASA CRM Transolver-3 表面](aero_cfd/nasa_crm_transolver3/README.md)
- [NASA CRM AB-UPT 表面](aero_cfd/nasa_crm_abupt/README.md)
- [汽车 Transolver-3 表面](aero_cfd/shapenet_car_transolver3_surface/README.md)
- [汽车 Transolver-3 体积](aero_cfd/shapenet_car_transolver3_volume/README.md)

配置数据根和运行根后运行。当前交叉实验范围见[验收记录](../.context/mvp/cross-model-acceptance.md)；原 NASA 两轮严格参考对标见[原验收记录](../.context/mvp/transolver3-acceptance.md)，两者目的不同。

源码更新后需重新安装 workspace 包再运行复制目录；实际验收使用重新构建的已安装 wheel，不依赖源码路径注入。

服务器执行五案例与50轮报告交付，见 [服务器操作手册](../docs/aero-cfd-server-runbook.md)。
