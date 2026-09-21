<!-- dojo-help: {"domain": "all", "kind": "catalog", "layer": "example", "summary": "从机器清单查看全部 standalone 和 extension，并进入逐案例页面。", "tasks": ["案例发现"], "title": "案例目录", "topic_id": "example:catalog"} -->
# 案例目录

案例机器清单由 `examples/case-manifest.json` 提供，安装资源中的 `indexes/cases.json` 是同一构建快照。使用：

```python
import ai4e_task as task
for case in task.list_examples():
    print(case["id"], case["type"], case.get("purpose"))
```

按案例 ID 调用 `read_help_topic("case:" + case_id)` 获取阶段、依赖、入口、基案例和覆盖文件。只有 standalone 是完整起点；extension 必须物化后运行。

地热研究使用 `geothermal.pcno`；温降扩展使用 `extension.pcno`。流程说明见[地热双场研究](../workflows/geothermal.md)。
