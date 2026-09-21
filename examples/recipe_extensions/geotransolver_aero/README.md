# GeoTransolver 外流研究扩展

以 aero_cfd.shapenet_car_geotransolver 为基础物化；替换 train.py、infer.py、post.py 并加入 variants.py。

训练使用 L1 替代 MSE；推理保存逐节点绝对压力误差，继承原 ID、未知单位保持 null；独立后处理读回该数组并复算核验及出图。用户可编辑网络参数、损失或新增步骤，无需修改框架。
