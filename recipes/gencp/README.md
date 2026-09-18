# GenCP 可复制研究入口

当前为三个数据集 × CNO/SiT-FNO 的缩小实验接入，最终验收状态见 [验收记录](../../.context/mvp/gencp-acceptance.md)。256 个训练窗口、16 个评价窗口、每场最多 1,000 次更新；保留原网格和物理时间窗口。不是论文完整训练。

安装 `ai4e-contrib[gencp]` 后，将本目录复制到仓库外。复制 `examples/gencp/<数据集>_<骨干>/config.yaml` 为本目录的 `config.yaml`，仓库六例默认指向本次已核验的恢复数据根。迁移到其他机器时修改 `data.root`、`data.processed_root`、`paths.output` 和 `run_root`。设备可改 `cpu`、`mps` 或 `cuda`。所有相对路径以配置文件为基准。

```bash
uv run python pipeline.py --config config.yaml
uv run python trainprep.py --config config.yaml
uv run python train.py --config config.yaml --set train.preparation=/absolute/preparation.json
uv run python single.py --config config.yaml --set train.preparation=/absolute/preparation.json --set infer.checkpoints=/absolute/weights.json
uv run python infer.py --config config.yaml --set train.preparation=/absolute/preparation.json --set infer.checkpoints=/absolute/weights.json
uv run python post.py --config config.yaml --set post.results=/absolute/results.json
```

Python 正文给出分场训练、条件绑定、同步/顺序更新、固定结果分析。配置只放参数和能力导入路径。`train.fit_field` 可独立重训一个场；调用公开的 `bind_checkpoint_group`，把新权重与其他场旧权重组合到新的 JSON。更新次数可不同，准备与变换身份必须相容。

恢复时设置 `train.resume.<field>` 为该场 `latest.pt`。恢复要求相同最终预算、数据、优化器和目标；旧轮次检查点缺少采样游标会拒绝。验证使用独立随机上下文，不改变训练随机流；latest 用于基准对照，best 记录原单场物理指标选优，不能混称耦合最佳。

`single` 使用已知其他场条件；`infer` 只接收历史或声明的外部边界。核热中子左边界和固体左边界来自发布数据真值，是参考实验前提。物理时间、生成时间和训练更新次数独立。FSI 不宣称长时间自回归。

固定结果是每场独立 NPY、字节摘要、物理时间/身份、权重组和能力来源。post 不加载网络；原始输出保持不变，SDF 平滑和 mask 作为派生结果保存。原算法参数与论文目标见各案例 `source-config.yaml` 和验收记录。限时对照用仓库 `tools/verification/gencp/budget.py`，同一组合重试共用账本。
