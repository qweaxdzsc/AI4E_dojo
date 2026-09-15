# 模块组：任务、数据集与可视化资产

## 业务链路

上传/内置案例 → 解析画像与数据质量检测 → 语义类型与方法推荐 → 参数 Schema 校验 → 预览 → 冻结 VisualizationSpec 与 Visualization。

## 模块所有权

- [`dataAssets`](../../backend/modules/dataAssets/)：`artifacts`、分类历史、上传去重、资产列表/详情和原始文件读取；Repository独占资产SQL。
- [`visDatasets`](../../backend/modules/visDatasets/)：真实解析器、画像、体检、统计和内容查看；分析结果通过dataAssets公开门面保存。
- [`visTaskManage`](../../backend/modules/visTaskManage/)：5 家族、19 类型、23 方法目录，动态参数 Schema，推荐接口和不可变 Spec 版本。
- [`visIO`](../../backend/modules/visIO/)：预览、冻结可视化、表现清单与 `artifact_visualizations` 表；通过前两个模块公开门面协作。

## 前端指针

- [`frontend/src/modules/dataAssets/`](../../frontend/src/modules/dataAssets/)：列表、详情、资产API与Model。
- [`frontend/src/modules/visDatasets/`](../../frontend/src/modules/visDatasets/)：解析、画像和重新分析API，无独立页面。
- [`frontend/src/modules/visTaskManage/`](../../frontend/src/modules/visTaskManage/)：推荐、案例、Spec、配置器、Preview 分发。
- [`frontend/src/modules/visIO/`](../../frontend/src/modules/visIO/)：预览、保存与查询 API 门面。

## 测试与联动

- `backend/tests/modules/test_data_assets.py`
- `backend/tests/modules/test_vis_datasets.py`
- `backend/tests/modules/test_vis_task_manage.py`
- `backend/tests/modules/test_vis_io.py`
- `backend/tests/test_contract.py` 覆盖推荐、参数、上传、版本冲突和冻结资产。

修改方法目录必须维持 5/19/23 计数或同步产品基线；修改上传路径必须保持 SHA-256 寻址和相对 storage key；修改 Spec/Visualization 写入必须继续验证乐观锁与非持久预览。
