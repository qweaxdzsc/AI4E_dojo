<!-- dojo-help: {"case_ids": ["recipe_extensions.sampling"], "domain": "recipe_extensions", "kind": "case", "layer": "example", "summary": "几何点采样函数替换和身份交接；先物化完整基案例，再按扩展说明修改。", "tasks": ["mesh", "point_fields", "sampling"], "title": "recipe_extensions.sampling", "topic_id": "case:recipe_extensions.sampling"} -->
# `recipe_extensions.sampling`

- 类型：`extension`
- 用途：参考变体与 Agent 组件组装示例
- 资源路径：`examples/recipe_extensions/sampling`

几何点采样函数替换和身份交接；先物化完整基案例，再按扩展说明修改。

- 数据形态：mesh, point_fields
- 训练机制：epoch
- 替换入口：sampling
- 限制：覆盖文件集不能直接当完整案例运行；未声明的行为沿用基案例。
- 限制：仅声明扩展演示范围，不据此扩大数值精度验收。
- 基案例：`aero_cfd.shapenet_car_abupt`
- 覆盖文件：
  - `custom_abilities.py`
  - `configuration.py`
  - `post.py`
  - `rawprep.py`
  - `config.yaml`
  - `pipeline.py`
  - `train.py`
  - `infer.py`
  - `trainprep.py`

## 物化流程

`copy_example` 会先复制完整基案例，再叠加声明的覆盖文件并写 provenance。
物化后必须重新检查配置、输入和恢复兼容性；不能直接运行原 extension 目录。

## 案例详细说明

来源：案例 README；SHA256 `c437ebbbe5d66708d68934ee53131b4938f42c6ccd210262accbcab92aa1607b`。

### 替换训练采样

复制本目录并安装 Dojo，配置数据根及输出目录后用 `uv run python pipeline.py` 执行。

`model.sampling.target` 选择本地普通函数；函数改变几何点选择顺序，同时将剩余采样和元信息交给原模型准备能力。它在训练逐样本取数时执行，不在 YAML 加步骤顺序。训练准备记录函数源码和参数，独立训练按同一引用恢复。

也可在 `trainprep.py` 的 `configure_sampling` 中直接传入 `operation`；此时取消配置中的 target。由于 direct callable 不写入用户配置，任何可独立启动并继续使用它的阶段也必须在 Python 正文显式传入同一 callable，例如训练脚本把它作为 `open_training(..., prepare=...)` 的参数。准备记录只证明当次准备实际调用的组件，不把冻结源码反向注入当前训练配置。采样能力须保留批次结构、原实体 ID、种子和轮次参数。

#### 物化说明

- `base_case`: `aero_cfd.shapenet_car_abupt`。该目录是 extension 参考覆盖集，不是独立流程。
- 物化时先复制完整基案例，再叠加清单声明的覆盖文件，并写出 `.dojo-provenance.json`；未声明冲突、缺少基案例或非空目标会失败。
- 物化目录随后可以由 Agent 自由修改、用 direct-core 运行或交给 `ai4e_task` Python API；扩展目录本身不会绑定本机数据或自动启动任务。

#### Agent Help Center

本目录是 `参考变体`。Agent 先读取帮助主题 `case:recipe_extensions.sampling`，再按主题关联的 workflow 和 API 参考核对输入、函数签名、产物与证据边界。支持 Python 帮助 API 时可调用：

```python
import ai4e_task as task
print(task.read_help_topic("case:recipe_extensions.sampling")["content"])
```

<!-- research-adaptation-details -->
#### 选择与改写说明

几何点采样函数替换和身份交接；先物化完整基案例，再按扩展说明修改。

数据形态：mesh, point_fields；训练机制：epoch。

##### 具体修改位置

- 基案例：`aero_cfd.shapenet_car_abupt`。先 `copy_example` 物化；返回的 `documentation.entry` 可定位基案例和扩展的说明副本。
- 本变体可改：`sampling`。
- 覆盖/新增文件：`custom_abilities.py`、`configuration.py`、`post.py`、`rawprep.py`、`config.yaml`、`pipeline.py`、`train.py`、`infer.py`、`trainprep.py`。逐项读这些文件的输入输出和基案例消费者，其他阶段继续继承。
- 物化后检查根配置；若扩展没有覆盖配置，按本页前文将本地组件显式接入，复制文件本身不等于采用了组件。

##### 运行与读回

- 运行前填写自己的输入与输出目录；先按本页原有命令/阶段说明执行短程连接验证。更改模型或科学定义时不得沿用不兼容检查点。
- 核对真实运行报告、检查点和固定预测；存在派生结果时必须从后处理读回。恢复与独立推理分别验证，不以导入成功替代。

##### 适用边界

- 覆盖文件集不能直接当完整案例运行；未声明的行为沿用基案例。
- 仅声明扩展演示范围，不据此扩大数值精度验收。


基案例完整说明：[本地正文](../aero_cfd/shapenet_car_abupt.md)。
