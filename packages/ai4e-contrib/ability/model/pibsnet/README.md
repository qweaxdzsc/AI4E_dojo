# PI-BSNet

唯一的两层 ReLU 参数网络和张量积 B 样条实现。公开 `PIBSNet`、`basis`、
`prepare_grid`、`prepare_points`、`evaluate_fields`；领域装配经 `component` 接入。

独立实现基于数学定义，参考仓库提交 `40ffb6239d865b6b7a16538559939a990e6d9cd5`。
梯形 `trapezoid.py`、`trapezoid_basis.py` 按锁定源码数值定义迁入所选实验，保留来源。未复制整套训练脚本；原仓库未提供明确 LICENSE。本模块不导入原仓库。

物理初边界修正、用户入口和未完成验收见共享 recipe README 与专项验收记录。

当前Neumann/Advection通过source_cases装配，neumann_numerics/advection_numerics保留锁定源码定义。Neumann汇总整轮损失后一次反传，Advection使用原首行插值及MSELoss；参数导数明确命名，不冒称物理导数。普通物理方程库不受影响。旧数据/准备/检查点须重新生成训练；没有案例双版本开关。
