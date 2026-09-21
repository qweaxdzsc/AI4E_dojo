<!-- dojo-help: {"domain": "search", "inputs": ["inputs.<stage>.<name>"], "kind": "tutorial", "layer": "help", "summary": "按任务、函数、配置键、产物、错误或案例检索帮助。", "tasks": ["检索 API", "错误定位"], "title": "搜索帮助", "topic_id": "getting-started:search-help"} -->
# 搜索帮助

优先用自然语言描述研究意图，再用精确符号收窄结果：

```python
import ai4e_task as task

hits = task.search_help("外流 CFD 更换采样并读取预测", layer="core.ability")
for hit in hits:
    print(hit["title"], hit["summary"], hit["case_ids"])

exact = task.describe_help_symbol("ai4e_core.run.TrainingRun.record_asset")
page = task.read_help_topic(exact["topic_id"])
```

检索排序依次考虑全限定符号、topic/case/recipe ID、标题与结构化字段、子串和词项重合。搜索结果中的 `path` 与 `anchor` 指向 Markdown 正文；`source_path` 与 `source_line` 指向当前版本源码。

仓库外导出后也可使用 `rg` 搜索 JSONL 与 Markdown。先从帮助首页的能力菜单直接进入，搜索只作补充。不要只读搜索摘要就调用函数；继续阅读完整 API 条目和能力教程，需要完整领域流程时再读关联 standalone。
