# PCNO 圆柱真实扩展

物化 `pcno.double_cylinder` 基础案例后覆盖本目录文件。
把 `components.network` 改为 `local_components.shifted_network`，以新实验训练，验证构造器实际生效。
在推理与后处理之间，流程调用本地speed函数保存速度模长；post读回该数组并产生derived_speed统计。
已有结果也可单独绑定inputs.post.results，只运行post，核验不调用网络。
