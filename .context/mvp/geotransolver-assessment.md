# GeoTransolver 集成前评估（2026-09-20）

> **20 GB 本机约束更新：**下文第 1–5 节保留最初针对用户提供的 v2 PDF 的评估。新增约束后，不再推荐 DrivAerML 作为本机首例；最新 v3 增加了小型保险杠碰撞实验，详见第 6 节。源码迁移仍是后续目标，本轮尚未实现。

## 结论与范围

**技术上适合接入 Dojo 的外流 CFD 应用，但当前只完成准入与方案评估，尚不满足正式迁移前的原实现复现门槛。** 推荐先做 DrivAerML 表面压力/壁面剪切应力，再扩展 DrivAerML 体场，最后核对 SHIFT-SUV / SHIFT-Wing。这不是已决定落地的实施计划，不套实施计划骨架；以下目录和新增接口均为建议，不代表已经实现。

本轮依照 `dojo-integrate-model` 阅读论文、参考源码及 Dojo 框架，检查公开数据入口、分片名单、配置与消费链；未下载完整样本，未执行模型前后向、训练、精度评价或安装测试。未修改算法、依赖、recipe 或正式服务。仓库已有未提交改动保留。正式 8000/5173 发布与 Web 冒烟在此次纯评估中不适用。

三项准入分别为：

- **数据：部分确认。** DrivAerML 非 gated，真实 VTP 的 1 KiB 范围读取返回 206；完整解码、字段/拓扑和全部分片可用性未验。SHIFT 两套数据均 manual gated，匿名 README 返回 401，当前不能认定可取得并可用。
- **指标：有明确论文目标，仍有口径歧义。** 主表数值、R² 与相对 L1 区分已确认；模型版本、部分超参数、体场压力参考值及归约协议需闭合。
- **源码：有正式模型及训练/推理/指标链。** 本地 PhysicsNeMo 为论文之后的版本，不能直接认定当前默认配置就是论文实验。数据预处理还需固定对应 Curator 或等价参考流程。

因此可以继续原实现准备与验证；不应直接宣称“准入全部通过”“模型已接入”或“论文可复现”。

## 1. 来源与实验身份

- 用户论文：`/Users/zonghui/Downloads/geotransolver.pdf`，20 页，arXiv:2512.20399v2，2025-12-24；SHA256 `355c590b7a6a2acbcb5df94c89dbb40656cd0d06b3984932fbf356003d9ca2d7`。正文与实验表已读取，表 1/5/6 所在页面另经渲染核对。
- 参考源码：`/Users/zonghui/work/new_code_project/physicsnemo`，HEAD `aa19b58a129f8d1fabdcaa41c6ca85d5dc01aae1`（2026-08-28）；本次检查只见未跟踪 `.DS_Store`，无已跟踪源码修改。
- 额外找到本地评测仓库：`/Users/zonghui/work/new_code_project/GEO-transolver/physicsnemo-cfd`，HEAD `0612ec4ed54484a47bfa134eda7b3b012a607624`。仅作为分片和评测包装参考，本轮未全面审计它的工作树或证明与论文版本相同。
- Dojo HEAD `477c47bc4cba83fd1e903800034d7d58286ee6d8`，工作树有既有修改；本评估以读到的当前源码为准。
- 模型及涉及的 PhysicsNeMo 文件为 Apache-2.0。若迁入，保留许可、NOTICE、来源版本、实际文件摘要和修改说明。

关键源码入口（相对 PhysicsNeMo 根）：

- `physicsnemo/models/geotransolver/geotransolver.py`：模型构造、上下文生成、GALE 堆叠与输出。
- `physicsnemo/models/geotransolver/context_projector.py`：切片投影、双向多尺度几何编码、共享上下文。
- `physicsnemo/nn/module/gale.py`、`physicsnemo/nn/module/physics_attention.py`：切片、自/交叉注意力、门控和反切片。
- `physicsnemo/nn/module/ball_query.py`、`physicsnemo/nn/functional/neighbors/radius_search/`：邻域查询及 Warp/Torch 后端。
- `physicsnemo/datapipes/cae/transolver_datapipe.py`：实际使用的数据变换、采样、几何和标签反变换；不可只按示例旧 `preprocess.py` 推断。
- `examples/cfd/external_aerodynamics/transformer_models/src/`：`train.py`、`compute_normalizations.py`、`inference_on_zarr.py`、`inference_on_vtk.py`、`inference_utils.py`、`metrics.py` 及 `conf/`。
- `examples/cfd/external_aerodynamics/unified_external_aero_recipe/`：当前统一案例的另一条参考入口；不可混用两条入口的默认值。

Darcy 示例明确写 GeoTransolver 尚未充分测试；结构碰撞、跌落、LoRA、GP/UQ、FLARE、时间条件不属于这份论文的目标案例，首轮不纳入。

## 2. 数据选择与资源

### DrivAerML：推荐首例

论文 §4.1.1 描述 500 个几何，约 1.4–1.5 亿体单元、900–1000 万表面点/单元、约 30 万 STL 点。不能把训练时的查询点预算当作原始数据规模。

[数据官网](https://caemldatasets.org/drivaerml/) 当前指向 [Hugging Face 数据集](https://huggingface.co/datasets/neashton/drivaerml)，数据许可 CC-BY-SA-4.0。2026-09-20 API 返回 `gated=false`、revision `5d448b209bf654503c64ce7261c34fa125f46392`。仅检查元数据与文件头，未获取完整数据。

公开 `run_1` 文件大小（实际元数据；GB 为十进制）：

- `boundary_1.vtp`：659,606,189 字节，约 0.660 GB。
- `drivaer_1.stl`：142,385,186 字节，约 0.142 GB。
- `boundary_cell_area_1.npy`：35,312,508 字节；另有很小的 force/reference/geometry CSV。
- `volume_1.vtu.00.part` + `.01.part`：26,843,545,600 + 22,208,751,243 = 49,052,296,843 字节，约 49.05 GB。

这只是一个样本，不能当作全数据集实测总量。表面优先能显著减少首轮下载和预处理需求，但完整论文表面复现仍需完整训练/评价名单，不是少量样本短训。

论文给的旧 `workflows/bench_example/drivaer_ml_files` 在线路径已返回 404。本地 CFD 仓库现有 `workflows/benchmarking/drivaer_ml_files/`（另有 deprecated 副本）：README 说明 484 个可用案例，CSV 实数为 **436 train + 48 validation**；论文把后者用于 test 报告，含阻力两端 OOD。读取 ID 还需按其角色命名，不能重新随机划分为普通 80/10/10。

- `train.csv` SHA256：`00086d73a232153610e409d63b9cf76e018f768033725df31ae00c24cc35a1db`。
- `validation.csv` SHA256：`dff5297ade2bb179759bdb3d76bb943225769c8219b5bd644fca04eb43a82115`。
- 本轮检查记录数、run_idx 各自唯一且两表 ID 无交集；实施时还须验证缺失文件和论文原名单身份。
- 不拿新数据网站的其他 splits 自动替代论文指向的 drag-aware 分片；模型选优与最终 48 例评价的使用方式须记录。

### SHIFT-SUV / SHIFT-Wing：后续候选

- [SHIFT-SUV](https://huggingface.co/datasets/luminary-shift/SUV)：论文使用全尺寸 Estate/Fastback 共 1996 例，80/10/10，名单与其引用的 AB-UPT benchmark 一致；不是四个尺度组全部混训。
- [SHIFT-Wing](https://huggingface.co/datasets/luminary-shift/WING)：论文用 1698 例（Mach 0.5 为 1138，Mach 0.85 为 560），80/10/10；GeoTransolver 两 Mach 联合训练，加入 Mach/AoA 全局条件。
- API 均 `gated=manual`、`license=cc-by-nc-4.0`，匿名 README 401。元数据可见不等于文件下载权限已获得，本轮未检查用户已有授权账户。
- API revision：SUV `0e3cd52ebff445c8eecbc26a17b2480b7c7709b2`；WING `c7bac069721483dca53078ed6a0e7a737e21480f`。当前数据仓库可能大于论文子集，必须锁定样本身份。
- Dojo 现有 `nasa_crm` 适配器读取 `trainingData_NASA-CRM.h5` / `testData_NASA-CRM.h5` 等表面文件，不能因名称都有 NASA CRM 就当作 SHIFT-Wing 的原始 VTP/VTU、工况和分片。

在本轮限定的 Dojo 训练目录、Noether、AB-UPT 文件名检索中未找到对应原始 VTP/STL 样本；这不是全盘数据不存在的证明。

### 算力判断

论文 §4.2 是最高 500 epoch、单 NVIDIA GB200 节点；未给足以推算本机完整用时的记录。不能可靠承诺小时数或最低显存。

当前 Dojo 环境实测 Torch 2.14.0、Muon 存在、CUDA 不可用、MPS 可用；PhysicsNeMo、Warp、jaxtyping、tensorstore 未安装，einops/zarr 已有。只做环境查询，未同步或安装依赖。

当前 radius_search 有纯 Torch 回退，但其全量 cdist 不适合论文规模：60k 查询 × 300k 几何，仅单个 float32 距离矩阵就需 **72 GB**，尚不含梯度、邻域和模型；当前示例 200k × 300k 为 240 GB。CPU/MPS 小输入诊断不能替代 CUDA/Warp 完整复现。未来先在隔离 CUDA 环境固定原依赖并测真实吞吐/峰值显存，再估算预算；新运行与缓存遵守 `dojo_train/geotransolver/<实验名>/` 约定。

## 3. 论文目标及必须澄清的差异

### 建议首轮目标

论文表 1 的 DrivAerML 48 例：表面压力相对 L1 **2.86%**、壁面剪切应力 **4.90%**、阻力 **R² 0.996**、升力 **R² 0.991**。体场另报压力 **3.09%**、速度 **4.02%**。均为作者报告值，本轮没有复现结果。

表头笼统写 Relative L1，但 §4.3、§5.3.1 明确 CD/CL 列是 R²。不可把 0.996 写成阻力误差 0.996%。论文不同表对体场压力给 3.09%、3.01%，表 5 另有 2.96% 的配置；需按具体实验分别保留，不能挑最有利数字作为同一基线。

SHIFT 完整目标另按表 6–9 分车型/Mach 报告。表 6 的压力值极小且表头注明百分数；在压力基准、单位与评价代码确认前不自行改成小数比例。表 9 的 R² 只显示到 1.0，不能解释为逐值无误差。

### 当前源码与论文的差异/风险

1. **查询点与邻域预算。** 论文表 5 最佳表面配置 60k/300k；当前示例 `data/core.yaml` 为 200k 查询，GeoTransolver 为 300k 几何。六尺度 radii `[0.01,0.05,0.25,1,2.5,5]` 相符，但源码逐尺度邻居 `[4,8,16,64,128,256]` 与论文表 4 的 kernel size 8/16/32 不能直接一一对应。要追溯论文配置/权重身份，不猜 32 代表哪个参数。
2. **优化器要看执行。** `conf/training/base.yaml` 写 AdamW；`train.py:815` 起将二维参数交给 Muon，其他参数交给 AdamW，组成 CombinedOptimizer。Muon 使用 `adjust_lr_fn="match_rms_adamw"`，lr=1e-3、weight_decay=1e-4；StepLR 每 100 epoch ×0.5。迁移必须覆盖两套状态及调度。当前配置为 501 epoch，论文为 up to 500；需核生效循环和最终权重。
3. **精度和选优。** 当前 Geo 示例顶层 `precision=float32`、`compile=true`、`use_te=false`；README 的默认 bf16 描述不能取代入口实参。seed、检查点选择、分布式有效批量需写入复现合同。论文的 GB200 节点不等于单 GPU。
4. **局部编码不是可任意替换的池化。** 论文 §3 的表达式描述相对坐标/特征及不变 reducer；当前 GeometricFeatureProcessor 使用 BQ 返回坐标，按邻居顺序展平成 K×3 后过 MLP+tanh。顺序、截断和补零影响输出；不能直接拿 Dojo/AB-UPT 半径图或 kNN+mean 当作等价替换。
5. **门控并不完全符合公式表述。** 论文式 (12) 写依赖 Pool(SA)/Pool(C) 的 gating network；当前 GALE weighted 模式为每层可学习标量 `state_mixing` 的 sigmoid。先建立版本差异清单，不擅自按公式改原代码并仍称原实现复现。
6. **SDF 与法向需保留算法语义。** 体场使用 winding-number SDF/最近面点；现有 Dojo VTK SDF 依赖面绕序。坐标先平移再按 `[12,4.5,3.25]` 缩放，半径在该坐标空间解释。不能直接混用未缩放几何、物理长度半径或最近顶点距离。
7. **分块是算法输入的一部分。** 当前 `batched_inference_loop` 随机排列查询，再按块独立前向；context 构建也依赖该块局部位置。必须记录随机流、几何采样、查询预算与逆序回贴，不能套 Transolver-3 的全场状态缓存，也不能承诺改变块大小不改变预测。
8. **指标需独立复算。** 当前 `metrics.py` 对剪切/速度的整体指标先求向量模长，再算模长差，不等同向量差的 L1。surface 推理拼回完整预测后重新算指标；通用分块 helper 则点数加权平均块内相对误差，volume 路径需与论文评测再对齐。论文式 (16) 与文字“样本平均”的归约层级存在歧义，应同时保留逐例分子/分母以支持复核。
9. **力与系数分开。** 当前表面示例 `coeff=1.0` 并恢复 rho/U 尺度后调用力积分，变量虽名 coeff，也不能未经核实便标成标准无量纲 CD/CL。须明确压力参考 p∞、面法向/面积、剪切符号、流向、参考面积和动压；R² 高不证明系数单位正确。

本轮确认的是差异和待验证风险，不把未执行的数值路径直接判作算法 bug。

## 4. 推荐分层接入方式

**原实现基线阶段**使用独立固定版本的 PhysicsNeMo 环境；**正式迁移阶段**推荐将可中立化能力提炼进 core，完整 GeoTransolver 装配及专属状态留 contrib。不让 Dojo core 依赖整套 PhysicsNeMo，也不以仅包装构造器作为交付。若保留外部模型包作研究连接，应明确这只是适配路径，尚未完成能力分层迁移。

### Core 能力：复用为主，按真实缺口新增

- `abilities/data/{source,extract,validate,filter,save,stats}`：复用 VTK/Zarr/数组、字段与实体身份校验、原子保存和统计；补原数据 cell-center/面积/字段读取需要的中立操作。rawprep 保留点/单元关系，不能把 CellData 静默变成 PointData。
- `abilities/geometry`：新增/扩展有明确语义的 radius-query（方向、顺序、邻居上限、padding）、必要的 winding-number SDF 后端；先与参考逐值/容差验证，不能默认现有 VTK 实现等价。
- `abilities/modeling/modules`：拟新增 learned slice/deslice、共享 context 交叉注意力与门控、多尺度邻域 MLP；可以用普通张量独立验证的部分归 core。已有 MLP 等仅在算术相同后复用。
- `abilities/sampling/transform`：复用身份索引与可逆变换，补与原入口一致的采样策略及坐标变换；字段单位与密度/速度无量纲化的绑定由应用提供。
- `abilities/training`：复用轮次执行、更新、检查点、RNG/调度恢复；补通用组合优化器或公开构造注入。当前 `build_optimizer` 不能只填一个字符串就复现 Muon+AdamW；参数分组属于模型连接。不要把原巨型训练脚本搬进 core。
- `abilities/eval/postproc/report`：复用固定数组 `evaluate_arrays` 的 scalar/magnitude `relative_mae`（即 L1 比值）、R²、样本聚合和表格/VTK。补中立压力/剪切面积积分；“跨样本力 R²”由应用装配，不误用单个场点上的 R²。

### Contrib：模型与数据语义

- 拟增 `ability/model/geotransolver/`：完整网络装配、维度与结构版本、原权重映射、来源/许可；尽量调用上述中立能力。模型专属 context 拼接与权重布局保留在此。
- 拟增 `application/aero_cfd/geotransolver/`：配置、模型输入/拼批、参数分组、原归一化协议、预测与分块连接。不要继承 Transolver-3 固定 stride=4、AdamW-only 或缓存推理限制。
- 拟增 `application/datasets/drivaerml/`：原 VTP/VTU/STL 与 CSV 分片、字段/单位/几何工况、官方缺例的明确记录。SHIFT 日后分别适配，不复用 NASA HDF5 名称掩盖数据差异。
- 表面模型输入：`local_embedding [B,N,6]`（xyz+单位法向）、`local_positions [B,N,3]`、`geometry [B,M,3]`、`global_embedding [B,1,2]`（当前 DrivAer 入口 rho/U）；输出 `[B,N,4]`（p/τx/τy/τz）。
- 体场当前入口 `[B,N,7]`（xyz/SDF/方向）→ `[B,N,5]`（ux/uy/uz/p/νt）；不能为匹配论文只报四个物理量而随意删掉训练输出 νt。
- SHIFT-Wing 条件须按 Mach/AoA 的真实来源重新绑定，不继续写死 DrivAer 的两个全局字段。

### Application / Recipe / Task

继续使用 `core/applications/aero_cfd` 的公开步骤；确有不足时增加中立注入点，不新增全仓组件协议或另一个 CFD 框架。

建议首例 `examples/aero_cfd/drivaerml_geotransolver_surface/`，必要时提供 `recipes/geotransolver/` 可复制正文。使用现有 `configuration.py`、`rawprep.py`、`trainprep.py`、`train.py`、`infer.py`、`post.py`、`pipeline.py` 约定，README 说明来源和复现范围；新增路径仍待实施设计确认。

交接链：

1. **rawprep**：只读官方输入，产出带样本 ID、cell ID、几何/拓扑/字段/工况与来源摘要的物理清单。原始处理失败不得发布完整成功清单。
2. **trainprep**：核字段、固定官方分片和训练统计，保存可反变换准备。不要将本次查询/几何采样预算错误冻结成通用准备的导入限制；预算属于生效模型/采样及复现记录。
3. **train**：显式构建模型、MSE、组合优化器、调度、评价和恢复，交给共享执行器；保存完整科学状态与有效配置。
4. **infer**：独立消费准备+权重，固定采样/块序，恢复物理量并按原 cell ID 保存预测、真值及网格。形状、单位或身份缺失时报错，不填零通过。
5. **post**：只读固定预测，计算论文指标、压力/剪切力分量、阻升力散点和场图；不用模型或重跑推理。派生字段须保存、读回并在下游使用。

Python 决定流程，YAML 只放参数；用 `inputs.<stage>.<name>` 与 `run_root/data_root`。从直接 `ai4e_core.run.launch` 到同目录 Task Python API 均须真实运行。Task 不加模型分支，不新增 `task-entry.json`。案例登记到 `examples/case-manifest.json` 并验证打包资源，但这不自动扩展 Web 官方目录。

## 5. 继续顺序与验收条件

1. **补齐复现合同**：确认 DrivAerML 表面为首目标；锁定原数据完整可用性、论文版本对应配置/预处理、436/48 名单、权重选择、精度、邻域与评测归约。先完成这些，才扩大数据和计算。
2. **原实现验证**：先真实样本完整读写、前后向和固定预测，测显存/速度；再按确认的论文设置原实现训练评价。短训只证明工程路径；加载权重只证明推演。正式迁移须原训练复现通过，或用户明确授权缩小工程范围并据实标记。
3. **分层迁移与等价性**：核原数据→模型输入、BQ 索引/补零、context、每层 GALE、前向/梯度/MSE、Muon+AdamW 更新/调度、反变换、完整预测与评价。误差门槛在对照前按 dtype/后端确定；不得按结果事后放宽。
4. **公开使用闭环**：实际 wheel 安装、仓库外复制、direct-core 与 Task 分阶段运行、停止/恢复、独立 infer/post、固定数组/VTK/指标读回。复制品修改采样/插入派生输出需造成可解释结果且不依赖原仓库源码路径。
5. **相关回归与扩展**：圈定新增 geotransolver 能力/数据/recipe/参考协议用例；回归训练优化/检查点、Transolver/AB-UPT 外流交接、固定结果评价、Task 资产/安装及固定用户源码基线。统一执行 `uv run --no-sync pytest <相关路径>`。新增测试名在实施时定义，不以本评估当成测试通过。
6. **体场与其他数据**：表面闭环成立后独立做体场 SDF、νt、巨量 IO/分块评价；SHIFT 等数据授权、分片、工况和基准明确后进入。若日后要求 Web，再单列注册/页面、安装发布和正式 8000/5173 实际冒烟，执行前按当次授权边界处理。

未来实现须同步对应 `docs/PRD/ai4e-core/{abilities,applications,run}/PRD.md`、`docs/PRD/ai4e-contrib/{ability,application}/PRD.md`，新增 recipe PRD；资源能力变动再覆盖 Task PRD。入口/边界变化更新 AGENTS，目录职责变化更新模块索引。本轮仅评估文档和日志，不写入“现有功能已支持 GeoTransolver”的 PRD 声明。

**下一步最有价值的工作是 DrivAerML 表面复现准备：核一个完整原始样本及预处理交接，追溯上述论文/配置差异，在隔离 CUDA 环境建立可执行的参考合同。** 数据下载、训练预算和正式迁移仍按后续明确范围执行。

## 6. 20 GB 以下、本机可运行与文献对标补充

本节取代上文的首例推荐，保留上文作为 v2 / 无容量约束时的记录。核查日期 2026-09-20；GB/TB 均为十进制。用户要求最终迁移源码进 Dojo，此轮优先寻找满足容量及文献指标要求的数据。不把小子集训练或跨模型比较写成 GeoTransolver 原论文复现。

### 6.1 三套气动数据：样本数少不代表文件小

实时 Hugging Face `usedStorage`：

- [DrivAerML](https://huggingface.co/datasets/neashton/drivaerml)：31,178,779,984,806 字节，约 **31.18 TB**。论文原始 500 个设计，可用名单 436/48。一个实测文件清单中的 run_1：表面 VTP 0.660 GB，STL 0.142 GB，体场 49.052 GB。
- [SHIFT-SUV](https://huggingface.co/datasets/luminary-shift/SUV)：31,976,738,570,903 字节，约 **31.98 TB**。论文选用 1996 个全尺寸模拟，80/10/10；并非四组全用。所查 full-scale estate/run_00001：表面 0.191 GB、一个 STL 0.252 GB、体场 3.248 GB。
- [SHIFT-Wing](https://huggingface.co/datasets/luminary-shift/WING)：10,629,797,591,718 字节，约 **10.63 TB**，三者公开仓库最小。论文用 1698 个模拟，80/10/10。所查 sample_000001：表面 0.237 GB、粗 STL 0.011 GB、体场 0.544 GB；这三项合计约 0.792 GB。

上述 TB 是仓库存储元数据，不是论文精确子集的下载总量；单例文件大小也不能当作全部样本实测平均。三者均不适合作为整个下载量 <20 GB 的首个本机基准。只有表面也不是几 GB：DrivAerML 按此单例粗估 484 例的 VTP+STL 已约 388 GB（仅量级估算）。SHIFT 仍为 manual gated。

轻量衍生版本也检查过：[EmmiAI/DrivAerML_subsampled_10x](https://huggingface.co/datasets/EmmiAI/DrivAerML_subsampled_10x) API 约 357 GB（README 约 375 GB），[Wing-sample](https://huggingface.co/datasets/luminary-shift/Wing-sample) 约 48.20 GB。均超预算；把完整数据固定采样成小文件会改变每轮重采样及全场评价，不能自动保持原对标协议。

### 6.2 新论文发现：GeoTransolver 有小型保险杠实验

[GeoTransolver v3](https://arxiv.org/html/2512.20399v3) 发布于 **2026-06-22**，用户提供的 v2 为 2025-12-24。v3 §A.1.4 / 表 4 新增：

- **Bumper Beam：135 个模拟，80/10/10**，变化几何缩放、撞击速度、壳厚和横向撞击位置。相对 L2：Transolver **0.00912**，GeoTransolver **0.00732**，GeoTransolver+FLARE **0.00680**，即 0.912%、0.732%、0.680%。这些都是作者报告值。
- **BIW：150 个模拟，90/5/5**，约 40 万节点、38 万单元、25 帧、120 ms，33 个前部零件厚度 ±20%。相对 L2 分别 **0.0160 / 0.0133 / 0.00895**。完整下载入口和大小未确认，不列入已满足 <20 GB 的数据。
- 保险杠模型为 6 层、8 头、256 hidden、128 slices，局部几何半径 `[0.05,0.25]`、邻居 `[8,32]`；保留了 GeoTransolver 多尺度几何路径，更适合验证模型特色。

**已找到生成路径，但原论文数据身份尚未闭合：**官方 [openradioss_dataset_gen](https://github.com/NVIDIA/physicsnemo/tree/aa19b58a129f8d1fabdcaa41c6ca85d5dc01aae1/examples/structural_mechanics/openradioss_dataset_gen) 提供完整 135 工况参数扫描。五种几何 × 三个速度（-5/-3/-7 mm/ms）× 三个厚度倍数（1/.7/1.3）× 一个圆柱直径 × 三个横向偏移（0/120/240 mm）。基础 deck 约 1.8 MB，输出可转 d3plot，再转 VTP/Zarr。

该生成器与论文参数描述相符，但缺少论文分片 ID、完整求解器版本/数值设置与训练权重身份，不能仅因工况数一致宣称同一实验。当前官方 `bumper_geotransolver_oneshot.yaml` 为 **121 train / 5 validation、51 帧**，与论文 80/10/10 不一致；默认训练 10000 epoch，也不能直接套论文泛述的 up to 500 epoch。还须确认指标是位置/位移、全部物理通道还是轨迹状态，以及式 (15) 跨样本范数比与源码逐时刻平均的对应关系。

本机为 **M5 Pro / 64 GiB 统一内存 / MPS、无 CUDA**。官方 OpenRadioss runner 指向 Linux GFortran 可执行文件，因此不是 Mac 上开箱即用；需要另行确认原生构建或 Linux 运行环境。训练与重新执行有限元仿真是两项不同成本。未运行求解器，不能承诺 135 例输出必定低于 20 GB 或给出本机耗时。

### 6.3 确实低于 20 GB 的公开保险杠数据，但不是论文原集

[AIRBORNEPANDA/BumperBeamCrashExample](https://huggingface.co/datasets/AIRBORNEPANDA/BumperBeamCrashExample)，revision `78f1302fba4d75926c6fdd22d01d5133efc14742`，非 gated。API usedStorage 约 15.30 GB，但**完整分页文件清单 4068 个文件的当前大小总和为 15,813,520,683 字节，即 15.814 GB**，后者用于下载量判断。

- 原始 TRAINING_DATA：14,456,805,611 字节；原始 VALIDATION_DATA：815,633,661 字节。
- Curated VTP：**124 train + 7 validation = 131 例**，511,271,775 + 28,968,274 字节，加 GLOBAL_FEATURES.json 后为 **540,256,043 字节（0.540 GB）**。
- 没有独立 test 目录。发布者 [生成仓库](https://github.com/HoussemMouradi/OpenRadioss2PhysicsNeMo) 明确这是 131 例随机厚度/撞击位置数据。
- 读取全部 global features，131 例 `velocity_x` 均为 **-5**；厚度和位置取连续随机值，不是论文/官方生成器的离散 135 工况。
- 实际下载并由 VTK 完整解码 Run100.vtp（4,118,718 字节）：**13,676 节点、13,678 单元、11 帧（t0…t100，间隔 10）**。位移在 PointData，应力/塑性应变在 CellData。只有这一例完整读取，不推断所有文件均有效。
- 数据卡未给出清楚的 license 声明；可访问不代表再发布权限已明确。代码和基础模型许可也不能替代数据许可。

**结论：可作为本机工程候选，不能用论文 0.00732 直接验收。** 不仅样本数量不同，参数分布、划分、时间分辨率也不同。无需下载全套 RAW 就可尝试读取 0.54 GB 的训练副本；但现行 51 帧配置不能直接消费 11 帧，需按数据明确设置，不能补帧后冒充原实验。

按此单例网格、135 例、51 帧、每节点五个 float32 值估算，纯训练数组约 **1.88 GB**，只说明紧凑格式有希望满足预算；不包括原始求解结果、连接关系、缓存/检查点，且不是原论文数据实测容量。单样本全量 N×N float32 距离矩阵约 0.75 GB，远小于气动案例但仍需测训练峰值内存。保持邻居顺序的分块查询可作为迁移优化候选，先做数值等价验证。

### 6.4 可立即获取、有小型文献基准的备选：Darcy

官方 [PhysicsNeMo Darcy 示例](https://github.com/NVIDIA/physicsnemo/tree/aa19b58a129f8d1fabdcaa41c6ca85d5dc01aae1/examples/cfd/darcy_transolver) 指向 [lkuang/example_data](https://huggingface.co/datasets/lkuang/example_data)。Darcy_421.zip 精确大小 **3,347,104,748 字节**；远程 ZIP 中央目录核对两个 MAT 解压合计 **3,385,056,203 字节**，压缩包加解压约 **6.73 GB**，尚未完整下载。Darcy_241.zip 0.821 GB，但不作为 421→85 的等价替代。

[原 Transolver 论文](https://arxiv.org/html/2402.02366v2) 表 2：Darcy 相对 L2 **0.0057（0.57%）**；原始 421×421，主实验降采样到 **85×85=7225 点，1000 train + 200 test**。原论文源码提供对应训练入口。

这个数值属于 **Transolver，而非 GeoTransolver**。PhysicsNeMo README 明示 GeoTransolver Darcy 尚未充分测试；其当前配置为 1024 训练例、4 层、128 hidden，且关闭局部几何特征，数据管道还存在 `.cuda()` 固定设备操作。因此不能直接抄默认配置对标 0.0057。

适合的研究目标是：先复现原 Transolver 的 Darcy 结果，再在完全相同数据/指标协议下迁移并比较 GeoTransolver。这是文献基线比较，有公开可核目标，但不是 GeoTransolver 原论文精度复现，也不能充分验证复杂变几何优势。

### 6.5 当前推荐与源码迁移方向

1. **若优先直接对标 GeoTransolver 本身：优先保险杠 135 工况路线。** 补原分片、求解器/时间输出设置与训练协议，先测单例生成和资源占用，再决定能否生成完整 <20 GB 副本。公开 131 例仅作工程对照，禁止混用实验身份。
2. **若优先现在就拿到完整小数据并有明确论文标尺：Darcy 更稳妥。** 约 6.73 GB 压缩+解压，沿 Transolver 1000/200、85²、0.0057 建立基线，GeoTransolver作为同协议的新比较项。
3. **不推荐本机从三套工业气动数据起步。** 容量和邻域计算同时超出这轮目标；不以随手取少量样本替代论文完整评价。

源码迁移目标已记录，不能只包一层 PhysicsNeMo。中立 slice/deslice、GALE、球查询/局部 MLP、组合优化进 core abilities；完整 GeoTransolver 装配进 contrib ability；Darcy 或碰撞的字段、归一化、时间条件和输出组织进各自 contrib application；recipe 显式表达准备→训练→推理→固定 post，复用 direct-core / Task。保险杠不能强行塞入 aero_cfd，CellData→PointData 转换需保持原 Curator 语义。

尚未执行源码迁移或训练：`dojo-integrate-model` §2 要求“目标数据可取得且可用、文献指标与评价口径明确、对应源码足以执行研究流程”，并要求正式迁移前原实现复现。当前严格的“GeoTransolver同实验 + <20 GB + 公开可取得”尚未三项闭合。若选择 Darcy 跨模型比较或公开 131 例工程迁移，应明确该研究范围，再依此实施，而不是默认为完整论文复现。

本轮新增证据：完整文件清单、论文 v3 HTML 文本、一个真实 VTP，保存在 `/Users/zonghui/work/project_simulation/dojo_train/` 下的 `bumper-hf-tree.json`、`geotransolver-v3-paper.txt`、`bumper-Run100.vtp`。仅数据读取及文档评估，不运行训练/模型测试、不更改依赖或正式服务。


## 7. 原始归档完成与实施计划（2026-09-20）

本节更新第 6 节的下载状态及单样本检查范围；历史评估原文保留。按用户指定位置分目录保存，没有修改原始文件或启动模型迁移/训练。

- **公开保险杠**：`/Users/zonghui/work/datasets/bumper_beam_crash/`，冻结 revision `78f1302fba4d75926c6fdd22d01d5133efc14742`。完整快照 **4068 个文件 / 15,813,520,683 字节（15.814 GB）**，全部大小及远端 LFS SHA256 / Git blob 摘要吻合。Run193 一个文件曾停滞，单独从同一版本重新取得并验证后完成全量核验，恢复过程已记入状态文件。
- **Darcy 421**：`/Users/zonghui/work/datasets/darcy_flow/`，冻结 revision `9763cc5c52c693144fb8869d8aede9b589c11909`。保存 `Darcy_421.zip` 和上游 README；ZIP **3,347,104,748 字节**，SHA256 `802825de9da7398407296c99ca9ceb2371c752f6a3bdd1801172e02ce19edda4`。ZIP CRC 全通过，两个解压 MAT 合计 **3,385,056,203 字节**，压缩与解压合计约 **6.732 GB**。未下载同仓库其他数据。
- 两套各自低于 20 GB，合计约 **22.55 GB**（不含微小来源清单和缓存），不是合计低于 20 GB。

**完整内容核验：**保险杠 131 个 VTP 全部可读，均 13,676 节点 / 13,678 单元，所有坐标和点/单元数组有限；129 例为 11 帧，Run194/Run203 为 12 帧。保留额外 t110，研究准备显式选择共同 0–100ms 的 11 帧。维持原 124 train / 7 validation，不虚构独立 test。Darcy 两个 MAT 的 `coeff/sol` 均为 `(1024,421,421)` 且全量有限；`coeff` 为 uint8、`sol` 为 float64。原精度保留，MPS 的目标/统计 float32 转换须在未来参考与 Dojo 两侧一致并独立核验。

**真实参考读取缺陷：**执行锁定 PhysicsNeMo 的原始 `load_vtp_file` 及连接辅助函数，Run100 有 11 个位移数组却只得到 `(1,13676,3)` 位置。优先正则只匹配 t0 后跳过回退；这是原函数真实执行证据，不是完整模型测试。已记录 `error.log`，计划要求在隔离参考副本修正时间解析、排序及字段对齐后再训练。原仓库源码尚未修改。源 deck 声明 kg/mm/ms，并保留 Altair CC BY-NC 4.0；不能据代码许可推断完整数据许可。

**证据入口：**各原始目录 `RAW_DATASET.md` 与 `_provenance/{remote-files,verified-files,download-status}.json`；保险杠另有 `curated-audit.json`、`reference-reader-audit.json`，Darcy 另有 `content-audit.json`。下载、核验日志和锁定原 Transolver Darcy 配置保存在 `/Users/zonghui/work/project_simulation/dojo_train/geotransolver/acquisition/`。

**后续执行顺序：**见 [实施计划](../../.cursor/plans/geotransolver-small-data-integration.plan.md)。P0 完成，P1 协议/参考修正 → P2 本机参考与文献基线 → P3 core/contrib 源码迁移 → P4 双案例流程 → P5 真实安装及 direct-core/Task 使用验收 → P6 科学结论。Darcy 0.0057 仍属于原 Transolver；公开 131 例保险杠仍不是论文 135 工况。迁移、学习效果和论文精度均未验收。

本轮为数据获取、内容审计及文档计划；未运行模型 pytest、未训练、未更改依赖或正式服务。文档结构、链接及差异空白检查通过，不能把数据核验记成算法验收。
