# ai4e-viz

- 状态：PLANNED
- 职责：只读 run/report artifact 的静态与交互渲染。
- 允许依赖：ai4e-spec。
- 禁止依赖：ai4e-core、模型、Trainer 和 Dataset 实现。

本目录同时是包工程根和源码根；未来由根构建配置映射为 Python 导入名 `ai4e_viz`，不得再嵌套同名目录。
