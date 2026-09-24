# 两个算子共用物理约束

从完整案例 operator_learning.darcy 物化后运行；本目录仅为覆盖资源。

物化后可改写物理损失权重或本地约束组件，固定准备、监督目标和结果读回仍由基案例交接。

```python
from ai4e_task import copy_example

copy_example("recipe_extensions.operator_physical_loss", "./operator_physical_loss")
```

设置独立 run_root、data_root 和数据输入后执行 `uv run --no-sync python pipeline.py --config config.yaml`。
模型家族与结构在 model 中声明；改变结构后必须开始新权重，不能恢复旧结构检查点。训练仍调用公共迭代执行器，固定预测保存后由 post 独立读回。

默认FNO；改为DeepONet时，将parameters改为sensor_stride、latent_dim、branch_hidden、trunk_hidden。两者都经同一FieldObjective调用已有residual_loss。物理解需满足正扩散、非负源与零Dirichlet，当前仅Darcy准入；最大值原理要求解非负。physical_weight=0关闭、0.1开启，反归一化在梯度图内。此项并非完整PDE残差，也不对非零采样外圈施加零值边界。派生数组由独立post消费。

默认小预算只验证工程连接；真实结果和安装范围见专项验收，不表示论文或生产精度。
