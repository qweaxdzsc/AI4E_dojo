# 自由组件连接

复制本目录到仓库外，执行 `uv run python pipeline.py`。运行记录和数据默认写到复制目录的兄弟目录。

修改 config.yaml 的 radius 调整参数；替换 user_steps.py 的普通函数或在 pipeline.py 插入 run.stage 调用扩展流程。输入输出不同就在 user_wiring.py 转换，不需要继承、注册或统一返回字典。

数据文件 features.json 可由后续用户代码直接读取；运行摘要保存输出引用。平台展示或跨进程交接只在实际使用时另行适配。本例不表示任意组件天然匹配。
