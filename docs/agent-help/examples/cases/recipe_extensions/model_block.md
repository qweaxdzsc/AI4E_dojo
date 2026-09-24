<!-- dojo-help: {"case_ids": ["recipe_extensions.model_block"], "domain": "recipe_extensions", "kind": "case", "layer": "example", "summary": "AB-UPT内部前馈激活替换；先物化完整基案例，再按扩展说明修改。", "tasks": ["mesh", "point_fields", "model_block"], "title": "recipe_extensions.model_block", "topic_id": "case:recipe_extensions.model_block"} -->
# `recipe_extensions.model_block`

- 类型：`extension`
- 用途：参考变体与 Agent 组件组装示例
- 资源路径：`examples/recipe_extensions/model_block`

AB-UPT内部前馈激活替换；先物化完整基案例，再按扩展说明修改。

- 数据形态：mesh, point_fields
- 训练机制：epoch
- 替换入口：model_block
- 限制：覆盖文件集不能直接当完整案例运行；未声明的行为沿用基案例。
- 限制：仅声明扩展演示范围，不据此扩大数值精度验收。
- 基案例：`aero_cfd.shapenet_car_abupt`
- 覆盖文件：
  - `variants.py`

## 物化流程

`copy_example` 会先复制完整基案例，再叠加声明的覆盖文件并写 provenance。
物化后必须重新检查配置、输入和恢复兼容性；不能直接运行原 extension 目录。

## 案例详细说明

来源：案例 README；SHA256 `9dc8ad9b6a5f070870c1beff3c0c226cfb23b5952c1141fe635c30acee82d90f`。

### 替换 AB-UPT 内部前馈激活

先复制完整 `examples/aero_cfd/shapenet_car_abupt/`，再将本目录 `variants.py` 放到副本。修改副本 config.yaml 的 `components.model: variants`，保留数据输入和其它参数。随后运行副本 pipeline.py；准备仍按该模型自己的声明生成，旧准备/检查点不自动迁写。

本地构造器创建原网络后、优化器创建前，将物理块前馈激活由 GELU 换为 SiLU；其它能力直接委托原组件。所有线性参数的名称和注册顺序不变，激活本身没有新增参数。本地 SOURCE 和 describe 声明文件摘要，形状相同仍区分算法身份。变体来源改变后从头训练，不能把形状相同解释成科学合同相同。

验证新旧前向不同、参数实际更新、相同变体连续/恢复结果一致；训练后旧推理缓存必须拒绝。输出继续由原 infer 保存，post 只读固定结果。实际测试见 `tests/integration/test_training_strategy_extensions.py`；本目录是覆盖文件集，不是完整模板。

恢复验收固定总训练计划，在第一轮保存检查点后继续第二轮；余弦调度总目标不可从一轮改成两轮来模拟相同训练。仓库外复制测试经真实 wheel 安装完成，部件直接测试另查前向变化和缓存失效。

#### 物化说明

- `base_case`: `aero_cfd.shapenet_car_abupt`。该目录是 extension 参考覆盖集，不是独立流程。
- 物化时先复制完整基案例，再叠加清单声明的覆盖文件，并写出 `.dojo-provenance.json`；未声明冲突、缺少基案例或非空目标会失败。
- 物化目录随后可以由 Agent 自由修改、用 direct-core 运行或交给 `ai4e_task` Python API；扩展目录本身不会绑定本机数据或自动启动任务。

#### Agent Help Center

本目录是 `参考变体`。Agent 先读取帮助主题 `case:recipe_extensions.model_block`，再按主题关联的 workflow 和 API 参考核对输入、函数签名、产物与证据边界。支持 Python 帮助 API 时可调用：

```python
import ai4e_task as task
print(task.read_help_topic("case:recipe_extensions.model_block")["content"])
```

<!-- research-adaptation-details -->
#### 选择与改写说明

AB-UPT内部前馈激活替换；先物化完整基案例，再按扩展说明修改。

数据形态：mesh, point_fields；训练机制：epoch。

##### 具体修改位置

- 基案例：`aero_cfd.shapenet_car_abupt`。先 `copy_example` 物化；返回的 `documentation.entry` 可定位基案例和扩展的说明副本。
- 本变体可改：`model_block`。
- 覆盖/新增文件：`variants.py`。逐项读这些文件的输入输出和基案例消费者，其他阶段继续继承。
- 物化后检查根配置；若扩展没有覆盖配置，按本页前文将本地组件显式接入，复制文件本身不等于采用了组件。

##### 运行与读回

- 运行前填写自己的输入与输出目录；先按本页原有命令/阶段说明执行短程连接验证。更改模型或科学定义时不得沿用不兼容检查点。
- 核对真实运行报告、检查点和固定预测；存在派生结果时必须从后处理读回。恢复与独立推理分别验证，不以导入成功替代。

##### 适用边界

- 覆盖文件集不能直接当完整案例运行；未声明的行为沿用基案例。
- 仅声明扩展演示范围，不据此扩大数值精度验收。


基案例完整说明：[本地正文](../aero_cfd/shapenet_car_abupt.md)。
