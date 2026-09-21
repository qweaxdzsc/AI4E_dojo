# 自定义物理场图片

将本目录复制到研究目录，安装 `ai4e-core[post]`。输入是已交付体网格的固定单样本推理清单。

`uv run python post.py /absolute/sample/manifest.json /absolute/output`

`custom_render.py` 是可替换的普通绘图函数；`post.py` 明确读取结果、绑定网格、生成速度平方字段、绘图、保存及读回。新字段随 VTK 文件保存，图片生成不改变原始输入。更换颜色、相机、添加切片或额外字段都在此目录修改，不要求修改框架。

## 物化说明

- `base_case`: `aero_cfd.shapenet_car_abupt`。该目录是 extension 参考覆盖集，不是独立流程。
- 物化时先复制完整基案例，再叠加清单声明的覆盖文件，并写出 `.dojo-provenance.json`；未声明冲突、缺少基案例或非空目标会失败。
- 物化目录随后可以由 Agent 自由修改、用 direct-core 运行或交给 `ai4e_task` Python API；扩展目录本身不会绑定本机数据或自动启动任务。

## Agent Help Center

本目录是 `参考变体`。Agent 先读取帮助主题 `case:recipe_extensions.physical_visualization`，再按主题关联的 workflow 和 API 参考核对输入、函数签名、产物与证据边界。支持 Python 帮助 API 时可调用：

```python
import ai4e_task as task
print(task.read_help_topic("case:recipe_extensions.physical_visualization")["content"])
```
