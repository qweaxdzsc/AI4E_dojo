# ShapeNet-Car / AB-UPT

复制本目录到个人实验目录，修改 config.yaml 的原始数据根、产物根和运行根。六个阶段/配置脚本与共享 aero_cfd recipe 一致，模板本身不是安装包。

在 Dojo 工作区安装汽车依赖：`uv sync --all-packages --extra abupt --inexact`。随后运行 `uv run --no-sync python /个人实验目录/pipeline.py`；独立阶段使用 rawprep.py、trainprep.py、train.py、post.py。已有准备由 train.preparation 指定，后处理由 post.checkpoint 指定检查点。

当前配置为 rawprep/trainprep/model/train/post 五段，采样与归一化位于 trainprep 下。默认正式 AB-UPT 网络；post 评估测试集并保存预测，完整网格查询由 post.query 控制，post.sample_indices 选择样本序号，post.query_chunk_size 控制查询块大小。调学习率、种子或锚点预算直接修改对应配置。

运行和数据目录应与脚本目录分开。旧顶层配置键目前被共享入口拒绝，自动兼容政策尚待确认；既有汽车正式两轮回归与双模型结果见 [验收记录](../../../.context/mvp/transolver3-acceptance.md)。
