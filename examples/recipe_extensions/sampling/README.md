# 替换训练采样

复制本目录并安装 Dojo，配置数据根及输出目录后用 `uv run python pipeline.py` 执行。

`model.sampling.target` 选择本地普通函数；函数改变几何点选择顺序，同时将剩余采样和元信息交给原模型准备能力。它在训练逐样本取数时执行，不在 YAML 加步骤顺序。训练准备记录函数源码和参数，独立训练按同一引用恢复。

也可在 `trainprep.py` 的 `configure_sampling` 中直接传入 `operation`；此时取消配置中的 target。由于 direct callable 不写入用户配置，任何可独立启动并继续使用它的阶段也必须在 Python 正文显式传入同一 callable，例如训练脚本把它作为 `open_training(..., prepare=...)` 的参数。准备记录只证明当次准备实际调用的组件，不把冻结源码反向注入当前训练配置。采样能力须保留批次结构、原实体 ID、种子和轮次参数。

## 物化说明

- `base_case`: `aero_cfd.shapenet_car_abupt`。该目录是 extension 参考覆盖集，不是独立流程。
- 物化时先复制完整基案例，再叠加清单声明的覆盖文件，并写出 `.dojo-provenance.json`；未声明冲突、缺少基案例或非空目标会失败。
- 物化目录随后可以由 Agent 自由修改、用 direct-core 运行或交给 `ai4e_task` Python API；扩展目录本身不会绑定本机数据或自动启动任务。

## Agent Help Center

本目录是 `参考变体`。Agent 先读取帮助主题 `case:recipe_extensions.sampling`，再按主题关联的 workflow 和 API 参考核对输入、函数签名、产物与证据边界。支持 Python 帮助 API 时可调用：

```python
import ai4e_task as task
print(task.read_help_topic("case:recipe_extensions.sampling")["content"])
```
