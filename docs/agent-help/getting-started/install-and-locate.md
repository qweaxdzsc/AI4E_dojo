<!-- dojo-help: {"domain": "installation", "errors": ["ModuleNotFoundError", "FileNotFoundError"], "kind": "tutorial", "layer": "help", "summary": "确认当前解释器、帮助资源、案例资源和实际安装源码。", "tasks": ["安装检查", "源码定位"], "title": "安装与定位", "topic_id": "getting-started:install-and-locate"} -->
# 安装与定位

先确认 Agent 和研究运行使用同一个 Python 解释器：

```python
import ai4e_task as task

info = task.guide_info()
print(info["python"])
print(info["help_root"])
print(info["examples"])
print(task.source_location("ai4e_core"))
```

`guide_info` 返回的路径是当前解释器看到的资源。不要根据仓库目录猜测安装副本。`source_location` 只定位模块，不加载模型或训练栈。若 `ai4e_contrib` 未安装，仍可搜索其静态帮助；真实运行相关案例前再安装案例声明的可选依赖。

仓库内开发可直接读取 `docs/agent-help/index.md`。仓库外使用可调用 `export_help` 导出完整帮助树，或由 `guide export` 同时导出 skill、启动指南和帮助中心。
