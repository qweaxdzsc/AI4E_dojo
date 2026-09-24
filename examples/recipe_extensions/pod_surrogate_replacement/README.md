# POD系数代理替换为MLP

使用 copy_example("recipe_extensions.pod_surrogate_replacement", "./pod_mlp_study") 物化完整 surrogate_modeling.double_cylinder 基案例。输入为该案例的共享POD准备，基底仅由训练轨迹拟合。

本地 pod_mlp.fit 通过公开共享迭代训练拟合已有MLP，pod_mlp.rebuild从普通数组恢复参数。配置components.fit/rebuild即可替换，无需修改框架注册表或继承估计器基类。参数hidden/updates/seed实际作用于新代理；family=custom声明本地变体。

可继续改写本地 fit/rebuild 或网络宽度形成新代理，但必须消费同一准备中的 POD 基底和标准化身份。

train阶段保存独立系数模型，infer读取准备内的同一POD解码到物理场并保存，post只读取固定结果。改变POD秩或标准化后旧状态明确拒绝。POD提供torch_decoder用于可微场重建，基底冻结；本例训练目标是系数MSE，不宣称SVD拟合可微或施加物理约束。

设置独立run_root/data_root和inputs.trainprep.dataset后，执行 `uv run --no-sync python pipeline.py --config config.yaml`。可已有准备时选择train/infer/post并配置对应输入。此扩展从头拟合MLP，最终状态恢复用于预测；完整训练检查点另保留，未给此recipe增加通用优化器恢复协议。小预算验收不代表预测精度达标。
