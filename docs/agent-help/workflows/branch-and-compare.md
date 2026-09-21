<!-- dojo-help: {"artifacts": ["metrics.json", "comparison"], "domain": "comparison", "kind": "workflow", "layer": "task", "summary": "从通过的基线派生变体并比较已经登记的固定指标。", "tasks": ["派生研究", "运行比较"], "title": "建立分支与比较运行", "topic_id": "workflow:branch-and-compare"} -->
# 建立分支与比较运行

先完成基线并固定数据、配置、检查点和指标语义。`fork_task` 创建研究分支，默认引用已有资产；只有自包含 bundle 才复制。变体只修改预先声明的研究因素，再提交新运行。

```python
branch = task.fork_task(project, baseline_task_id, name="loss-variant")
current = task.read_configuration(project, branch["id"])
task.save_configuration(project, branch["id"], patch, revision=current["revision"])
variant = task.wait_run(project, task.submit_run(project, branch["id"])["id"])
comparison = task.compare_runs(project, baseline_run_id, variant["id"], save=True)
```

`compare_runs` 只比较已登记指标，不重新计算科学结果。缺失声明的比较条件或指标时应判为不可比，不能填空值后宣称一致。
