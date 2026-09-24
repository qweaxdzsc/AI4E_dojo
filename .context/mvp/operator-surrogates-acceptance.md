# 算子与传统代理集成验收（2026-09-22）

三组并行实现后由主控归并，再完成11个基础组合串行真实训练/拟合及独立参考对照、两个Darcy物理开关分支、八个独立wheel/Python/Task案例。约定工程集成范围已通过；论文复现、生产精度和新增Web模型不在本次结论内。

## 范围与依据

DeepONet、FNO、POD、RSM、RBF、Kriging、LightGBM遵循唯一架构第5.2节。POD是表示，预测由系数代理与解码组合；LightGBM使用可选官方4.6.0引擎。物理能力复用既有constraint，不新增PINN。来源/变体/许可见`tools/verification/operator_surrogates/sources.json`；11组合按计划串行，独立参考和Dojo均为工程短预算，不宣称论文或生产精度。

实验根：`/Users/zonghui/work/project_simulation/dojo_train/operator_surrogates/`。失败、重试、准备、参考、扩展及安装共同记入`budget/budget.json`，每组合累计上限10800秒；计时队列建立前的共享开发检查按每组合60秒保守占额，此占额不是实测总计算。历史经典准备只读复用，不改写原数据。正式8000/5173及主环境未更新，无新增Web模型消费链。

## 已核数据与科学边界

- NASA官方105/44工况，六输入Mach/AlphaMean/aileronInboard/aileronOutboard/htp/elevator，三响应c_d/c_l/c_my；完整二次设计秩28。仅全局属性表，不冒充平台网格准备。统计仅训练拟合，跨文件同属性或完全重复行拒绝。
- DoubleCylinder两训练轨迹与独立验证轨迹，128²、三历史到下一采样帧，66/8窗口。POD按轨迹/时间去重训练快照拟合一次，历史和目标使用同一目标尺度；两种代理共享基底。POD误差底限与最终代理误差分开。
- Darcy32/8、85²；原论文正扩散系数3/12、源项f=1、真实边界u=0。样本外圈最大目标绝对值约0.000379663，不能当作精确零边界。因此本批约束为最大值原理的非负解违约，保持可微反归一化，不宣称完整PDE残差。来源证据`evidence/darcy-constraint-source.json`。
- ShapeNet8/2、32³；传感器固定参考格索引，各车映射到自身物理包围盒，输入含物理坐标与有效域，不假定固定共同物理传感器。完整预测、原实体回贴和覆盖率按固定结果记录。

## 组件与真实执行状态

A锁定上游算术参考与独立FP64 DFT，CPU/MPS通过，CUDA缺环境跳过；DeepXDE策略/读出及NeuralOperator谱前向以独立harness执行，未运行完整上游训练工程。B代数24项、应用14项通过；C固定统计17项及NASA身份3项通过。主控普通批预测/安全保存/物理目标检查通过；后续最终相关集合以最新实跑记录更新。

最终圈定集合 **209 passed、1 skipped**；唯一跳过为CUDA不可用。包括新能力/配置/真实证据门禁、旧经典网络必要回归和固定用户源码的真实wheel基线，未修改基线摘要。新增/修改范围Ruff通过，572份生成Help检查通过；最后资源元数据和公开导出排序变动后，21项资源/文档检查及最终安装资源复制再次通过。最终JUnit为`evidence/final-tests.xml`；早期因测试临时目录父目录缺失的fixture错误保留在`final-tests-attempt1.xml`，修正执行目录后全组通过。

## 统一矩阵与结果

五个神经组合均为CPU FP32、100有效更新，真实batch轨迹、损失、最终权重、完整测试预测在固定容差rtol=1e-5/atol=1e-6内与独立参考一致。DeepONet修正后不放宽原门槛。代数/统计使用FP64；Kriging两侧采用各自实现的解析profile-ML梯度，NASA三个目标16/16/20步、POD两个目标43/29步明确收敛；初始4步结果保留但不充当收敛证据。LightGBM12轮并核原生状态追加2轮与不中断14轮逐值一致。

| 组合 | 参考/Dojo/完整预测耗时（秒） | 测试误差口径与结果 |
| --- | ---: | --- |
| rsm-nasa | 3.45 | 逐字段整体relative L2：c_d=0.1791, c_l=0.0464, c_my=0.0603 |
| rbf-nasa | 0.09 | 逐字段整体relative L2：c_d=0.1306, c_l=0.0456, c_my=0.0522 |
| kriging-nasa | 0.32 | 逐字段整体relative L2：c_d=0.0414, c_l=0.0293, c_my=0.0321 |
| lightgbm-nasa | 0.28 | 逐字段整体relative L2：c_d=0.2276, c_l=0.2449, c_my=0.5475 |
| pod-rbf-double | 1.22 | 逐字段整体relative L2：velocity_x=0.1645, velocity_y=0.7462, pressure=0.3732, sdf=0.0221 |
| pod-kriging-double | 1.15 | 逐字段整体relative L2：velocity_x=0.1653, velocity_y=0.7467, pressure=0.3725, sdf=0.0213 |
| deeponet-darcy | 2.09 | 样本等权relative L2 0.5385 |
| fno-darcy | 1.44 | 样本等权relative L2 0.1754 |
| fno-double | 2.55 | 样本等权relative L2 0.3171 |
| deeponet-shape | 3.76 | 样本等权relative L2 0.3106 |
| fno-shape | 8.95 | 样本等权relative L2 0.1277 |

不同任务及聚合口径不混排排名；所有逐字段MAE/RMSE、归一化、身份和参考差在`evidence/summary.json`所列原记录中。POD秩2仅验证拆装与持久化，velocity_y约0.746的相对误差明显较大；独立SVD投影下限单列于POD报告，不把低秩截断误差归咎代理。LightGBM12轮同样未调至准确度最优。ShapeNet只在有效插值支撑回贴评价，覆盖率在原网格报告中，不声称所有原网格点都可准确预测。

## 物理能力与重组结果

同一已有残差归约接收Darcy可微反归一化和有效域。FNO开/关100更新的参数最大差0.00388，测试负值比例约3.256%→3.171%，负值违约均方约2.686e-8→2.452e-8；不将此小差异宣称普遍物理精度提升。DeepONet本次两分支始终未触发负解违约，参数及预测相同，这是约束不活跃的正确结果；非退化测试另证明该损失可传到两个模型参数。证据`evidence/physics-comparison.json`。

三项实际用户扩展均已安装后复制执行：MLP与前馈块重组DeepONet分支、POD系数代理替换为既有MLP、同一物理目标接入算子。POD冻结解码器的梯度到MLP有独立检查；其SVD基底拟合没有冒充可微训练。派生输出在分支/约束扩展中完成保存和独立消费。

## 安装、恢复与交付

- 八个案例均在独立`installed/`环境执行direct流程与Task。五个神经案例另验1→2更新恢复与连续2更新：模型、优化器、流、历史及随机科学状态逐值一致；只有运行路径/有效配置快照不同。三种代理案例按拟合状态读回验，不伪造代数优化器恢复。
- 全部案例搬移固定结果，并临时隐藏本次旧准备、检查点和结果副本后运行post-only；原始用户数据未改动。输出身份、字段、单位、真值、mask及实际时间保持一致。
- 六组传统状态另在已安装wheel中重建和推理，所有固定数组与源执行逐值相等，包括真实LightGBM原生引擎、Kriging方差和POD解码，见`evidence/wheel-model-states.json`。
- 环境复用既有数值依赖，但spec/core/contrib/task实际导入及Task worker所有已加载Dojo模块均来自独立安装根；LightGBM4.6的OpenMP库显式取现有Torch提供的libomp。没有sync或重启用户主环境/8000/5173，不宣称完全独立的系统依赖环境。
- 八项日志、恢复、Task完成态及每次尝试见`evidence/installed.json`；源码/wheel逐文件摘要见`evidence/installed-source-hashes.json`。生成Help及案例资源随task wheel交付。

## 架构归并与失败修正

建模能力实际消费公开计算：DeepONet复用前馈/分支主干读出，FNO复用谱块/阶段/前馈投影；POD、RSM、RBF、Kriging分别复用冻结基、多项式、径向与协方差/条件状态。没有增加框架层或统一估计器协议；可选LightGBM官方后端保持明确边界。拟合归training、普通批执行归inference、安全状态归data/save，应用只绑定数据和物理语义。

归并修复了普通预测缓冲别名覆盖、监督广播、原生状态文本摘要缺失、OmegaConf列表未转换、NASA换路径重复数据泄漏，以及真实FP32查询和GLS有限差分误差。失败原记录与固定参数诊断均保留，没有改容差、替换真值或清空预算。泛化只补已发现的公共边界，没有建立通用模型调度/自动物理导数系统。

最终每组合最高预算记账 97.84 秒（约 1.63 分钟），包含失败、扩展、安装和保守预留，均小于180分钟；这是计算预算记账，不是整个开发会话时长。
