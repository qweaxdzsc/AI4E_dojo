# shapenet_volume 算子网络研究

完整流程为rawprep → trainprep → train → infer → post，Python正文显示每步交接。使用 `copy_example("operator_learning.shapenet_volume", "./study")` 复制后，设置config.yaml的inputs.rawprep.source、run_root和data_root；有共享准备时直接绑定inputs.train.preparation与inputs.infer.preparation，选择train/infer/post。

```bash
uv run --no-sync python pipeline.py --config config.yaml
```

默认FNO；model.parameters含逐轴modes、width、depth及逐轴padding，channels-first转换在应用连接中完成。FNO必须对完整空间域前向，不能把空间格切块当作独立样本。双圆柱三帧历史按时间再通道顺序合并，只开放FNO；当前步是下一个采样帧，不猜物理步长。

Darcy与ShapeNet可将model.family改为deeponet，parameters替换为 `{sensor_stride: 8, latent_dim: 16, branch_hidden: [32, 32], trunk_hidden: [32, 32]}`。传感器按参考网格索引固定、C序展平；ShapeNet每车网格对应自身物理包围盒，并将物理坐标、distance、valid纳入输入，不声称各车传感器物理位置相同。主干消费每例真实物理查询坐标。多输出使用split_branch。分支/主干/读出可通过components.model的普通构造器替换。

监督在训练统计归一化空间计算，推理反归一化并保留实体ID、有效域、字段和单位；ShapeNet保留原网格回贴及覆盖率。统计仅拟合训练切片。train.physical_weight仅Darcy允许非零，调用已有残差损失对物理非负解违约归约；依据正扩散、f=1和零真实边界的最大值原理。不是完整PDE残差，不强迫采样外圈为零。

独立恢复设置inputs.train.resume，train.updates是累计目标；模型结构、组件、训练统计或损失权重变化不能继续旧状态。独立infer绑定准备/检查点；post仅需固定结果，不重新预测。components.derived/consume可加入普通派生数组并完成保存读回。

默认100更新是工程短训起点，每模型/数据组合的参考、训练、准备、恢复、重试和安装验证累计不超过3小时。train.seconds只约束单次调用；组合总账本由验证主控维护。实际结果见专项验收，不宣称论文精度或Web模型开放。
