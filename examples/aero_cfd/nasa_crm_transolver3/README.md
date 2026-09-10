# nasa_crm_transolver3

复制本目录到个人实验目录，修改 config.yaml 中的来源、数据产物与运行路径。阶段脚本与共享 aero_cfd 模板一致，不是安装包。

在 Dojo 环境先执行 `uv sync --all-packages --extra transolver3 --inexact`（机翼案例）；然后运行 `uv run --no-sync python /个人实验目录/pipeline.py`。独立阶段使用对应脚本和同一配置；已有准备通过 train.preparation 指定，后处理用 post.checkpoint 指向检查点。

默认模型规模为正式网络。机翼案例默认两轮；后处理推理全测试集、网格默认随机一例，完整导出用 `--set post.all_samples=true`。仅补后处理可设 post.infer=false 并指定原数据、预测和检查点路径。不会把跳过硬件测试或小模型结果当成正式验收。

当前案例使用 rawprep / trainprep / model / train / post 五段配置，运行顺序为 rawprep → trainprep → train → post。采样与归一化位于 trainprep 下，脚本和配置目录必须与数据、运行输出目录分开。
