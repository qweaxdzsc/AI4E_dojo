# Darcy 能力替换

在基础 Darcy 案例副本中保留 variants.py，将 components.loss 设置为 variants.squared_relative_loss、components.derived 为 variants.error_field、components.consume 为 variants.consume_error。重新训练和预测后，独立 post 校验并读取新增误差数组。目标改变后的检查点不能用原目标恢复。
