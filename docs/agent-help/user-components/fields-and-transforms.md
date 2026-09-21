<!-- dojo-help: {"domain": "components", "kind": "how-to", "layer": "user-component", "summary": "添加字段时贯通身份、单位、分量、保存、统计和模型输入。", "tasks": ["编写用户组件", "组件调用证明"], "title": "字段与变换", "topic_id": "user-component:fields"} -->
# 字段与变换

字段声明必须说明 point/cell 归属、实体 ID 顺序、分量、单位及物理/归一化状态。筛选改变实体数时，同步更新同组字段和身份。

变换应提供正反方向和冻结参数读回。新字段只有在保存、清单、统计、准备、模型输入、预测和 post 中完整消费后才算接入。

## 推荐起点

物化 `recipe_extensions.field_mapping`。它从完整外流 standalone 出发，在 rawprep 中新增速度模长，并贯通保存、统计、归一化、模型输入和推理门禁。

纯数组能力不依赖 Dojo：

```python
# custom_abilities.py
import numpy as np


def speed_magnitude(velocity):
    if velocity.ndim != 2 or velocity.shape[1] != 3:
        raise ValueError("velocity 必须是 N×3")
    return {"speed": np.linalg.norm(velocity, axis=-1, keepdims=True)}
```

在 `rawprep.py` 的真实处理顺序中登记：

```python
data = pre.map_fields(
    data,
    name="速度模长",
    operation=speed_magnitude,
    inputs=cfg.rawprep.speed.inputs,
    outputs=cfg.rawprep.speed.outputs,
)
```

配置必须声明输入绑定、输出名称、实体对齐、分量、单位来源和状态：

```yaml
rawprep:
  speed:
    inputs:
      velocity: volume.velocity
    outputs:
      speed:
        name: volume_speed
        entity_like: volume.velocity
        components: 1
        unit_from: volume.velocity
        state: physical
```

`map_fields` 是登记点；样本循环真正执行时才调用 `speed_magnitude`。因此“配置存在”或“步骤登记成功”不是调用证据。

## 完整交接链

新增字段后逐项核对：

1. extract 后能取得源字段，实体数和原 ID 一致。
2. filter 同步筛选同组字段和身份；point mask 不应用于 CellData。
3. save 清单包含字段名称、shape、dtype、单位、状态和内容摘要。
4. stats 只使用本次成功交付的训练分片。
5. normalization 冻结正变换参数，并能执行反变换。
6. trainprep 把字段接入正确 domain 的 features/targets/conditioning。
7. 模型 `data_specs` 声明正确分量数。
8. infer 保存物理或明确标记的归一化状态。
9. post 按同一实体身份读回，不通过数组长度猜对应关系。

## 验证

对一个固定样本保存源速度、派生模长和原 ID，读回后逐值比较 `sqrt(vx²+vy²+vz²)`。再执行一次 trainprep 和模型前向，证明 `volume_speed` 不是只写未读。修改或删除该能力后，依赖它的准备、模型输入或推理应明确失效，而不是补零继续运行。

单位未知时保持未知；不能根据字段名推断为 m/s。归一化数组与物理数组必须区分状态，post 指标通常应在物理量上计算。
