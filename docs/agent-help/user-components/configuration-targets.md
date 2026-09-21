<!-- dojo-help: {"domain": "components", "kind": "how-to", "layer": "user-component", "summary": "把可重建组件路径与参数写入复制目录配置。", "tasks": ["编写用户组件", "组件调用证明"], "title": "全限定组件配置", "topic_id": "user-component:configuration-targets"} -->
# 全限定组件配置

配置使用 `package.module:object` 或案例现行加载器支持的全限定路径形式。加载器负责 import、构造和错误报告；run 不解释模型参数。

保存前验证模块可从目标解释器导入。源码快照证明来源，不应把所有脚本字节差异当作拒绝研究分支的条件。

## 先确认加载格式

不同 application 可能接受 `package.module.object`、`package.module:object` 或整个模块路径。不要在帮助页统一猜一种格式；先查询所选配置加载器：

```python
import ai4e_task as task

case = task.read_help_topic("case:parametric_pde.neumann_diffusion")
for hit in task.search_help("load_component", limit=10):
    print(hit["topic_id"], hit["source_path"])
```

参数化 PDE 当前 `load_component` 使用点号分隔对象；外流模型配置通常指向提供一组公开函数的模块。复制目录中的相对本地模块必须能由阶段脚本的实际解释器找到，不能靠开发仓库 `PYTHONPATH`。

## 建议配置形态

```yaml
components:
  model: variants
  sampler: custom_sampling.reverse_geometry
  objective: objectives.relative_mse
train:
  learning_rate: 0.0001
  max_epochs: 2
```

配置只保存可重建声明。运行时对象、闭包、lambda、打开的文件、设备句柄和已实例化 optimizer 不写入 YAML。

## 加载与校验边界

配置加载器负责：

1. 合并案例默认值与用户 YAML；
2. 应用 `--set` 点号覆盖；
3. 以配置文件位置解析相对路径；
4. 拒绝未知旧键和互相冲突的新旧键；
5. 校验组件路径和参数结构；
6. 返回最终配置给 `run.launch`。

`ai4e_core.run` 不解释外流、PDE 或模型专属参数。组件构造和领域参数转换留在 contrib/application 或复制后的案例连接中。

## Task 中编辑配置

Task 管理的同一案例使用修订保护：

```python
import ai4e_task as task

current = task.read_configuration(project, task_id)
config = current["config"]
config["components"]["model"] = "variants"
saved = task.replace_configuration(
    project,
    task_id,
    config,
    revision=current["revision"],
)
```

局部编辑可使用 `save_configuration`；完整替换使用 `replace_configuration`。运行时一次性覆盖可传给 `submit_run(overrides=[...])`。编辑和运行不创建正式版本，但每次运行会捕获当时的代码、配置和外部输入。

## 验证

从案例目录外启动阶段脚本，检查 `run_dir/inputs/config.yaml` 中的最终组件路径和参数；再从阶段报告或组件身份记录证明它被调用。只验证 YAML 中出现字符串，无法证明加载、构造或计算真实发生。
