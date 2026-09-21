<!-- dojo-help: {"case_ids": ["geotransolver.darcy", "geotransolver.bumper_beam", "recipe_extensions.geotransolver", "aero_cfd.shapenet_car_geotransolver", "aero_cfd.nasa_crm_geotransolver", "recipe_extensions.geotransolver_aero"], "domain": "parametric-pde", "kind": "workflow", "layer": "workflow", "summary": "具名网格场与轨迹的core能力、完整recipe、Task与独立post。", "tasks": ["模型集成", "core能力", "Darcy", "保险杠", "Task", "恢复", "能力替换"], "title": "GeoTransolver研究流程", "topic_id": "workflow:geotransolver"} -->
# GeoTransolver 具名网格场与轨迹研究

GeoTransolver 的可复用数据、几何、注意力和训练计算位于 core；贡献侧只组合网络和绑定 Darcy/保险杠及外流语义。本期通过 Python、可复制案例与 Task 使用，不登记 Web。当前验收范围从案例说明和集成记录核对；短训对照不代表论文复现。

## 选择与复制

安装 `ai4e-contrib[geotransolver]` 和 `ai4e-task`，使用该安装环境的 Python。原始数据由调用方指定，生成数据及运行目录独立配置。

```python
import ai4e_task as task

task.copy_example("geotransolver.darcy", "./darcy")
task.copy_example("geotransolver.bumper_beam", "./bumper")
```

每套案例包含 README、配置、配置加载器及五个显式阶段、pipeline。配置 `inputs.rawprep.source`、`run_root`、`data_root` 后运行复制目录中的 pipeline。`pipeline.stages` 选择顺序子集，阶段先后由 Python 正文决定。

- Darcy：smooth1前1000训练/smooth2前200评价，原421网格保留，模型采样85网格。全局float32标量统计，物理空间逐样本相对L2。
- 保险杠：124训练/7验证，共同11帧，预测后续10帧全部节点。初态、时间和原始单元场保存在物理数据中，转点及邻域缓存属于模型准备。

## 独立步骤与恢复

`inputs.trainprep.dataset` 指向物理清单；`inputs.train.preparation` 和 `inputs.infer.preparation` 指向模型准备清单；`inputs.infer.checkpoint` 指向固定完整检查点；`inputs.post.results` 指向固定结果清单。与本次上游返回值冲突时报错。

Darcy/保险杠训练默认20次更新及120秒，用于本机工程检查。`train.updates` 是累计更新目标；`inputs.train.resume` 恢复模型、全部优化器、调度器、随机数与样本游标。短训更新数不会压缩原参考学习率日程。训练与推理分别声明device；普通PyTorch CPU/MPS float32支持，其他扩展分支明确拒绝。

post只读取固定预测、真值、拓扑及派生数组，不构建模型。将整个结果目录复制到其他位置，设置新的 `inputs.post.results`，选择 `[post]` 即可读回。输出包括VTKHDF、逐样本/时间/字段指标、CSV、误差曲线和场图。

## 使用 Task

```python
import ai4e_task as task
from pathlib import Path
import yaml

project = Path("./research")
task.create_project(project)
config = yaml.safe_load(Path("./darcy/config.yaml").read_text())
current = task.new_task(project, "Darcy", source="./darcy", configuration=config)
record = task.submit_run(project, current["id"])
result = task.wait_run(project, record["id"], timeout=600)
```

为跨目录执行，程序调用前将公共输入/输出解析为明确路径，或调用案例配置加载器。Task复用同一Python正文，未新增模型专用分支。

## 替换能力

复制 `recipe_extensions.geotransolver` 会物化Darcy基础案例并添加 variants。设置 `components.loss=variants.squared_relative_loss`、`components.derived=variants.error_field`、`components.consume=variants.consume_error`：训练目标改变，推理新增有符号误差数组，独立post验证并消费。目标改变后拒绝继续旧目标检查点。

普通脚本也可直接组合 `relative_norm`、`tensor_moments`、`radius_indices`、`ContextProjector`、`GALEBlock`、`CombinedOptimizer` 和 `fit_fields`。这些core能力不导入贡献包或PhysicsNeMo。参数和返回布局从真实API索引查询。

## ShapeNet-Car 与 NASA CRM

复制 `aero_cfd.shapenet_car_geotransolver` 或 `aero_cfd.nasa_crm_geotransolver`。设置 `inputs.trainprep.dataset` 为既有完整 PT/VTKHDF 物理清单，配置数据和运行目录，执行 pipeline。需要原始处理时显式设置 rawprep 来源并把 rawprep 加入阶段。

外流默认两轮，`train.max_epochs` 为累计轮次目标。四层 128 维基础 GALE 关闭局部编码；训练每域最多 8192 查询点，几何按样本固定，推理按 8192 块恢复全部实体。块大小和种子改变属于新实验。NASA 全局条件六维，ShapeNet 双域不构造虚假工况。NASA CRM 不等于论文 SHIFT-Wing。

复制 `recipe_extensions.geotransolver_aero` 可修改实际 L1 监督、保存压力绝对误差并由独立 post 读回绘图。固定结果必须完整复制数组及网格；post 不消费检查点或运行网络。
