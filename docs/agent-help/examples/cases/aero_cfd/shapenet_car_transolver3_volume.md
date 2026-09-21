<!-- dojo-help: {"case_ids": ["aero_cfd.shapenet_car_transolver3_volume"], "domain": "aero_cfd", "kind": "case", "layer": "example", "summary": "汽车体积预测", "title": "aero_cfd.shapenet_car_transolver3_volume", "topic_id": "case:aero_cfd.shapenet_car_transolver3_volume"} -->
# `aero_cfd.shapenet_car_transolver3_volume`

- 类型：`standalone`
- 用途：汽车体积预测
- 资源路径：`examples/aero_cfd/shapenet_car_transolver3_volume`
- 模型：`Transolver-3`
- 数据集：`shapenet_car`
- 入口：`pipeline.py`
- Recipe 来源：`aero_cfd`
- 依赖：`ai4e-core`, `ai4e-contrib`

## 阶段

- `rawprep.py`
- `trainprep.py`
- `train.py`
- `infer.py`
- `post.py`

## 使用流程

1. 用 `check_example` 检查资源，再用 `copy_example` 复制到仓库外空目录。
2. 阅读复制目录的 README、config、pipeline 和全部阶段脚本。
3. 先直接执行 pipeline；需要版本、后台运行或恢复时再把同一目录交给 Task。
4. 按 README 读回配置、阶段摘要、检查点、预测、指标和 post 结果。

目录和文件存在不代表运行成功；当前真实输入、预算和证据边界以案例 README 为准。
