# 数据来源与存储治理

本文用于区分“项目实现”“内置案例”“用户上传”和“可重建运行时文件”，避免把依赖或报告中间产物误认为业务源码。

## 数据来源

| 范围 | 性质 | 来源与用途 | 是否可删除 |
| --- | --- | --- | --- |
| `frontend/src`、`backend/*.py`、`backend/scripts`、测试与 `.circleci` | 项目实现 | 前后端源码、接口、渲染适配、测试和 CI 配置 | 否 |
| `resources/examples` | 内置文件型案例 | 风洞 CSV、叶片 VTU、燃烧室 VTI、羽流 Parquet、应力 NPZ、日志 CSV、STL/PLY/OBJ、聚变站 GLB 及同源静态快照 | 否；案例功能依赖 |
| `fixtures/gs` | G-S 精选案例 | 来自 `multi_geometry_baseline` 的八模型指标、八种几何的 PINO/传统解/比较结果和归档来源 HTML；manifest 记录 57 个文件的大小与 SHA-256 | 否；G-S 资产与报告依赖 |
| `backend/modules/visTaskManage/examples.py` | 确定性生成案例 | 不落大型源文件；运行时为 23 个可视化方法分别生成轻量案例 payload | 可重建，但源码不可删 |
| `var/objects/datasets` | 用户上传 | 通过上传—解析—推荐流程保存的原始文件，按 SHA-256 去重 | 否；用户数据 |
| `var/db/ai4e_vis.sqlite3` | 运行状态 | 资产、画像、推荐、冻结 Spec、Visualization、报告及导出任务 | 否；运行真源 |
| `var/exports/reports` | 报告导出 | 成功的 PDF、HTML、离线 ZIP 和日志；Quarto 项目源及重复 assets 属于可重建中间物 | 只清理中间物 |
| `backend/cache`、`__pycache__`、`test-results`、`node_modules/.vite` | 派生缓存 | 转换、测试、Python 字节码与 Vite 预构建缓存 | 是 |
| `frontend/dist` | 构建产物 | 生产构建输出 | 可重建；验收后清理 |
| `backend/.venv`、`frontend/node_modules` | 运行依赖 | Python 与前端依赖 | 可重装；为保证当前版本立即可运行，本轮保留 |
| `backend/.tools/quarto/1.10.18` | 固定工具 | Quarto CLI 1.10.18 与 Typst；macOS 官方包含双架构工具 | 保留当前架构，删除未使用架构 |

## 内置案例文件明细

`resources/examples` 约 110 MB，全部属于演示/验收案例而不是平台源码：

- PLT：`cfd_wing_pressure_surface.csv`、`wind_tunnel_ts_pitot.csv`、`wind_tunnel_cp_survey.csv`、`stress_tensor_cycle118.npz`、`simulation_log_raw.csv`。
- FLD/ENT：`combustor_temp_volume.vti`、`turbine_blade_mesh.vtu`、`particle_traj_plume.parquet`。
- GEO：`heater_plate_field.stl`、`wing_surface_geometry.ply`、`nozzle_geometry.obj`、`fusion_station_geometry.glb`。其中聚变站 GLB 约 74 MB，是单个最大业务案例。
- 报告/离线降级媒体：`data/assets` 下的 O3DV/Trame 同源截图和羽流视频。

其中 A-1030 的 STL 被刻意保留为“声明为 FLD、实际检测为 GEO”的负面校验案例；它不是损坏文件。

## 2026-08-24 容量审计与处理

压缩前项目约 3.2 GB，压缩后约 2.2 GB，释放约 1.0 GB。主要变化：

| 目录 | 压缩前 | 压缩后 | 处理 |
| --- | ---: | ---: | --- |
| `backend/state/report_exports` | 905 MB | 198 MB | 保留 5 个成功导出及日志，删除失败项目和重复 Quarto source/assets；PDF 只保留 PDF，连接版 HTML 保留完整 output，离线 HTML 保留 ZIP |
| `backend/.tools/quarto` | 719 MB | 423 MB | 当前机器为 arm64，删除 296 MB x86_64 工具；Quarto 1.10.18 随后验证成功 |
| `frontend/node_modules` | 443 MB | 389 MB | 仅删除 54 MB `.vite` 缓存，依赖主体保留 |
| `backend/test-results` 与字节码缓存 | 约 7 MB | 按需重建 | 删除测试输出与 `__pycache__` |
| `backend/.venv` | 1.0 GB | 1.0 GB | 保留，避免影响当前后端运行 |
| `resources/examples` / `fixtures` / `var/objects/datasets` | 约 142 MB | 约 142 MB | 全部保留 |
| `frontend/dist` | 9.2 MB | 0 | 验收通过后删除，可随时重建 |

## 持续治理

- 新的 Quarto 导出完成后，`quarto_service.compact_export_directory` 自动删除可重建中间物，避免每次导出重复保存约 75 MB 聚变站 GLB。
- Quarto 安装脚本会在 macOS 上只保留当前 CPU 架构，并在清理后执行 `quarto --version`。
- 手动维护使用 `backend/scripts/prune_runtime_storage.py`。默认只做 dry-run；复核清单后使用 `--apply`。
- 清理脚本硬性保护 `.venv`、`node_modules` 主体、`dist`、`data`、`fixtures`、`uploads`、SQLite 和真实报告输出。
