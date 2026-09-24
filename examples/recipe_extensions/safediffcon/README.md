# 控制研究扩展

复制SafeDiffCon模板和本目录`variants.py`到仓库外实验目录，按模板README设置模型、引导或派生组件路径。三种变体使用独立输出位置；数值和实际运行证据见SafeDiffCon 运行记录。

安全变体只改变采样时的安全梯度，并增加控制能量惩罚；校准、重加权与评价阈值保持基线语义，因此可直接比较结果。

## 物化说明

- `base_case`: `safediffcon.burgers`。该目录是 extension 参考覆盖集，不是独立流程。
- 物化时先复制完整基案例，再叠加清单声明的覆盖文件，并写出 `.dojo-provenance.json`；未声明冲突、缺少基案例或非空目标会失败。
- 物化目录随后可以由 Agent 自由修改、用 direct-core 运行或交给 `ai4e_task` Python API；扩展目录本身不会绑定本机数据或自动启动任务。

## Agent Help Center

本目录是 `参考变体`。Agent 先读取帮助主题 `case:recipe_extensions.safediffcon`，再按主题关联的 workflow 和 API 参考核对输入、函数签名、产物与证据边界。支持 Python 帮助 API 时可调用：

```python
import ai4e_task as task
print(task.read_help_topic("case:recipe_extensions.safediffcon")["content"])
```

<!-- research-adaptation-details -->
## 选择与改写说明

控制网络、安全目标和安全裕量计算替换；先物化完整基案例，再按扩展说明修改。

数据形态：field_sequence, control_trajectory；训练机制：iteration, diffusion_control。

### 具体修改位置

- 基案例：`safediffcon.burgers`。先 `copy_example` 物化；返回的 `documentation.entry` 可定位基案例和扩展的说明副本。
- 本变体可改：`network`、`objective`、`diagnostics`。
- 覆盖/新增文件：`variants.py`。逐项读这些文件的输入输出和基案例消费者，其他阶段继续继承。
- 物化后检查根配置；若扩展没有覆盖配置，按本页前文将本地组件显式接入，复制文件本身不等于采用了组件。

### 运行与读回

- 运行前填写自己的输入与输出目录；先按本页原有命令/阶段说明执行短程连接验证。更改模型或科学定义时不得沿用不兼容检查点。
- 核对真实运行报告、检查点和固定预测；存在派生结果时必须从后处理读回。恢复与独立推理分别验证，不以导入成功替代。

### 适用边界

- 覆盖文件集不能直接当完整案例运行；未声明的行为沿用基案例。
- 仅声明扩展演示范围，不据此扩大数值精度验收。
