# 脚本物理场分析验收

状态：本切片已完成实施与圈定验收（2026-09-15）。真实小预算训练、外部安装和 Linux 离屏分别按下方范围记录。

## 实现边界

- core `abilities/postproc/visualization` 提供纯 Python/PyVista 分析、显示和图片；`abilities/postproc/export/visualization.py` 独立保存文件。
- `abilities/eval/region_statistics.py` 统计有效实体；现有九项评价复用，恒定真值 R² 修正为不可定义。
- `applications/aero_cfd/post` 绑定固定字段和网格，默认不开启自动分析；配置路径仅在启用后补充。
- `train/physical.py` 透传轮次观察；`infer/snapshot.py` 复用当前模型的预测和物理输出，保护模式和 RNG。
- recipe 显式排列步骤，`TrainingRun.execute_samples` 拥有样本循环；文件在数据目录，运行摘要仍由 writer 保存。
- 旧推理检查点、准备产物、公开 post 入口与 Web 后端不迁移。

## 圈定入口

- A1：`test_post_visualization_fields.py`；A2/A7：`test_post_visualization_render.py`。
- A3/A5：`test_post_visualization_sections.py`；A4：`test_post_visualization_vectors.py`；A6：`test_post_visualization_probe.py`。
- B：`test_post_region_statistics.py`、`test_post_result_metrics.py`、`test_infer_metric_aggregation.py`。
- C：`test_post_visualization_export.py`；D1/E1：`test_post_analysis_recipe.py`；D2：`test_train_post_observation.py`。
- D3/E2：`test_post_visualization_installation.py` 与 `examples/recipe_extensions/physical_visualization`。
- E3：能力清单、recipe 文档、架构文档专项测试。
- 真实数据：`test_post_visualization_abupt.py`，需显式 `DOJO_POST_REAL_MANIFEST`、`DOJO_POST_RAW_ROOT`。

所有上述 Python 测试位于 `tests/integration`，使用 `uv run pytest <圈定路径>`。skip 不能计为通过。

## 产物

持久证据根：`/Users/zonghui/work/project_simulation/dojo_train/physical-post-abilities`。
真实场来自现存 AB-UPT 结果，源数组和网格只读引用；训练观察小预算另行记录，不声明生产精度。

## 接口迁移

只增加公开接口：post 的读取/绑定/评价/分析/绘图/保存，infer 的 predict_snapshot，训练 physical.configure_callbacks。已有接口签名及固定外部用户源码不改。
合法样本名包含分组斜杠时，磁盘目录使用可移植名称与身份摘要；原身份写在清单。重跑默认拒绝覆盖，可显式 overwrite_analysis。

## 文件职责与公开合作流程

- `abilities/postproc/visualization/{fields,sections,vectors,probe,display,render}.py`：分别选择数组、变换网格、构造矢量/流线、空间采样、设置相机、生成像素。所有函数不解释案例配置或模型。
- `abilities/postproc/export/visualization.py`：独立原子保存 PNG、VTP/VTU、探针/剖面 CSV；`abilities/eval/region_statistics.py` 负责统计算术。
- `applications/aero_cfd/post/field_binding.py`：固定字段、ID、有效性和网格绑定；`field_analysis.py`：领域字段映射与可替换分析调用；`field_rendering.py`：共同色标、单位、实际显示参数和替换函数来源。
- `post/analysis.py`：只读来源与样本引用、清单检查和等权批次汇总；`analysis_export.py`：样本事务、文件摘要及失败恢复。全场和区域统计同时出现在 metrics.json 与 metrics.csv；无真值保留 unavailable 及原因，并继续交付预测场统计。
- `infer/snapshot.py`：复用既有单样本预测与物理反变换，不读磁盘检查点；`train/physical.configure_callbacks`：仅适配现有轮次回调，分别记录快照和分析耗时。
- `recipes/aero_cfd` 与 `examples/aero_cfd/shapenet_car_abupt` 的 post.py 显式排列评价→绑定→分析→绘图→保存；train.py 明确决定快照时机；contrib configuration.py 解释参数。其余四例不自动启用新输出。
- `examples/recipe_extensions/physical_visualization`：普通函数替换绘图，新增 speed_squared 字段后保存、读回并交付下游。

独立调用：recipe 选择固定报告 → run.execute_samples 顺序执行 → application 绑定当前样本 → eval/postproc 计算 → save 写数据目录 → writer 写轻量运行报告。首错时 recipe 从公开 BatchExecutionError.summary 发布 partial 清单并继续抛错，之前提交的样本保持可读。

训练调用：现有 fit 轮次事件 → recipe 选择 epoch → infer 从当前模型生成内存快照 → 相同 analyze_sample 正文 → 返回现有训练循环。来源含 run、epoch、updates、当前权重摘要；快照保护各子模块混合模式、梯度及 Python/NumPy/Torch 随机状态。

## 明确的产物与数值口径

- fields/ 保存本次选择的完整域网格；analysis/ 保存派生网格；figures/ 保存像素；profiles/ 保存逐位置、距离、有效性和完整分量。目录中的 manifest 只登记实际成功文件。
- 云图显示体网格外表面，内部场通过切面展示；不加入体积光线投射。point/cell 显式选择；cell→point 插值显式启用，派生几何不复用原始实体 ID。
- 预测和真值共色标与相机；difference、vector_error、magnitude_difference 分别表示分量差、向量差模长、模长差；误差默认 magma，原场 viridis。实际范围、相机、尺寸和显示设置随图片登记。
- 指标读取 float64 完整有效字段，与箭头/渲染抽样无关；区域统计默认实体等权，剖面/探针域外点排除且计数。没有真值时不生成伪误差。恒定小数真值的 R² 为 null，CSV 为空并附原因。
- 重跑默认拒绝覆盖。显式覆盖先暂存完整样本再提升，失败保留上次成品；来源数组修改后拒绝提交。旧数据、检查点和固定源码基线未因新显示参数迁移。

## 验证环境与持久证据

- macOS：PyVista 0.49.0 / VTK 9.7.0，真实 ShapeNet-Car 固定 AB-UPT 场输出七张 PNG、七份完整/派生网格、剖面和指标，并读回验证。
- `delivery/test_real_abupt_training_snaps0/training/verification.json`：CPU、维度24、1个训练样本与1个不同测试样本，两轮快照；有/无观察的训练输入、每轮损失和最终权重逐值一致；第一轮检查点恢复到第二轮后权重逐值一致；检查点路径不存在时独立 post 仍成功。
- `linux-headless/verification.json`：独立 Linux 临时环境，DISPLAY 未设置，实际 vtkEGLRenderWindow；七种图像和对应网格/CSV 生成、保存、读回。安装 core/spec 实际 wheel，复用独立环境中的计算依赖；不代表 Linux 上完整训练已验收。
- 实际安装测试构建 core/spec/contrib wheel，隔离到外部 target 路径；复制官方 post 模板与自定义扩展并运行，交付场、图、指标后读回。未安装 PyVista 的隔离进程中，普通导入和指标仍成功，三维调用才给出 extras 安装提示。
- 训练均为工程交接小预算，不能声称生产精度或正式规模性能。机器之间不要求图片逐像素相同；场算术与数据读回按数值检查。

## 最终测试结果

- `final-scoped.xml` / `.log`：55 passed，0 failed，0 skipped。覆盖三维各能力、固定数组评价、统计、事务、独立调用、训练观察、真实 wheel、自定义扩展和文档。
- `delivery.xml` / `.log`：末次字段绑定修改后，13 passed，0 failed，0 skipped；包含全部真实场输出、两轮真实训练/恢复、无模型 post、纯指标不读网格内容、CLI 覆盖和 wheel 复制案例。
- `final-compatibility.xml` / `.log`：14 passed，0 failed，0 skipped；旧锚点 post 兼容、五官方案例与固定工作流逐值对照和轮次恢复。
- 其余必要回归共圈定 109 项：公共用户源码基线、infer 阶段/兼容、旧 post/网格、训练循环/检查点、配置、task/Web 指标、扩展和文档。初次 108 passed；唯一失败是测试把新 post 显示参数整段复制到 infer。按 infer 公开允许键修正测试装配后，受影响 post 用例包含在上述 14 项复跑中通过；生产 infer 仍严格拒绝未知键，未更改固定用户源码基线。
- 新增/修改源码的 Ruff 检查与格式检查通过。未以全仓测试替代专项验收；当前环境没有 mypy 可执行文件，未将类型检查记为通过。PyVista/VTK 与历史 TorchScript 的未来弃用提示不影响本轮功能结果。

上述日志和 XML 均位于持久证据根。Linux 为 EGL 无显示环境的分析与图片能力验收；CPU 两轮只证明工程交接和观察无数值干扰，不代表生产规模训练精度。
