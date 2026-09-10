# 参考输入夹具

reference.pt 由 tools/generate_abupt_inputs.py 执行锁定 Noether 的真实归一化处理器与原样提取的 AeroABUPT.forward 产生，在骨干调用边界捕获输入。使用固定显式下标，不比较两框架随机数算法。source.json 保存版本、文件摘要、夹具摘要和生成命令。正式模型测试不依赖外部仓库；重新生成需要参考仓库环境。此夹具验证输入，不验证 Noether 模型输出。

`normalization.json` 由锁定 Noether 实际 MeanStdNormalization/PositionNormalizer 生成，含源码 SHA256。`test_reference_arithmetic.py` 精确检查 FP32 正反变换，并保留旧记录版本 1 的语义。
