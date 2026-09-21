<!-- dojo-help: {"case_ids": ["parametric_pde.convection_diffusion"], "domain": "parametric_pde", "kind": "case", "layer": "example", "summary": "参数化 PDE 研究", "title": "parametric_pde.convection_diffusion", "topic_id": "case:parametric_pde.convection_diffusion"} -->
# `parametric_pde.convection_diffusion`

- 类型：`standalone`
- 用途：参数化 PDE 研究
- 资源路径：`examples/parametric_pde/convection_diffusion`
- 模型：`PI-BSNet`
- 数据集：`convection_diffusion`
- 入口：`pipeline.py`
- Recipe 来源：`parametric_pde`
- 依赖：`ai4e-core`, `ai4e-contrib`

## 阶段

- `generate.py`
- `rawprep.py`
- `trainprep.py`
- `train.py`
- `infer.py`
- `post.py`

## 使用流程

1. 用 `check_example` 检查资源，再用 `copy_example` 复制到仓库外空目录。
2. 阅读复制目录的 README、config、pipeline 和全部阶段脚本。
3. 先直接执行 pipeline；需要版本、后台运行或恢复时再把同一目录交给 Task。
4. 按 README 读回配置、阶段摘要、检查点、预测、指标和 post 结果。

目录和文件存在不代表运行成功；当前真实输入、预算和证据边界以案例 README 为准。
