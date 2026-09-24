# GeoTransolver 外流研究扩展

以 aero_cfd.shapenet_car_geotransolver 为基础物化；替换 train.py、infer.py、post.py 并加入 variants.py。

训练使用 L1 替代 MSE；推理保存逐节点绝对压力误差，继承原 ID、未知单位保持 null；独立后处理读回该数组并复算核验及出图。用户可编辑网络参数、损失或新增步骤，无需修改框架。

<!-- research-adaptation-details -->
## 选择与改写说明

外流L1目标与固定绝对误差场读回；先物化完整基案例，再按扩展说明修改。

数据形态：mesh, point_fields；训练机制：epoch。

### 具体修改位置

- 基案例：`aero_cfd.shapenet_car_geotransolver`。先 `copy_example` 物化；返回的 `documentation.entry` 可定位基案例和扩展的说明副本。
- 本变体可改：`objective`、`inference_fields`、`post`。
- 覆盖/新增文件：`train.py`、`infer.py`、`post.py`、`variants.py`。逐项读这些文件的输入输出和基案例消费者，其他阶段继续继承。
- 物化后检查根配置；若扩展没有覆盖配置，按本页前文将本地组件显式接入，复制文件本身不等于采用了组件。

### 运行与读回

- 运行前填写自己的输入与输出目录；先按本页原有命令/阶段说明执行短程连接验证。更改模型或科学定义时不得沿用不兼容检查点。
- 核对真实运行报告、检查点和固定预测；存在派生结果时必须从后处理读回。恢复与独立推理分别验证，不以导入成功替代。

### 适用边界

- 覆盖文件集不能直接当完整案例运行；未声明的行为沿用基案例。
- 仅声明扩展演示范围，不据此扩大数值精度验收。
