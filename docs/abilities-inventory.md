# Dojo 当前 Ability 清单（源码盘点）

盘点日期：2026-09-10。目的：先看清已有能力，再讨论工作流节点粒度。

## 阅读口径

- 本表覆盖当前工作区 core abilities 的 **76 个实现文件**，以及 contrib ability 的 **17 个实现文件**；包含尚未提交的现有源码。文件数量不等于业务原子数量。
- 每行按一个实现模块归组；入口列展开该文件直接定义的非下划线函数、类及其公开方法。同一行可能包含多个可单独调用的能力。
- `__init__.py` 的包说明与再导出不重复列为能力；component 门面的再导出在后文单列。私有辅助函数、常量、异常类的内部实现不单独当作业务节点。
- **实现状态：下表均有源码定义；本次仅静态核对，未重新运行算法或训练验收。** 不把源码存在等同于任意设备、任意数据或数值等价验收通过。
- “范围与边界”是阅读提示；表中同时包含数据契约、底层组件、运行辅助和完整循环，不表示它们都适合做拖拽节点。
- 这是源码导航快照，不替代长期产品说明：[core abilities PRD](../docs/PRD/ai4e-core/abilities/PRD.md)、[contrib ability PRD](../docs/PRD/ai4e-contrib/ability/PRD.md)。

## 分类总览

| 类别 | 实现文件数 |
| --- | ---: |
| 数据：来源与读取 | 9 |
| 数据：字段提取与记录 | 2 |
| 数据：校验 | 5 |
| 数据：标记与筛选 | 4 |
| 数据：编码与保存 | 6 |
| 数据：统计量 | 5 |
| 变换 | 6 |
| 几何 | 4 |
| 采样 | 2 |
| 模型构造与通用网络组件 | 6 |
| 监督约束 | 2 |
| 训练 | 10 |
| 推理 | 4 |
| 评估 | 5 |
| 后处理 | 6 |
| 贡献模型：AB-UPT | 11 |
| 贡献模型：Transolver-3 | 6 |

## 能力明细

### 数据：来源与读取

| 编号 | 能力 | 做什么 | 当前入口（类后括号为公开方法） | 范围与边界 | 源码 |
| --- | --- | --- | --- | --- | --- |
| A001 | NPY 格式适配 | NumPy NPY 转为无网格 VTK 对象，使用 FieldData 保留数组与恢复信息。 | `load` | 输出 VTK FieldData；不凭空构造网格或点场。 | [data/source/adapter/npy.py](../packages/ai4e-core/abilities/data/source/adapter/npy.py) |
| A002 | VTK 家族格式适配 | VTK 家族文件：读取为保留原始拓扑和字段的 VTK 对象。 | `load` | 保留具体网格类型、拓扑及关联数组。 | [data/source/adapter/vtk.py](../packages/ai4e-core/abilities/data/source/adapter/vtk.py) |
| A003 | 多压缩包解压 | 多包解压：只认压缩格式，不认数据集。 | `is_archive`<br>`extract_archives` | 按显式输入调用；业务阶段与参数由上层装配。 | [data/source/download/archives.py](../packages/ai4e-core/abilities/data/source/download/archives.py) |
| A004 | HuggingFace 下载 | HuggingFace 通用下载：整库快照或单文件。 | `download_huggingface_snapshot`<br>`download_huggingface_file` | 按显式输入调用；业务阶段与参数由上层装配。 | [data/source/download/huggingface.py](../packages/ai4e-core/abilities/data/source/download/huggingface.py) |
| A005 | 网址下载 | 普通网址下载，不解释文件内容。 | `download_url` | 按显式输入调用；业务阶段与参数由上层装配。 | [data/source/download/url.py](../packages/ai4e-core/abilities/data/source/download/url.py) |
| A006 | 物理产物清单索引 | 已提交数据清单索引：只解析一次元数据，张量按样本读取。 | `ManifestIndex`（`read`, `describe`, `content_digest`） | 按已提交清单索引；张量按样本读取。 | [data/source/manifest.py](../packages/ai4e-core/abilities/data/source/manifest.py) |
| A007 | 具名物理数据视图 | 物理张量公开视图：具名域和样本条件与文件布局解耦。 | `PhysicalView`（`describe`, `content_digest`, `read`） | 旧产物无来源 ID 时显式使用产物行身份。 | [data/source/physical.py](../packages/ai4e-core/abilities/data/source/physical.py) |
| A008 | 文件读取与目录读取 | 通用读取：先校验路径，再按格式转换为统一 VTK 内存对象。 | `infer_format`<br>`read_file`<br>`read_many`<br>`read_tree` | 仅已登记格式；目录读取不等于业务样本发现。 | [data/source/read.py](../packages/ai4e-core/abilities/data/source/read.py) |
| A009 | 分片名单读取与人数检查 | 按传入名单列分片，不扫盘冒充官方顺序。 | `load_split_lists`<br>`load_split_expected`<br>`require_split_counts` | 读取既有名单，不提供随机划分算法。 | [data/source/split.py](../packages/ai4e-core/abilities/data/source/split.py) |

### 数据：字段提取与记录

| 编号 | 能力 | 做什么 | 当前入口（类后括号为公开方法） | 范围与边界 | 源码 |
| --- | --- | --- | --- | --- | --- |
| A010 | 字段记录与实体身份契约 | 具名字段与行身份契约；身份由提取方声明，校验方不猜测数组来源。 | `GroupContract`<br>`FieldRecord` | 数据契约类型；不是可执行处理节点。 | [data/extract/records.py](../packages/ai4e-core/abilities/data/extract/records.py) |
| A011 | 坐标与具名场提取 | 按精确名称和点/单元归属提取 VTK 数值字段，优先保留共享视图。 | `extract_coordinates`<br>`extract_field`<br>`extract_scalars`<br>`extract_vectors` | 明确 point/cell 归属；不做两者转换，不计算单元中心。 | [data/extract/vtk_fields.py](../packages/ai4e-core/abilities/data/extract/vtk_fields.py) |

### 数据：校验

| 编号 | 能力 | 做什么 | 当前入口（类后括号为公开方法） | 范围与边界 | 源码 |
| --- | --- | --- | --- | --- | --- |
| A012 | 数组行数对齐检查 | 校验多个数组首维对齐。 | `require_same_leading_dim` | 按显式输入调用；业务阶段与参数由上层装配。 | [data/validate/aligned.py](../packages/ai4e-core/abilities/data/validate/aligned.py) |
| A013 | 字段来源与行身份检查 | 同组数量、归属与行身份校验，返回可记录的报告。 | `ValidationIssue`<br>`ValidationReport`<br>`FieldValidationError`<br>`validate_records`<br>`require_valid_records` | 按显式输入调用；业务阶段与参数由上层装配。 | [data/validate/fields.py](../packages/ai4e-core/abilities/data/validate/fields.py) |
| A014 | 数据、文件与源码摘要 | 只读内容摘要：比较输入、权重和来源，不采样、不修改随机流。 | `fingerprint`<br>`file_fingerprint`<br>`source_fingerprint` | 按显式输入调用；业务阶段与参数由上层装配。 | [data/validate/fingerprint.py](../packages/ai4e-core/abilities/data/validate/fingerprint.py) |
| A015 | 输出规划与覆盖预检 | 无写入的输出规划，供 dry-run 和提交共用。 | `validate_filemap`<br>`validate_destination`<br>`plan_output` | 按显式输入调用；业务阶段与参数由上层装配。 | [data/validate/output.py](../packages/ai4e-core/abilities/data/validate/output.py) |
| A016 | 模型输入与物理域绑定检查 | 物理域与模型字段绑定检查，禁止跨域同形数组静默错配。 | `validate_bindings` | 按显式输入调用；业务阶段与参数由上层装配。 | [data/validate/physical.py](../packages/ai4e-core/abilities/data/validate/physical.py) |

### 数据：标记与筛选

| 编号 | 能力 | 做什么 | 当前入口（类后括号为公开方法） | 范围与边界 | 源码 |
| --- | --- | --- | --- | --- | --- |
| A017 | 表面重合点标记 | 用精确坐标标出不与表面重合的体积点，不删点。 | `exterior_mask` | 精确坐标相等；输出 mask，不删点。 | [data/filter/coincident.py](../packages/ai4e-core/abilities/data/filter/coincident.py) |
| A018 | 具名字段与身份同步筛选 | 对已声明身份的点组统一筛选，保留原数组与原 ID。 | `filter_records` | 点 mask 不适用于 CellData；同步保留身份。 | [data/filter/records.py](../packages/ai4e-core/abilities/data/filter/records.py) |
| A019 | 多数组同步筛选 | 按布尔 mask 沿首维筛选一组对齐数组，不改原数组。 | `apply_aligned_mask` | 按显式输入调用；业务阶段与参数由上层装配。 | [data/filter/select.py](../packages/ai4e-core/abilities/data/filter/select.py) |
| A020 | 网格有效顶点标记 | 用 VTK 单元类型和点号生成有效点 mask。 | `resolve_cell_type`<br>`used_vertex_mask` | 输出 mask，不直接删除原网格顶点。 | [data/filter/used_vertices.py](../packages/ai4e-core/abilities/data/filter/used_vertices.py) |

### 数据：编码与保存

| 编号 | 能力 | 做什么 | 当前入口（类后括号为公开方法） | 范围与边界 | 源码 |
| --- | --- | --- | --- | --- | --- |
| A021 | NPY 与 JSON 原子保存 | 数组数据产物原子写入；不负责运行日志或运行配置。 | `atomic_path`<br>`save_npy`<br>`save_json` | 数据目录写入；不接管 run 日志和配置。 | [data/save/arrays.py](../packages/ai4e-core/abilities/data/save/arrays.py) |
| A022 | 字段编码为张量 | 把具名场记录编码为 float32 张量。 | `encode_field` | 按显式输入调用；业务阶段与参数由上层装配。 | [data/save/encode.py](../packages/ai4e-core/abilities/data/save/encode.py) |
| A023 | 冻结变换保存与归一化物化 | 归一化方法记录：版本目录内原子提交，不覆盖不同变换。 | `save_record`<br>`materialize` | 冻结记录与可选数据物化是两种操作。 | [data/save/normalization.py](../packages/ai4e-core/abilities/data/save/normalization.py) |
| A024 | 张量和张量包读写 | 具名张量目录提交；覆盖失败恢复旧目录，不承担业务字段选择。 | `BackupCleanupWarning`<br>`write_tensor_file`<br>`write_named_tensors`<br>`load_named_tensor`<br>`load_named_tensors` | 逻辑名与文件由调用方声明；提供提交失败恢复。 | [data/save/store.py](../packages/ai4e-core/abilities/data/save/store.py) |
| A025 | 保留拓扑与身份的 VTKHDF 导出 | VTKHDF 公共网格写出：保留拓扑、具名场及原实体身份。 | `write_vtkhdf` | 受支持网格；未选实体回贴为 NaN。 | [data/save/vtkhdf.py](../packages/ai4e-core/abilities/data/save/vtkhdf.py) |

### 数据：统计量

| 编号 | 能力 | 做什么 | 当前入口（类后括号为公开方法） | 范围与边界 | 源码 |
| --- | --- | --- | --- | --- | --- |
| A026 | 具名字段流式统计 | 具名数组流统计；不读取样本目录、不解释训练分片或物理字段名。 | `fit_statistics` | 只消费数组流；训练分片选择由上层负责。 | [data/stats/fit.py](../packages/ai4e-core/abilities/data/stats/fit.py) |
| A027 | 统计量文件读写 | 读入或写出统计量文件。 | `load_statistics`<br>`write_statistics` | 按显式输入调用；业务阶段与参数由上层装配。 | [data/stats/load.py](../packages/ai4e-core/abilities/data/stats/load.py) |
| A028 | 总体矩流式累计 | 沿实体首维流式累计总体矩，保留尾维而不合并实体和通道。 | `accumulate_moments` | 按显式输入调用；业务阶段与参数由上层装配。 | [data/stats/moments.py](../packages/ai4e-core/abilities/data/stats/moments.py) |
| A029 | 物理视图训练统计冻结 | 按具名物理视图拟合训练变换，点和样本使用不同统计单位。 | `freeze` | 点场按点累计、工况按样本累计。 | [data/stats/physical.py](../packages/ai4e-core/abilities/data/stats/physical.py) |
| A030 | 总体矩累计器 | 总体矩累计；明确保持逐数组 float64 求和顺序用于参考对照。 | `PopulationMoments`（`update`, `finalize`） | 按显式输入调用；业务阶段与参数由上层装配。 | [data/stats/population.py](../packages/ai4e-core/abilities/data/stats/population.py) |

### 变换

| 编号 | 能力 | 做什么 | 当前入口（类后括号为公开方法） | 范围与边界 | 源码 |
| --- | --- | --- | --- | --- | --- |
| A031 | 坐标范围归一化与逆变换 | 共享边界坐标缩放：正反变换与显式范围门禁。 | `CoordinateNormalization`（`apply`, `inverse`） | 按显式输入调用；业务阶段与参数由上层装配。 | [transform/coordinate_normalization.py](../packages/ai4e-core/abilities/transform/coordinate_normalization.py) |
| A032 | 点场通道整理与显式零场 | 点场通道整理与显式零场派生，不绑定场名或领域。 | `prepare_fields` | 按显式输入调用；业务阶段与参数由上层装配。 | [transform/fields.py](../packages/ai4e-core/abilities/transform/fields.py) |
| A033 | 冻结归一化组合与重建 | 具名场的冻结变换组合与可序列化重建，不感知领域、数据集或运行目录。 | `Identity`（`apply`, `inverse`）<br>`Normalization`（`record`, `digest`, `apply`, `inverse`） | 按显式输入调用；业务阶段与参数由上层装配。 | [transform/normalization.py](../packages/ai4e-core/abilities/transform/normalization.py) |
| A034 | 工况与点标签标准化 | 具名工况与点标签的冻结 float32 标准化能力。 | `FieldNormalization`（`apply`, `inverse`） | 按显式输入调用；业务阶段与参数由上层装配。 | [transform/pointfields.py](../packages/ai4e-core/abilities/transform/pointfields.py) |
| A035 | 均值标准差变换与逆变换 | 均值标准差变换：参数校验与可微正反变换。 | `Standardization`（`apply`, `inverse`） | 按显式输入调用；业务阶段与参数由上层装配。 | [transform/standardization.py](../packages/ai4e-core/abilities/transform/standardization.py) |

### 几何

| 编号 | 能力 | 做什么 | 当前入口（类后括号为公开方法） | 范围与边界 | 源码 |
| --- | --- | --- | --- | --- | --- |
| A036 | 点到网格表面距离 | 体积点到网格表面的有符号距离；先校验全部单元为支持的二维面。 | `mesh_signed_distance` | 输入须为支持的二维面网格；与最近顶点距离不同。 | [geometry/mesh_sdf.py](../packages/ai4e-core/abilities/geometry/mesh_sdf.py) |
| A037 | 点到最近表面顶点距离 | 体积点到最近表面顶点的非负距离与方向。 | `nearest_vertex_distance_and_direction` | 最近顶点非负欧氏距离，不是点到面距离。 | [geometry/nearest.py](../packages/ai4e-core/abilities/geometry/nearest.py) |
| A038 | 二维表面门禁与私有副本 | 完整 VTK 表面的公共门禁与私有工作副本，转换中保留原点身份。 | `PreparedSurface`<br>`require_surface_mesh`<br>`prepare_surface` | 不从体网格自动提取外壳。 | [geometry/surface.py](../packages/ai4e-core/abilities/geometry/surface.py) |
| A039 | 表面点法向与有效性 | 表面法向按原始点身份回贴，孤立点以零值及有效性 mask 表达。 | `surface_point_normals_with_mask`<br>`surface_point_normals` | 原点序返回；孤立点为零并带无效标记。 | [geometry/surface_normals.py](../packages/ai4e-core/abilities/geometry/surface_normals.py) |

### 采样

| 编号 | 能力 | 做什么 | 当前入口（类后括号为公开方法） | 范围与边界 | 源码 |
| --- | --- | --- | --- | --- | --- |
| A040 | 无放回抽点与字段联动 | 无放回抽点与独立可复现随机流，不绑定模型字段。 | `point_indices`<br>`select_aligned` | 无放回；不含曲率自适应或通用重要性采样。 | [sampling/points.py](../packages/ai4e-core/abilities/sampling/points.py) |
| A041 | 跨步分块与原点序恢复 | 跨步分块与点序恢复；数据字段始终共用原始点下标。 | `indices`<br>`reconstruct` | 跨步分块；回填拒绝缺块和重复覆盖。 | [sampling/stride.py](../packages/ai4e-core/abilities/sampling/stride.py) |

### 模型构造与通用网络组件

| 编号 | 能力 | 做什么 | 当前入口（类后括号为公开方法） | 范围与边界 | 源码 |
| --- | --- | --- | --- | --- | --- |
| A042 | 注入构造器创建模型 | 模型构造与重建信息，参数语义由模型组件定义。 | `construct` | 按显式输入调用；业务阶段与参数由上层装配。 | [modeling/construction.py](../packages/ai4e-core/abilities/modeling/construction.py) |
| A043 | 前馈 MLP 组件 | 线性层、GELU 与线性层组成的前馈网络。 | `Mlp`（`forward`） | 模型内部组件；并非完整可训练模型。 | [modeling/modules/feed_forward.py](../packages/ai4e-core/abilities/modeling/modules/feed_forward.py) |
| A044 | 连续位置编码与 RoPE 频率 | 连续坐标正余弦嵌入，以及用于旋转位置编码的频率构造。 | `ContinuousSincosEmbed`（`forward`）<br>`RopeFrequency`（`forward`） | 模型内部组件；仅实现声明支持的模式。 | [modeling/modules/position_encoding.py](../packages/ai4e-core/abilities/modeling/modules/position_encoding.py) |
| A045 | 模型输入与批次预检 | 模型要求预检，不推断或转换模型的数据布局。 | `validate_inputs` | 按显式输入调用；业务阶段与参数由上层装配。 | [modeling/requirements.py](../packages/ai4e-core/abilities/modeling/requirements.py) |
| A046 | 初始权重加载与参数冻结 | 初始状态字典加载与参数冻结，完整续训由训练层负责。 | `initialize_weights` | 加载初始权重与冻结；完整续训在 training。 | [modeling/weights.py](../packages/ai4e-core/abilities/modeling/weights.py) |

### 监督约束

| 编号 | 能力 | 做什么 | 当前入口（类后括号为公开方法） | 范围与边界 | 源码 |
| --- | --- | --- | --- | --- | --- |
| A047 | 同形张量监督比较 | 同形张量的比较方法；供监督项选用，不解释场名。 | `compare` | MSE、MAE、Huber、relative L2；目标范数过小时相对 L2 失败。 | [constraint/compare.py](../packages/ai4e-core/abilities/constraint/compare.py) |
| A048 | 具名监督项与权重聚合 | 严格形状的监督比较与可配置权重。 | `supervised`<br>`supervised_mse` | 监督约束；不表示 PDE、边界条件或守恒损失已实现。 | [constraint/supervised.py](../packages/ai4e-core/abilities/constraint/supervised.py) |

### 训练

| 编号 | 能力 | 做什么 | 当前入口（类后括号为公开方法） | 范围与边界 | 源码 |
| --- | --- | --- | --- | --- | --- |
| A049 | 拼批、几何索引偏移与设备交接 | 收批原语：密集堆叠、稀疏拼接与局部索引偏移。 | `stack`<br>`concatenate_geometry`<br>`to_device` | 按显式输入调用；业务阶段与参数由上层装配。 | [training/batch.py](../packages/ai4e-core/abilities/training/batch.py) |
| A050 | 训练周期回调 | 训练周期回调：普通可调用对象，不要求继承框架基类。 | `PeriodicCallback` | 按显式输入调用；业务阶段与参数由上层装配。 | [training/callbacks.py](../packages/ai4e-core/abilities/training/callbacks.py) |
| A051 | 训练状态捕获与恢复 | 轮次边界状态打包与严格兼容恢复。 | `capture`<br>`restore`<br>`restore_selection` | 恢复核对语义；轮次边界恢复不等于任意 batch 精确恢复。 | [training/checkpoint.py](../packages/ai4e-core/abilities/training/checkpoint.py) |
| A052 | 参数量、内存与进度诊断 | 训练诊断：规模、参数量、峰值内存与条件预计剩余时间。 | `parameter_count`<br>`peak_memory`<br>`report_setup`<br>`report_progress` | 按显式输入调用；业务阶段与参数由上层装配。 | [training/diagnostics.py](../packages/ai4e-core/abilities/training/diagnostics.py) |
| A053 | 可恢复训练循环 | 默认轮次循环：有效更新、评估、信号收尾及检查点策略。 | `fit` | 完整执行能力，内部包含循环；不是单个数学算子。 | [training/loop.py](../packages/ai4e-core/abilities/training/loop.py) |
| A054 | 模型参数指数移动平均 | 模型参数的指数移动平均，仅在有效优化器更新后推进。 | `MovingAverage`（`update`） | 按显式输入调用；业务阶段与参数由上层装配。 | [training/moving_average.py](../packages/ai4e-core/abilities/training/moving_average.py) |
| A055 | 在线损失窗口统计 | 在线损失窗口：每批记账，冲刷得到窗口平均。 | `OnlineLoss`（`empty`, `record`, `flush`） | 按显式输入调用；业务阶段与参数由上层装配。 | [training/online.py](../packages/ai4e-core/abilities/training/online.py) |
| A056 | 优化器构造与参数更新 | 显式设备、可换优化器与单次参数更新。 | `Lion`（`step`）<br>`resolve_device`<br>`build_optimizer`<br>`parameter_groups`<br>`update` | Adam、AdamW、Lion；清梯度、反向、缩放解除、裁剪与更新。 | [training/optimization.py](../packages/ai4e-core/abilities/training/optimization.py) |
| A057 | 学习率调度与更新步数 | 公开学习率调度：按名构造，绑定总有效更新步。 | `total_updates`<br>`build_scheduler` | constant/none、cosine、warmup_cosine。 | [training/schedule.py](../packages/ai4e-core/abilities/training/schedule.py) |
| A058 | 预测与目标字段分流 | 预测与目标分流：缺键或多键发警告，不补默认值。 | `route` | 缺失/额外字段发警告；监督门禁继续负责拒绝无效计算。 | [training/split.py](../packages/ai4e-core/abilities/training/split.py) |

### 推理

| 编号 | 能力 | 做什么 | 当前入口（类后括号为公开方法） | 范围与边界 | 源码 |
| --- | --- | --- | --- | --- | --- |
| A059 | 模型上下文分块查询 | 通过注入的模型上下文执行分块查询，并保证异常时释放资源和恢复模式。 | `query_model` | 算法上下文由调用方注入；异常时释放缓存并恢复模式。 | [inference/query.py](../packages/ai4e-core/abilities/inference/query.py) |
| A060 | 推理随机流隔离与临时种子 | 独立推理的可复现随机上下文，不读取训练状态或改变调用方随机流。 | `preserve_randomness`<br>`seeded_randomness` | 按显式输入调用；业务阶段与参数由上层装配。 | [inference/randomness.py](../packages/ai4e-core/abilities/inference/randomness.py) |
| A061 | 从检查点重建推理模型 | 推理检查点重建：只迁移模型权重，不恢复训练进度。 | `rebuild` | 仅恢复权重；不恢复优化器和训练进度。 | [inference/rebuild.py](../packages/ai4e-core/abilities/inference/rebuild.py) |
| A062 | 流式推理生命周期 | 流式推理执行；模型组件拥有算法，框架拥有模式和资源边界。 | `predict_stream` | 专用推理算法由模型组件提供。 | [inference/stream.py](../packages/ai4e-core/abilities/inference/stream.py) |

### 评估

| 编号 | 能力 | 做什么 | 当前入口（类后括号为公开方法） | 范围与边界 | 源码 |
| --- | --- | --- | --- | --- | --- |
| A063 | 共享模型评估 | 共享评估执行，保证结束和异常时恢复模型模式与随机流。 | `evaluate` | 按显式输入调用；业务阶段与参数由上层装配。 | [eval/evaluation.py](../packages/ai4e-core/abilities/eval/evaluation.py) |
| A064 | 完整场误差累计 | 物理场总误差累计；标量场与声明的向量模长分别统计。 | `FieldTotals`（`update`, `finalize`） | 按显式输入调用；业务阶段与参数由上层装配。 | [eval/field_totals.py](../packages/ai4e-core/abilities/eval/field_totals.py) |
| A065 | 逐样本物理场指标 | 逐样本物理场指标；零目标范数显式计为相对误差不可用。 | `field_metrics` | MSE、MAE、relative L2；零真值范数的相对误差不可用。 | [eval/metrics.py](../packages/ai4e-core/abilities/eval/metrics.py) |
| A066 | 具名物理指标累计 | 通用具名物理指标，累计元素而不是平均样本指标。 | `PhysicalMetrics`（`update`, `finalize`） | 按元素累计，不直接平均各样本指标。 | [eval/physical.py](../packages/ai4e-core/abilities/eval/physical.py) |
| A067 | 逐点监督评估 | 逐点监督评估；按实际元素累计，保留参考浮点运算空间。 | `evaluate` | 按显式输入调用；业务阶段与参数由上层装配。 | [eval/pointwise.py](../packages/ai4e-core/abilities/eval/pointwise.py) |

### 后处理

| 编号 | 能力 | 做什么 | 当前入口（类后括号为公开方法） | 范围与边界 | 源码 |
| --- | --- | --- | --- | --- | --- |
| A068 | 原点匹配、比较网格与平面切割 | 共享几何上的模型比较、原点映射与物理平面切割。 | `match_points`<br>`attach_valid_mesh`<br>`cut_plane`<br>`surface`<br>`write_polydata` | 处理数值与拓扑；页面、图像和报告渲染在 viz。 | [postproc/comparison.py](../packages/ai4e-core/abilities/postproc/comparison.py) |
| A069 | 完整表面场 HDF5 与 VTP 导出 | 完整表面场导出；字段名由业务装配显式提供。 | `write_h5`<br>`write_vtp` | 按显式输入调用；业务阶段与参数由上层装配。 | [postproc/export/field_surface.py](../packages/ai4e-core/abilities/postproc/export/field_surface.py) |
| A070 | 预测回贴原始表面与体网格 | 把预测场写回原始网格，并按模版门禁验收表面 VTP 与体积 VTU。 | `extract_point_field`<br>`write_surface_mesh`<br>`surface_mesh_point_count`<br>`write_volume_mesh`<br>`verify_mesh_outputs` | 按显式输入调用；业务阶段与参数由上层装配。 | [postproc/export/mesh.py](../packages/ai4e-core/abilities/postproc/export/mesh.py) |
| A071 | 锚点点云导出 | 把锚点坐标与具名场写成带独立顶点单元的 VTK 点云。 | `write_pointcloud` | 每点有顶点单元的点云；不代表原始表面网格。 | [postproc/export/pointcloud.py](../packages/ai4e-core/abilities/postproc/export/pointcloud.py) |
| A072 | 表面拓扑描述、面积与朝向 | 表面拓扑描述、面积比与朝向；保持参考几何算法次序。 | `SurfaceTopology`（`face_count`, `euler_characteristic`）<br>`surface_area_ratio`<br>`orient_topology` | 现有实现具有 NASA 表面数据语义，不视为任意网格修复器。 | [postproc/surface_geometry.py](../packages/ai4e-core/abilities/postproc/surface_geometry.py) |

### 贡献模型：AB-UPT

| 编号 | 能力 | 做什么 | 当前入口（类后括号为公开方法） | 范围与边界 | 源码 |
| --- | --- | --- | --- | --- | --- |
| A073 | AB-UPT 专用拼批 | 按固定域布局收批，支持不等几何点数和独立目标。 | `collate` | 模型专用实现；不自动成为 core 通用能力。 | [model/abupt/batch.py](../packages/ai4e-contrib/ability/model/abupt/batch.py) |
| A074 | AB-UPT 组件公开门面 | AB-UPT 组件公开出口；保留原构造器身份与数值行为。 | `training_parameters` | 门面复用其他文件能力；不重复计为新增算法。 | [model/abupt/component.py](../packages/ai4e-contrib/ability/model/abupt/component.py) |
| A075 | AB-UPT 有序域布局 | AB-UPT 有序域、字段及 token 输入契约，不依赖框架配置系统。 | `DomainLayout`（`split`） | 模型专用实现；不自动成为 core 通用能力。 | [model/abupt/domains.py](../packages/ai4e-contrib/ability/model/abupt/domains.py) |
| A076 | AB-UPT 推理缓存与分块上下文 | 仅限无梯度评估的模型绑定缓存与分块查询生命周期。 | `model_signature`<br>`ModelCache`（`validate`, `geometry_only`）<br>`InferenceContext`（`query`, `chunks`, `close`） | 无梯度、进程内缓存；不能序列化为检查点。 | [model/abupt/inference.py](../packages/ai4e-contrib/ability/model/abupt/inference.py) |
| A077 | AB-UPT 构造、前向与结构描述 | 贡献多域 AB-UPT 的显式构造及无缓存训练入口。 | `construct`<br>`predict`<br>`describe` | 模型专用实现；不自动成为 core 通用能力。 | [model/abupt/model.py](../packages/ai4e-contrib/ability/model/abupt/model.py) |
| A078 | AB-UPT 域注意力、调制与输出头 | 共享权重的域注意力、条件调制与独立 K/V 投影。 | `Modulation`（`forward`）<br>`initialize_linear`<br>`KVProjection`（`forward`）<br>`DomainBlock`（`heads_view`, `project_kv`, `forward`, `forward_domains`）<br>`DomainReadout`（`out_features`, `forward`） | 模型专用实现；不自动成为 core 通用能力。 | [model/abupt/modules/blocks/domain.py](../packages/ai4e-contrib/ability/model/abupt/modules/blocks/domain.py) |
| A079 | AB-UPT 旋转位置编码 | 在输入设备上执行复数旋转，保留同设备反向传播。 | `rope` | 模型专用实现；不自动成为 core 通用能力。 | [model/abupt/modules/rope.py](../packages/ai4e-contrib/ability/model/abupt/modules/rope.py) |
| A080 | AB-UPT 超节点池化 | 基于位置、邻域检索和消息聚合构造超节点特征。 | `SupernodePoolingPosonly`（`compute_src_and_dst_indices`, `create_messages`, `accumulate_messages`, `forward`） | radius/k 邻域；abspos/relpos 模式；MPS 邻域检索经 CPU。 | [model/abupt/modules/supernode_pooling_posonly.py](../packages/ai4e-contrib/ability/model/abupt/modules/supernode_pooling_posonly.py) |
| A081 | AB-UPT 多域完整网络 | AB-UPT 多域骨干：显式域布局、条件调制与逐层推理缓存。 | `AnchoredBranchedUPT`（`train`, `forward`） | 完整模型；布局与结构版本受约束，不接受旧双域扁平参数。 | [model/abupt/network.py](../packages/ai4e-contrib/ability/model/abupt/network.py) |
| A082 | AB-UPT 物理样本准备、监督与全点预测 | AB-UPT 在物理数据视图上的输入准备与完整域查询。 | `prepare_sample`<br>`loss`<br>`predict_sample` | 模型专用实现；不自动成为 core 通用能力。 | [model/abupt/preparation.py](../packages/ai4e-contrib/ability/model/abupt/preparation.py) |
| A083 | AB-UPT 按域采样与字段绑定 | 按域绑定字段、独立抽点、样本级条件与监督目标准备。 | `prepare_inputs` | 模型专用实现；不自动成为 core 通用能力。 | [model/abupt/sampling.py](../packages/ai4e-contrib/ability/model/abupt/sampling.py) |

### 贡献模型：Transolver-3

| 编号 | 能力 | 做什么 | 当前入口（类后括号为公开方法） | 范围与边界 | 源码 |
| --- | --- | --- | --- | --- | --- |
| A084 | Transolver-3 物理状态缓存与解码网络 | 将物理状态缓存与完整网格解码分为两个网络。 | `PhysicalStateCachingModel`（`forward`）<br>`FullMeshDecodingModel`（`forward`） | 模型专用实现；不自动成为 core 通用能力。 | [model/transolver3/amortize.py](../packages/ai4e-contrib/ability/model/transolver3/amortize.py) |
| A085 | Transolver-3 组件公开门面与默认值 | Transolver 组件出口和参考案例默认值；不持有工作流循环。 | `resolve`<br>`training_parameters` | 当前参考入口限制 batch=1、workers=0、fp32、AdamW 等；不是任意组合承诺。 | [model/transolver3/component.py](../packages/ai4e-contrib/ability/model/transolver3/component.py) |
| A086 | Transolver-3 全表面缓存推理 | 全表面物理状态缓存与解码；保留参考逐层、逐块计算顺序。 | `SurfaceInference`（`predict`） | 模型专用实现；不自动成为 core 通用能力。 | [model/transolver3/inference.py](../packages/ai4e-contrib/ability/model/transolver3/inference.py) |
| A087 | Transolver-3 构造、前向与结构描述 | Transolver 公开适配：具名输入输出，不向框架泄露列表式调用。 | `construct`<br>`describe`<br>`predict` | 模型专用实现；不自动成为 core 通用能力。 | [model/transolver3/model.py](../packages/ai4e-contrib/ability/model/transolver3/model.py) |
| A088 | Transolver-3 完整网络与内部块 | Transolver 分块网络；保留锁定参考算法和参数注册次序。 | `Physics_Attention_Irregular_Mesh`（`forward`, `chunk_stats`, `slice_attend`, `chunk_weights`, `chunk_deslice_to_out`）<br>`MLP`（`forward`）<br>`Transolver_block`（`forward`, `forward_chunks`）<br>`Model`（`initialize_weights`, `forward`） | 模型内部类与完整网络并列；仅支持源码已实现的选项。 | [model/transolver3/network.py](../packages/ai4e-contrib/ability/model/transolver3/network.py) |
| A089 | Transolver-3 物理样本准备、监督与全点预测 | Transolver 点场绑定与跨步数据组织；不识别具体数据集名称。 | `domain_binding`<br>`arrays`<br>`prepare_sample`<br>`loss`<br>`predict_sample` | 一次训练一个显式域；全域预测恢复原点序。 | [model/transolver3/preparation.py](../packages/ai4e-contrib/ability/model/transolver3/preparation.py) |

## 组件门面的复用出口

下列出口由 component 汇集，实际实现已在上表中列出，不重复计数。

| 门面 | 再导出或绑定的入口 | 边界 |
| --- | --- | --- |
| AB-UPT component | `construct`、`describe`、`predict`、`collate`、`prepare_inputs`、`InferenceContext`、`resolve`、`prepare_sample`、`loss`、`predict_sample`、`training_parameters` | `resolve` 当前复用 aero_cfd application 的默认展开；其余主体按源码链接查阅。 |
| Transolver-3 component | `construct`、`describe`、`predict`、`SurfaceInference`、`resolve`、`prepare_sample`、`loss`、`predict_sample`、`training_parameters` | 默认展开与参考配置门禁属于该模型入口；模型内部算法没有单独变成工作流节点。 |

## 占位、未列入和容易混淆的范围

| 项目 | 当前归属或边界 |
| --- | --- |
| core abilities/report | 当前未找到 Python 实现文件；不列作已实现报告能力。 |
| PDE、边界条件、守恒约束损失 | 当前 constraint 实现为监督比较；不列作已交付物理约束。 |
| 完整 AB-UPT / Transolver-3 | 在 contrib ability；core modeling 提供构造、权重、预检与少量网络组件。 |
| rawprep / trainprep / model / train / post | application 业务装配分类，不是五个底层 ability。 |
| 数据集样本发现、NASA / ShapeNet 来源适配 | 属于 application / contrib application，不混入本表；本表的 read_tree 只读取目录文件。 |
| Stage / Pipeline、run 写入与执行、task 管理 | 位于 abilities 之外，不计为本表能力。 |
| 图像、报告页面和独立文件预览 | 在 ai4e-viz 等模块；本表 postproc 主要交付数值、拓扑及文件。 |
| 通用 DAG、节点调度、任意 Python 与图双向转换 | 本表不作为这些工作流功能的交付证明。 |

## 核查方法与验收入口

- 扫描两个能力目录的全部 Python 文件，读取模块和公开声明，并针对方法选项、模型门面与实现限制核对源码。
- 文档检查覆盖实现文件遗漏、直接定义的公开入口遗漏、仓内链接及索引发现性；不导入模型、不执行计算。
- 文档相关检查：`uv run pytest tests/integration/test_ability_inventory_document.py`。
- 原有功能验收范围继续以 AGENTS 与相应 `.context/mvp/*acceptance.md` 为准。

## 本次简表核对时补录的实现

保留 A001–A089 原编号，新增四项编号；当前共 93 项实现模块，属于源码补录，未重新运行算法验收。

| 编号 | 能力 | 做什么 | 当前入口 | 范围与边界 | 源码 |
| --- | --- | --- | --- | --- | --- |
| A090 | Zarr 张量读写 | 具名张量或独立成员映射的 Zarr 编码与读回。 | `write_zarr`<br>`read_zarr` | 保持 dtype/形状；目录事务由 store 提供。 | [data/save/zarr.py](../packages/ai4e-core/abilities/data/save/zarr.py) |
| A091 | 模型结构查看 | 以真实输入执行 TorchVista 并发布 HTML 与来源记录。 | `trace` | 需要可执行的模型和输入；不把跟踪成功当数值正确性证明。 | [modeling/inspection.py](../packages/ai4e-core/abilities/modeling/inspection.py) |
| A092 | MinMax 正反变换 | 以冻结最小最大边界执行缩放和物理量恢复。 | `MinMax`（`apply`, `inverse`） | 常量分量有明确处理；范围检查不自动截断。 | [transform/minmax.py](../packages/ai4e-core/abilities/transform/minmax.py) |
| A093 | 同实体场差值 | 校验单位、身份、坐标和拓扑后计算 left-right，支持文件交付。 | `difference`<br>`compare_files` | 严格匹配，不插值、不配准。 | [postproc/difference.py](../packages/ai4e-core/abilities/postproc/difference.py) |
