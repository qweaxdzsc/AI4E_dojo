# 平台算法交接验收（2026-09-10）

本记录只声明算法子计划验收；HTTP、浏览器与三维工作区的集成由主 Agent 另行验收。

- 规范配置将采样放在 `model.sampling`，旧 `trainprep.sampling` 单键兼容，双键拒绝；算法内部及旧冻结准备继续使用原语义。
- `ai4e_core.applications.aero_cfd.inspection.execute(request)` 提供案例能力、真实数据目录、阶段输入校验、TorchVista 和严格差值。配置来自 task 捕获结果，组件由显式声明加载。
- 提取容器编译到既有样本路由，混合点/单元字段保留独立成员。PT/Zarr 共用原子目录事务；清单绑定输出成员、训练别名和源实体身份文件，内容变化使准备失效。
- 通用 Min-Max 支持常量分量和反变换，沿用原坐标算术；新 Min-Max 拒绝手填边界，拟合仅消费训练分片。原参考统计和已冻结参数保留历史兼容，不将历史证据迁写成新统计。
- `train.manifest` 交接原始产物；`train.preparation` 交接准备；准备文件自身固定 manifest；`post.checkpoint` 交接独立后处理。共享 ShapeNet 原始处理现在返回 manifest 路径，修复先前字典被当作路径的问题。

## 真实数据与正式模型

四组合都从原始数据重新提取为两个输出、多个成员，经过准备、正式网络单轮训练与完整选定测试样本后处理。汽车为 train 1 / test 1；NASA 为 train 8 / validation 1 / test 1（单样本条件标准差为零不能拟合，未用伪造统计绕过）。网络参数、层数和采样配置保持所选正式 example；此为少样本短训验收，不是生产规模精度声明。

- 汽车 AB-UPT：18,634,180 参数，PT；`/private/tmp/dojo-algorithm-handoff-v4/shapenet_car_abupt/result.json`。
- 汽车 Transolver-3 surface：11,332,033 参数，PT；`/private/tmp/dojo-algorithm-handoff-v3/shapenet_car_transolver3_surface/result.json`。
- NASA AB-UPT：19,736,644 参数，Zarr；`/private/tmp/dojo-algorithm-handoff-v5/nasa_crm_abupt/result.json`。本次使用公开 `surface/point/...`、`surface/global/conditions` 等 field_id 字符串；没有内部对象路由或 PT 中转。
- NASA Transolver-3：11,335,876 参数，Zarr；`/private/tmp/dojo-algorithm-handoff-v5/nasa_crm_transolver3/result.json`。

四份真实 TorchVista HTML 位于 `/private/tmp/dojo-platform-traces/<case>/model.html`，来源配置修订和实际训练样本记录在对应 `model-inspection.json`。跟踪执行实际网络前向；失败不发布局部 HTML。

可复现实跑入口：`uv run tests/integration/algorithm_real_handoff.py <case> <新输出目录>`。真实 MPS 验收在允许访问 Apple GPU 的进程完成；沙箱内 MPS 不可用的失败运行未计为通过。

## 差值与身份

NASA 新后处理清单记录拓扑摘要、实体集合和 cp/cf 的无量纲单位 `1`。差值可以直接消费已登记预测 PT 和同样本 manifest，自动读取原 ID 与坐标。真实 454404×1 cp prediction−truth 结果位于 `/private/tmp/dojo-platform-real-difference/difference.pt`。未知单位、不同拓扑、不同 ID 或坐标均拒绝，不自动配准。汽车来源未声明单位时保持不可比；可通过明确 `dataset.field_units` 声明物理单位，不能从字段名称猜测。

早期 NASA v4 新多输出记录有输出循环变量覆盖 `source.sample` 的错误，已修复并增加身份断言；上述最终验收仅采用 v5，旧失败/错误证据保留不覆盖。

## 测试与导航

圈定用例为 `test_algorithm_platform_contract.py`、`test_normalized_dataset.py`、`test_train_normalize_sample.py`、`test_dataset_recipe.py`、`test_cross_model_training.py`、`test_model_preparation_contract.py`、`test_cross_model_recipe.py`、`test_recipe_configuration.py`、`test_aero_cfd_examples.py`；最终结果由本目录 `web-algorithm-results/tests.txt` 记录。测试覆盖 PT/Zarr 大整数与成员、混合实体、Min-Max、采样失效、真实跟踪及失败、旧规范化、复制 recipe 和真实物理训练契约。没有使用全仓测试或工程构建代替这些用例。

证据副本、逐组合摘要和源码 SHA-256 位于 `web-algorithm-results/`。主索引应链接本记录，但不能将本记录的算法通过等同为整体平台完成。

## 真实网格导出补验收

发现共享物理后处理曾忽略 `post.export_vtk`，上文四组历史结果仅证明 PT 预测交付，不能作为网格导出证据。现已接入来源拓扑回贴与独立 mesh 进度阶段；新增表面四边形、体四面体、原身份及重复身份拒绝测试，关闭开关的复制 recipe 流程明确无 VTP/VTU。圈定 `test_physical_mesh_export.py test_cross_model_recipe.py test_cross_model_comparison.py test_comparison_visualization.py` 共 12 项通过。四组真实 HTTP post 重跑由主 Agent 统一执行，结果以总验收记录为准，不重训或改写历史产物。

坐标声明补链：显式 `dataset.coordinate_space{id,unit}` 经公开配置检查、post 清单、VTP/VTU FieldData 与差值 sidecar 传播。字段单位不冒充坐标单位，缺失保持未知。只读检查真实 NASA testData 根、Sample001 和 CoordinateX/Y/Z 属性，未发现单位声明，因此没有补填实际 NASA 单位。新增声明测试与网格/平台算法回归通过；未重训，未更改历史预测。
