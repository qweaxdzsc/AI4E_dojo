# ai4e-spec

- 状态：可安装，已交付最小模型协议
- 职责：稳定的数据、组件和 artifact 契约。
- 允许依赖：Python 标准库的轻量能力。
- 禁止依赖：其他 ai4e 包、torch、numpy、服务或渲染实现。

components/model.py 已交付 ModelFactory 和 ModelRequirements；完整 FieldSpec、Sample 与 artifact schema 仍为规划。

本目录同时是包工程根和源码根；由根构建配置映射为 Python 导入名 `ai4e_spec`，不得再嵌套同名目录。
