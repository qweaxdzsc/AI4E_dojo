# 五组交叉实验

独立输出根包含 examples/<案例>/config.yaml、selection.json、runs、predictions、comparison、reports。先从仓库复制五例并设置物理 PT、原始几何和独立运行路径。固定名单来自排序后的测试样本，以独立 NumPy default_rng(42) 无放回取五个，前三个出图。

统一入口（均通过 uv run）：

- `python tools/verification/cross_model/train.py <输出根>`：顺序执行五组配置指定轮数的训练，登记明确新建的运行；成功项不重复训练。
- `python tools/verification/cross_model/post.py <输出根>`：消费已登记的最后检查点和冻结准备，完整点场评价。
- `python tools/verification/cross_model/compare.py <输出根>`：生成 NASA 和汽车两份比较报告。
- `--render-only`：仅更新图像，不重新训练或评价。

当前真实实验输出根与证据见 `.context/mvp/cross-model-acceptance.md`。原模型仓库只读，不作为正式包依赖。NASACRM 截面以对称中面到正 Y 翼尖的半展长计算；汽车切面为完整物理包围盒中间 Y、Z 平面。

完整服务器执行与报告格式见 [服务器操作手册](../../../docs/aero-cfd-server-runbook.md)。新预算必须使用新的实验根，已有成功登记不会因配置变更自动重训。
