# GenCP 独立参考与限时验收

`reference.py` 从锁定的原仓库提取原函数定义和原模型类；不调用 Dojo 数值实现。`budget.py` 以每个数据集×骨干为一个账本，失败/重试累计；175 分钟停止新命令并向当前计算请求中断，180 分钟终止。异常丢失监督状态须核实补记时间，不能清空账本重来。

`compare.py` 必须指定训练运行，不自动选最新。比较逐更新损失、权重、EMA、单场生成、耦合预测、真值和逐分量指标；局部 FP32 rtol=1e-4/atol=1e-6，最终相对 L2 不超过参考 1.05 倍，近零用事先约定的绝对 1e-6。`learning.py` 使用同一验证样本与初始噪声，比较训练前后归一化轨迹误差，不能把目标训练损失下降直接当成泛化改善。

从仓库根执行，先替换下面的绝对路径和案例名。NT 原参考数据目录指向 `raw/NTcouple`；两个 FSI 指向其上级 `raw`。

```bash
uv run python tools/verification/gencp/budget.py --ledger /experiment/budget.json -- \
  uv run python tools/verification/gencp/reference.py --source /source/GenCP \
  --data /data/raw/NTcouple --dataset ntcouple --backbone sit_fno \
  --output /experiment/reference --updates 1000
uv run python tools/verification/gencp/budget.py --ledger /experiment/budget.json -- \
  uv run python recipes/gencp/pipeline.py --config examples/gencp/ntcouple_sit_fno/config.yaml \
  --set data.root=/data/raw --set paths.output=/experiment/dojo --set run_root=/experiment/dojo/runs
uv run python tools/verification/gencp/budget.py --ledger /experiment/budget.json -- \
  uv run python tools/verification/gencp/compare.py --root /experiment --dataset ntcouple \
  --backbone sit_fno --run /experiment/dojo/runs/EXACT_RUN_ID
uv run python tools/verification/gencp/budget.py --ledger /experiment/budget.json -- \
  uv run python -m tools.verification.gencp.learning --root /experiment --source /source/GenCP \
  --dataset ntcouple --backbone sit_fno
DOJO_GENCP_ACCEPTANCE=1 uv run pytest tests/integration/test_gencp_acceptance.py
```

参考源码导入问题的处理、论文目标与原实现协议差异集中在 `.context/mvp/gencp-acceptance.md`。实验目录 reference/dojo 包含权重、原始预测、真值及图；comparison.json、learning.json、budget.json 分别给工程一致性、学习效果与累计用时。最终报告不能把这三项合成“论文已复现”。
