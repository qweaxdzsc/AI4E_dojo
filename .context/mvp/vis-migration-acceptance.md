# AI4E_Viz 迁移与任务配置资产验收

日期：2026-09-14。范围为用户批准的独立可视化模块迁移、任务配置资产、Trame工作台与Web交接；不涉及训练算法或运行目录改造。**三类结果分别判断，不用文件存在或构建通过替代功能验收。**

## 1. 完整迁入：通过圈定检查

来源为AI4E_Vis版本 `879e3a5d333e91ceae10da16d5228cad8661a7fd`。385份跟踪文件与8份额外规则/技能文件全部保留相对路径，共393份；311份内容保持不变，82份为安装、治理、接口或验收适配。源码、13模块、JSX应用、资源、夹具、规则、技能、架构和PRD均保留。原Dojo可视化库七类目录共存。

- [逐文件来源哈希与处置](../../packages/ai4e-viz/docs/migration/source-manifest.json)。
- [完整当前目录](../../packages/ai4e-viz/docs/migration/file-inventory.md)。
- [安装、分层、API与脚本接入](../../packages/ai4e-viz/docs/migration/dojo-integration.md)。
- 原源仓库保持未修改；不迁移.git、运行数据库、依赖、缓存、机器连接配置或用户业务数据。
- 原九示例通过显式构建测试；240帧Miller时序与几何复用回归通过。旧入口导入不再创建全部场景。
- 旧SQLite图表和报告读取继续回归；新保存接口要求context，这是明确协议变化。
- 实际wheel构建、外部安装、CLI与Trame会话、保存均通过；安装前后逐文件SHA256一致，没有向包安装目录写入运行或业务文件。前端dist构建后打入wheel。

## 2. 统一配置资产链路：通过圈定检查

任务公开存储区域 → Server固定来源/context → 独立Vis配置Repository → 任务visualizations → 重新读取/重开已通过真实进程与HTTP验证。

已验证：只保存asset.json和spec.json、不复制原数据、不自动截图；原数据哈希不变；期望修订冲突与失败恢复；幂等、配置摘要、篡改检测；缓存删除后仍能列出与读取；复制配置目录后可读；路径/符号链接越界拒绝；原数据缺失和递归复合成员变更报错；保存不增加任务版本；归档任务拒绝新写入。

导出在显式调用时创建，成功清单最后提交；取消/失败不发布成功文件。PNG、CSV、MP4实际读回，WebM解码为1280×720的真实视口图像。增加导出不会改变配置摘要。报告文档的新引用冻结项目、任务、资产、修订、摘要和视图，后续r2不会改变报告r1生成的PNG；原SQLite引用继续可读。

新保存与新导出都不写训练runs或recipe。工作会话为内存/子进程状态，不默认落盘VTK对象。

## 3. 三维物理场：本机核心功能通过，完整跨环境验收未完成

已通过真实VTK计算或交互：

- 本地与远程Trame实际渲染（本机macOS）、旋转/相机保存、方向视图、适窗、外围坐标标尺。
- point/cell字段与矢量分量/模长、颜色带/层数/范围、透明度与面/网格模式、光照。
- 切面、Glyph、流线、等值面/等高线计算；坐标Probe、射线实体拾取数值检验和时序提取，域外返回无效标记。
- 多源图层、双视口、显隐和相机联动约束；默认不联动，未声明同空间不自动对齐。实现支持1/2/4视口，四视口数值测试与真实浏览器均通过。
- PVD/显式帧的精确时间选择、缺帧行为、拓扑变化和时序数据提取；保留原Miller案例。
- PNG、CSV、MP4实际文件、PNG序列生产接口、浏览器WebM录制；固定配置/时间/相机轨迹交付给同一输出器。
- 两个独立Trame进程互不影响；非法Apply保留旧画面；进程退出与安装后启动通过。

浏览器证据：
- 独立应用：实际字段选择与Apply、相机拖动、保存、PNG下载、WebM录制、刷新后重开；空间Probe、鼠标实体拾取与切面Apply均通过；独立PVD浏览器还验证正反播放、逐帧、暂停、四视口和显式相机联动。
- 宿主：文件预览/后处理/比较三种模式通过公开visualization组件，验证真实双层iframe、HTTP/WS及保存；另实际从项目文件页面点击文件、选择目标任务进入Trame。
- 三种模式测试不等同于从科研任务完整训练、post执行、差值计算再进入新工作台的全页面端到端验收。未声称这些新增科研链路已全部重跑。

**仍未完成的专项验证：**

1. 当前为macOS，Linux远程渲染、EGL/OSMesa、阴影和Linux稳定编码未实测；不能仅按平台条件声明渲染能力可用。
2. Glyph、流线、等值分析的各种参数组合未逐项跑浏览器；当前有真实VTK数值测试。PNG序列已实际读回，完整科研页面三个入口仍需独立研究案例端到端验收。
3. 完整Quarto二进制报告导出与原九示例独立旧UI浏览器回归未在本轮完整执行；固定引用校验及实际PNG生产链通过。
4. 通用时序当前接PVD/显式frames；native VTKHDF内部时间轴未专门接入。普通PT/NPY/H5/Zarr只接受明确点几何声明，不猜测体网格拓扑。
5. 本期未做大规模多用户/大数据性能或跨机器搬运验收。源码文件名相较计划有合并，具体见接入说明，不把空目录当交付。

## 测试、实际文件和重跑

本次圈定Python套件：**140 passed**；随后远程交互、四视口、PNG序列与架构补验：**14 passed**（与前一套有重叠，不相加冒充独立用例数）。包括迁入模块、架构门禁、原HTTP契约/九示例/Miller，以及Dojo迁移、宿主保存、原preview/pipeline/extended/Web架构回归。wheel独立安装测试：**1 passed**。原Vis前端Vitest：**13 passed**。两前端build和check:architecture通过；未跑全Dojo测试冒充本切片验收。

```bash
PYTHONPATH=packages/ai4e-viz/backend uv run --no-sync pytest --import-mode=importlib packages/ai4e-viz/backend/tests/modules packages/ai4e-viz/backend/tests/test_architecture.py packages/ai4e-viz/backend/tests/test_contract.py packages/ai4e-viz/backend/tests/test_miller_animation.py packages/ai4e-viz/backend/tests/test_excel_implemented_features.py tests/integration/test_viz_migration_layout.py tests/integration/test_viz_host_bindings.py tests/integration/test_viz_file_preview.py tests/integration/test_viz_pipeline.py tests/integration/test_viz_extended.py tests/integration/test_web_architecture.py
uv run --no-sync pytest tests/integration/test_viz_installation.py
npm run --prefix packages/ai4e-viz/frontend test
npm run --prefix packages/ai4e-viz/frontend check:architecture
npm run --prefix packages/ai4e-web check:architecture
```

完整证据根：`/Users/zonghui/work/project_simulation/dojo_train/vis_migration/`。

- `backend-tests.xml`、`backend-tests.log`：140项最终结果。
- `wheel-tests.xml`、`wheel-tests.log`、`wheel-acceptance/`：实际wheel构建/安装、源码内容核验与外部保存。
- `frontend-tests.log`、`vis-build.log`、`web-build.log`：前端验证。
- `final-physics-tests.log`：后续14项真实会话/四视口/输出/架构补验。
- `remote-browser/browser-results.json`：远程模式交互、保存、PNG、WebM、重开、Probe和拾取；`video-validation.json`核验本地/远程视频尺寸、实际非空像素和文件摘要。
- `timeline-browser/timeline-results.json`：真实PVD正反播放、逐帧、暂停、四视口和相机联动。
- `browser/browser-results.json`、`physical-scalar.png`、`download.png`、`recording.webm`：独立应用实际交互。
- `host/host-browser-results.json`、`preview-embedded.png`、`post-embedded.png`、`comparison-embedded.png`、`project-files-entry.png`：宿主证据。
- 早期失败截图和调试日志可能保留；以最终results.json/XML标记为准，不使用旧截图证明修复后行为。
