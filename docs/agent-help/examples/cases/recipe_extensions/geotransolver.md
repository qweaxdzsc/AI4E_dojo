<!-- dojo-help: {"case_ids": ["recipe_extensions.geotransolver"], "domain": "recipe_extensions", "kind": "case", "layer": "example", "summary": "平方相对损失与固定误差数组读回", "title": "recipe_extensions.geotransolver", "topic_id": "case:recipe_extensions.geotransolver"} -->
# `recipe_extensions.geotransolver`

- 类型：`extension`
- 用途：平方相对损失与固定误差数组读回
- 资源路径：`examples/recipe_extensions/geotransolver`
- 基案例：`geotransolver.darcy`
- 覆盖文件：
  - `variants.py`

## 物化流程

`copy_example` 会先复制完整基案例，再叠加声明的覆盖文件并写 provenance。
物化后必须重新检查配置、输入和恢复兼容性；不能直接运行原 extension 目录。
