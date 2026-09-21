# JOREK RMHD 双组实验工具

这是主控工具，不是交给实验 Agent 的训练模板。Neumann 旧入口与结果保持原样。

顺序为 `prepare → preflight → materials → probe → run → evaluate → summarize`。所有命令使用：

```bash
uv run --no-sync python -m tools.verification.dojo_validity.rmhd <命令> --comparison <主控比较目录>
```

`prepare` 改用 `--base <dojo_train> --data-root <原始JOREK目录>`，返回独立比较目录。preflight只消费训练/验证，固定500epoch；失败不启动正式组。materials只交网络、初始化、协议、原始分片和通用安装材料，组内环境和派生数据仍由Agent实际创建。

probe验证实际组工作根、独立临时MPS诊断环境及公网代理；诊断环境随后删除。还必须保存 `evidence/worker-check.json` 与 `evidence/cli-capability.json` 的实际通过证据，验证冻结预测、无真值/断网边界、CLI工具/原session续接及请求usage。不能手写passed绕过验收。

run为单组创建新CLI并串行调度双方round00和五轮，组内保留session。失败继续原session，开发验证可反馈，隐藏评价不能进入run。两组最终选择锁定后，evaluate独立复制环境，以只读冻结提交、当前历史输入和无网络worker预测，主控FP64复算。summarize只写比较目录。

统一提交接口、抽样序列摘要和baseline证据要求由materials交付的SUBMISSION.md定义。逐组第一条提示仅增加Dojo组的GUIDE入口。Dojo使用可选，学习计编码成本。

Seatbelt仅允许明确系统运行时、组根或冻结候选；系统GPU驱动是只读前提。公网经每次CLI专用代理，拒绝本机/内网/保留地址；VPN合成DNS地址通过固定公共HTTPS DNS解析为核过的公网数值IP。TLS内容不检查，不能把域名记录当作无污染证明。

隐藏推理采用父进程计时和固定数值数组交换，50ms包含同口径通信拷贝开销。加载与归档另计。共享数组不包含未来真值，评分器不import候选。候选跨请求缓存预测、查表或干预计时属于协议违规。

圈定测试：`uv run --no-sync pytest tests/integration/test_dojo_validity_rmhd.py tests/integration/test_dojo_validity.py tests/integration/test_dojo_validity_cli.py`。工具验收、预实验和正式五轮须分开陈述。

每次CLI新建/续接的权限取自主控比较配置，并核验组内protocol初始摘要。组内改写路径不能增加授权。评价时钟与窗口起点分开保存；保持最后帧及逐场改善只作诊断，主指标不变。
