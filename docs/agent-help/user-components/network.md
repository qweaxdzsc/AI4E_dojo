<!-- dojo-help: {"domain": "components", "kind": "how-to", "layer": "user-component", "summary": "替换网络构造器，同时保持字段、形状、设备和检查点合同。", "tasks": ["编写用户组件", "组件调用证明"], "title": "编写和替换网络", "topic_id": "user-component:network"} -->
# 编写和替换网络

网络可以是普通 `torch.nn.Module`，不需要继承 Dojo 基类。阶段脚本从配置解析全限定构造器，application 只接收已经构造或可构造的组件。

替换前核对输入/输出形状、字段顺序、坐标和物理量状态。结构变化后旧检查点通常不可恢复；必须先做前向、一次更新、保存、读回和推理。

## 先选接入方式

- 整体替换：实现案例模型组件要求的 `construct`/`build`、`describe`、`step` 或 `predictions`，并在 `components.model` 指向新模块。
- 局部替换：先调用基模型构造器，再替换某个公开子模块。`recipe_extensions.model_block` 展示 AB-UPT 激活替换。
- 网络工厂：在支持 `components.network` 的案例中提供普通构造函数。`recipe_extensions.wdno` 展示这一方式。

不要根据名字猜接口。先查询模型组件和构造器：

```python
import ai4e_task as task

for hit in task.search_help("construct model component", layer="contrib.ability", limit=10):
    print(hit["topic_id"], hit["case_ids"])
```

## 局部替换实例

下面的结构与 `recipe_extensions.model_block` 一致：复用已验证的 AB-UPT 组件，只把物理块 MLP 激活替换为 SiLU。

```python
# variants.py，放在物化后的 standalone 根目录
import hashlib
from pathlib import Path

from torch import nn
from ai4e_contrib.ability.model.abupt import component as base
from ai4e_contrib.ability.model.abupt.model import construct as original

SOURCE = base.SOURCE + ":silu:" + hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def __getattr__(name):
    return getattr(base, name)


def construct(**parameters):
    model = original(**parameters)
    for block in model.blocks:
        block.mlp.act = nn.SiLU()
    return model


def describe(model):
    return {**base.describe(model), "variant": SOURCE}


construct.describe = describe
```

在复制目录的配置中连接：

```yaml
components:
  model: variants
```

`__getattr__` 只把未修改的公开模型能力委托给原组件；它不是全仓注册机制。若领域 application 要求的函数没有被提供，加载或执行应明确失败。

## 运行与验证

1. 用新目录重新执行需要模型声明的准备阶段。
2. 用同一固定样本比较基线与变体前向；形状必须相同，数值应按研究预期改变。
3. 执行至少一次优化更新，核对目标参数发生变化。
4. 在运行快照或阶段报告中读回 `SOURCE`/`describe` 身份。
5. 保存新检查点并用新组件完成独立 infer；不要复用旧推理缓存。
6. 对结构或来源不一致的旧检查点，保留拒绝恢复的错误证据。

应读回的证据包括 `inputs/config.yaml` 中的组件路径、源码快照或来源摘要、模型描述、检查点 contract、训练更新数、预测清单和 post 指标。相同参数名或相同输出形状不能证明两个网络科学等价。

## 检查点边界

新增、删除或重排参数通常使严格权重恢复失败。即使参数形状不变，激活、注意力、归一化或前向连接变化也改变算法身份；默认从头训练。若研究只做权重初始化，必须把“只加载权重”与包含优化器、调度器、EMA、更新步和 RNG 的完整恢复分开记录。


## 可选 FLARE++ 注意力组件

FLARE++ 是网络内部可选的注意力计算，不是输入预处理或训练框架。公开组件只用普通 Torch，不导入 PhysicsNeMo 或 contrib。用户按需组合；它不自动替换 GALE 或其他已有模型。

```python
import torch
from ai4e_core.abilities.modeling.modules.flare_attention import FLAREPlusPlus

attention = FLAREPlusPlus(dim=32, heads=4, dim_head=8, n_global_queries=8)
x = torch.randn(2, 17, 32)  # 批次、token、特征
y = attention(x)            # 同形输出；可接用户的残差、MLP 或预测头
y.square().mean().backward()
```

`dim`、`heads`、`dim_head`、`n_global_queries` 必须为正整数；内部总宽度允许与 `dim` 不同。`attn_scale=None` 使用每头宽度的平方根倒数，显式值须正且有限；`dropout` 是输出投影后的概率，`eval()` 时关闭。接口详见 [FLARE++ API](../api/core/abilities/modeling/modules/flare_attention.md)。

仅接受普通 `(B, N, dim)` 浮点张量且 `N>0`。不同调用可以改变 `N`，但没有 padding/causal mask；不支持 token 分片或 Transformer Engine。只有组件可用，不表示 GeoTransolver 已开放 `GALE_FPP`，也不表示平台新增模型选择。模型级的上下文、checkpoint 身份及数据适配由用户的局部连接承担。
