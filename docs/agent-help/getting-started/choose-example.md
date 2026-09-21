<!-- dojo-help: {"domain": "examples", "errors": ["KeyError", "FileExistsError", "ValueError"], "kind": "tutorial", "layer": "example", "summary": "从 standalone 开始，按需物化 extension。", "tasks": ["案例选择", "复制案例"], "title": "选择并复制案例", "topic_id": "getting-started:choose-example"} -->
# 选择并复制案例

```python
from pathlib import Path
import ai4e_task as task

candidates = task.list_examples(case_type="standalone")
case_id = "parametric_pde.neumann_diffusion"
check = task.check_example(case_id)
if not check["ok"]:
    raise RuntimeError(check["errors"])
result = task.copy_example(case_id, Path("./neumann-study"))
```

standalone 是完整可运行目录。extension 是基案例上的参考变体，`copy_example` 会复制 `base_case`、叠加声明的覆盖文件并写 `.dojo-provenance.json`。目标目录必须为空；复制不会绑定本机数据，也不会启动任务。

选择后必须阅读案例 README、config、configuration、pipeline 和全部阶段脚本。模型名相同不等于数据字段、训练目标或恢复状态兼容。
