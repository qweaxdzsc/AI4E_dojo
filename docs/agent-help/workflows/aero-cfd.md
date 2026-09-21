<!-- dojo-help: {"case_ids": ["aero_cfd.shapenet_car_transolver3_surface"], "domain": "aero-cfd", "kind": "workflow", "layer": "workflow", "summary": "从 aero_cfd.shapenet_car_transolver3_surface 完成 direct-core、组件变体、Task 和证据读回。", "tasks": ["选择案例", "直接运行", "组件变体", "Task 托管", "证据读回"], "title": "外流 CFD 研究流程", "topic_id": "workflow:aero-cfd"} -->
# 外流 CFD 研究流程

本流程以 ShapeNet-Car 表面 Transolver-3 为完整起点。若研究体场、NASA CRM 或 AB-UPT，应选择对应 standalone，不要只改模型名而保留不相容字段与准备合同。

## 1. 搜索并选择案例

```python
import ai4e_task as task
case_id = 'aero_cfd.shapenet_car_transolver3_surface'
print(task.search_help("外流 表面 压力 Transolver", limit=10))
print(task.read_help_topic("case:" + case_id)["content"])
assert task.check_example(case_id)["ok"]
task.copy_example(case_id, "./study-case")
```

## 2. 核对数据和字段

阶段顺序是 `rawprep → trainprep → train → infer → post`。检查数据组件声明、manifest、surface/volume 来源、point/cell 归属、字段分量、单位、几何派生、筛选和分片。ShapeNet 与 NASA 的原始处理方式不能互换。

## 3. 阅读显式步骤

`rawprep.py` 应能看见 read、extract、geometry、field mapping、select、save 和 statistics；`trainprep.py` 负责领域输入装配与归一化；`train.py` 负责模型、目标和公开训练循环；`infer.py` 负责恢复、预测、评价和固定结果；`post.py` 只读固定结果。

## 4. direct-core 建立基线

从案例目录外执行：

```text
python /absolute/study-case/pipeline.py --config /absolute/study-case/config.yaml
```

先用小样本和短训验证接线。读回最终配置、处理后 manifest、preparation、训练协议、checkpoint、预测清单、物理字段、指标、VTK/图像和 post 报告。原始 manifest 与本次成功产物 manifest 分开。

## 5. 建立组件变体

- 网络：物化 `recipe_extensions.model_block`，替换公开模型组件或局部块。
- 字段：物化 `recipe_extensions.field_mapping`，贯通派生字段、统计、归一化和模型输入。
- 采样：物化 `recipe_extensions.sampling`，在独立 train/infer 的真实调用点连接 sampler。
- 推理评价/字段：参考 `recipe_extensions.inference_metrics` 和 `recipe_extensions.inference_fields`。
- 可视化：参考 `recipe_extensions.physical_visualization`，保持固定预测不变。

每个变体从 `base_case` 物化，先读 `.dojo-provenance.json`，再只改变预先声明的研究因素。

## 6. 证明真实调用

对网络核对模型描述、来源摘要、参数更新和 checkpoint contract；对字段核对实体 ID、单位、保存/读回和模型消费；对采样核对实际索引、预算、seed 和调用次数；对 infer/post 核对结果与资产依赖。配置字符串存在不能单独作为证据。

## 7. 独立 infer 与 post

独立 infer 明确绑定 preparation 和 checkpoint，输出固定预测及内容摘要。独立 post 明确绑定 infer 结果；缺结果时必须失败，不允许退回模型预测。历史兼容入口可以保留，但新流程的 post 不加载网络。

## 8. Task 托管


```python
project = task.create_project("./study")
record = task.new_task(project, "surface-pressure", source="./study-case")
submitted = task.submit_run(project, record["id"])
completed = task.wait_run(project, submitted["id"], timeout=120)
```

需要分阶段运行时，用 `read_configuration`/`replace_configuration` 选择阶段并显式绑定上一步固定产物。Task 负责快照、后台运行、停止、恢复和比较，不解释外流字段或训练参数。

## 9. 恢复和比较

恢复前固定数据/preparation、模型来源、采样、目标、optimizer 和调度合同。结构或字段改变时从头训练。用 `fork_task` 建立变体，`compare_runs` 只比较已登记且语义相同的指标；字段、单位、split 或数据身份不同应判不可比。

## 10. 结论边界

短训证明参数进入运行、组件被调用、状态可保存恢复、预测和 post 可交接。学习效果需要预先声明的指标和多轮结果；论文级结论还需要论文数据、协议、预算和统计对照。
