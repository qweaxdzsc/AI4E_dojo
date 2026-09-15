# 替换训练采样

复制本目录并安装 Dojo，配置数据根及输出目录后用 `uv run python pipeline.py` 执行。

`model.sampling.target` 选择本地普通函数；函数改变几何点选择顺序，同时将剩余采样和元信息交给原模型准备能力。它在训练逐样本取数时执行，不在 YAML 加步骤顺序。训练准备记录函数源码和参数，独立训练按同一引用恢复。

也可在 `trainprep.py` 的 `configure_sampling` 中直接传入 `operation`；此时取消配置中的 target。采样能力须保留批次结构、原实体 ID、种子和轮次参数。
