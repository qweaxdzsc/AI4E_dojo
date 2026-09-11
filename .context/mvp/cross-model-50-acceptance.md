# 五案例50轮本地实验

状态：运行中，尚未完成验收。NASA AB-UPT已完成50轮、4200更新；其余案例和最终报告仍待完成。独立输出根 `/private/tmp/dojo-cross-model-50`。

五组沿用正式网络、物理PT与固定五测试样本；MPS/fp32、50 epoch、从头训练、关闭训练期评价，学习率调度预算为50轮。NASA各4200更新，汽车各39450更新。顺序执行train、post、compare，阶段状态与墙钟耗时记录在 execution.json；成功注册不复用历史单轮目录。

验收入口：`DOJO_CROSS_MODEL_RESULTS=/private/tmp/dojo-cross-model-50 DOJO_CROSS_MODEL_EPOCHS=50 DOJO_CROSS_MODEL_DEVICE=mps uv run python -m pytest tests/integration/test_cross_model_acceptance.py`。默认环境仍验收历史1轮MPS；新增显式预算与设备选择，同时检查全部轮次损失有限。跳过不算完成。

报告应在 reports/nasa/index.html 与 reports/shapenet/index.html；完成之前这些路径不表示报告已交付。物理指标按固定样本全点重新计算，曲线/云图保持共同几何与色标。
