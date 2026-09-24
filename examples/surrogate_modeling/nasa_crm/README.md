# NASA CRM 全局代理

六个全局工况预测 `c_d/c_l/c_my` 三个无量纲响应；默认二次 RSM，105 条公开训练样本的二次设计矩阵必须满足 28 列满秩。这是全局代理任务，不是百万点场预测或平台网格准备。`trainprep` 直接读取 HDF5 组属性，训练/验证必须是不同来源文件。同名 Sample 保留来源身份。

在 `inputs.trainprep.train_h5` 和 `test_h5` 填写已取得的 NASA CRM 两个文件路径。

复制后可改写代理构造、拟合或评价步骤；训练/验证来源身份和三项响应定义不得隐式改变。

## 运行与交接

复制本目录到研究工作目录，安装 Dojo 后执行 `uv run --no-sync python pipeline.py --config config.yaml`。配置的相对路径相对于配置文件；将 `run_root/data_root` 显式设为自己的独立实验目录（如 `../outputs/study/`）。Python 正文依次执行 trainprep → train → infer → post；`pipeline.stages` 只筛选范围。

独立执行时设置 `inputs.train.preparation`、`inputs.infer.preparation/checkpoint` 或 `inputs.post.results`，再执行对应脚本。拟合状态与准备可整体搬移；推理在计算前核对准备及子清单摘要、字段、单位、训练统计、模型与组件声明。post 只读固定结果，可以在移走原数据和拟合状态之后复算。

`train.seconds=9000` 是拟合阶段的协作截止；单次不可中断的 BLAS 需要外层进程硬截止。每个实际组合最多 10800 秒，包括准备、独立参考、Dojo、重试和恢复核对；主控负责累计账和串行执行，本模板不宣称阶段时限等于完整预算。代数模型没有伪造的 epoch、优化器或继续训练；重新拟合产生新的状态。

## 自定义能力

`components.fit` 显式选择全限定普通函数，调用为 `(family, x, y, params, deadline=..., cancelled=...) -> (model, state, diagnostics)`；`components.rebuild` 接收 state 并返回带 `predict(x)` 的普通对象。自定义拟合使用 `model.family: custom`，参数由实际函数解释。只保存可重建的普通字典、标量和数组；不 pickle 返回的 model，不要求继承基类或注册框架。

默认可切换 RSM、RBF、Kriging、LightGBM，并同步修改 parameters。LightGBM 需要显式安装可选 boosting 依赖。Kriging 固定结果另外保存 latent 边际方差：NASA 为恢复物理响应尺度的方差，POD 为系数方差；不声称联合物理场协方差，post 的均值评价不依赖方差。

本模板交付可执行流程；真实数据精度与时间以主控独立验收记录为准。
