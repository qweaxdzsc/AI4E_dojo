# 新增速度模长

复制本目录并安装 Dojo。先配置原始数据根、数据输出和运行目录，再用 `uv run python pipeline.py` 执行。

`custom_abilities.py` 只处理数组；`rawprep.py` 在提取之后登记速度模长。`rawprep.speed` 声明输入和输出，`save_fields` 保存新字段，统计使用本次训练分片，归一化与模型体积输入通过 `volume_speed` 衔接。未知速度单位保持未知，不猜为 m/s。

修改能力后重新执行原始处理与准备；独立训练使用 `train.preparation`。删除计算步骤时也要删除对新字段的消费，否则明确失败。

本例开启 require_features：推理输入必须含速度模长。默认交付已保存实体上的锚点预测，query=false；任意完整网格查询需要另外提供对应点的速度模长，不能把缺失特征静默当成零。此例用于验证能力交接，不作为未知速度预测的精度基线。
