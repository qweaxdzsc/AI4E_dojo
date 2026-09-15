# Excel 功能点逐项测试矩阵

> 来源：`可视化功能模块.xlsx` / Sheet“功能模块” / `A1:F116`。测试日期：2026-08-29。
> 本矩阵判断的是重构前已有能力在当前模块化仓库中是否仍可运行，不用“P0”推断实现状态。

## 判定口径

- `implemented`：已有用户入口、真实数据或Renderer，并有自动化或浏览器运行证据。
- `partial`：只实现工作簿所述能力的一部分，限制必须明确列出。
- `demo_only`：只有样例、领域校验、枚举或描述符，没有完整用户业务链路。
- `not_implemented`：没有可确认的现有实现。
- `unverified`：存在代码线索，但本轮无法形成可靠运行证据。

自动化证据入口：

- 后端专项：`backend/tests/test_excel_implemented_features.py`。
- 前端专项：`frontend/e2e/excel-implemented-features.spec.js`。
- 既有跨模块契约：`backend/tests/test_contract.py`。
- 既有三服务链路：`frontend/e2e/upload-recommend-draw.spec.js`。

## 逐功能结论

| Excel序号 | 功能类 | 功能项 | 状态 | 本轮证据与实际断言 | 限制/未通过原因 |
| --- | --- | --- | --- | --- | --- |
| 1 | 几何可视化交互 | 旋转、平移、缩放 | implemented | E2E 进入A-1027的O3DV iframe，验证手势说明、放大/缩小按钮并实际点击 | 旋转和平移由O3DV手势承载 |
| 2 | 几何可视化交互 | 坐标轴 | not_implemented | 未找到可见坐标轴或开关 | `up`参数只是相机上方向，不是坐标轴组件 |
| 3 | 几何可视化交互 | 不同视图、适合窗口 | partial | E2E实际点击“复位视图”；O3DV支持投影和相机参数 | 没有前/后/左/右/轴测视图工具栏 |
| 4 | 几何可视化交互 | 点击高亮（点、线、面、体切换） | not_implemented | 无页面控件、业务事件或回归证据 | O3DV内核潜在能力不等于产品已接入 |
| 未编号（4之后） | 几何可视化交互 | 框选、多选、反选和取消选择 | not_implemented | 无选择状态模型和页面入口 | — |
| 5 | 几何可视化交互 | 隐藏体、面（部件） | not_implemented | 无部件显示状态与控件 | — |
| 6 | 几何可视化交互 | 透明度切换（体、全局） | not_implemented | 无用户可操作透明度控件 | 材质参数线索不构成已接入功能 |
| 7 | 几何可视化交互 | 剖切（三维剖切） | not_implemented | 无剖切面状态、控件或结果 | — |
| 8 | 几何可视化交互 | 颜色渲染 | partial | O3DV接受材质/背景参数，页面可显示材质颜色 | 无部件级颜色编辑交互 |
| 9 | 几何可视化交互 | 光照、阴影效果 | demo_only | O3DV/Three.js默认材质和光照参与渲染 | 无业务配置、开关和专项用户断言 |
| 10 | 几何可视化交互 | 几何结构树 | not_implemented | 页面无结构树 | GLB多几何解析统计不能替代结构树 |
| 11 | 几何可视化交互 | 距离、角度、面积、体积测量 | not_implemented | 无测量工具或持久化结果 | — |
| 13 | 数据集查看 | 抽查 | implemented | 后端读取A-1025真实CSV，断言5,941行、字段与时序列；前端Perspective显示真实行列 | 当前以数据预览进行抽查 |
| 14 | 数据集查看 | 数据集体检报告 | partial | 专项测试断言缺失率、最小值、最大值、均值；既有测试覆盖解析失败和NaN问题 | 没有方差、分位数及完整输入参数空间覆盖报告 |
| 15 | 数据集查看 | 待定义 | not_implemented | 需求本身未定义 | — |
| 19 | 三维物理场可视化交互 | 旋转、平移、缩放 | implemented | E2E进入真实Trame/vtk.js iframe；九类场景均为`vtkRenderWindow` | 交互由vtk.js本地视图承载 |
| 20 | 三维物理场可视化交互 | 坐标轴 | not_implemented | 未发现Orientation/Axes组件 | 相机`ViewUp`不等于坐标轴显示 |
| 21 | 三维物理场可视化交互 | 不同视图、适合窗口 | partial | E2E验证“重置视角”；Trame可切换九类数据视图 | 无标准方向视图按钮 |
| 22 | 三维物理场可视化交互 | 云图（物理场） | implemented | 六个标量/矢量案例逐项验证Renderer URL与数据；VTK标量场使用LookupTable/TransferFunction | 色带编辑另见第28项 |
| 23 | 三维物理场可视化交互 | 矢量图（物理场） | implemented | 栅格、体、拓扑三类矢量案例均接入Trame；VTK Glyph真实构建箭头 | 当前是箭头，不是流线 |
| 24 | 三维物理场可视化交互 | 切面 | not_implemented | 交互场景无切面Actor或控制器 | A-1028静态中截面快照不能代替交互切面 |
| 25 | 三维物理场可视化交互 | 流线 | not_implemented | 当前矢量场实际使用`vtkGlyph3D`箭头 | 方法描述中的“流线”未接入场景 |
| 26 | 三维物理场可视化交互 | 等值面 | implemented | 专项测试验证体场包含一个Volume和两个Contour Actor（1100K/1500K） | 等值面数值当前硬编码，不可编辑 |
| 27 | 三维物理场可视化交互 | 等高线 | not_implemented | 无等高线Actor和控件 | — |
| 未编号（27之后） | 三维物理场可视化交互 | Probe提取数据 | demo_only | `probe.py`只规范化三维坐标 | 没有从真实数据集取值、页面展示或保存结果 |
| 28 | 三维物理场可视化交互 | 颜色条编辑（颜色带、层数、范围） | not_implemented | 当前LookupTable/TransferFunction为场景硬编码 | Schema参数未贯通到实时Trame场景 |
| 29 | 三维物理场可视化交互 | 透明度 | demo_only | 体场和等值面设置了固定透明度 | 无用户编辑入口 |
| 30 | 三维物理场可视化交互 | 显示模式切换（面、网格） | not_implemented | 无Surface/Wireframe运行时切换 | 不同案例预设不能替代同结果模式切换 |
| 31 | 三维物理场可视化交互 | 光照、阴影效果 | demo_only | 体场`ShadeOn`、场景包含固定VTK Light | 无用户开关或参数链路 |
| 32 | 三维物理场可视化交互 | 时序播放、前进、倒退、暂停 | partial | 后端验证240帧且原位复用拓扑；桌面E2E点击下一帧并已有播放/暂停/上一帧基线；移动端用滑块方向键前进 | 390px下“下一帧”按钮超出iframe可视区，键盘替代操作可用 |
| 33 | 三维物理场可视化交互 | 动画录制 | not_implemented | 只有请求校验对象 | 无录制、编码或文件输出链路 |
| 34 | 三维物理场可视化交互 | 支持多结果导入 | not_implemented | 只有结果ID去重纯函数 | 无导入、加载和用户入口 |
| 35 | 三维物理场可视化交互 | 多窗口分层展示 | not_implemented | 无多窗口页面状态 | — |
| 36 | 三维物理场可视化交互 | 多结果统一视角 | not_implemented | 无跨视口相机同步 | — |
| 37 | 三维物理场可视化交互 | 多结果显示隐藏切换 | not_implemented | 无多结果图层状态 | — |
| 38 | 三维物理场可视化交互 | 调用配置项 | partial | 23个方法都有JSON Schema、默认值和参数校验 | 部分物理场参数尚未传入Trame真实场景 |
| 40 | 数据提取 | 点数据提取 | demo_only | 二级模块可校验`point`请求 | 无真实数据抽取和输出 |
| 41 | 数据提取 | 线数据提取 | demo_only | 二级模块可校验`line`请求 | 无真实数据抽取和输出 |
| 42 | 数据提取 | 面数据提取 | demo_only | 二级模块可校验`surface`请求 | 无真实数据抽取和输出 |
| 43 | 数据提取 | 体数据提取 | demo_only | 二级模块可校验`volume`请求 | 无真实数据抽取和输出 |
| 44 | 数据提取 | 时序数据提取 | demo_only | 可生成合法时序索引 | 无读取真实场、结果和导出链路 |
| 45 | 数据提取 | 聚合数据提取（面平均、最大、最小） | demo_only | 可校验聚合方法名 | 未执行真实聚合计算 |
| 46 | 数据提取 | 调用配置项 | not_implemented | 无提取配置API和保存链路 | — |
| 48 | 数据预览 | 二维表格预览 | implemented | CASE-TABLE返回真实列和行；桌面/移动E2E验证Perspective可访问数据表和列头 | — |
| 49 | 数据预览 | 二维散点图预览 | implemented | CASE-OPTIMIZATION由ECharts SVG绘制真实Pareto散点；桌面/移动E2E验证SVG | 三维点集CASE-POINT-SET明确不用于冒充二维散点 |
| 50 | 数据预览 | 二维折线图预览 | implemented | CASE-SERIES返回真实序列并由ECharts SVG绘制；桌面/移动E2E验证 | — |
| 51 | 数据预览 | 二维柱状图预览 | implemented | CASE-DISTRIBUTION返回真实bins/counts并由ECharts柱状图绘制；桌面/移动E2E验证 | — |
| 52 | 数据预览 | 多维云图预览 | partial | 矩阵/张量案例可用二维热力图读取切片 | 无独立多维云图交互工作区 |
| 55 | 图片预览 | PNG、JPG直接打开预览 | implemented | 后端验证真实PNG签名；前端桌面/移动E2E断言图片自然宽度大于0；JPG扩展由领域规则支持 | 主要运行样例为PNG |
| 56 | 图片预览 | 支持缩放 | not_implemented | 图片当前仅`object-fit`适配容器 | 无缩放控件或手势状态 |
| 58 | 可视化资产保存 | 以任务形式保存 | implemented | 既有契约验证Preview不落库、保存创建Spec与Visualization、版本冲突；报告编排E2E可引用保存结果 | — |
| 60 | 可视化资产导出 | 导出数据（CSV） | demo_only | `SUPPORTED_EXPORT_FORMATS`声明CSV | 无导出API、文件生成和下载 |
| 61 | 可视化资产导出 | 导出图片（PNG） | demo_only | 仅声明PNG格式，报告截图属于不同业务 | 无可视化图片导出链路 |
| 62 | 可视化资产导出 | 导出视频（MP4） | demo_only | 仅声明MP4格式 | 无视频编码和下载 |
| 63 | 可视化资产导出 | 导出VTK | demo_only | 仅声明VTK格式 | 无文件生成和下载 |
| 65 | 脚本提取支持 | 支持命令/脚本化提取结果 | demo_only | automation只校验脚本名称和文本 | 明确不执行任意代码，也不产生提取结果 |
| 67 | MCP支持 | 操作MCP化 | demo_only | MCP模块只构造工具描述符 | 没有可连接的MCP Server与真实工具调用 |
| 71 | 原数据脚本化提取 | 保存脚本 | not_implemented | 无Repository和保存API | — |
| 76 | 结构化输入 | 结构化入库 | partial | dataAssets把文件、画像、分类和存储键写入SQLite；CSV/JSON/NPZ等可解析 | 不是通用结构化数据平台 |
| 77 | 结构化输出 | 结构化入库（原表述） | partial | API输出结构化JSON，VisualizationSpec/报告文档可持久化 | 工作簿“输出/入库”语义冲突，需PRD澄清 |
| 80 | 报告管理 | 报告增删改查 | partial | E2E真实创建、查询、复制；草稿PATCH可更新；API可读取 | 没有报告删除接口，不能判定完整CRUD |
| 81 | 报告管理 | 筛选、排序、搜索、视图切换 | partial | E2E验证搜索；页面支持状态筛选 | 没有显式排序和列表/卡片视图切换 |
| 82 | 报告管理 | 报告收藏 | not_implemented | 无收藏字段、API或控件 | — |
| 83 | 报告管理 | 报告版本管理 | implemented | E2E冻结v1；既有契约验证冻结快照和按版本读取 | — |
| 84 | 报告管理 | 报告母版管理（HTML） | partial | 创建时可选内置模板，Quarto可导出连接版/离线HTML | 没有母版CRUD和独立母版资产管理 |
| 85 | 报告管理 | 报告母版管理（PPTX、Word） | not_implemented | 无PPTX/Word母版和导出链路 | — |
| 87 | 报告编排 | 选择母版 | partial | 新建报告可选analysis/validation/weekly/blank | 选择的是内置脚手架，不是可管理母版资产 |
| 88 | 报告编排 | 选择已保存可视化内容 | implemented | 桌面/移动E2E创建可视化后从素材库添加，保存冻结引用 | — |
| 89 | 报告编排 | 新增内容块 | implemented | 编排领域支持多种块；E2E新增Visualization块 | — |
| 90 | 报告编排 | 拖拽填充内容 | implemented | dnd-kit接入，既有测试验证跨行移动；专项E2E验证移动按钮可达 | 移动端主要使用上下移动替代拖拽手势 |
| 94 | 可视化任务管理 | 任务增删改查 | partial | Spec/Visualization可创建、查询、追加不可变版本 | 不支持删除，更新采用追加版本而非原地修改 |
| 95 | 可视化任务管理 | 任务结构持久化 | implemented | SQLite保存Spec版本、参数、Renderer、结果和内容哈希；乐观锁有契约测试 | — |
| 99 | 三维格式转换器 | STEP | not_implemented | Converter无STEP Reader | Excel目标未实现 |
| 100 | 三维格式转换器 | STL | implemented | 专项测试构造真实三角形STL、转换GLB、校验`glTF`头并由VTK重新读取 | 输出目标是O3DV可读GLB |
| 103 | 二维格式转换器 | DXF | not_implemented | Converter无DXF Reader | — |
| 105 | 数据格式转换器 | CSV转JSON给前端显示 | implemented | 专项测试读取真实CSV并返回列、dtype、统计结构；Perspective/ECharts消费JSON | 不是通用文件转换下载服务 |
| 107 | 几何渲染引擎 | 集成three.js | partial | 自托管O3DV内部基于Three.js，真实GLB在O3DV显示 | 产品不提供独立Three.js业务引擎，权威几何Renderer是O3DV |
| 109 | 三维物理场引擎 | 集成VTK与Trame | implemented | 九类场景逐一验证为`vtkRenderWindow`；浏览器连接真实Trame/vtk.js | — |
| 110 | 三维物理场引擎 | 解析 | implemented | VTU/VTI/NPZ/CSV/Parquet等案例具有真实解析画像；Miller校验240×148×176 | 支持格式范围以方法注册表为准 |
| 111 | 三维物理场引擎 | 渲染显示 | implemented | 六类场方法映射到不同Trame view，桌面/移动均进入真实iframe | 个别高级后处理功能仍未接入 |

## 本轮运行结果

- 共识别80个非空功能项：`implemented 22`、`partial 15`、`demo_only 16`、`not_implemented 27`、`unverified 0`。
- 后端原模块与跨模块契约基线：`67 passed`。
- 新增Excel后端专项：`18 passed`。
- 新增Excel桌面端E2E：`6 passed`。
- 新增Excel移动端E2E：`6 passed`，第32项保留移动端按钮可达性限制。
- 加入专项后的后端最终全量：`107 passed, 1 skipped`。
- 前端架构门禁通过，Vitest为`13 passed`，生产构建通过。
- 完整三服务Playwright（既有主链路+Excel专项、桌面+移动）：`31 passed, 1 skipped`。
- 本轮没有修改原始Excel，也没有把`not_implemented`或`demo_only`计为通过。
