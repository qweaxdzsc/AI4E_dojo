# Dojo 合并后的 Ability 清单（讨论稿 v2）

日期：2026-09-10。

本版按“用户要完成什么、该操作交付什么、哪些实现必须一起工作”归并，**不按 ability 文件夹或函数数量分类**。主清单按 **rawprep、trainprep、model、train、post 五个使用场景**展开，每项标明操作、策略、模型内计算单元或复合流程。五阶段只是查阅入口，不要求能力只能属于一个阶段，也不改变目录。

v1 的 **17 项业务大组 + 7 项策略**保留为后文 O/P 索引，不再把它们当作原子能力总数。修订重点：将模型与训练的大组展开；有实质计算语义的模型内部组件保留为嵌套能力，只有契约、机械辅助和薄包装被吸收。

这是对当前实现的能力归类建议，**不是代码合并、公开 API 变更或拖拽节点已实现的声明**。原始 [源码明细表（89 项及新增 4 项）](abilities-inventory.md) 保留对照；本版逐条说明其归属，没有把未列入主清单的实现删除。长期功能行为仍以 [core abilities PRD](PRD/ai4e-core/abilities/PRD.md) 和 [contrib ability PRD](PRD/ai4e-contrib/ability/PRD.md) 为准。

快速定位：[rawprep 原始处理](#stage-rawprep) · [trainprep 数据准备](#stage-trainprep) · **[model 模型能力](#stage-model) · [train 训练能力](#stage-train) · [post 后处理能力](#stage-post)**。

## 1. 本版如何合并

“独立”指有清楚的业务目的、显式输入和可识别的输出，不指没有依赖，也不指必须独立进程或落盘。代码短不是唯一排除条件；代码很长也不一定构成独立业务能力。

| 角色 | 判断标准 | 本版处理 | 例子 |
| --- | --- | --- | --- |
| 业务操作 | 用户能单独说明目的，检查结果，并决定是否执行或换实现 | 在五阶段主表中展开，O 编号只作能力大组索引 | 读取文件、筛选点场、训练模型、预测物理场 |
| 可替换策略 | 有独立研究选择，但依赖宿主循环、模型状态或数据组织才能发挥作用 | 在对应阶段主表中展开，同时保留 P 策略索引 | 采样、监督损失、优化器、学习率调度 |
| 支撑实现 | 保证主能力正确执行；通常不应让用户单独安排调用顺序 | 并入主能力，列在吸收说明与对照表 | 身份校验、输出预检、检查点状态捕获、随机流保护 |
| 模型内部组件 | 是网络计算的组成部分，输入输出依赖模型内部约定 | 在 model/post 明确展开为嵌套能力，保留专用契约；不直接当作顶层执行任务 | MLP、位置编码、K/V 投影、注意力块、物理状态缓存网络 |
| 契约与薄包装 | 描述数据，或完成类型解析、转发、取属性、简单整理 | 并入使用它的操作或策略 | FieldRecord、infer_format、supervised_mse、face_count |

同一文件的函数可以归属不同角色。例如 `optimization.py` 中，优化器构造属于 P05，设备解析属于 O13/O14 的运行支撑，单次反向与更新由 O13 的循环执行；不会把整个文件强行当成一个原子。

主表中的“现状”只有两种含义：**现成入口**表示已有对应操作入口，但仍需要有效参数及依赖；**组合口径**表示本版把现有入口归成同一业务能力，当前仍通过多次调用或 application 装配完成，不宣称有新增统一函数。

## 2. 五阶段合并能力主表

**这五类只是使用场景，不是把目录再抄一遍。** 每行按结果语义或可替换算法划分；同一源码可以服务多行，同一能力也可跨阶段复用。O/P 是第 3、4 节的大组索引，A 是原始源码条目。父流程、内部单元和跨阶段复用项不相加计数。

这里的“模型内计算单元”和“训练内执行单元”有实质能力，但依赖对应上下文；既不能因为不能单独跑作业就删除，也不表示现有模型已经支持界面任意插拔。下表仅描述当前源码及本版归并建议。

<a id="stage-rawprep"></a>

### 2.1 rawprep：原始数据处理

| 编号 | 合并后的能力 | 层级/角色 | 输入 → 输出 | 可独立选择或修改的内容 | 吸收的辅助与边界 | 大组索引 | 原始依据 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R01 | 获取外部数据 | 操作 | 地址/仓库及输出位置 → 本地文件，可选解压 | 来源、下载范围；下载和解压可分别运行 | 格式识别和解压判断随获取合并。 | O01 | A003、A004、A005 |
| R02 | 读取原始文件 | 操作 | 路径 → VTK 对象及原字段/拓扑 | 文件或目录范围、已支持格式 | 格式推断、路径检查与适配隐藏在读取内；NPY 不自动变网格。 | O02 | A001、A002、A008 |
| R03 | 提取具名字段 | 操作 | VTK 及字段声明 → 坐标、标量/矢量及身份 | 字段名、分量、point/cell 归属 | 字段记录类型和形状检查随提取合并。 | O04 | A010、A011、A012、A013 |
| R04 | 标记与筛选点场 | 操作 | 规则或 mask 与对齐场 → 标记或筛后字段/身份 | 有效顶点、精确表面重合、已有 mask | mask 应用与身份同步不可分开丢失；不修改原拓扑。 | O05 | A017、A018、A019、A020 |
| R05 | 表面法向计算 | 操作 | 二维面网格 → 原点序法向和有效性 | 是否启用、输入表面 | 表面门禁、副本和原 ID 回贴随计算合并。 | O06 | A038、A039 |
| R06 | 几何距离计算 | 操作/方法族 | 查询点与表面 → 距离、方向及方法特有输出 | 最近顶点或点到面 | 两种方法不等价；保留有无符号、最近点输出差异。 | O07 | A036、A037、A038 |
| R07 | 数据产物保存 | 操作/方法族 | 场或网格与目标 → PT、NPY/JSON 或 VTKHDF | 字段映射、格式与覆盖选择 | 编码、输出预检和提交恢复合并；清单发布仍由装配负责。 | O11 | A015、A021、A022、A024、A025 |
| R08 | 训练字段统计 | 操作 | 选定训练数组流 → 总体矩与字段统计 | 统计样本/字段和既有统计来源 | 累计器、update/finalize 和统计文件读写合并；与 D03 共享实现。 | O08 | A026、A027、A028、A030 |

<a id="stage-trainprep"></a>

### 2.2 trainprep：训练数据准备

| 编号 | 合并后的能力 | 层级/角色 | 输入 → 输出 | 可独立选择或修改的内容 | 吸收的辅助与边界 | 大组索引 | 原始依据 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D01 | 打开物理数据与分片 | 操作 | manifest/名单 → 可读样本与身份 | 分片、样本与字段 | 索引、读取和分片人数检查合并；不是随机划分。 | O03 | A006、A007、A009、A024 |
| D02 | 绑定模型输入与监督字段 | 策略/准备操作 | 物理域、工况与模型声明 → inputs/targets 布局 | 域和字段映射、显式零场 | 通道整理、条件广播和输入门禁合并；保持模型专用签名。 | P03 | A016、A032、A045、A075、A082、A083、A089 |
| D03 | 冻结归一化参数 | 操作 | 训练数据/统计来源 → 冻结记录 | 方法与统计来源 | 记录、摘要与参数检查合并，不用测试集拟合。 | O08 | A023、A027、A029、A030 |
| D04 | 应用冻结变换 | 操作/方法族 | 字段与记录 → 归一化字段 | 坐标、z-score、恒等及相应字段 | 参数获取与通道广播不单列；逆变换在 H03 复用。 | O09 | A031、A033、A034、A035 |
| D05 | 采样与跨步分块 | 两种可选策略 | 点与预算 → 选中下标或互补块 | 无放回预算、块数和跨步选择 | P01/P02 保留为不同策略；采样并非只准备一次，训练迭代中可重复。 | P01、P02 | A040、A041、A083、A089 |
| D06 | 模型专用拼批 | 策略 | 准备后的样本 → 批次及几何身份 | 批次大小与模型拼批方法 | stack、几何偏移、字段联动并入拼批；不能从支持拼批推导所有模型支持任意 batch。 | P03 | A049、A073 |
| D07 | 物化归一化数据 | 操作 | 数据/变换/输出声明 → 归一化版本及完整清单 | 是否物化、目录和版本 | 批量应用与提交清理合并；不是强制训练前置。 | O10 | A023 |

<a id="stage-model"></a>

### 2.3 model：模型构建与模型内部能力

| 编号 | 合并后的能力 | 层级/角色 | 输入 → 输出 | 可独立选择或修改的内容 | 吸收的辅助与边界 | 大组索引 | 原始依据 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| M01 | 构造模型与结构声明 | 装配操作 | 构造器/参数/域声明 → 模型实例与结构说明 | AB-UPT、Transolver-3、模型参数 | 工厂转发、参数提取和 describe 为支撑；不是把它们各算一个原子。 | O12 | A042、A074、A075、A077、A085、A087 |
| M02 | 加载初始权重 | 状态操作 | 模型与状态字典 → 严格加载权重的模型 | 权重来源 | 键匹配检查随加载合并；不恢复优化器或训练进度。 | O12 | A046 |
| M03 | 冻结指定参数 | 配置策略 | 模型与参数前缀 → 可训练参数范围 | 冻结哪些已有参数 | 前缀匹配和 requires_grad 修改合并；与 M02 共用 initialize_weights，但研究意图独立，不强行合成一项。 | O12 | A046 |
| M04 | 连续坐标嵌入 | 模型内计算单元 | 连续坐标 → 正余弦位置特征 | 维度、波长及支持的坐标形状 | 频率生成、正余弦、补齐组成完整编码；不是普通格式转换。 | O12 | A044 |
| M05 | 旋转位置编码 | 模型内计算单元 | 坐标频率与特征 → 旋转后的特征 | 已有 RoPE 参数与特征布局 | RopeFrequency 与 rope 归为相关计算单元，保留实数/复数及设备边界。 | O12 | A044、A079 |
| M06 | 前馈特征变换 | 模型内计算单元 | 隐藏特征 → 经 MLP 更新的特征 | 已有维度、激活和层结构参数 | 线性层与激活组合；core Mlp 与 Transolver MLP 实现不同，不宣称统一接口。 | O12 | A043、A088 |
| M07 | 超节点几何池化 | 模型内计算单元 | 几何点、超节点与邻域声明 → 超节点特征 | radius/k、位置模式和预算相关参数 | 邻域检索、位置消息与聚合合并；MPS 邻域检索经 CPU。 | O12 | A080 |
| M08 | 条件特征调制 | 模型内计算单元 | 隐藏特征与条件向量 → 调制特征 | 已有条件开关与维度声明 | 条件到缩放/平移的投影及广播合并；当前为 AB-UPT 组件。 | O12 | A078 |
| M09 | 域注意力交互 | 模型内计算单元 | 域 token、几何/锚点、位置与条件 → 更新的域特征 | 模型已支持的域交互布局 | Q/K/V 投影、拆头、注意力及配套前馈随块合并；遵守参数共享与缓存约定。 | O12 | A078、A081 |
| M10 | 物理切片注意力交互 | 模型内计算单元 | 点特征 → 经物理切片聚合、交互及回贴的特征 | 切片数、头数及已有块参数 | 切片权重、token 聚合、attention/deslice 组成完整单元；Transolver 专用。 | O12 | A088 |
| M11 | 域输出映射 | 模型内计算单元 | 域隐藏特征 → 声明输出通道 | 域输出维度及已有条件配置 | DomainReadout 的归一化、调制与输出投影合并；不等于最终物理逆变换。 | O12 | A078 |
| M12 | 完整网络装配 | 复合模型 | 输入布局与模型结构 → 完整 AB-UPT/Transolver 网络 | 已有完整模型选项 | 组合上述计算单元；它是父容器，不与内部组件相加声称独立能力总数。 | O12 | A081、A088 |

<a id="stage-train"></a>

### 2.4 train：训练设置与训练执行能力

| 编号 | 合并后的能力 | 层级/角色 | 输入 → 输出 | 可独立选择或修改的内容 | 吸收的辅助与边界 | 大组索引 | 原始依据 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T01 | 监督目标与损失聚合 | 训练策略 | 预测、目标、字段与权重 → loss 及分项 | MSE/MAE/Huber/relative L2；按模型可用范围 | 字段分流、形状门禁和别名合并；Transolver 参考路线保持自己的 MSE 口径。 | P04 | A047、A048、A058、A082、A089 |
| T02 | 优化器及参数分组 | 训练策略 | 可训练参数与配置 → 优化器 | Adam/AdamW/Lion、权重衰减策略 | 分组、优化器构造及其状态归一起；设备解析不是优化算法。 | P05 | A056 |
| T03 | 学习率调度 | 训练策略 | 优化器与预算 → 调度状态/学习率 | constant、cosine、warmup_cosine 和支持的调度单位 | 预算计算随调度合并；推进时机由 T05 保证。 | P06 | A057 |
| T04 | 单次有效训练更新 | 训练内执行单元 | 模型、批次、step、优化器与累积状态 → loss 及更新标记 | 累积步、裁剪；scaler 按已支持路线注入 | 清梯度、反向、解除缩放、裁剪、step 合成完整更新；不各自画顶层节点。 | O13 | A056 |
| T05 | 训练循环与执行预算 | 复合执行流程 | 模型、批次提供器、策略与轮次预算 → 训练轨迹/最终状态 | 轮次、验证间隔、恢复等现有设置 | 调度、EMA、回调与更新顺序由循环管理；不把“训练”当作唯一的训练能力。 | O13 | A053 |
| T06 | 训练期验证与模型选优 | 训练内操作 | 模型与验证集 → 评估结果、最佳分数及选优状态 | 评估间隔、比较规则及当前路线支持的分片 | evaluate 为评估能力，最佳判定在 fit；共同装配，当前不是新增统一选优函数。 | O13、O15 | A051、A053、A063、A067 |
| T07 | 训练状态捕获与兼容恢复 | 状态操作 | 模型/优化器/随机和数值状态 ↔ 检查点状态 | 恢复来源及现有保存策略 | capture/restore/restore_selection 合并；文件写入仍由 run 执行，不冒充任意 batch 恢复。 | O13 | A051 |
| T08 | 指数移动平均权重 | 训练策略 | 有效更新后的模型 → 独立 EMA 状态 | 启用及衰减参数 | 更新与保存/恢复配合训练循环，普通复制字典不独立列能力。 | P07 | A054 |
| T09 | 训练观测与周期回调 | 过程支撑机制 | 训练事件与分项 loss → 进度摘要/周期回调 | 日志频率、声明的回调 | 参数计数、内存读数、窗口累计和 flush 不各自计原子；框架日志实际写入仍在 run。 | O13 | A050、A052、A055 |

<a id="stage-post"></a>

### 2.5 post：推理、评价、回贴与结果处理能力

| 编号 | 合并后的能力 | 层级/角色 | 输入 → 输出 | 可独立选择或修改的内容 | 吸收的辅助与边界 | 大组索引 | 原始依据 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| H01 | 重建推理模型 | 状态操作 | 构造器、结构与检查点 → 已加载权重的模型 | 兼容检查点来源 | 结构/语义检查随重建；不加载训练优化器状态。 | O14 | A061 |
| H02 | 查询点或完整域预测 | 操作/模型专用策略 | 模型、物理样本/查询点与准备信息 → 对应点预测 | 锚点/指定点/完整域及分块方式 | AB-UPT 缓存查询、Transolver 状态缓存/解码按各自实现组合；缓存创建/验证/释放不单独接线。 | O14 | A059、A062、A076、A082、A084、A086、A089 |
| H03 | 预测逆变换 | 跨阶段复用操作 | 归一化预测与冻结记录 → 物理量 | 输出字段和原冻结参数 | 复用 D04 同一变换能力；不重新拟合统计。 | O09、O14 | A031、A033、A034、A035 |
| H04 | 物理指标评价 | 操作 | 同身份预测与真值 → MSE/MAE/relative L2 等指标 | 场、分量、有效点集及现有统计口径 | field_metrics 与累计器合并成评价能力；零范数处理与训练 loss 保持区别。 | O15 | A063、A064、A065、A066、A067 |
| H05 | 预测回贴与有效网格构造 | 操作 | 预测、原点身份与原网格 → 含预测的有效网格 | 字段与目标域 | 身份匹配、有效单元选择和现有模板门禁合并；存在组合调用，不宣称所有路线统一入口。 | O16、O17 | A068、A070 |
| H06 | 表面与物理切面提取 | 操作/方法族 | 含真值/预测的网格 → 表面或切面场 | 表面模式或切面轴/位置 | surface/cut_plane 及共同拓扑插值合并；不包含渲染。 | O17 | A068 |
| H07 | 结果文件导出 | 操作/方法族 | 预测、坐标/网格与输出目标 → PT/HDF5/VTP/VTU 等产物 | 字段、目标路径、点云或网格方式 | 格式写出、原子保存、输出验收归导出；点云不能冒充有原始面拓扑。 | O16 | A021、A024、A069、A070、A071 |
| H08 | 来源相关的表面拓扑检查与定向 | 专用操作 | 已有拓扑、坐标、节点面积/法向 → 面积诊断或定向后的拓扑 | 当前 NASA 语义输入 | 面积累计、朝向翻转与拓扑计数合并；不声称任意点云重建或通用网格修复。 | O16 | A072 |

从这张主表可以直接区分：**优化器是策略，训练更新是循环内执行单元，训练循环是复合流程；位置编码与注意力是模型内计算单元，模型工厂是装配入口。** 合并辅助函数应保留这些层级，不能把它们统一压成“模型”“训练”两个大盒子。

## 3. 业务大组索引（保留 v1 对照，不代表最终原子粒度）

以下分组服务阅读，不对应目录，也不代表唯一执行顺序。每项的前置条件均由调用方或现有业务装配提供。

### 3.1 取得与整理可用数据

| 编号 | 合并后的能力 | 输入 → 交付结果 | 吸收的实现 | 当前边界与现状 |
| --- | --- | --- | --- | --- |
| O01 | 获取外部数据文件 | HuggingFace 仓库/文件或 URL、目标目录 → 本地文件；按需解压 | 整库/单文件下载、URL 下载、压缩包识别和解压 | **组合口径**。下载与解压仍可分开调用；不解释数据集内容，不包含平台上传。 |
| O02 | 读取原始数值文件 | 文件路径、格式或文件集合 → 保留字段与拓扑的 VTK 对象 | 格式判断、路径预检、VTK/NPY 适配、单文件/多文件/目录读取 | **现成入口**。NPY 以 FieldData 承载，不自动产生网格；不包含 NASA 专用来源适配。 |
| O03 | 打开已准备的物理数据 | 已提交 manifest、分片与字段选择 → 按样本读取的具名物理数据及身份 | 清单索引、PhysicalView、张量读回、分片名单读取与人数检查 | **组合口径**。复用现有 PT/清单链路；不新增随机划分或任意格式数据集协议。 |
| O04 | 提取并整理具名字段 | VTK 对象、字段名与 point/cell 归属 → 坐标/具名场及明确的身份记录 | 坐标/标量/矢量提取、FieldRecord/GroupContract、所需通道整理与校验 | **组合口径**。提取不做 point/cell 转换；来源和身份由装配显式绑定。标量补通道不是独立业务能力。 |
| O05 | 按规则筛选对齐点场 | 点场与身份、有效顶点/表面重合规则或已有 mask → 同步筛选后的字段与身份 | mask 生成、单元类型解析、统一套 mask、前后身份检查 | **组合口径**。可仅输出标记用于检查；点 mask 不得用于 CellData，不在此修改原始网格拓扑。 |
| O06 | 计算表面点法向 | 支持的二维表面网格 → 原点序法向及有效性标记 | 表面门禁、私有副本、法向计算与原 ID 回贴 | **现成入口**。孤立点以零值和无效标记表达；不自动抽取体网格外壳。 |
| O07 | 计算几何距离特征 | 查询点、目标表面 → 距离与方向；点到面方法另交付面上最近点 | 最近表面顶点算法，或带表面门禁的点到网格面算法 | **组合口径**。两种方法必须明确选择：最近顶点距离非负，点到面距离有符号；不得混名或视为数值等价。 |

### 3.2 确定数据变换并交付数据

| 编号 | 合并后的能力 | 输入 → 交付结果 | 吸收的实现 | 当前边界与现状 |
| --- | --- | --- | --- | --- |
| O08 | 确定并冻结归一化参数 | 训练数据、方法声明或既有统计量 → 可复用的冻结变换记录 | 数组流统计、总体矩累计、统计量读写、物理视图 freeze、参数记录与摘要 | **组合口径**。已有独立统计函数及物理视图 freeze；点场和工况统计单位不同。训练样本选择归上层，不能用测试集重新拟合。 |
| O09 | 执行字段正反变换 | 字段、冻结记录、正向/反向选择 → 归一化值或恢复后的物理值 | 坐标缩放、z-score、恒等变换、工况/标签变换、记录重建 | **现成入口**。属于同一能力族，但张量/NumPy 路线和算术顺序有差别，不承诺统一签名。逆变换使用原冻结参数。 |
| O10 | 物化归一化数据版本 | 数据索引、冻结变换、样本准备方法与目标目录 → 归一化张量及版本清单 | 批量 apply、版本目录、记录保存、完整清单提交与失败清理 | **现成入口**。这是有持久产物的独立操作，不与 O09 的内存变换混算；不是所有训练都必须先物化。 |
| O11 | 保存可复用的数据产物 | 具名字段/张量或网格、输出映射 → PT、NPY/JSON 或 VTKHDF 数据文件 | 编码、字段与输出校验、原子文件/目录提交、覆盖恢复 | **组合口径**。不同产物保留不同契约：PT/NPY 不能替代网格拓扑，VTKHDF 保留拓扑与身份；跨文件清单发布仍由现有上层完成。 |

### 3.3 形成模型与实验结果

| 编号 | 合并后的能力 | 输入 → 交付结果 | 吸收的实现 | 当前边界与现状 |
| --- | --- | --- | --- | --- |
| O12 | 构建模型并设置初始状态 | 模型选择、结构参数、可选权重/冻结规则 → 可训练模型与结构说明 | 工厂调用、AB-UPT/Transolver 构造、内部网络组件、权重初始化、参数冻结、模型要求检查 | **组合口径**。core 的 construct 虽短，但它连接的是完整模型能力；完整网络位于 contrib。输入预检在有样本时执行；初始权重不等于续训状态。 |
| O13 | 执行训练或兼容续训 | 模型、批次提供器、监督/优化策略、预算及可选恢复点 → 更新后的模型、检查点和训练记录 | 循环、反向与更新、调度推进、评估、选优、EMA、回调、日志统计、设备及恢复保护 | **现成入口**。由现有 application 装配后调用 fit；P 策略作为内部可替换部分。恢复遵守状态与语义门禁，不承诺任意 batch 精确恢复。 |
| O14 | 使用模型预测物理场 | 模型/检查点、物理样本或查询点、准备记录 → 按目标点身份对应的预测 | 权重重建、模型输入准备、查询/流式推理、专用缓存、随机流与模式保护、逆变换 | **组合口径**。完整物理域预测与锚点/指定点查询属于不同模式，不能用子集冒充全点；文件交付接 O16。 |
| O15 | 评价预测结果 | 对齐的预测与真值，或模型与评估批次 → 具名指标与分项结果 | 逐样本指标、逐点评估、总体误差累计、模型评估执行与模式恢复 | **组合口径**。模型评估路线可在内部前向，不要求先保存 O14 输出；累计口径、物理/归一化空间与零范数处理必须保留。 |
| O16 | 导出可检查的预测产物 | 预测、点身份、可选原网格/表面拓扑、输出目标 → 点云、表面/体网格或数组文件 | 原场查找、原点回贴、拓扑检查/朝向处理、点云/VTP/VTU/HDF5/张量保存、输出验收 | **组合口径**。点云不等于原始网格；现有 surface/volume 写出含压力/速度模板约定，NASA 拓扑辅助不是通用网格修复。 |
| O17 | 制作共享几何上的比较数据 | 已对齐的多模型预测、真值、原网格、表面/切面选择 → 含各场的比较网格或切面 | 原点匹配、有效单元选取、场回贴、表面提取、物理平面切割与 VTP 保存 | **组合口径**。跨运行是否可比由上层先判断；这里只制作比较数据，不包含图像和报告页面渲染。 |

O11 与 O16 复用部分保存函数，但使用目的和输入前提不同：前者交付后续可消费的数据，后者解释预测与原始几何的对应关系。共享实现不因此复制，也不把“写一次文件”再算作第三项能力。

## 4. 可替换策略索引

这些能力有研究价值，应能选择和替换；它们通常随宿主操作反复执行，不应要求用户在顶层为每次调用接线。它们不是没有能力，而是具有不同的使用层级。

| 编号 | 合并后的策略能力 | 放在哪里使用 | 输入 → 结果 | 吸收内容及边界 |
| --- | --- | --- | --- | --- |
| P01 | 点采样 | O13 的样本准备、O14 的锚点准备；也可用于数据处理 | 候选点、预算、样本/轮次身份与种子 → 下标及对齐字段子集 | point_indices + select_aligned；模型按域策略复用或绑定它。无放回抽样已有，不代表曲率自适应采样已有。 |
| P02 | 跨步分块与顺序恢复 | 模型样本准备和完整预测 | 点数、块数与块身份 → 点下标；分块结果 → 原点序结果 | indices + reconstruct；Transolver 专用预测保留自己的回贴实现，不声称所有分块都调用同一恢复函数。 |
| P03 | 模型输入与批次组织 | O13、O14、需要模型前向的 O15 | 物理字段、模型布局、工况与样本集合 → inputs / targets / metadata | 域绑定、prepare_sample/prepare_inputs、通道拼接、显式零场、collate、stack、几何索引偏移及输入校验。模型专用契约不同，不当作任意模型通用拼批。 |
| P04 | 监督目标与损失计算 | O13 的训练 step；O15 的监督分数 | 预测与目标、字段对应和权重 → 可反向标量及分项 | compare、supervised、模型专用 loss 与字段 route；MSE/MAE/Huber/relative L2 是方法选择，别名不单列。Transolver 参考路线固定等权标准化 MSE，不能自动套全部方法。 |
| P05 | 优化器与更新规则 | O13 | 模型参数、学习率及优化器参数 → 优化器状态与更新规则 | Adam/AdamW/Lion、参数分组；清梯度、反向、解除缩放与更新时机归训练循环。算法选择值得保留，循环动作不各自成为节点。 |
| P06 | 学习率调度 | O13 | 优化器、有效更新预算及调度参数 → 随进度变化的学习率 | constant/none、cosine、warmup_cosine、总更新数计算；逐轮或逐更新推进须匹配实际模型路线。 |
| P07 | 权重指数移动平均（EMA） | O13，作为可选训练策略 | 有效更新后的模型与衰减参数 → 独立 EMA 状态 | MovingAverage 及更新逻辑；状态捕获/恢复随训练检查点，不让用户手动安排每一步调用。 |

## 5. 辅助实现与嵌套计算单元的不同处理

| 支撑类型 | 代表函数/类型 | 归入的能力 | 不单列的原因 |
| --- | --- | --- | --- |
| 字段与身份契约 | FieldRecord、GroupContract、ValidationIssue/Report/Error、require_same_leading_dim、validate_records、validate_bindings、validate_inputs | O03–O07、O11、O12、P03 | 描述或验证有效输入；应成为操作前后条件。仍可由开发者独立调用诊断，但用户不应漏接后还能继续静默计算。 |
| 输出安全与事务 | validate_filemap、validate_destination、plan_output、atomic_path、BackupCleanupWarning | O10、O11、O16、O17 | 必须与实际提交共同生效，单独完成预检不能保证稍后写入成功。 |
| 来源与内容摘要 | fingerprint、file_fingerprint、source_fingerprint、content_digest、normalization.digest | O03、O08、O10、O12–O14 | 支撑身份、冻结与兼容检查；本表不扩张为已交付跨运行内容缓存。 |
| 设备、随机流与资源保护 | resolve_device、to_device、preserve_randomness、seeded_randomness、模式恢复、缓存 close | O13–O15、P01、P03 | 与真正消费设备、随机数和缓存的操作绑定；独立拖一个“设种子”不能表达完整生命周期。 |
| 检查点生命周期 | capture、restore、restore_selection、推理 rebuild 内的兼容校验 | O13、O14 | 恢复需要模型结构和相应状态；训练续训与只加载推理权重保留不同语义，不把文件加载当作完整恢复。 |
| 训练监控与回调机制 | parameter_count、peak_memory、report_setup、report_progress、OnlineLoss、PeriodicCallback | O13；评估结果来自 O15 | 属于过程观测和扩展机制。用户可配置频率/回调，但计数、冲刷、触发不是独立训练业务。 |
| 模型内部计算块 | Mlp、ContinuousSincosEmbed、RopeFrequency、DomainBlock、KVProjection、Modulation、SupernodePooling、Transolver_block 等 | O12 的模型实现；专用缓存/解码参与 O14 | 在 model 主表中继续展开为嵌套计算单元；保留参数共享、布局和数值次序约束。不能因为依赖网络上下文，就与类型解析等机械辅助同等吸收。 |
| 类型解析、简单整理与别名 | infer_format、is_archive、resolve_cell_type、extract_scalars/vectors、supervised_mse、face_count、euler_characteristic、training_parameters | 各自主操作或策略 | 没有新的业务结果，或是同一方法的便利入口；仍保留源码/API，不独立计数。 |

**不能靠合并抹掉的差异：** 统计拟合与应用变换；内存变换与物化；初始权重与完整续训；最近顶点距离与点到面距离；预测子集与完整域；归一化空间损失与物理空间指标；点云与带拓扑网格。它们可以共享代码或归在同一能力族，但输入、输出和行为选项要继续明确。

## 6. 原始 89 项与新增 4 项如何归入本版

这是追溯附录。O/P 编号表示业务大组归属（细粒度能力见第 2 节），允许同一实现支撑多项能力，不代表复制代码；“归并说明”对混合文件按函数职责拆分。源码链接沿用原始表的实际文件。

<details>
<summary>展开完整归属对照（A001–A093，逐项无遗漏）</summary>

| 原编号 | 原始实现模块 | 本版归属 | 归并说明 | 源码 |
| --- | --- | --- | --- | --- |
| A001 | NPY 格式适配 | O02 | 格式适配收进读取，load 不再按格式重复计能力。 | [data/source/adapter/npy.py](../packages/ai4e-core/abilities/data/source/adapter/npy.py) |
| A002 | VTK 家族格式适配 | O02 | 格式适配收进读取，保留各格式能力边界。 | [data/source/adapter/vtk.py](../packages/ai4e-core/abilities/data/source/adapter/vtk.py) |
| A003 | 多压缩包解压 | O01 | 解压是获取数据的可选操作；is_archive 是其判断支撑。 | [data/source/download/archives.py](../packages/ai4e-core/abilities/data/source/download/archives.py) |
| A004 | HuggingFace 下载 | O01 | 快照和单文件是同一获取能力的范围选项。 | [data/source/download/huggingface.py](../packages/ai4e-core/abilities/data/source/download/huggingface.py) |
| A005 | 网址下载 | O01 | URL 是获取来源选项，下载实现继续独立。 | [data/source/download/url.py](../packages/ai4e-core/abilities/data/source/download/url.py) |
| A006 | 物理产物清单索引 | O03 | 索引类、read、describe 和摘要共同支撑数据打开。 | [data/source/manifest.py](../packages/ai4e-core/abilities/data/source/manifest.py) |
| A007 | 具名物理数据视图 | O03 | 具名物理视图与身份说明共同交付可消费数据。 | [data/source/physical.py](../packages/ai4e-core/abilities/data/source/physical.py) |
| A008 | 文件读取与目录读取 | O02 | 单个/多个/目录是读取范围；infer_format 为内部解析。 | [data/source/read.py](../packages/ai4e-core/abilities/data/source/read.py) |
| A009 | 分片名单读取与人数检查 | O03 | 名单读取与人数校验是数据打开的边界，不新增划分能力。 | [data/source/split.py](../packages/ai4e-core/abilities/data/source/split.py) |
| A010 | 字段记录与实体身份契约 | O04、O05、P03 | 契约类型随字段组织传递，不作为可执行操作。 | [data/extract/records.py](../packages/ai4e-core/abilities/data/extract/records.py) |
| A011 | 坐标与具名场提取 | O04 | 坐标与具名场提取为一项业务；标量/矢量入口按同一选择规则归组。 | [data/extract/vtk_fields.py](../packages/ai4e-core/abilities/data/extract/vtk_fields.py) |
| A012 | 数组行数对齐检查 | O04、O05、P03 | 首维检查并入输入门禁，不代替完整身份检查。 | [data/validate/aligned.py](../packages/ai4e-core/abilities/data/validate/aligned.py) |
| A013 | 字段来源与行身份检查 | O04、O05、O11 | 校验执行与报告/异常类型并入字段交付门禁。 | [data/validate/fields.py](../packages/ai4e-core/abilities/data/validate/fields.py) |
| A014 | 数据、文件与源码摘要 | O03、O08、O10、O12、O13、O14 | 内容/文件/源码摘要是来源与兼容支撑，不新增缓存能力。 | [data/validate/fingerprint.py](../packages/ai4e-core/abilities/data/validate/fingerprint.py) |
| A015 | 输出规划与覆盖预检 | O10、O11、O16 | 输出规划与提交共同归属保存能力。 | [data/validate/output.py](../packages/ai4e-core/abilities/data/validate/output.py) |
| A016 | 模型输入与物理域绑定检查 | P03 | 模型输入绑定校验随模型准备执行。 | [data/validate/physical.py](../packages/ai4e-core/abilities/data/validate/physical.py) |
| A017 | 表面重合点标记 | O05 | 精确重合规则可只出 mask，或供同组筛选使用。 | [data/filter/coincident.py](../packages/ai4e-core/abilities/data/filter/coincident.py) |
| A018 | 具名字段与身份同步筛选 | O05 | 身份检查与字段筛选一起保留。 | [data/filter/records.py](../packages/ai4e-core/abilities/data/filter/records.py) |
| A019 | 多数组同步筛选 | O05 | 简单数组套 mask 吸收到筛选，不再单独命名业务。 | [data/filter/select.py](../packages/ai4e-core/abilities/data/filter/select.py) |
| A020 | 网格有效顶点标记 | O05 | 有效顶点规则保留；类型解析属于辅助。 | [data/filter/used_vertices.py](../packages/ai4e-core/abilities/data/filter/used_vertices.py) |
| A021 | NPY 与 JSON 原子保存 | O11、O16、O17 | NPY/JSON 是输出方法，atomic_path 为共用事务支撑。 | [data/save/arrays.py](../packages/ai4e-core/abilities/data/save/arrays.py) |
| A022 | 字段编码为张量 | O11 | float32 编码随数据提交，调用方仍须明确精度选择。 | [data/save/encode.py](../packages/ai4e-core/abilities/data/save/encode.py) |
| A023 | 冻结变换保存与归一化物化 | O08、O10 | save_record 归冻结记录保存；materialize 独立归物化操作。 | [data/save/normalization.py](../packages/ai4e-core/abilities/data/save/normalization.py) |
| A024 | 张量和张量包读写 | O03、O11、O16 | load_* 归数据打开；write_* 归保存；备份告警是提交状态。 | [data/save/store.py](../packages/ai4e-core/abilities/data/save/store.py) |
| A025 | 保留拓扑与身份的 VTKHDF 导出 | O11 | 拓扑与原 ID 保留是 VTKHDF 输出方式的契约。 | [data/save/vtkhdf.py](../packages/ai4e-core/abilities/data/save/vtkhdf.py) |
| A026 | 具名字段流式统计 | O08 | 具名数组统计是冻结参数的基础，可由开发者单独调用。 | [data/stats/fit.py](../packages/ai4e-core/abilities/data/stats/fit.py) |
| A027 | 统计量文件读写 | O08、O10 | 统计文件读写支撑参数读取和记录持久化。 | [data/stats/load.py](../packages/ai4e-core/abilities/data/stats/load.py) |
| A028 | 总体矩流式累计 | O08 | 总体矩累计是统计内部数值能力，不单独对用户计数。 | [data/stats/moments.py](../packages/ai4e-core/abilities/data/stats/moments.py) |
| A029 | 物理视图训练统计冻结 | O08 | 物理视图上的完整冻结入口。 | [data/stats/physical.py](../packages/ai4e-core/abilities/data/stats/physical.py) |
| A030 | 总体矩累计器 | O08 | 累计器的 update/finalize 共同完成一项统计动作。 | [data/stats/population.py](../packages/ai4e-core/abilities/data/stats/population.py) |
| A031 | 坐标范围归一化与逆变换 | O09 | 坐标正反变换是一种变换方法。 | [transform/coordinate_normalization.py](../packages/ai4e-core/abilities/transform/coordinate_normalization.py) |
| A032 | 点场通道整理与显式零场 | O04、P03 | 标量补通道归整理；显式零场归模型准备，不自动猜缺失物理场。 | [transform/fields.py](../packages/ai4e-core/abilities/transform/fields.py) |
| A033 | 冻结归一化组合与重建 | O09、O08、O10 | 正反变换归 O09；record/digest 支撑冻结与物化；Identity 不独立计数。 | [transform/normalization.py](../packages/ai4e-core/abilities/transform/normalization.py) |
| A034 | 工况与点标签标准化 | O09、P03 | 工况与点标签变换保留其计算路线，由输入准备使用。 | [transform/pointfields.py](../packages/ai4e-core/abilities/transform/pointfields.py) |
| A035 | 均值标准差变换与逆变换 | O09 | z-score 正反变换是一种变换方法。 | [transform/standardization.py](../packages/ai4e-core/abilities/transform/standardization.py) |
| A036 | 点到网格表面距离 | O07 | 点到面方法；保留有符号距离和最近点语义。 | [geometry/mesh_sdf.py](../packages/ai4e-core/abilities/geometry/mesh_sdf.py) |
| A037 | 点到最近表面顶点距离 | O07 | 最近顶点方法；不能替代点到面算法。 | [geometry/nearest.py](../packages/ai4e-core/abilities/geometry/nearest.py) |
| A038 | 二维表面门禁与私有副本 | O06、O07 | 表面检查、私有副本和类型封装随几何操作执行。 | [geometry/surface.py](../packages/ai4e-core/abilities/geometry/surface.py) |
| A039 | 表面点法向与有效性 | O06 | 带有效性输出为完整能力；仅数组返回为兼容入口。 | [geometry/surface_normals.py](../packages/ai4e-core/abilities/geometry/surface_normals.py) |
| A040 | 无放回抽点与字段联动 | P01 | 抽样与同组字段联动作为整体策略。 | [sampling/points.py](../packages/ai4e-core/abilities/sampling/points.py) |
| A041 | 跨步分块与原点序恢复 | P02 | 分块与恢复保留对应关系，非每一块独立工作流节点。 | [sampling/stride.py](../packages/ai4e-core/abilities/sampling/stride.py) |
| A042 | 注入构造器创建模型 | O12 | 简单工厂包装随完整模型构建吸收，不单独叫构造器调用能力。 | [modeling/construction.py](../packages/ai4e-core/abilities/modeling/construction.py) |
| A043 | 前馈 MLP 组件 | O12 | MLP 在 M06 保留为嵌套计算能力，O12 是其业务大组。 | [modeling/modules/feed_forward.py](../packages/ai4e-core/abilities/modeling/modules/feed_forward.py) |
| A044 | 连续位置编码与 RoPE 频率 | O12 | 位置嵌入与频率/旋转在 M04/M05 保留为模型内能力，不是独立训练任务。 | [modeling/modules/position_encoding.py](../packages/ai4e-core/abilities/modeling/modules/position_encoding.py) |
| A045 | 模型输入与批次预检 | O12、P03 | 输入字段及批次检查随有实际输入时执行。 | [modeling/requirements.py](../packages/ai4e-core/abilities/modeling/requirements.py) |
| A046 | 初始权重加载与参数冻结 | O12 | 初始权重和冻结为模型设置选项，不混入完整恢复。 | [modeling/weights.py](../packages/ai4e-core/abilities/modeling/weights.py) |
| A047 | 同形张量监督比较 | P04 | 比较方法作为监督项选择，保留方法数值差异。 | [constraint/compare.py](../packages/ai4e-core/abilities/constraint/compare.py) |
| A048 | 具名监督项与权重聚合 | P04 | 具名项与权重聚合为监督目标；MSE 别名不重复计数。 | [constraint/supervised.py](../packages/ai4e-core/abilities/constraint/supervised.py) |
| A049 | 拼批、几何索引偏移与设备交接 | P03、O13、O14 | stack/几何偏移归拼批；to_device 为消费侧运行支撑。 | [training/batch.py](../packages/ai4e-core/abilities/training/batch.py) |
| A050 | 训练周期回调 | O13 | 回调触发机制归训练过程，回调业务本身由注入者定义。 | [training/callbacks.py](../packages/ai4e-core/abilities/training/callbacks.py) |
| A051 | 训练状态捕获与恢复 | O13 | 训练状态打包、恢复及选优恢复同属训练生命周期。 | [training/checkpoint.py](../packages/ai4e-core/abilities/training/checkpoint.py) |
| A052 | 参数量、内存与进度诊断 | O13 | 规模、参数、内存、进度为监控支撑。 | [training/diagnostics.py](../packages/ai4e-core/abilities/training/diagnostics.py) |
| A053 | 可恢复训练循环 | O13 | 保留完整训练操作；内部步骤不平铺为顶层能力。 | [training/loop.py](../packages/ai4e-core/abilities/training/loop.py) |
| A054 | 模型参数指数移动平均 | P07 | EMA 是可选策略；更新时机由训练执行方保证。 | [training/moving_average.py](../packages/ai4e-core/abilities/training/moving_average.py) |
| A055 | 在线损失窗口统计 | O13 | 在线损失记账和冲刷归过程监控。 | [training/online.py](../packages/ai4e-core/abilities/training/online.py) |
| A056 | 优化器构造与参数更新 | P05、O13、O14 | 优化器/参数分组归 P05；反向更新归 O13；设备解析为运行支撑。 | [training/optimization.py](../packages/ai4e-core/abilities/training/optimization.py) |
| A057 | 学习率调度与更新步数 | P06 | 调度构造与预算计算合并，推进由训练循环负责。 | [training/schedule.py](../packages/ai4e-core/abilities/training/schedule.py) |
| A058 | 预测与目标字段分流 | P04 | 预测/目标分流为监督绑定支撑，缺键警告不替代损失门禁。 | [training/split.py](../packages/ai4e-core/abilities/training/split.py) |
| A059 | 模型上下文分块查询 | O14 | 分块查询与模式/缓存生命周期一起归推理。 | [inference/query.py](../packages/ai4e-core/abilities/inference/query.py) |
| A060 | 推理随机流隔离与临时种子 | O13、O14、O15 | 随机流保护随实际调用使用；不承诺 MPS 训练精确复现。 | [inference/randomness.py](../packages/ai4e-core/abilities/inference/randomness.py) |
| A061 | 从检查点重建推理模型 | O14 | 只恢复推理权重；保留与 O13 续训的差别。 | [inference/rebuild.py](../packages/ai4e-core/abilities/inference/rebuild.py) |
| A062 | 流式推理生命周期 | O14 | 流式执行是推理方式；专用算法继续由模型组件提供。 | [inference/stream.py](../packages/ai4e-core/abilities/inference/stream.py) |
| A063 | 共享模型评估 | O15 | 包含模型前向的评估方式，模式与随机流保护内置。 | [eval/evaluation.py](../packages/ai4e-core/abilities/eval/evaluation.py) |
| A064 | 完整场误差累计 | O15 | 完整场累计器是评估内部机制，保留点数加权口径。 | [eval/field_totals.py](../packages/ai4e-core/abilities/eval/field_totals.py) |
| A065 | 逐样本物理场指标 | O15 | 对已有预测计算指标，不要求再次执行模型。 | [eval/metrics.py](../packages/ai4e-core/abilities/eval/metrics.py) |
| A066 | 具名物理指标累计 | O15 | 具名字段累计与最终汇总为同一评估过程。 | [eval/physical.py](../packages/ai4e-core/abilities/eval/physical.py) |
| A067 | 逐点监督评估 | O15 | 逐点模型评估是特定路线，保留两种数值空间。 | [eval/pointwise.py](../packages/ai4e-core/abilities/eval/pointwise.py) |
| A068 | 原点匹配、比较网格与平面切割 | O17 | 点匹配、有效网格、表面/切面与保存形成比较数据操作。 | [postproc/comparison.py](../packages/ai4e-core/abilities/postproc/comparison.py) |
| A069 | 完整表面场 HDF5 与 VTP 导出 | O16 | 完整表面 HDF5/VTP 输出方式，不各自增加业务能力。 | [postproc/export/field_surface.py](../packages/ai4e-core/abilities/postproc/export/field_surface.py) |
| A070 | 预测回贴原始表面与体网格 | O16 | 原场查找、回贴、点数检查与网格验收随导出执行。 | [postproc/export/mesh.py](../packages/ai4e-core/abilities/postproc/export/mesh.py) |
| A071 | 锚点点云导出 | O16 | 点云是独立输出选项，保留其没有原始面拓扑的边界。 | [postproc/export/pointcloud.py](../packages/ai4e-core/abilities/postproc/export/pointcloud.py) |
| A072 | 表面拓扑描述、面积与朝向 | O16 | 已有表面拓扑的朝向调整与面积诊断为来源相关支撑；不声称可从任意点云重建拓扑。 | [postproc/surface_geometry.py](../packages/ai4e-core/abilities/postproc/surface_geometry.py) |
| A073 | AB-UPT 专用拼批 | P03 | AB-UPT 专用收批并入模型输入准备。 | [model/abupt/batch.py](../packages/ai4e-contrib/ability/model/abupt/batch.py) |
| A074 | AB-UPT 组件公开门面 | O12、P03、P04、O14 | 门面按实际功能分流；training_parameters 为参数提取，不额外计数。 | [model/abupt/component.py](../packages/ai4e-contrib/ability/model/abupt/component.py) |
| A075 | AB-UPT 有序域布局 | O12、P03 | DomainLayout 及 split 是布局支撑，不是独立数据处理。 | [model/abupt/domains.py](../packages/ai4e-contrib/ability/model/abupt/domains.py) |
| A076 | AB-UPT 推理缓存与分块上下文 | O14 | 模型签名、缓存校验、查询和释放形成一个推理生命周期。 | [model/abupt/inference.py](../packages/ai4e-contrib/ability/model/abupt/inference.py) |
| A077 | AB-UPT 构造、前向与结构描述 | O12、O13、O14 | construct/describe 服务构建，predict 为训练和推理使用的前向。 | [model/abupt/model.py](../packages/ai4e-contrib/ability/model/abupt/model.py) |
| A078 | AB-UPT 域注意力、调制与输出头 | O12 | M08/M09/M11 分别保留条件调制、域注意力和输出头；投影、拆头和初始化随所属单元合并。 | [model/abupt/modules/blocks/domain.py](../packages/ai4e-contrib/ability/model/abupt/modules/blocks/domain.py) |
| A079 | AB-UPT 旋转位置编码 | O12 | 旋转与频率合为 M05 模型内能力，保留代码层复用。 | [model/abupt/modules/rope.py](../packages/ai4e-contrib/ability/model/abupt/modules/rope.py) |
| A080 | AB-UPT 超节点池化 | O12 | 邻域检索、消息生成和聚合合为 M07 超节点池化，不再展开为机械步骤。 | [model/abupt/modules/supernode_pooling_posonly.py](../packages/ai4e-contrib/ability/model/abupt/modules/supernode_pooling_posonly.py) |
| A081 | AB-UPT 多域完整网络 | O12、O13、O14 | 完整 AB-UPT 是 O12 的模型选项，训练和预测消费该实例。 | [model/abupt/network.py](../packages/ai4e-contrib/ability/model/abupt/network.py) |
| A082 | AB-UPT 物理样本准备、监督与全点预测 | P03、P04、O14 | prepare_sample、loss、predict_sample 分别归输入、监督与预测。 | [model/abupt/preparation.py](../packages/ai4e-contrib/ability/model/abupt/preparation.py) |
| A083 | AB-UPT 按域采样与字段绑定 | P01、P03 | 按域抽样与输入绑定归模型准备，复用采样策略。 | [model/abupt/sampling.py](../packages/ai4e-contrib/ability/model/abupt/sampling.py) |
| A084 | Transolver-3 物理状态缓存与解码网络 | O14 | 物理状态缓存网络和完整解码网络共同完成模型专用推理。 | [model/transolver3/amortize.py](../packages/ai4e-contrib/ability/model/transolver3/amortize.py) |
| A085 | Transolver-3 组件公开门面与默认值 | O12、P03、P04、O14 | 组件门面和默认展开支撑模型路线；不把 resolve/参数提取单列。 | [model/transolver3/component.py](../packages/ai4e-contrib/ability/model/transolver3/component.py) |
| A086 | Transolver-3 全表面缓存推理 | O14 | 专用缓存与解码的迭代执行，缓存生命周期按样本。 | [model/transolver3/inference.py](../packages/ai4e-contrib/ability/model/transolver3/inference.py) |
| A087 | Transolver-3 构造、前向与结构描述 | O12、O13、O14 | 构造/描述与前向按使用位置归属，不重复计算模型能力。 | [model/transolver3/model.py](../packages/ai4e-contrib/ability/model/transolver3/model.py) |
| A088 | Transolver-3 完整网络与内部块 | O12、O13、O14 | 完整网络及其注意力/MLP/块为模型实现，非多个业务节点。 | [model/transolver3/network.py](../packages/ai4e-contrib/ability/model/transolver3/network.py) |
| A089 | Transolver-3 物理样本准备、监督与全点预测 | P02、P03、P04、O14 | 域绑定/arrays/prepare_sample 归输入；loss 归监督；predict_sample 归全点预测。 | [model/transolver3/preparation.py](../packages/ai4e-contrib/ability/model/transolver3/preparation.py) |

| A090 | Zarr 张量读写 | O03、O11、O16 | 作为数据读写格式并入打开和保存。 | [data/save/zarr.py](../packages/ai4e-core/abilities/data/save/zarr.py) |
| A091 | 模型结构查看 | O12 | 并入模型构建后的结构查看，辅助发布与来源记录不单列。 | [modeling/inspection.py](../packages/ai4e-core/abilities/modeling/inspection.py) |
| A092 | MinMax 正反变换 | O09 | 归为冻结变换的方法，与坐标兼容入口复用算术。 | [transform/minmax.py](../packages/ai4e-core/abilities/transform/minmax.py) |
| A093 | 同实体场差值 | O15、O16 | 差值作为结果比较方式，身份校验和文件提交随操作合并。 | [postproc/difference.py](../packages/ai4e-core/abilities/postproc/difference.py) |

</details>

## 7. 本版边界

- 只调整讨论清单的粒度，现有目录、函数、模型组件、配置和执行语义保持原状；**“归入”不代表本轮移动代码**。
- 支撑函数仍可保留为公开 API，供开发者和 Agent 使用；从主清单吸收不等于删除或强制私有化。模型内计算单元在第 2 节明确列出，允许代码层嵌套组合，但不承诺已提供界面任意连线或跨模型替换。
- 五阶段主表和 17 项业务大组都不等于已经可以拖拽的节点；要成为界面节点，仍需确认输入输出、参数、可连接条件和失败反馈。这里不新增工作流平台实施计划。
- 当前 PDE/边界条件/守恒约束损失、core abilities/report 的实现缺口，继续按原始清单保留，不通过合并补成“已有”。
- 本轮核对了当前源码、相关装配调用和原始 89 项归属（本次简表核对另补录 4 项），没有重新执行算法、训练或数值对照。文档检查只证明对照完整、来源链接可定位与条目引用一致，不能自动证明业务粒度是最终正确答案。

文档验收：`uv run pytest tests/integration/test_ability_inventory_document.py tests/integration/test_ability_merged_document.py`。
