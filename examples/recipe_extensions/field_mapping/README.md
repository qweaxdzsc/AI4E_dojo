# 新增速度模长

复制本目录并安装 Dojo。先配置原始数据根、数据输出和运行目录，再用 `uv run python pipeline.py` 执行。

`custom_abilities.py` 只处理数组；`rawprep.py` 在提取之后登记速度模长。`rawprep.speed` 声明输入和输出，`save_fields` 保存新字段，统计使用本次训练分片，归一化与模型体积输入通过 `volume_speed` 衔接。未知速度单位保持未知，不猜为 m/s。

修改能力后重新执行原始处理与准备；独立训练使用 `train.preparation`。删除计算步骤时也要删除对新字段的消费，否则明确失败。

本例开启 require_features：推理输入必须含速度模长。默认交付已保存实体上的锚点预测，query=false；任意完整网格查询需要另外提供对应点的速度模长，不能把缺失特征静默当成零。此例用于验证能力交接，不作为未知速度预测的精度基线。

## 物化说明

- `base_case`: `aero_cfd.shapenet_car_abupt`。该目录是 extension 参考覆盖集，不是独立流程。
- 物化时先复制完整基案例，再叠加清单声明的覆盖文件，并写出 `.dojo-provenance.json`；未声明冲突、缺少基案例或非空目标会失败。
- 物化目录随后可以由 Agent 自由修改、用 direct-core 运行或交给 `ai4e_task` Python API；扩展目录本身不会绑定本机数据或自动启动任务。

## Agent Help Center

本目录是 `参考变体`。Agent 先读取帮助主题 `case:recipe_extensions.field_mapping`，再按主题关联的 workflow 和 API 参考核对输入、函数签名、产物与证据边界。支持 Python 帮助 API 时可调用：

```python
import ai4e_task as task
print(task.read_help_topic("case:recipe_extensions.field_mapping")["content"])
```

<!-- research-adaptation-details -->
## 选择与改写说明

物理字段派生与保存、统计和归一化交接；先物化完整基案例，再按扩展说明修改。

数据形态：mesh, point_fields；训练机制：epoch。

### 具体修改位置

- 基案例：`aero_cfd.shapenet_car_abupt`。先 `copy_example` 物化；返回的 `documentation.entry` 可定位基案例和扩展的说明副本。
- 本变体可改：`field_transform`。
- 覆盖/新增文件：`custom_abilities.py`、`configuration.py`、`post.py`、`rawprep.py`、`config.yaml`、`pipeline.py`、`train.py`、`infer.py`、`trainprep.py`。逐项读这些文件的输入输出和基案例消费者，其他阶段继续继承。
- 物化后检查根配置；若扩展没有覆盖配置，按本页前文将本地组件显式接入，复制文件本身不等于采用了组件。

### 运行与读回

- 运行前填写自己的输入与输出目录；先按本页原有命令/阶段说明执行短程连接验证。更改模型或科学定义时不得沿用不兼容检查点。
- 核对真实运行报告、检查点和固定预测；存在派生结果时必须从后处理读回。恢复与独立推理分别验证，不以导入成功替代。

### 适用边界

- 覆盖文件集不能直接当完整案例运行；未声明的行为沿用基案例。
- 仅声明扩展演示范围，不据此扩大数值精度验收。
