# AB-UPT 多域组件

原始网络：AB-UPT `2211068fd58600c52ed38de692f020e2d2b7c987`。输入与缓存设计参考 Noether `313e6c5c2ff31f283a3e5935b4d85888aac6b025`。许可集中在 LICENSE；原始与参考摘要见 source.json。

本地修改：结构版本 3 以有序命名域替代固定双域；输出字段决定头宽度，支持局部特征、全局及几何条件。保留原几何池化与 core 唯一前馈/位置编码实现。网络正式运行不导入外部仓库。旧接口、配置和检查点不兼容。

`forward` 接受 geometry_position、geometry_supernode_idx、geometry_batch_idx、domain_anchor_positions，以及可选 domain_query_positions、domain_anchor_features、domain_query_features、conditioning_inputs、geometry_conditioning_inputs、kv_cache。返回 `(predictions, cache)`；训练组件 `predict` 仅返回预测。输出 `{domain}_{field}` 和 `query_{domain}_{field}` 保持 `(B,N,C)`。

域内固定点数允许 B>1，几何点数可不同、超节点数相同，不提供 padding。默认 B=1。缓存只在 eval/no_grad 中使用；InferenceContext 预填充 anchors 后接受 query，支持 geometry_only 与完整逐层缓存，退出释放，状态变化拒绝。默认分块 1024。锁定 ShapeNet-Car 默认配置的 CPU 全量两轮训练、复制流水线与恢复已按参数和指标对照；结果与环境边界见仓库 `.context/mvp/abupt-reference-acceptance.md`。其他域/条件/特征组合仅有功能回归，不泛称所有配置数值等价。

配置与运行见根 recipes/aero_cfd；当前逐项验收见 `.context/mvp/abupt-multidomain-acceptance.md`。默认规模仅构造检查，真实训练验收使用合法小网络和 CPU。
