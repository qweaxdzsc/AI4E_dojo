# 可组合经典网络验收（2026-09-22）

本轮按用户已批准的主/A/B/C计划实施；设计唯一正文为 `docs/AI4E_Dojo_ARCHITECTURE (1).md` 第5.2节。用户明确先并行集成、再统一串行训练。工作区含其他任务修改，未回滚或改写其记录。本轮约定的经典网络结构、十三组合短训、三个重组、外复制和安装Task范围已完成；不扩展为论文或生产精度结论。

## 架构归并结果

- A组交付共享FeedForward、循环块/循环段、MLP/RNN；C组的标准FFN和图编码/更新直接复用同一FeedForward，后者复用已有ProjectedMlp，旧Mlp保持原权重键和默认数学。
- B组交付卷积、基本/瓶颈残差、空间缩放、跳连融合；卷积段、多尺度编码和跳连解码真实组装CNN、ResNet、U-Net。二维/三维显式选择，不将单个torch算子机械包装成新的全仓协议。
- C组交付标准注意力、Transformer块、patch编解码、图编码与消息更新；TransformerEncoder和GraphProcessor组装完整PatchTransformer/GraphNetwork。模块不反向依赖完整模型，网络阶段不是run.Stage。
- 完整网络均在core；contrib/classic_networks只管理数据字段、布局、配置、物理身份和业务交接。recipe明示准备/训练/推理/post，Dojo侧调用现有IterationStream和共享train_model；独立参考循环只在验证工具中存在。
- 三个用户重组为ResUNet、注意力瓶颈U-Net、CNN-RNN，使用公开组件与替换点；没有引入新注册中心、统一Tensor协议或第二套运行器。
- 泛化修正：图边复用已有induced_subgraph与sender-minus-receiver边特征；循环状态显式传入返回，不跨窗口暗存；patch补齐mask与物理有效域分开；回贴仅接受八顶点均有效的单元；准备包含可搬移物理快照，post只读固定结果。

## 数据与数值范围

- Darcy：smooth1前32训练、smooth2前8测试，421²按步长5到85²，输入xy与系数、目标解；统计仅拟合训练。
- ShapeNet-Car：官方名单排序8/2，体速度插值到各例32³包围盒；输入xyz、原体顶点无符号面距离的线性插值近似、valid。保留PT/VTKHDF与原实体；固定结果包含原点回贴预测、真值、身份、有效mask、样本offset及覆盖率。仅有效支撑区域计误差，不宣称原网格全点有效。
- Double Cylinder：两训练轨迹、一验证轨迹，128²；三历史帧到下一采样帧，66/8窗口。RNN训练每窗口1024点，推理全部窗口全部点；CNN-RNN重组按真实时间编码完整空间。
- 十三组是MLP/CNN/ResNet/U-Net/GNN/Transformer各自Darcy与ShapeNet，加RNN双圆柱。seed42、Adam0.001、batch1，100/50/20更新按实测预算选择；每组累计180分钟，含准备分摊、失败、参考、恢复、推理、重组与安装计算。
- GNN是显式残差MPNN变体（先聚合残差更新后的边），不等价于DeepMind原实现的先聚合增量。ResNet是小stem/场回归头变体，U-Net是same-padding插值解码回归变体。来源、版本、许可与区别在 `tools/verification/classic_networks/sources.json`。
- 位置编码保持既有FP32计算，double缓冲在计算处转回坐标dtype；不声明FP64位置精度。没有论文精度改善门槛，误差如实报告。

## 证据入口与最终结果

统一实验根 `/Users/zonghui/work/project_simulation/dojo_train/classic_networks/`：`evidence/preparation.json`为真实来源及准备身份，`evidence/matrix.json`为逐组合结果，`budget/`为持久累计账本，`matrix/`保留全部成功和失败尝试。

十三组合均完成100次更新，使用固定初值/批次独立参考及20→100更新恢复。模型状态、完整测试集物理预测和恢复权重最大差均为0；恢复另检查优化器矩、采样次序/游标、全部随机流、合同、历史和其他可恢复状态，只有运行路径元数据effective_config不作等值要求。完整结果及最终累计预算见 `evidence/final-matrix.json`，原始尝试及失败保持。

- MLP、CNN、GNN、Transformer的Darcy/ShapeNet，以及ResNet/U-Net的Darcy和RNN双圆柱：MPS FP32。
- ResNet/U-Net的ShapeNet：CPU FP32严格对照，原因见下方设备诊断；MPS此前真实训练完成但严格参考对照失败，不计该设备通过。
- ShapeNet每个模型两测试样本原点回贴覆盖分别为69.07%/69.24%；该范围内计算分量误差，不宣称全部原点有效。
- 来源距离输入是线性插值近似，标准注意力不是几何注意力，RNN是逐点时间基线。总体relative_l2仅作本案例诊断，尤其混合物理单位时不作为跨模型/跨数据集公平指标；正式记录提供逐字段MSE和单位。

六个安装案例均实际从spec/core/contrib/task wheel物化，先Python 1更新→恢复到2更新→完整infer/post，再Task独立进程1更新→完整infer/post。三个扩展为ResUNet、注意力瓶颈U-Net、CNN-RNN，均有真实更新、严格权重读回及新增预测模长保存/消费。六例准备、权重、固定结果均复制到新目录，摘要一致；独立post仅保留固定结果输入，禁用准备/权重/源输入，报告和指标语义不变。数据层另有原路径隐藏后的解析回贴验证。见 `evidence/installed.json` 和各报告 `relocations`、worker PID与模块位置。

独立安装目录为实验根 `installed/`，33个相关core/contrib计算源码与安装字节一致；六项最终安装资源检查通过，wheel摘要见 `evidence/installed-resources-final.json`。最终README内部导航修正只改变说明，重新生成Help并更新独立task wheel；此前实跑计算源码未变，不重复训练。

累计账本包括准备分摊、测速、参考、Dojo、完整推理/post、恢复、失败/诊断、安装重放及最终测试/构建分摊；最慢组合ResNet-ShapeNet约58秒，全部远低于180分钟。计算阶段计时不同于包括分析/编辑/等待的整次开发会话时长。没有sync主环境或操作8000/5173；交付为源码与独立wheel，用户正式环境未重装，本批无Web新入口。

圈定274个用例：首次271通过、3个资源文档门禁失败；修正可安装README的内部导航后，18项受影响资源/Help用例复跑全通过，原3项均闭合。零skip。包含旧MeshGraphNet/PCNO/GeoTransolver、固定用户源码基线及实际wheel检查；未改基线摘要。全部相关源码Ruff通过；Agent Help生成一致性通过。日志为 `evidence/pytest-final.log`、`evidence/pytest-doc-final.log`。三维MPS padding的View Ops性能提示保留，不是未记录的CPU计算回退。

设备诊断：ResNet三维在MPS上的同模型重复前向逐值相等，但重复反向最大差7.81e-6，独立参考梯度最大差8.05e-6；CPU两项均为0。证据 `evidence/resnet3d-diagnostic.json`。故该组正式严格数值对照显式切换CPU，保留MPS失败与累计预算，不宣称MPS连续/恢复逐值一致，不放宽容差。

U-Net三维同样在MPS长轨迹对照超出固定容差；最小重复梯度差4.66e-10，CPU重复及独立参考均0（evidence/unet3d-diagnostic.json）。该组明确改CPU并通过100更新全验证。其余GNN两组MPS的权重、完整恢复与完整test参考预测均通过。


Transformer参考补充：最初显式公式长FP32轨迹存在不同投影/SDPA算术次序，且参考ReLU错误使用clamp_min导致零点子梯度不符。修正参考ReLU并保留显式QK-softmax-V小输入前后向检查；长轨迹新增直接映射权重到原生PyTorch运算的独立参考，明确CPU eval fastpath与MPS functional路径，不调用core forward。两组最终100更新及完整预测/恢复均通过，容差未改变。证据 `acceptance/native-attention-oracle.json`；参考不是完整上游项目复现。

来源范围、布局边界与可替换点分别落实在唯一架构5.2、core abilities PRD第十一章、contrib application PRD第八章与classic recipes PRD；集成技能保留三个部分并要求实际组合证据。三个子Agent及主计划已标记实施续接，经验日志记录已证实错误与候选流程。新增能力无额外Python依赖，不引入整套外部模型库或第二套训练框架。
