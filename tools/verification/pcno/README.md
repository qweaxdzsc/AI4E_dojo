# PCNO 参考与数值对照

当前已完成代码集成及短预算对照，范围和剩余回归问题见[验收记录](../../../.context/mvp/pcno-acceptance.md)。用户已停止250轮长训练；本目录保留历史工具，不自动启动或续接长训练。

原源码为 Code Ocean capsule 8000337 v1.0，commit `dc4cd4417ed7f97715ffb47496690ce60f7665a3`，GPL-3.0。源文件只读；core与contrib保留许可证及来源摘要。`vendor.py`是一次性拆分工具，会覆盖已提取模块，不能把重复提取当成正常运行入口。

## 当前快速对照

使用同一隔离环境运行原版和实际Dojo wheel。保留完整80×80×5×21网格、模式1、宽度8、作者统计量和250轮学习率/损失日程，以更新次数缩小验证范围。每分支独立seed7；训练前按两侧、两个分支及评价/保存合计估算预算。

```bash
uv run --no-sync --python <隔离解释器> -m tools.verification.pcno.short_reference \
  --source <原源码目录> --data <发布数据目录> \
  --output <新的参考输出目录> --branch temp --updates 21 --stable-vis
```

温度原源码在第6次更新出现NaN梯度；`--stable-vis`明确启用未激活黏度分支的安全输入修正。活跃公式和前向不改；修正版必须与未经修正的失败基线分开记录。压力原版当前一轮数值与同修正Dojo一致。`diagnose_temperature.py`仅观察原函数并捕获首次非法梯度。

- `compare_short.py`：固定rtol=1e-5/atol=1e-6比较模型、优化器、调度、随机流、顺序与损失，不允许NaN当通过。
- `check_initial_gradient.py`：全分辨率首步各项损失、裁剪前梯度与冻结参考对照。
- `check_predictions.py`：读取固定预测，用原模块同权重核对每组首末例的双场、物理残差和井级量，明确只覆盖所选案例。
- `recovery.py`：公开run入口执行真实中断并恢复，固定2次更新目标，以逐值一致比较两个分支。
- `data_audit.py`、`economy.py`：数据身份与作者既有预测经济回放。

24例轮换验证和回算不是独立测试。18例发布场等于作者预存预测，不可报告独立精度。短训成功只证明工程连接和对照，不表示收敛、生产预测或9450例论文复现。未成熟预测的经济公式可能出现未定义值，保留来源行为并单独报告。

## 保留的历史工具

`reference.py`、`verify_first_step.py`、`predict.py`、`finish_reference.py`保留原250轮方案及冻结检查点格式。`predict.py`仍拒绝未完成250轮的“最终基线”，不能用短训冒充原目标完成。`finish_reference.py`当前没有运行；再次启动须重新约定长训练范围。历史普通作者检查点缺少RNG和游标，仅支持明确权重导入。
