# Tests

原型 v3 复用浏览器检查，新增原始处理三栏、示例文件匹配、PT/VTKHDF、预检和模拟日志、recipe 配置／执行范围／交接弹窗；不执行算法。

线框原型浏览器检查：`PLAYWRIGHT_MODULE=<已安装的 Playwright 模块路径> node tests/integration/web_wireframe_browser.cjs`。只访问本地 HTML，检查版本树→比较→报告、文件预览、批量计划→任务工作台、八步导航及草稿保留；不调用训练服务。

平台设计稿相关检查：`uv run pytest tests/integration/test_web_design_documents.py`。覆盖产品稿本地链接与标题锚点、六节 PRD 结构、功能编号一致性和架构唯一正文；不验证尚未实现的 Web/Server 功能。

- `contract/`：验证模型安装资源、spec 自足及 core/contrib 依赖方向。
- `integration/`：验证跨包与阶段交接。
- `regression/`：验证 recipe 基准不被静默改变；当前仍为空。

本切片相关用例：

```bash
uv run pytest tests/integration/test_train_dataset_read.py
```

训练准备、官方分片与按对照表读盘。案例前处理入口仍在 `test_shapenet_pre_recipe.py`，其中 `@pytest.mark.local_data` 可核对整库 889 个已写出样本。落盘与编排夹具仍在 `test_pre_materialize.py`。几何与提取清洗门禁仍在对应文件。验收核对工作区导入，并使用 Python 3.12。

离线用例始终跑：落盘与编排用最小夹具。几何、域标记、提取清洗和下载/读取用例仍在对应文件里。

真实冒烟也在读取与提取文件里，条件不满足会 **skip**，不会当失败：

- `@pytest.mark.network`：能连上 `huggingface.co:443` 才真下 `hf-internal-testing/tiny-random-bert` 的 `config.json`，缓存写在 pytest 临时目录，测完删除。
- `@pytest.mark.local_data`：相对仓库根找 `../../datasets/shapenet_car_cfd/mlcfd_data/training_data`，读两个已有样本。可用环境变量改路径：

```bash
# 相对仓库根，或写绝对路径
AI4E_SHAPENET_RAW=../../datasets/shapenet_car_cfd/mlcfd_data/training_data \
  uv run pytest tests/integration/test_extract_clean.py tests/integration/test_geometry_domain.py tests/integration/test_pre_materialize.py tests/integration/test_shapenet_pre_recipe.py tests/integration/test_train_dataset_read.py -m local_data -v
```

只跑真实冒烟：

```bash
uv run pytest tests/integration/test_source_download.py -m network -v
uv run pytest tests/integration/test_source_read.py tests/integration/test_extract_clean.py tests/integration/test_geometry_domain.py tests/integration/test_pre_materialize.py tests/integration/test_shapenet_pre_recipe.py tests/integration/test_train_dataset_read.py -m local_data -v
```

只跑离线（跳过真实冒烟）：

```bash
uv run pytest tests/integration/test_extract_clean.py tests/integration/test_geometry_domain.py tests/integration/test_pre_materialize.py tests/integration/test_shapenet_pre_recipe.py tests/integration/test_train_dataset_read.py -m "not local_data"
```

正式网络拟合与复制案例短训走 `auto` 设备：优先 CUDA/MPS，没有加速器时警告后继续用 CPU，不跳过。点名 CUDA/MPS 不可用仍按训练门禁失败。

本期 A1–I4 完整测试节点、统一命令和结果见 [AB-UPT 验收记录](../.context/mvp/abupt-acceptance.md)。真实网络门禁不因依赖缺失而 skip。

多域接口相关六组测试见 `.context/mvp/abupt-multidomain-acceptance.md`；参考夹具位于 tests/fixtures/abupt_inputs。

三阶段与锁定 Noether 的验收入口见 [参考验收记录](../.context/mvp/abupt-reference-acceptance.md)。`test_recipe_three_stage.py` 覆盖复制入口、准备引用、数据冲突、最终配置与调度恢复边界；`test_reference_arithmetic.py` 使用官方归一化器的独立夹具；`test_train_boundary_alignment.py` 覆盖不完整累积组、回调异常恢复、EMA 与实际诊断值。完整规模权重与指标差分报告保存在 `.context/mvp/abupt-reference-results/`。

## Task 本地包

`test_task_management/assets/execution/contracts/recipe/installation/documents.py` 覆盖任务切片；精确用例、运行命令、安装副本注意事项和实际结果见 `.context/mvp/task-acceptance.md`。两个 MPS 相关回归 skip 不算硬件验收。

- `integration/rawprep_detail_browser.cjs`：独立原始处理 HTML 的文件浏览、字段选择、唯一输出名称、取消语义及弹窗检查。通过 `PLAYWRIGHT_MODULE` 指定已有 Playwright 运行时。

## Web / Server

平台专项命令见 AGENTS.md 最后一节；当前四组合实跑、浏览器环境和边界见 `.context/mvp/web-integrated-acceptance.md`；`.context/mvp/web-rawprep-acceptance.md` 保留历史首期记录。前端需先启动本机 API 与 Vite；测试建立独立项目，原始数据只读。

- `integration/test_web_integrated_pipeline.py`：真实 HTTP/viz 二进制对照、生成类型及显式四阶段实跑 CLI。
- `integration/test_web_platform_operations.py`：修订、固定资产、真实共享进程、订阅取消、恢复及版本创建快照。
- `packages/ai4e-web/e2e/`：真实平台自动交互、原型主面板几何、TorchVista、NASA 网格和多窗口；订阅夹具测试与真实服务证据分开记录。
- `packages/ai4e-web/e2e/home-entry.spec.ts`：从首页真实点击、空项目创建与任务恢复、归档失效、1440/1920首页布局与原型封面摘要。首页入口不能只通过深链接测试验收；本次修复后21项回归记录在整合验收的 `homepage-correction/` 子目录。

- `integration/web_integrated_browser.cjs`：整合原型六阶段嵌入、单层外壳、步骤切换保留编辑及回项目导航；使用本地 Playwright。

任务绑定修正：`test_web_dataset_binding.py`覆盖四案例、修订、受控目录与失效拒绝；`test_web_binding_real.py`以真实ShapeNet/NASA完成绑定、原始处理和逐值预览。真实测试必须显式设置`DOJO_BINDING_REAL_ROOT`，输出使用dojo_train实验目录。证据见`.context/mvp/web-integrated-results/task-binding-correction/`。
