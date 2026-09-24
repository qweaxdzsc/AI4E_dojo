# PCNO 圆柱真实扩展

物化 `pcno.double_cylinder` 基础案例后覆盖本目录文件。
把 `components.network` 改为 `local_components.shifted_network`，以新实验训练，验证构造器实际生效。
在推理与后处理之间，流程调用本地speed函数保存速度模长；post读回该数组并产生derived_speed统计。
已有结果也可单独绑定inputs.post.results，只运行post，核验不调用网络。

<!-- research-adaptation-details -->
## 选择与改写说明

网络替换与速度模长数组读回；先物化完整基案例，再按扩展说明修改。

数据形态：regular_grid, field_sequence；训练机制：iteration。

### 具体修改位置

- 基案例：`pcno.double_cylinder`。先 `copy_example` 物化；返回的 `documentation.entry` 可定位基案例和扩展的说明副本。
- 本变体可改：`network`、`post`。
- 覆盖/新增文件：`pipeline.py`、`local_components.py`。逐项读这些文件的输入输出和基案例消费者，其他阶段继续继承。
- 物化后检查根配置；若扩展没有覆盖配置，按本页前文将本地组件显式接入，复制文件本身不等于采用了组件。

### 运行与读回

- 运行前填写自己的输入与输出目录；先按本页原有命令/阶段说明执行短程连接验证。更改模型或科学定义时不得沿用不兼容检查点。
- 核对真实运行报告、检查点和固定预测；存在派生结果时必须从后处理读回。恢复与独立推理分别验证，不以导入成功替代。

### 适用边界

- 覆盖文件集不能直接当完整案例运行；未声明的行为沿用基案例。
- 仅声明扩展演示范围，不据此扩大数值精度验收。
