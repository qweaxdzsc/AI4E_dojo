<!-- dojo-help: {"domain": "components", "kind": "how-to", "layer": "user-component", "summary": "用配置、身份、阶段报告、状态变化和结果形成证据链。", "tasks": ["编写用户组件", "组件调用证明"], "title": "证明组件真实调用", "topic_id": "user-component:proof"} -->
# 证明组件真实调用

至少同时检查：最终配置中的组件路径和参数；阶段报告中的规范身份；调用次数或更新状态；检查点结构或步数；本次预测、指标和 post 清单；恢复时的检查点来源。

只打印类名、import 成功、命令返回 0 或目录存在都不足以证明研究组件参与了计算。

## 四层证据

### 1. 选择证据

读取 `run_dir/inputs/config.yaml`，确认最终生效的全限定路径、参数、数据输入、设备、随机种子和预算。源 `config.yaml` 不能代替最终配置，因为默认值和 `--set` 可能改变结果。

### 2. 调用证据

阶段报告记录规范组件身份、源码摘要、调用次数或实际样本/更新数。对纯函数可在测试中包装计数器；正式运行应由 application 在真实调用点报告来源，不能只在加载时打印名称。

```python
calls = {"count": 0}


def traced(operation):
    def wrapped(*args, **kwargs):
        calls["count"] += 1
        return operation(*args, **kwargs)
    return wrapped
```

计数器只适合测试进程；跨进程正式证据应写入阶段报告或固定产物，不依赖内存变量。

### 3. 状态与结果证据

训练组件需要证明参数、optimizer step、调度器或 EMA 状态按预期变化；推理组件需要证明固定 checkpoint 产生了当前预测；post 需要证明指标和图表依赖当前结果清单。资产与指标索引必须绑定内容摘要和数据身份。

### 4. 对照证据

保持数据、初始化、预算和评价协议不变，只改变目标组件。比较基线与变体的前向、梯度、状态、预测和指标。若同时改变多个因素，应建立独立分支并明确哪些结论不可归因到单个组件。

## 建议读回脚本

```python
import json
from pathlib import Path

run_dir = Path("/absolute/run")
config = (run_dir / "inputs/config.yaml").read_text(encoding="utf-8")
summary = json.loads((run_dir / "summary.json").read_text())
assets = json.loads((run_dir / "artifacts/assets.json").read_text())

assert summary["failed"] is False
assert summary["research_status"] == "completed"
print(config)
print(summary["reports"])
print(assets["items"])
```

实际文件是否存在以所选阶段为准；例如只运行 train 时不应强求 infer 结果。

## 恢复证据

记录来源运行 ID、checkpoint 路径和摘要、恢复前 epoch/update、恢复后目标、固定 preparation 身份和训练合同。连续执行与恢复执行应在声明容差内一致。完整恢复失败时保留原错误；不要删掉 optimizer/contract 后改称成功恢复。

## 结论等级

- 工程接线：入口、参数、组件调用、保存和读回正确。
- 状态/预测一致性：连续与恢复或两种入口在固定输入上对齐。
- 学习效果：预先声明的指标随训练或变体发生有意义变化。
- 论文级精度：数据、协议、预算、指标、重复实验和参考结果均对齐。

smoke 通常只支持第一层，必要时可支持小规模恢复一致性；不能从短训直接得出后两层结论。
