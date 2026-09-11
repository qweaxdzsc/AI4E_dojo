# ai4e-viz

通过稳定文件独立检查和生成显示资产；只依赖 spec 和第三方读取/渲染库，不构建模型或执行训练。

`uv run python -m ai4e_viz` 从标准输入读取请求。旧 `{path,operation,options}` 请求继续返回单 JSON；协议版本 1 请求返回 NDJSON progress/result/error。服务解析源路径并管理操作、取消及缓存生命周期。

新增 pipeline 执行表面、平面切片/裁切、标量阈值、点标量等值。体网格先过滤再抽取显示表面；点云不自动重建体，单元标量不自动插值到点。serialization 将坐标、拓扑、字段、掩码写入分离二进制文件并最后发布 manifest。默认单显示结果限制 128 MiB。

VTK 家族、HDF5/H5、PT/NPY/Zarr 支持成员和维度切片；PT 使用 weights_only。HDF5 多样本同构组只列一份字段。大整数以字符串传给表格保持精度。字段统计只用于观察，不作为归一化配置。

验证：`uv run pytest tests/integration/test_viz_pipeline.py tests/integration/test_viz_file_preview.py`。当前新增工作区仍需完整浏览器资源、联动及原型视觉验收；不能以构建通过声明全部可视化交付。
