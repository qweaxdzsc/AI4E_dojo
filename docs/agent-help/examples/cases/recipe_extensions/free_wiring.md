<!-- dojo-help: {"case_ids": ["recipe_extensions.free_wiring"], "domain": "recipe_extensions", "kind": "case", "layer": "example", "summary": "参考变体与 Agent 组件组装示例", "title": "recipe_extensions.free_wiring", "topic_id": "case:recipe_extensions.free_wiring"} -->
# `recipe_extensions.free_wiring`

- 类型：`extension`
- 用途：参考变体与 Agent 组件组装示例
- 资源路径：`examples/recipe_extensions/free_wiring`
- 基案例：`aero_cfd.shapenet_car_abupt`
- 覆盖文件：
  - `configuration.py`
  - `user_wiring.py`
  - `config.yaml`
  - `points.json`
  - `pipeline.py`
  - `user_steps.py`

## 物化流程

`copy_example` 会先复制完整基案例，再叠加声明的覆盖文件并写 provenance。
物化后必须重新检查配置、输入和恢复兼容性；不能直接运行原 extension 目录。
