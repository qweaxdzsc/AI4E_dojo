<!-- dojo-help: {"domain": "meshgraphnet", "kind": "recipe", "layer": "recipe", "recipe_ids": ["meshgraphnet"], "summary": "meshgraphnet 维护源的阶段、配置和 standalone 对应关系。", "title": "meshgraphnet Recipe", "topic_id": "recipe:meshgraphnet"} -->
# meshgraphnet Recipe

Recipe 是仓库内维护源，阶段包括 rawprep、trainprep、train、infer、post、pipeline。Python 文件展示真实步骤和普通返回值交接，YAML 只提供参数和能力选择。

Agent 实际研究从相应 standalone 开始。使用 `search_help('meshgraphnet', kind="recipe")` 查询此 recipe 的全部公开函数、源码位置和关联案例；生成的逐函数参考位于同目录 `api.md`。

修改公共阶段时同时核对 recipe 与 manifest 声明的 `shared_stage_files`，配置、数据根和预算允许不同，阶段输入键、恢复交接和产物语义不能漂移。
