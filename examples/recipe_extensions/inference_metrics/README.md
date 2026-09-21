# 自定义推理评价

把 `metrics.py` 复制到仓库外的外流 recipe 目录，在 `infer.py` 里调用：

```python
from metrics import physical_metrics
job = infer_stage.configure_evaluation(job, settings=cfg.infer,
                                       sample_operation=physical_metrics)
```

也可设置 `infer.sample_metric.target: metrics.physical_metrics`。登记时不执行；执行时消费已还原物理空间的数组，不能再次调用模型。返回每个所选字段的一行记录，包含 field_id、values、undefined、algorithm、实体数量和选择声明。算法版本进入结果证据和导出，不与不同算法口径静默比较。

此例保持标准公式，用显式版本证明用户函数实际执行。自定义公式应独立提供数值夹具；未定义值保存 None 和原因。`test_infer_extensions.py` 在外部复制模板后实跑、保存、读回并核验用户版本与真实 VTK。

## 物化说明

- `base_case`: `aero_cfd.shapenet_car_abupt`。该目录是 extension 参考覆盖集，不是独立流程。
- 物化时先复制完整基案例，再叠加清单声明的覆盖文件，并写出 `.dojo-provenance.json`；未声明冲突、缺少基案例或非空目标会失败。
- 物化目录随后可以由 Agent 自由修改、用 direct-core 运行或交给 `ai4e_task` Python API；扩展目录本身不会绑定本机数据或自动启动任务。

## Agent Help Center

本目录是 `参考变体`。Agent 先读取帮助主题 `case:recipe_extensions.inference_metrics`，再按主题关联的 workflow 和 API 参考核对输入、函数签名、产物与证据边界。支持 Python 帮助 API 时可调用：

```python
import ai4e_task as task
print(task.read_help_topic("case:recipe_extensions.inference_metrics")["content"])
```
