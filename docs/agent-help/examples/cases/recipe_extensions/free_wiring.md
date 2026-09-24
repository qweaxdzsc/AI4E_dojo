<!-- dojo-help: {"case_ids": ["recipe_extensions.free_wiring"], "domain": "recipe_extensions", "kind": "case", "layer": "example", "summary": "普通函数自由连接与阶段返回值交接；先物化完整基案例，再按扩展说明修改。", "tasks": ["mesh", "point_fields", "steps", "components"], "title": "recipe_extensions.free_wiring", "topic_id": "case:recipe_extensions.free_wiring"} -->
# `recipe_extensions.free_wiring`

- 类型：`extension`
- 用途：参考变体与 Agent 组件组装示例
- 资源路径：`examples/recipe_extensions/free_wiring`

普通函数自由连接与阶段返回值交接；先物化完整基案例，再按扩展说明修改。

- 数据形态：mesh, point_fields
- 训练机制：epoch
- 替换入口：steps, components
- 限制：覆盖文件集不能直接当完整案例运行；未声明的行为沿用基案例。
- 限制：仅声明扩展演示范围，不据此扩大数值精度验收。
- 基案例：`aero_cfd.shapenet_car_abupt`
- 覆盖文件：
  - `configuration.py`
  - `user_wiring.py`
  - `config.yaml`
  - `points.json`
  - `pipeline.py`
  - `user_steps.py`

## 物化流程

`copy_example` 会先复制完整基案例，再叠加声明的覆盖文件并写 provenance。
物化后必须重新检查配置、输入和恢复兼容性；不能直接运行原 extension 目录。

## 案例详细说明

来源：案例 README；SHA256 `a47b462a9a05e5ee63f811478786e76b7ba0da9ab8e760a750a65c54a6db19b7`。

### 自由组件连接

复制本目录到仓库外，执行 `uv run python pipeline.py`。运行记录和数据默认写到复制目录的兄弟目录。

修改 config.yaml 的 radius 调整参数；替换 user_steps.py 的普通函数或在 pipeline.py 插入 run.stage 调用扩展流程。输入输出不同就在 user_wiring.py 转换，不需要继承、注册或统一返回字典。

数据文件 features.json 可由后续用户代码直接读取；运行摘要保存输出引用。平台展示或跨进程交接只在实际使用时另行适配。本例不表示任意组件天然匹配。

#### 物化说明

- `base_case`: `aero_cfd.shapenet_car_abupt`。该目录是 extension 参考覆盖集，不是独立流程。
- 物化时先复制完整基案例，再叠加清单声明的覆盖文件，并写出 `.dojo-provenance.json`；未声明冲突、缺少基案例或非空目标会失败。
- 物化目录随后可以由 Agent 自由修改、用 direct-core 运行或交给 `ai4e_task` Python API；扩展目录本身不会绑定本机数据或自动启动任务。

#### Agent Help Center

本目录是 `参考变体`。Agent 先读取帮助主题 `case:recipe_extensions.free_wiring`，再按主题关联的 workflow 和 API 参考核对输入、函数签名、产物与证据边界。支持 Python 帮助 API 时可调用：

```python
import ai4e_task as task
print(task.read_help_topic("case:recipe_extensions.free_wiring")["content"])
```

<!-- research-adaptation-details -->
#### 选择与改写说明

普通函数自由连接与阶段返回值交接；先物化完整基案例，再按扩展说明修改。

数据形态：mesh, point_fields；训练机制：epoch。

##### 具体修改位置

- 基案例：`aero_cfd.shapenet_car_abupt`。先 `copy_example` 物化；返回的 `documentation.entry` 可定位基案例和扩展的说明副本。
- 本变体可改：`steps`、`components`。
- 覆盖/新增文件：`configuration.py`、`user_wiring.py`、`config.yaml`、`points.json`、`pipeline.py`、`user_steps.py`。逐项读这些文件的输入输出和基案例消费者，其他阶段继续继承。
- 物化后检查根配置；若扩展没有覆盖配置，按本页前文将本地组件显式接入，复制文件本身不等于采用了组件。

##### 运行与读回

- 运行前填写自己的输入与输出目录；先按本页原有命令/阶段说明执行短程连接验证。更改模型或科学定义时不得沿用不兼容检查点。
- 核对真实运行报告、检查点和固定预测；存在派生结果时必须从后处理读回。恢复与独立推理分别验证，不以导入成功替代。

##### 适用边界

- 覆盖文件集不能直接当完整案例运行；未声明的行为沿用基案例。
- 仅声明扩展演示范围，不据此扩大数值精度验收。


基案例完整说明：[本地正文](../aero_cfd/shapenet_car_abupt.md)。
