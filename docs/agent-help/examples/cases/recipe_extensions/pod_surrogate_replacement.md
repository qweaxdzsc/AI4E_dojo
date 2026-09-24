<!-- dojo-help: {"case_ids": ["recipe_extensions.pod_surrogate_replacement"], "domain": "recipe_extensions", "kind": "case", "layer": "example", "summary": "POD系数代理替换；先物化完整基案例再运行。", "tasks": ["regular_grid", "fit", "rebuild"], "title": "recipe_extensions.pod_surrogate_replacement", "topic_id": "case:recipe_extensions.pod_surrogate_replacement"} -->
# `recipe_extensions.pod_surrogate_replacement`

- 类型：`extension`
- 用途：POD系数代理替换
- 资源路径：`examples/recipe_extensions/pod_surrogate_replacement`

POD系数代理替换；先物化完整基案例再运行。

- 数据形态：regular_grid
- 训练机制：iteration
- 替换入口：fit, rebuild
- 限制：短预算工程集成，不代表论文或生产精度。
- 基案例：`surrogate_modeling.double_cylinder`
- 覆盖文件：
  - `README.md`
  - `config.yaml`
  - `pod_mlp.py`

## 物化流程

`copy_example` 会先复制完整基案例，再叠加声明的覆盖文件并写 provenance。
物化后必须重新检查配置、输入和恢复兼容性；不能直接运行原 extension 目录。

## 案例详细说明

来源：案例 README；SHA256 `238b2c9b59e95067bae737c0cf25805741402a93c9247be99626d297be4df265`。

### POD系数代理替换为MLP

使用 copy_example("recipe_extensions.pod_surrogate_replacement", "./pod_mlp_study") 物化完整 surrogate_modeling.double_cylinder 基案例。输入为该案例的共享POD准备，基底仅由训练轨迹拟合。

本地 pod_mlp.fit 通过公开共享迭代训练拟合已有MLP，pod_mlp.rebuild从普通数组恢复参数。配置components.fit/rebuild即可替换，无需修改框架注册表或继承估计器基类。参数hidden/updates/seed实际作用于新代理；family=custom声明本地变体。

可继续改写本地 fit/rebuild 或网络宽度形成新代理，但必须消费同一准备中的 POD 基底和标准化身份。

train阶段保存独立系数模型，infer读取准备内的同一POD解码到物理场并保存，post只读取固定结果。改变POD秩或标准化后旧状态明确拒绝。POD提供torch_decoder用于可微场重建，基底冻结；本例训练目标是系数MSE，不宣称SVD拟合可微或施加物理约束。

设置独立run_root/data_root和inputs.trainprep.dataset后，执行 `uv run --no-sync python pipeline.py --config config.yaml`。可已有准备时选择train/infer/post并配置对应输入。此扩展从头拟合MLP，最终状态恢复用于预测；完整训练检查点另保留，未给此recipe增加通用优化器恢复协议。小预算验收不代表预测精度达标。


基案例完整说明：[本地正文](../surrogate_modeling/double_cylinder.md)。
