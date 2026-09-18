# 替换 AB-UPT 内部前馈激活

先复制完整 `examples/aero_cfd/shapenet_car_abupt/`，再将本目录 `variants.py` 放到副本。修改副本 config.yaml 的 `components.model: variants`，保留数据输入和其它参数。随后运行副本 pipeline.py；准备仍按该模型自己的声明生成，旧准备/检查点不自动迁写。

本地构造器创建原网络后、优化器创建前，将物理块前馈激活由 GELU 换为 SiLU；其它能力直接委托原组件。所有线性参数的名称和注册顺序不变，激活本身没有新增参数。本地 SOURCE 和 describe 声明文件摘要，形状相同仍区分算法身份。变体来源改变后从头训练，不能把形状相同解释成科学合同相同。

验证新旧前向不同、参数实际更新、相同变体连续/恢复结果一致；训练后旧推理缓存必须拒绝。输出继续由原 infer 保存，post 只读固定结果。实际测试见 `tests/integration/test_training_strategy_extensions.py`；本目录是覆盖文件集，不是完整模板。

恢复验收固定总训练计划，在第一轮保存检查点后继续第二轮；余弦调度总目标不可从一轮改成两轮来模拟相同训练。仓库外复制测试经真实 wheel 安装完成，部件直接测试另查前向变化和缓存失效。
