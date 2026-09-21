<!-- dojo-help: {"case_ids": ["recipe_extensions.geotransolver_aero"], "domain": "recipe_extensions", "kind": "case", "layer": "example", "summary": "外流L1训练与固定绝对误差场读回", "title": "recipe_extensions.geotransolver_aero", "topic_id": "case:recipe_extensions.geotransolver_aero"} -->
# `recipe_extensions.geotransolver_aero`

- 类型：`extension`
- 用途：外流L1训练与固定绝对误差场读回
- 资源路径：`examples/recipe_extensions/geotransolver_aero`
- 基案例：`aero_cfd.shapenet_car_geotransolver`
- 覆盖文件：
  - `train.py`
  - `infer.py`
  - `post.py`
  - `variants.py`

## 物化流程

`copy_example` 会先复制完整基案例，再叠加声明的覆盖文件并写 provenance。
物化后必须重新检查配置、输入和恢复兼容性；不能直接运行原 extension 目录。
