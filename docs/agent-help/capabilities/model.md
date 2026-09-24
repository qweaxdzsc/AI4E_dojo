<!-- dojo-help: {"topic_id": "capability:model", "title": "网络与模型组件", "kind": "tutorial", "layer": "capability", "domain": "model", "summary": "经典网络、DeepONet/FNO 与传统代理模型；按 block、可复用阶段和完整架构组合", "tasks": ["已有 PyTorch 模型", "网络构造", "模型组件", "MLP", "CNN", "ResNet", "U-Net", "Transformer", "GNN", "RNN", "DeepONet", "FNO", "POD", "RSM", "RBF", "Kriging", "LightGBM"], "symbols": ["ai4e_core.abilities.modeling.construction.construct", "ai4e_core.abilities.training.diagnostics.parameter_count", "ai4e_core.abilities.modeling.models.mlp.MLP", "ai4e_core.abilities.modeling.models.cnn.CNN", "ai4e_core.abilities.modeling.models.resnet.ResNet", "ai4e_core.abilities.modeling.models.unet.UNet", "ai4e_core.abilities.modeling.models.transformer.PatchTransformer", "ai4e_core.abilities.modeling.models.gnn.GraphNetwork", "ai4e_core.abilities.modeling.models.rnn.RNN", "ai4e_core.abilities.modeling.models.deeponet.DeepONet", "ai4e_core.abilities.modeling.models.fno.FNO", "ai4e_core.abilities.modeling.models.pod.POD", "ai4e_core.abilities.modeling.models.rsm.ResponseSurface", "ai4e_core.abilities.modeling.models.rbf.RBFInterpolator", "ai4e_core.abilities.modeling.models.kriging.Kriging", "ai4e_core.abilities.modeling.models.lightgbm.LightGBMPredictor", "ai4e_core.abilities.modeling.modules.feed_forward.FeedForward", "ai4e_core.abilities.modeling.modules.convolution.ConvBlock", "ai4e_core.abilities.modeling.modules.residual.BasicResidualBlock", "ai4e_core.abilities.modeling.modules.attention.SelfAttention", "ai4e_core.abilities.modeling.modules.graph_message_passing.GraphInteraction", "ai4e_core.abilities.modeling.modules.recurrent.RecurrentBlock", "ai4e_core.abilities.modeling.modules.branch_trunk.BranchTrunkReadout", "ai4e_core.abilities.modeling.modules.spectral.SpectralConv", "ai4e_core.abilities.modeling.modules.spectral.FourierBlock", "ai4e_core.abilities.modeling.modules.reduced_basis.ReducedBasis", "ai4e_core.abilities.modeling.modules.reduced_basis.FrozenBasisDecoder", "ai4e_core.abilities.modeling.modules.polynomial.PolynomialBasis", "ai4e_core.abilities.modeling.modules.radial.RadialBasis", "ai4e_core.abilities.modeling.modules.covariance.SquaredExponential", "ai4e_core.abilities.modeling.modules.covariance.KrigingCondition", "ai4e_core.abilities.modeling.stages.convolution.ConvStage", "ai4e_core.abilities.modeling.stages.convolution.ResidualStage", "ai4e_core.abilities.modeling.stages.multiscale.MultiScaleEncoder", "ai4e_core.abilities.modeling.stages.multiscale.SkipDecoder", "ai4e_core.abilities.modeling.stages.transformer.TransformerEncoder", "ai4e_core.abilities.modeling.stages.graph.GraphProcessor", "ai4e_core.abilities.modeling.stages.recurrent.RecurrentStage", "ai4e_core.abilities.modeling.stages.fourier.FourierStage"], "navigation_order": 3} -->
# 网络与模型组件

已有 torch.nn.Module 可直接交给神经网络训练入口；普通代理对象使用各自拟合和预测 API，无须继承 Dojo 基类。construct 调用普通构造器并返回模型与独立的参数副本；内部注意力、图消息传递、编码器等按 modeling API 选择。

这里不提供万能模型协议：前向参数、轴、输出和重建参数仍由研究代码声明。模型结构变更要重新检查 checkpoint 兼容性；内置模块的许可与适用范围要分别核对。

## 按组合尺度选择公开能力

计算 block、可复用阶段、完整架构都属于 core modeling 的组合尺度。这里说明使用入口；网络阶段不等于 run 的执行阶段，普通组件按自己的输入输出连接，无须统一基类或组件协议。完整模型真实复用公开组件；需要局部变化时先选择替换点，再检查轴、状态、梯度和保存读回。

以下链接进入对应模块的 API，包含构造器和公开方法签名；全限定前缀是 `ai4e_core.abilities.modeling`。

- **MLP / RNN**：[FeedForward](../api/core/abilities/modeling/modules/feed_forward.md) → [MLP](../api/core/abilities/modeling/models/mlp.md)；[RecurrentBlock](../api/core/abilities/modeling/modules/recurrent.md) → [RecurrentStage](../api/core/abilities/modeling/stages/recurrent.md) → [RNN](../api/core/abilities/modeling/models/rnn.md)。MLP 保留前导维度；RNN 消费 `[B,T,C]`，返回序列和末状态，同一序列续段才显式回传状态。
- **CNN / ResNet / U-Net**：[ConvBlock](../api/core/abilities/modeling/modules/convolution.md)、[残差块](../api/core/abilities/modeling/modules/residual.md)、[空间重采样](../api/core/abilities/modeling/modules/spatial_resampling.md)、[SkipFusion](../api/core/abilities/modeling/modules/skip_fusion.md) → [ConvStage / ResidualStage](../api/core/abilities/modeling/stages/convolution.md)、[MultiScaleEncoder / SkipDecoder](../api/core/abilities/modeling/stages/multiscale.md) → [CNN](../api/core/abilities/modeling/models/cnn.md)、[ResNet](../api/core/abilities/modeling/models/resnet.md)、[UNet](../api/core/abilities/modeling/models/unet.md)。采用通道在前的二维/三维网格；替换时核对各尺度分辨率和跳连通道。
- **Transformer / GNN**：[注意力](../api/core/abilities/modeling/modules/attention.md)、[Transformer block](../api/core/abilities/modeling/modules/transformer.md)、[PatchEmbedding](../api/core/abilities/modeling/modules/patch_embedding.md)、[PatchReconstruction](../api/core/abilities/modeling/modules/patch_reconstruction.md) → [TransformerEncoder](../api/core/abilities/modeling/stages/transformer.md) → [PatchTransformer](../api/core/abilities/modeling/models/transformer.md)；[图编码与读出](../api/core/abilities/modeling/modules/graph_encoding.md)、[GraphInteraction](../api/core/abilities/modeling/modules/graph_message_passing.md) → [GraphProcessor](../api/core/abilities/modeling/stages/graph.md) → [GraphNetwork](../api/core/abilities/modeling/models/gnn.md)。patch/token、网格和节点表示需显式转换；图边、mask 与实体顺序由调用方交接。
- **DeepONet**：[FeedForward](../api/core/abilities/modeling/modules/feed_forward.md) 与 [BranchTrunkReadout](../api/core/abilities/modeling/modules/branch_trunk.md) → [DeepONet](../api/core/abilities/modeling/models/deeponet.md)。可替换 branch/trunk/readout；固定传感器特征顺序，输入 `[B,F]`，查询为 shared `[Q,D]` 或 per_sample `[B,Q,D]`，输出 `[B,Q,O]`。多输出显式选择 split_branch/split_trunk/split_both。
- **FNO**：[SpectralConv / FourierBlock](../api/core/abilities/modeling/modules/spectral.md) → [FourierStage](../api/core/abilities/modeling/stages/fourier.md) → [FNO](../api/core/abilities/modeling/models/fno.md)。可替换 lifting/operator/projection；模型输入通道在前，lifting/projection 局部消费末轴通道，operator 消费通道在前张量。modes 与 padding 逐空间轴声明；padding 不是物理边界。全局谱运算保留完整空间域，不能切局部网格冒充完整预测。
- **POD**：[ReducedBasis / FrozenBasisDecoder](../api/core/abilities/modeling/modules/reduced_basis.md) → [POD](../api/core/abilities/modeling/models/pod.md)。POD 提供编码、解码、重建和状态，需连接系数预测器才能预测新工况；`torch_decoder` 冻结基但保留系数梯度。
- **RSM / RBF / Kriging**：[PolynomialBasis](../api/core/abilities/modeling/modules/polynomial.md)、[RadialBasis](../api/core/abilities/modeling/modules/radial.md)、[SquaredExponential / KrigingCondition](../api/core/abilities/modeling/modules/covariance.md) → [ResponseSurface](../api/core/abilities/modeling/models/rsm.md)、[RBFInterpolator](../api/core/abilities/modeling/models/rbf.md)、[Kriging](../api/core/abilities/modeling/models/kriging.md)。普通对象消费 `[N,d]`，预测与拟合分开；Kriging 均值/方差、潜在场/观测噪声含义显式选择。不强造没有独立复用意义的中间阶段。
- **LightGBM**：[LightGBMPredictor](../api/core/abilities/modeling/models/lightgbm.md) 复用官方可选后端，每目标独立 Booster；保留特征顺序与原生树文本，不拆出另一套树训练内核。

## 从完整案例继续组合

经典网络从 `classic_networks.darcy`、`classic_networks.shapenet_volume`、`classic_networks.double_cylinder` 定位；重组见 `recipe_extensions.network_composition` 系列。算子网络从 `operator_learning.darcy`、`operator_learning.double_cylinder`、`operator_learning.shapenet_volume` 定位；传统代理从 `surrogate_modeling.nasa_crm`、`surrogate_modeling.double_cylinder` 定位。

用 `list_examples(query="network_composition")` 查真实案例 ID，`read_help_topic("case:<id>")` 读正文，再 `copy_example` 复制；DeepONet 分支替换、物理损失和 POD 系数预测器替换分别见 `recipe_extensions.operator_branch_replacement`、`recipe_extensions.operator_physical_loss`、`recipe_extensions.pod_surrogate_replacement`。这些案例提供短预算工程证据，不代表论文或生产精度。

普通对象的拟合、批次预测和保存分别继续阅读[训练](training.md)、[推理](inference.md)、[数据与状态](data.md)；物理目标独立见[损失与约束](loss.md)。

## 直接入口

- `ai4e_core.abilities.modeling.construction.construct`
- `ai4e_core.abilities.training.diagnostics.parameter_count`

使用 `ai4e_task.describe_help_symbol` 核对当前安装版本的签名和源码；这里的例子验证调用，不代表生产精度。

## 可执行小例子

将代码保存到独立研究目录的 `source/demo.py`，从研究目录启动；不同例子用不同工作目录。

```python
import torch
from ai4e_core.abilities.modeling.construction import construct
from ai4e_core.abilities.training.diagnostics import parameter_count

options = {"in_features": 3, "out_features": 2}
model, resolved = construct(torch.nn.Linear, options)
assert model(torch.ones(4, 3)).shape == (4, 2)
assert parameter_count(model) == 8
resolved["out_features"] = 9
assert options["out_features"] == 2

# 完整 MLP 可用作另一架构的 branch，公开前馈块也可独立调用。
from ai4e_core.abilities.modeling.modules.feed_forward import FeedForward
from ai4e_core.abilities.modeling.models.mlp import MLP
from ai4e_core.abilities.modeling.models.deeponet import DeepONet
from ai4e_core.abilities.modeling.models.fno import FNO

block = FeedForward(3, 8, (4,))
branch = MLP(3, 8, feed_forward=block)
operator = DeepONet(3, 2, 8, branch=branch)
values = operator(torch.ones(2, 3), torch.ones(5, 2))
assert values.shape == (2, 5, 1)
values.square().mean().backward()
assert all(p.grad is not None for p in block.parameters())
fno = FNO(1, 1, modes=(2, 2), width=4, depth=1)
assert fno(torch.ones(2, 1, 8, 8)).shape == (2, 1, 8, 8)
```

## 继续阅读

[接入细节](../user-components/network.md) · [帮助首页](../index.md)
