<!-- dojo-help: {"case_ids": ["recipe_extensions.model_block"], "domain": "recipe_extensions", "kind": "case", "layer": "example", "summary": "参考变体与 Agent 组件组装示例", "title": "recipe_extensions.model_block", "topic_id": "case:recipe_extensions.model_block"} -->
# `recipe_extensions.model_block`

- 类型：`extension`
- 用途：参考变体与 Agent 组件组装示例
- 资源路径：`examples/recipe_extensions/model_block`
- 基案例：`aero_cfd.shapenet_car_abupt`
- 覆盖文件：
  - `variants.py`

## 物化流程

`copy_example` 会先复制完整基案例，再叠加声明的覆盖文件并写 provenance。
物化后必须重新检查配置、输入和恢复兼容性；不能直接运行原 extension 目录。
