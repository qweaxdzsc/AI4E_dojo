<!-- dojo-help: {"domain": "components", "kind": "how-to", "layer": "user-component", "summary": "用普通函数或对象接入研究流程，不要求继承全局组件基类。", "tasks": ["编写用户组件", "组件调用证明"], "title": "用户组件总览", "topic_id": "user-component:overview"} -->
# 用户组件总览

用户组件可以拥有自己的输入输出类型，不要求继承 Dojo 基类。已有研究代码可在自己的调用处连接能力；需要完整领域流程时复制 standalone，在阶段脚本中转换相邻组件。可持久化配置保存全限定 import 路径和构造参数；闭包和 lambda 不能作为可重建声明。

先建立基线；按研究目标选择变更因素并记录。每个变体都记录最终配置、组件身份、调用计数或阶段报告，以及对应检查点和结果。

## 从哪一层修改

- 只改参数：修改复制目录的 `config.yaml`，由 `configuration.py` 校验和转换。
- 替换一个普通算法函数：在复制目录新增模块，以全限定路径连接，或在阶段脚本中直接传入。
- 改领域步骤的连接：修改复制目录中的 `rawprep.py`、`trainprep.py`、`train.py`、`infer.py` 或 `post.py`。
- 改阶段顺序或建立研究分支：修改 `pipeline.py`，继续使用 `run.stage` 留下阶段边界。
- 需要版本、后台执行、停止、恢复或比较：保持同一案例目录不变，交给 `ai4e_task`。

## 完整领域案例的接入过程

1. 先从能力菜单或领域 workflow 定位现有入口，再按需搜索 API 和 extension。
2. 需要完整案例时复制一个 standalone；单工具或已有代码接入直接参考对应能力教程，不要求复制。
3. 运行未修改基线并保存最终配置、阶段摘要和固定结果。
4. 在案例目录中新增 `my_components.py`，函数签名以实际调用方为准。
5. 在配置或阶段脚本中显式连接组件；不要写入 core 私有会话或跨层内部字典。
6. 先做最小输入检查，再做一次真实更新或推理。
7. 从 `inputs/config.yaml`、阶段报告、组件来源、检查点和结果清单证明调用发生。
8. 组件语义、模型结构或准备数据身份变化时，从头准备或训练；只有合同一致时才完整恢复。

## 通用组件骨架

```python
# my_components.py
CALLS = 0


def transform(value, *, scale: float = 1.0):
    """普通 Python 输入输出；调用方负责把它连接到领域数据。"""
    global CALLS
    CALLS += 1
    return value * scale


def describe() -> dict:
    """返回可序列化身份，便于阶段报告证明实际来源。"""
    return {"component": f"{__name__}.transform", "calls": CALLS}
```

组件本身不应写 `summary.json`、伪造资产索引或接管 Task 状态。需要写产物时，由阶段调用 `TrainingRun().output_dir(...)`、`record_asset`、`record_metric` 和 `report`。

## 可直接参考的覆盖集

- `recipe_extensions.model_block`：替换网络内部模块并改变来源身份。
- `recipe_extensions.field_mapping`：新增字段、保存、统计、归一化和模型消费。
- `recipe_extensions.sampling`：替换真实训练与推理采样调用点。
- `recipe_extensions.inference_metrics`：注入物理评价函数。
- `recipe_extensions.inference_fields`：生成并交付派生预测字段。
- `recipe_extensions.physical_visualization`：自定义 post 绘图。
- `recipe_extensions.wdno`：替换网络、目标、优化器、调度器和更新函数。

先调用 `read_help_topic("case:<extension-id>")` 查看基案例和覆盖文件，再用 `copy_example` 物化完整目录。

## 证据边界

import 成功只证明符号可见；前向通过只证明形状能连接；一次反向与参数变化证明组件参与更新；恢复一致性还需要固定数据、配置、来源和检查点合同；论文级结论需要完整数据、预算和评价协议。
