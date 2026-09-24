<!-- dojo-help: {"case_ids": ["recipe_extensions.physical_visualization"], "domain": "recipe_extensions", "kind": "case", "layer": "example", "summary": "固定物理场的可视化渲染替换；先物化完整基案例，再按扩展说明修改。", "tasks": ["mesh", "point_fields", "renderer"], "title": "recipe_extensions.physical_visualization", "topic_id": "case:recipe_extensions.physical_visualization"} -->
# `recipe_extensions.physical_visualization`

- 类型：`extension`
- 用途：参考变体与 Agent 组件组装示例
- 资源路径：`examples/recipe_extensions/physical_visualization`

固定物理场的可视化渲染替换；先物化完整基案例，再按扩展说明修改。

- 数据形态：mesh, point_fields
- 训练机制：epoch
- 替换入口：renderer
- 限制：覆盖文件集不能直接当完整案例运行；未声明的行为沿用基案例。
- 限制：仅声明扩展演示范围，不据此扩大数值精度验收。
- 基案例：`aero_cfd.shapenet_car_abupt`
- 覆盖文件：
  - `post.py`
  - `custom_render.py`

## 物化流程

`copy_example` 会先复制完整基案例，再叠加声明的覆盖文件并写 provenance。
物化后必须重新检查配置、输入和恢复兼容性；不能直接运行原 extension 目录。

## 案例详细说明

来源：案例 README；SHA256 `d7233b391fcdc3e1ddf7208167ac7e05b6aa3d810871b6d9541cb5880d23a798`。

### 自定义物理场图片

将本目录复制到研究目录，安装 `ai4e-core[post]`。输入是已交付体网格的固定单样本推理清单。

`uv run python post.py /absolute/sample/manifest.json /absolute/output`

`custom_render.py` 是可替换的普通绘图函数；`post.py` 明确读取结果、绑定网格、生成速度平方字段、绘图、保存及读回。新字段随 VTK 文件保存，图片生成不改变原始输入。更换颜色、相机、添加切片或额外字段都在此目录修改，不要求修改框架。

#### 物化说明

- `base_case`: `aero_cfd.shapenet_car_abupt`。该目录是 extension 参考覆盖集，不是独立流程。
- 物化时先复制完整基案例，再叠加清单声明的覆盖文件，并写出 `.dojo-provenance.json`；未声明冲突、缺少基案例或非空目标会失败。
- 物化目录随后可以由 Agent 自由修改、用 direct-core 运行或交给 `ai4e_task` Python API；扩展目录本身不会绑定本机数据或自动启动任务。

#### Agent Help Center

本目录是 `参考变体`。Agent 先读取帮助主题 `case:recipe_extensions.physical_visualization`，再按主题关联的 workflow 和 API 参考核对输入、函数签名、产物与证据边界。支持 Python 帮助 API 时可调用：

```python
import ai4e_task as task
print(task.read_help_topic("case:recipe_extensions.physical_visualization")["content"])
```

<!-- research-adaptation-details -->
#### 选择与改写说明

固定物理场的可视化渲染替换；先物化完整基案例，再按扩展说明修改。

数据形态：mesh, point_fields；训练机制：epoch。

##### 具体修改位置

- 基案例：`aero_cfd.shapenet_car_abupt`。先 `copy_example` 物化；返回的 `documentation.entry` 可定位基案例和扩展的说明副本。
- 本变体可改：`renderer`。
- 覆盖/新增文件：`post.py`、`custom_render.py`。逐项读这些文件的输入输出和基案例消费者，其他阶段继续继承。
- 物化后检查根配置；若扩展没有覆盖配置，按本页前文将本地组件显式接入，复制文件本身不等于采用了组件。

##### 运行与读回

- 运行前填写自己的输入与输出目录；先按本页原有命令/阶段说明执行短程连接验证。更改模型或科学定义时不得沿用不兼容检查点。
- 核对真实运行报告、检查点和固定预测；存在派生结果时必须从后处理读回。恢复与独立推理分别验证，不以导入成功替代。

##### 适用边界

- 覆盖文件集不能直接当完整案例运行；未声明的行为沿用基案例。
- 仅声明扩展演示范围，不据此扩大数值精度验收。


基案例完整说明：[本地正文](../aero_cfd/shapenet_car_abupt.md)。
