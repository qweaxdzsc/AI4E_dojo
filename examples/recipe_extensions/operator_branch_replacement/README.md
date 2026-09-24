# DeepONet分支重组

从完整案例 operator_learning.shapenet_volume 物化后运行；本目录仅为覆盖资源。

物化后改写本地分支网络与配置连接即可形成变体，主干查询坐标和输出读回仍沿基案例契约。

```python
from ai4e_task import copy_example

copy_example("recipe_extensions.operator_branch_replacement", "./operator_branch_replacement")
```

设置独立 run_root、data_root 和数据输入后执行 `uv run --no-sync python pipeline.py --config config.yaml`。
模型家族与结构在 model 中声明；改变结构后必须开始新权重，不能恢复旧结构检查点。训练仍调用公共迭代执行器，固定预测保存后由 post 独立读回。

本地分支使用公开MLP和前馈块进行局部残差组合，主干与读出仍使用DeepONet。新增派生预测范数保存并由user_outputs.consume读回；这里保留原字段单位语义，不将混合分量范数当速度。

默认小预算只验证工程连接；真实结果和安装范围见专项验收，不表示论文或生产精度。
