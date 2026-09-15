# 参数化 PDE：独立数据生成与 PI-BSNet

用户修改 `config.yaml`；方程是 contrib 中普通 PyTorch 函数，不要求 Field、Equation
对象或 YAML 导数表达式。特殊研究使用可安装用户模块，通过 `train.step` 注入普通
`step(model, prepared)`，返回 `loss` 与 `losses`。函数收到单实例准备包，是否每实例更新
由 `train.update_group` 决定，用户函数不得自行 backward 或 optimizer.step。

## 使用顺序

在安装了 `ai4e-contrib[pibsnet]` 的环境中，从仓库根运行。例如 Neumann：

```bash
uv run python recipes/parametric_pde/generate.py --config examples/parametric_pde/neumann_diffusion/generate.yaml
uv run python recipes/parametric_pde/pipeline.py --config examples/parametric_pde/neumann_diffusion/config.yaml
```

也可以分别调用 `rawprep.py`、`trainprep.py`、`train.py`、`post.py`。独立 post 必须
用 `--set post.checkpoint=/实际路径/checkpoints/last.pt` 指定已训练权重。
恢复使用 `--set train.resume=/实际路径/checkpoints/latest.pt`，同时增大 max_epochs；
不要重跑已经生成的准备目录。改变准备语义时写入新目录，失败不会发布完整清单。

本机缓存显式指定 `UV_CACHE_DIR=/Users/zonghui/work/project_simulation/dojo_train/pibsnet/cache/uv`。
示例的数据/运行路径遵循本机约定；复制到其他机器后修改路径。路径相对配置文件解析。
源码采用单层打包，开发修改后刷新可编辑安装；安装验收不能以源码 import 代替 wheel。

## 配置位置

- `dataset.manifest`：已独立生成的物理数据，不会在训练时生成。
- `model.control_points/degree/hidden_dim`：控制网格与网络。
- `model.sampling`：监督点、内部、初值、命名边界、周期点对；准备阶段冻结。
- `model.boundary_conditions`：边界 → u → type/value/gradient。
- `model.initial_conditions.u`：目标及交角规则。
- `model.constraints`：损失方式、归约、权重；物理条件与训练权重分开。
- `train.update_group`：epoch_sum 或 instance；默认对应原案例更新次数。
- `train.gradient_clip: null`：不裁剪，保留原生梯度。
- `trainprep.execute/train.execute`：显式允许数值执行；关闭时只检查。

常规边界：`fixed_value` 需要 value，`fixed_gradient` 需要物理外法向 gradient，
`zero_gradient` 不接受额外目标。函数目标写 `{function: my_pde.conditions.target}`，
函数接收物理坐标张量与实例参数字典。梯形物理坐标列为 t,Y,X，法向列为 X,Y。
未知字段、边界、旧采样键和冲突周期条件拒绝；不静默补默认值。

原始 Python 扩展示例见 `examples/parametric_pde/equations.py`。用户模块安装后用
全限定导入路径接入，不依靠当前目录碰巧可以 import。

## 修正与证据边界

当前正式训练/对照完成情况以 `.context/mvp/pibsnet-acceptance.md` 为准。
小网络两轮只证明链路，不代表正式预算精度。

Neumann、Advection已选择原参数样条及原数据生成路径：Neumann先顺序汇总整轮损失再一次反传；Advection恢复首行插值覆盖及原MSELoss。两例导数输出键为parameter_t/parameter_x/parameter_xx，不能直接当作物理导数传入普通方程库。CD、Burgers进一步原代码对齐待范围确认。梯形已按用户选定十实例实验迁入：原Euler近似数据、完整40000输出、初始系数内部零/四边一、原参数空间样条递推、Eq.84形式的近似残差。默认3000轮、30000次更新、PDE权重0.001。参数导数不能标为物理导数，仍保留论文与源码的未决差异。
Advection 的model.hard_initial表示原初始控制行插值，不表示解析lifting，也不承诺非恒定初值逐点严格满足。CD 只硬施加右边界，
初值保留软约束能力但参考默认权重为零。梯形固定初始控制平面并记录实际违约，不把系数赋值误称为全点严格满足初值。
因此 CD 自由输出数为25×24（原为24×24）；梯形输出完整控制网格后覆盖初边界，其余带硬边界模型仍只预测自由系数；
网络拓扑、约束和数据变化必须与原仓库分开报告，不能声明数值等价。

原仓库未发现LICENSE文件；Neumann、Advection及梯形数值函数按锁定源码迁入，其余方程/物理样条按数学定义实现，来源信息记录于模型目录。

梯形生成配置默认train=10、test=10，连续MT19937流在训练后保留一次单例展示的抽样消耗。默认新目录`trapezoid_dojo_10`；旧数据、准备和检查点不覆盖。网格子集支持`model.sampling`，离网采样及特殊条件目前明确拒绝，不能静默忽略。独立post同时报告`mean_relative_l2`（全时空）与`mean_time_relative_l2`（逐时间空间L2，再平均时间/实例）。

## 原文献参数与采样范围

正式默认 `model.sampling.interior.include_boundary: true`，表示沿用原脚本完整时空网格计算 PDE 项，包括初值和边界点。用户研究严格内部配点时显式关闭，但这改变参考协议，必须重新准备，不能沿用原预算对齐结论。

泛化配置为 `examples/parametric_pde/generalization.yaml`，复用 Advection 数据。`train.evaluation` 控制既有训练循环在零基 0、50、…、1950、1999 轮后评价完整测试集，未开启时不额外评价。`tools/verification/pibsnet/generalization.py` 严格核对正式评价次数后才拟合经验关系。

用户已要求所有正式验证使用原文献参数。不得通过改初始化、优化器、权重或训练预算把失败结果标成复现通过。源码缺陷修正与物理点集协议在专项验收中逐项披露。非 Neumann 初值罚项及全部周期罚项默认权重为零，只记录监测值；启用这些权重属于用户研究配置，不能沿用原目标对齐结论。

原案例用户自定义训练步可以调用`ai4e_contrib.ability.model.pibsnet.component.predictions(model, prepared, cfg)`获得场与具名参数导数。使用内置step时不需创建自定义组件；改变原条件或增加周期罚项需明确自定义训练目标，不能沿用参考精度结论。
