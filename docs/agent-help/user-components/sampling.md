<!-- dojo-help: {"domain": "components", "kind": "how-to", "layer": "user-component", "summary": "显式连接采样器并记录预算、种子、来源域和输出身份。", "tasks": ["编写用户组件", "组件调用证明"], "title": "采样组件", "topic_id": "user-component:sampling"} -->
# 采样组件

采样器使用普通函数或对象，参数由所属阶段配置提供。登记采样步骤不等于已经执行；报告必须来自真实执行点。

变更点数或拓扑后同步字段与实体身份。采样预算属于当前运行参数，不能混入冻结准备产物的导入兼容条件。

## 选择接入层

- 通用索引抽样：查询 `ai4e_core.abilities.sampling`，直接组合 uniform、random、spatial 等公开能力。
- 模型输入组织：替换模型组件公开的 sampler/prepare_inputs，使几何点、锚点和查询点保持模型所需布局。
- 物理点集：在参数化 PDE 准备中声明 supervised、interior、initial、boundary 和 periodic 采样。

先搜索当前案例使用的符号：

```python
import ai4e_task as task

hits = task.search_help("sampling seed geometry anchor query", limit=20)
for hit in hits:
    print(hit["topic_id"], hit["case_ids"])
```

## 模型采样变体

`recipe_extensions.sampling` 保持 AB-UPT 的输入合同，只改变几何点选择顺序：

```python
import torch
from ai4e_contrib.ability.model.abupt.sampling import prepare_inputs


def reverse_geometry(fields, config, **kwargs):
    binding = kwargs["bindings"]["geometry_field"]
    count = len(fields[binding])
    budget = min(count, int(config["geometry"]["max_points"]))
    indices = dict(kwargs.pop("indices", None) or {})
    indices["geometry"] = torch.arange(count - 1, count - budget - 1, -1)
    return prepare_inputs(fields, config, indices=indices, **kwargs)
```

阶段脚本必须在每个可独立启动的真实调用点传入该函数。只在 pipeline 连续路径中连接，会让独立 `train.py` 或 `infer.py` 静默回到默认采样器。

## 参数化 PDE 点集

典型配置包含：

```yaml
model:
  sampling:
    seed: 42
    supervised: {method: all}
    interior: {method: all, include_boundary: true}
    initial: {method: all}
    boundaries:
      left: {method: all}
      right: {method: all}
```

边界名称必须与实际边界条件一致；周期边界需要成对索引，不能独立随机后再按位置猜配对。改变物理采样会改变准备内容身份，依赖该 preparation 的检查点通常不可完整恢复。

## 必须记录的证据

- sampler 的全限定名称和源码摘要；
- 随机流、seed、epoch/update 作用域；
- 来源实体数、请求预算、实际点数、是否放回和不足策略；
- 输出索引及其原实体 ID；
- 训练与推理是否使用相同或明确不同的采样策略；
- 同 seed 重放结果和不同 seed 的预期差异。

`max_points`、anchor 数和 query 数属于当前模型运行预算，不应写入通用数据准备的导入门禁。若采样改变拓扑或邻接关系，则还需重新建立图/邻域及其字段对齐证据。
