# ai4e-core

- 状态：可安装；本切片交付数据源下载、路径读取、VTK 家族/NPY 统一 VTK 内存适配、字段提取、有效点 mask、重合点标记、点数对齐、套对齐 mask、具名场落盘与读回、官方分片与打开样本，统计量，外流 pre 的读抽洗、几何与单样本/批量落盘，外流 train 选定 AB-UPT 与读盘探测，最小 Stage/Pipeline，以及 run 开车与写入。
- 职责：原子能力、业务装配和本地执行引擎。
- 允许依赖：`ai4e-spec`，以及本切片声明的 `huggingface-hub`、NumPy、OmegaConf、PyYAML、Torch、VTK。
- 禁止依赖：recipes、task、viz、server、web、Noether。

本目录同时是包工程根和源码根；由构建配置映射为 Python 导入名 `ai4e_core`，不得再嵌套同名目录。

## 本切片边界

- `abilities/data/source/download/`：HuggingFace 整库/单文件、普通网址、多包解压。不管数据集内容，不删除已知缺文件的样本目录。
- `abilities/data/source/read.py`：校验文件存在且格式有适配器，再读单文件；多文件和递归循环调用单文件。
- `abilities/data/source/adapter/`：一种格式一个文件。VTK 家族返回原生 `vtkDataObject`，NPY 返回以 FieldData 承载数组的 `vtkDataObject`。
- `abilities/data/extract/`：只从已读入的 VTK 内存对象抽出点坐标与具名点/单元标量或矢量。
- `abilities/data/filter/`：有效点 mask、与表面坐标精确重合的体积点标记，以及落盘前套对齐 mask；不删原数组。
- `abilities/data/validate/`：同组来源、归属、数量和行身份校验，以及共用输出预检。
- `abilities/data/save/`：具名场记录、编码为 float32 张量、按对照表写/读 `.pt`。覆盖使用临时目录与备份恢复，cell 打包由业务配置决定。
- `abilities/data/source/split.py`：按传入名单列分片并校验人数。
- `applications/aero_cfd/trainprep/dataset.py`：规范化预处理根、打开样本并派生表面距离全零场。
- `abilities/data/stats/`：读入 YAML/JSON 统计量、按数组流累计矩；训练样本与字段选择在 rawprep/stats。
- `abilities/geometry/`：点到最近表面顶点（只吃坐标）、点到网格表面（先校验全部单元为支持的二维面）、表面点法向。两套距离字段名分开；点到面失败不降级为点到点。
- `base/config/`：OmegaConf 加载案例 YAML，支持点号覆盖。
- `applications/base/`：最小 Stage / Pipeline。
- `applications/aero_cfd/rawprep/`：read/derive/select/save/stats 五模块提供独立业务步骤，recipe 显式排列顺序，run 执行样本循环。不做 VTK 压力对 `press.npy` 的对照。
- `applications/aero_cfd/train/`：`fitting.py` 装配正式训练、评估和恢复；`resolve.py` 展开默认并联合校验；旧只读标准阶段仅保留兼容导出，实现迁入 trainprep/dataset.py。
- `run/`：runner 驱动管道，execute 负责逐样本执行与失败汇总；writer 独占运行配置、最终生效配置、源码快照、日志和摘要，业务报告经 reports 交付。

预处理 `.pt` 不是 run 产物。不引入 `hydra-core`。变换、采样、建模组件、监督、训练和评估已交付；完整字段体系、缓存、全网格推理和报告仍为规划。

接口与使用约定见 [abilities PRD](../../docs/PRD/ai4e-core/abilities/PRD.md)、[applications PRD](../../docs/PRD/ai4e-core/applications/PRD.md) 和 [run PRD](../../docs/PRD/ai4e-core/run/PRD.md)。

## 按需 Dataset 与脚本会话

`applications/base/dataset.py` 保存样本引用与顺序步骤；`rawprep/dataset.py` 封装按需处理、清单与统计。用户不写样本循环，`run/dataset.py` 逐样本执行并释放数组。`run/session.py` 支持普通脚本、路径插值和单次会话；`base/events.py` 发能力事件，writer 统一记录日志、原始配置与最终生效配置。训练准备支持按产物 manifest 的实际路径和字段状态读盘。使用入口见 [可复制模板](../../recipes/aero_cfd/README.md)。
