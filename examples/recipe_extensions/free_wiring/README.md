# 自由组件连接

复制本目录到仓库外，执行 `uv run python pipeline.py`。运行记录和数据默认写到复制目录的兄弟目录。

修改 config.yaml 的 radius 调整参数；替换 user_steps.py 的普通函数或在 pipeline.py 插入 run.stage 调用扩展流程。输入输出不同就在 user_wiring.py 转换，不需要继承、注册或统一返回字典。

数据文件 features.json 可由后续用户代码直接读取；运行摘要保存输出引用。平台展示或跨进程交接只在实际使用时另行适配。本例不表示任意组件天然匹配。

## 物化说明

- `base_case`: `aero_cfd.shapenet_car_abupt`。该目录是 extension 参考覆盖集，不是独立流程。
- 物化时先复制完整基案例，再叠加清单声明的覆盖文件，并写出 `.dojo-provenance.json`；未声明冲突、缺少基案例或非空目标会失败。
- 物化目录随后可以由 Agent 自由修改、用 direct-core 运行或交给 `ai4e_task` Python API；扩展目录本身不会绑定本机数据或自动启动任务。

## Agent Help Center

本目录是 `参考变体`。Agent 先读取帮助主题 `case:recipe_extensions.free_wiring`，再按主题关联的 workflow 和 API 参考核对输入、函数签名、产物与证据边界。支持 Python 帮助 API 时可调用：

```python
import ai4e_task as task
print(task.read_help_topic("case:recipe_extensions.free_wiring")["content"])
```
