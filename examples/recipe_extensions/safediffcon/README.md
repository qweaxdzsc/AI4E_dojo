# 控制研究扩展

复制SafeDiffCon模板和本目录`variants.py`到仓库外实验目录，按模板README设置模型、引导或派生组件路径。三种变体使用独立输出位置；数值和实际运行证据见SafeDiffCon 运行记录。

安全变体只改变采样时的安全梯度，并增加控制能量惩罚；校准、重加权与评价阈值保持基线语义，因此可直接比较结果。

## 物化说明

- `base_case`: `safediffcon.burgers`。该目录是 extension 参考覆盖集，不是独立流程。
- 物化时先复制完整基案例，再叠加清单声明的覆盖文件，并写出 `.dojo-provenance.json`；未声明冲突、缺少基案例或非空目标会失败。
- 物化目录随后可以由 Agent 自由修改、用 direct-core 运行或交给 `ai4e_task` Python API；扩展目录本身不会绑定本机数据或自动启动任务。

## Agent Help Center

本目录是 `参考变体`。Agent 先读取帮助主题 `case:recipe_extensions.safediffcon`，再按主题关联的 workflow 和 API 参考核对输入、函数签名、产物与证据边界。支持 Python 帮助 API 时可调用：

```python
import ai4e_task as task
print(task.read_help_topic("case:recipe_extensions.safediffcon")["content"])
```
