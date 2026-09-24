<!-- dojo-help: {"topic_id": "workflow:case-discovery", "title": "从案例说明定位改写入口", "kind": "workflow", "layer": "workflow", "domain": "research", "summary": "列表摘要帮助初选，案例正文解释交接，extension描述相对基案例的变化", "tasks": ["选择案例", "复制案例", "extension", "案例说明"], "symbols": ["ai4e_task.list_examples", "ai4e_task.copy_example"]} -->
# 从案例说明定位改写入口

列表的 `research` 给出用途、数据形态、训练机制、替换点和限制。它是初选说明，不保证形状或科学定义自动兼容。标签描述已实现流程，不决定研究者下一轮怎么优化。

```python-fragment
import ai4e_task as task
candidates = task.list_examples(data_form="regular_grid", training_pattern="iteration")
for case in candidates:
    print(case["id"], case["research"])
print(task.read_help_topic("case:geotransolver.darcy")["content"])
```

`query` 是大小写无关子串；多个条件取交集，结果保留清单顺序。无匹配时放宽筛选再读正文，不把“没搜到”当作工具不存在。旧条目没有新标签时只按原用途检索，不猜标签。

案例帮助主题包含真实README生成的正文和来源摘要。具体输入输出、修改文件、运行恢复及证据边界都在正文；API签名仍从对应符号页核对。

```python-fragment
receipt = task.copy_example("recipe_extensions.tail_batch", "./my-tail-study")
print(receipt["documentation"]["entry"])
# 进入 my-tail-study/.dojo-docs/index.md，可同时读基案例与变体。
```

extension先物化完整base_case再叠加声明文件；复制后的根README和脚本保持原来源字节，说明副本单独交付。副本里的有效文件链接指向研究目录；未交付历史参考会明确标注，不能充当操作步骤。需要全部离线帮助时使用export_guide/export_help，它们同时交付案例正文和基案例主题。

两个小型变体：尾批见 `case:recipe_extensions.tail_batch`；具名用户状态、验证和最佳快照恢复见 `case:recipe_extensions.research_state`。变体只证明工程交接，不能据此宣布论文复现。
