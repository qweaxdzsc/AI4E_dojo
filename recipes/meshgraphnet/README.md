# MeshGraphNets / CylinderFlow

这是可复制的二维固定网格时空预测 Recipe。Python 文件决定
`rawprep → trainprep → train → infer → post` 顺序，YAML 只提供参数和阶段选择。

`inputs.rawprep.source` 可以指向包含 `meta.json` 与官方 train/valid/test TFRecord 的目录，
也可以指向按 split 保存的 `.pt` 小样本。`rawprep.max_trajectories` 可限制本次读取的
轨迹条数，不改写源分片。运行目录和数据目录必须分离；`post.py` 只读取 infer 写出的
固定 bundle，不重新运行模型。PhysicsNeMo 仅作为结构参考，Dojo 运行时不依赖它。

默认参数对齐 DeepMind CFD 设置：128 隐宽、15 个 processor block、batch 2、速度噪声
0.02、前 1000 步只累计统计、总目标一千万步。`infer.steps: all` 使用测试轨迹全部可用
时间；小样本短训只验证工程路径，不能作为论文精度证据。

```bash
uv run --no-sync python recipes/meshgraphnet/pipeline.py \
  --config recipes/meshgraphnet/config.yaml \
  --set inputs.rawprep.source=/absolute/path/to/cylinder_flow
```
