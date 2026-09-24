<!-- dojo-help: {"topic_id": "user-component:checkpoint-state", "title": "用户内存状态的保存与恢复", "kind": "how-to", "layer": "user-component", "domain": "training", "summary": "可选save/validate/load连接，保持静态兼容声明与可变状态分离", "tasks": ["用户状态", "检查点恢复", "state_bindings"], "symbols": ["ai4e_core.applications.base.iteration_training.train_model", "ai4e_core.abilities.training.checkpoint.capture_iteration", "ai4e_core.abilities.training.checkpoint.restore_iteration"]} -->
# 用户内存状态的保存与恢复

无状态组件不需要新增接口。原有模型、优化器、流、RNG、EMA、scheduler、scaler继续沿用框架自己的恢复，不能重复登记。

有状态的用户目标或选择策略可显式传入 `state_bindings`。每个名字提供三个普通函数：save返回完整内存状态；validate只检查传入副本、不得改变活对象；load恢复该状态。算法兼容声明仍在 `algorithm_state`/contract 中，可变计数与最佳值不要放进去。

```python-fragment
bindings = {
    "selection": {
        "save": local_selection.state_dict,
        "validate": local_selection.validate_state_dict,
        "load": local_selection.load_state_dict,
    }
}
result = train_model(model, optimizer, stream, batch, objective,
                     updates=updates, session=session, contract=contract,
                     namespace="train", state_bindings=bindings,
                     checkpoint_every=3, evaluate_every=2, evaluate=evaluate)
```

这里local_selection是本地组件，需同时保存 `BestMetric` 状态与获胜的独立权重快照，预检二者位置/来源匹配。选择器不负责文件写入；保存仍交给writer。完整可复制写法见 `case:recipe_extensions.research_state`。

两个周期按有效更新计数，示例7更新时验证2/4/6/7、保存3/6/7；同一步先验证再保存。未指定验证周期时沿用保存周期；底层fit_iterations未指定保存周期时保持原来的跟随评价行为。自定义iterate不支持独立周期时只接受等周期，差异设置在模型更新前拒绝。

检查点的附加用户状态是版本化具名集合。恢复时名称必须与显式连接一致，不能丢弃旧状态或补造缺失值。先预检再加载，加载异常时回滚框架管理状态与用户保存的内存快照；若用户load连原快照也无法读回，明确报回滚失败。文件、服务、其他进程等外部副作用不在此承诺内，不能在validate/load里执行。检查点仍只接受可信本地文件。

旧检查点不包含用户状态且本次也未启用连接时继续可读；旧文件缺少本次要求的状态则拒绝，不伪造迁移。
