# 自定义推理评价

把 `metrics.py` 复制到仓库外的外流 recipe 目录，在 `infer.py` 里调用：

```python
from metrics import physical_metrics
job = infer_stage.configure_evaluation(job, settings=cfg.infer,
                                       sample_operation=physical_metrics)
```

也可设置 `infer.sample_metric.target: metrics.physical_metrics`。登记时不执行；执行时消费已还原物理空间的数组，不能再次调用模型。返回每个所选字段的一行记录，包含 field_id、values、undefined、algorithm、实体数量和选择声明。算法版本进入结果证据和导出，不与不同算法口径静默比较。

此例保持标准公式，用显式版本证明用户函数实际执行。自定义公式应独立提供数值夹具；未定义值保存 None 和原因。`test_infer_extensions.py` 在外部复制模板后实跑、保存、读回并核验用户版本与真实 VTK。
