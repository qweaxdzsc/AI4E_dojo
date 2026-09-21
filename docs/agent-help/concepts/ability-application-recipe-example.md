<!-- dojo-help: {"domain": "all", "kind": "concept", "layer": "concept", "summary": "说明计算、领域装配、维护源和交付目录的关系。", "title": "Ability、Application、Recipe 与 Example", "topic_id": "concept:composition-layers"} -->
# Ability、Application、Recipe 与 Example

ability 的输入输出由函数自身定义，不存在全仓统一组件基类。application 只在选择该业务步骤时要求调用约定。recipe 是仓库内维护源，Python 决定顺序，YAML 提供参数和能力选择。example 是完整复制交付物，不依赖 recipe 目录。

变体优先在复制后的 standalone 中修改；可重复参考的变体整理为带 `base_case` 和 `override_files` 的 extension。
