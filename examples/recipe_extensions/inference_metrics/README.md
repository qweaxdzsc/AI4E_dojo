# 自定义推理评价

把 `metrics.py` 复制到仓库外的外流 recipe 目录，在 `infer.py` 里调用：

```python
from metrics import physical_metrics
job = infer_stage.configure_evaluation(job, settings=cfg.infer,
                                       sample_operation=physical_metrics)
```

也可设置 `infer.sample_metric.target: metrics.physical_metrics`。登记时不执行；执行时消费已还原物理空间的数组，不能再次调用模型。返回每个所选字段的一行记录，包含 field_id、values、undefined、algorithm、实体数量和选择声明。算法版本进入结果证据和导出，不与不同算法口径静默比较。

此例保持标准公式，用显式版本证明用户函数实际执行。自定义公式应独立提供数值夹具；未定义值保存 None 和原因。`test_infer_extensions.py` 在外部复制模板后实跑、保存、读回并核验用户版本与真实 VTK。

## 物化说明

- `base_case`: `aero_cfd.shapenet_car_abupt`。该目录是 extension 参考覆盖集，不是独立流程。
- 物化时先复制完整基案例，再叠加清单声明的覆盖文件，并写出 `.dojo-provenance.json`；未声明冲突、缺少基案例或非空目标会失败。
- 物化目录随后可以由 Agent 自由修改、用 direct-core 运行或交给 `ai4e_task` Python API；扩展目录本身不会绑定本机数据或自动启动任务。

## Agent Help Center

本目录是 `参考变体`。Agent 先读取帮助主题 `case:recipe_extensions.inference_metrics`，再按主题关联的 workflow 和 API 参考核对输入、函数签名、产物与证据边界。支持 Python 帮助 API 时可调用：

```python
import ai4e_task as task
print(task.read_help_topic("case:recipe_extensions.inference_metrics")["content"])
```

<!-- research-adaptation-details -->
## 选择与改写说明

物理字段评价函数的局部替换；先物化完整基案例，再按扩展说明修改。

数据形态：mesh, point_fields；训练机制：epoch。

### 具体修改位置

- 基案例：`aero_cfd.shapenet_car_abupt`。先 `copy_example` 物化；返回的 `documentation.entry` 可定位基案例和扩展的说明副本。
- 本变体可改：`metrics`。
- 覆盖/新增文件：`metrics.py`。逐项读这些文件的输入输出和基案例消费者，其他阶段继续继承。
- 物化后检查根配置；若扩展没有覆盖配置，按本页前文将本地组件显式接入，复制文件本身不等于采用了组件。

### 运行与读回

- 运行前填写自己的输入与输出目录；先按本页原有命令/阶段说明执行短程连接验证。更改模型或科学定义时不得沿用不兼容检查点。
- 核对真实运行报告、检查点和固定预测；存在派生结果时必须从后处理读回。恢复与独立推理分别验证，不以导入成功替代。

### 适用边界

- 覆盖文件集不能直接当完整案例运行；未声明的行为沿用基案例。
- 仅声明扩展演示范围，不据此扩大数值精度验收。
