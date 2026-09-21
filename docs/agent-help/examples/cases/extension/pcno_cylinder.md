<!-- dojo-help: {"case_ids": ["extension.pcno_cylinder"], "domain": "extension", "kind": "case", "layer": "example", "summary": "替换网络并保存读回速度模长", "title": "extension.pcno_cylinder", "topic_id": "case:extension.pcno_cylinder"} -->
# `extension.pcno_cylinder`

- 类型：`extension`
- 用途：替换网络并保存读回速度模长
- 资源路径：`examples/recipe_extensions/pcno_cylinder`
- 基案例：`pcno.double_cylinder`
- 覆盖文件：
  - `pipeline.py`
  - `local_components.py`

## 物化流程

`copy_example` 会先复制完整基案例，再叠加声明的覆盖文件并写 provenance。
物化后必须重新检查配置、输入和恢复兼容性；不能直接运行原 extension 目录。
