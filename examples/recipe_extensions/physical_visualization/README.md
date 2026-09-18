# 自定义物理场图片

将本目录复制到研究目录，安装 `ai4e-core[post]`。输入是已交付体网格的固定单样本推理清单。

`uv run python post.py /absolute/sample/manifest.json /absolute/output`

`custom_render.py` 是可替换的普通绘图函数；`post.py` 明确读取结果、绑定网格、生成速度平方字段、绘图、保存及读回。新字段随 VTK 文件保存，图片生成不改变原始输入。更换颜色、相机、添加切片或额外字段都在此目录修改，不要求修改框架。
