<!-- dojo-help: {"topic_id": "workflow:pcno-cylinder", "title": "PCNO圆柱配对研究", "kind": "workflow", "layer": "recipe", "domain": "spatiotemporal_pde", "summary": "官方来源准入、双圆柱监督/连续性对照和固定结果扩展。", "tasks": ["圆柱预测", "物理约束验证", "恢复", "扩展输出"], "case_ids": ["pcno.double_cylinder", "extension.pcno_cylinder"], "symbols": ["ai4e_core.run.launch", "ai4e_task.copy_example"]} -->
# PCNO 圆柱研究

使用 `ai4e_task.copy_example("pcno.double_cylinder", target)` 复制完整研究正文，绑定原始双圆柱来源并把运行和数据根指向代码目录外。通过直接 Python 入口运行，再按需把同一目录交给 Task。

历史3帧预测12帧；5条训练轨迹、1条留出验证。训练集拟合统计，数据按窗口读取，不复制整个训练集。未来真实SDF仅用于损失与离线评价。

`inputs.train.resume` 绑定生成的 `train/resume.json`，保留科学配置才能精确恢复。更新预算属于科学配置；增加目标不能冒充原目标续训。
`inputs.infer.preparation` 和 `inputs.infer.checkpoints` 可独立绑定，`inputs.post.results` 只读取固定预测。

扩展案例 `extension.pcno_cylinder` 包含普通替换构造器和速度模长分析，必须以新实验验证替换；固定结果扩展可以独立运行，不需要再次预测。
来源是外部只读依赖，复制准备清单不会自动带走原始HDF5。

CylinderFlow 官方原始子集可用下载公开函数获取，但当前分片线性三角散度未通过既定准入，因此没有登记可训练完整案例。不能从网络构造成功推断数据和物理目标一致。

比较初始化、末帧保持、监督模型与物理模型，报告每分量/时距误差及散度。小数据短训和单次种子不能声明论文复现或统计显著性。
