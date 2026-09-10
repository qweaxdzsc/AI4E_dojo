---
name: Recipe 五段配置与运行快照职责修正
overview: 案例解释五段 YAML 并提取原库参数，run 通过通用加载回调冻结最终用户配置，运行事实另行记录；库方法与产物版本不因分组更改。
todos:
  - id: configuration
    content: 五段配置、默认展开、路径解析与稳定参数提取
    status: completed
  - id: snapshot
    content: 通用 config_loader、冻结快照、来源报告和显式预检参数
    status: completed
  - id: recipe
    content: rawprep 案例入口调用原 datapre 业务方法
    status: completed
  - id: consumers
    content: task 选择器、缺条件保护及参考工具参数
    status: completed
  - id: acceptance
    content: 相关回归、实际安装、真实 MPS 两轮及补跑验收
    status: completed
isProject: false
---

# Recipe 五段配置与运行快照职责修正计划

## 业务描述总结

- **做什么**：研究者以五段配置组织实验，运行快照保存同一份最终生效配置。
- **怎么做**：案例加载、校验、展开默认值并提取业务参数；业务库保持稳定接口；运行模块记录配置和运行事实，不解释五段业务字段。
- **完成标准**：相关测试、实际安装和真实加速设备全流程验收通过；未通过项不得宣称完成。

## 讨论

### 文件名与库接口分开

案例 `rawprep`（原始处理）调用库既有 `datapre`（前处理业务方法），不要求函数同名。案例阶段日志采用新名称，内部业务报告值保留原契约。

### 配置与事实分开

五段用户配置、各阶段业务参数、运行生成的事实分开管理。开始运行后不以业务参数覆盖输入快照；数据来源和分片进入报告，准备与检查点引用使用既有产物。

### 兼容与范围

旧用户扁平键和旧案例阶段拒绝，原库参数接口继续有效。本轮从头准备训练用于验收，不新增产物版本或旧检查点禁用规则，不改变模型、原子能力及数值容差。

## 实施评审

### 功能点

**主功能 A：正确读取实验配置**

BDD：
- Given 研究者填写新案例配置
- When 加载实验
- Then 得到完整的五段配置和等价的原库参数

子功能：
- A1：五段映射及旧用户键拒绝。
- A2：默认值、插值和相对路径正确。
- A3：两类模型输入语义保持一致。

**主功能 B：忠实记录实验输入**

BDD：
- Given 案例已准备最终配置
- When 创建运行
- Then 快照冻结，业务参数不再覆盖它

子功能：
- B1：运行接受案例加载函数。
- B2：快照与检查点附带配置一致。
- B3：实际来源、分片和动态产物另行记录。

**主功能 C：完整运行与独立补跑**

BDD：
- Given 研究者选择执行范围
- When 运行案例流水线
- Then 原业务接口正确交接，失败保留诊断和部分产物

子功能：
- C1：新前处理入口调用原库方法。
- C2：准备、训练、恢复和仅网格补跑正确。
- C3：干跑、日志、预检和覆盖保护保持正确。

**主功能 D：正确对照实验条件**

BDD：
- Given 两份实验记录
- When 比较结果
- Then 使用实际条件，缺少声明不能判为相同

子功能：
- D1：任务绑定及指标选择器读取新路径。
- D2：参考工具保留非默认参数。
- D3：声明条件缺失时阻断可比结论。

**辅助 E：说明与索引同步。**

**辅助 F：安装和真实设备验收。**

### 接口

案例 `configuration.py`（配置模块）接收路径和覆盖，输出五段生效配置；阶段参数提取返回独立的原业务输入副本。默认展开复用组件规则，不复制算法。

`run.launch(config_loader=...)`（运行加载回调）由调用方提供解析；原外流路径解析移至 application（业务装配）兼容入口。`run.execute(settings=...)`（保存预检设置）显式接收案例业务参数，运行器只转交，不读取五段字段。

`record_config`（配置确认）仅接受相同配置的幂等确认；数据发现使用 `reports.dataset`（来源报告），检查点附带冻结的用户配置。

### 架构改动

- R1：案例持有配置展示及参数提取，隔离 YAML 结构与库接口。
- R2：run 接收通用加载回调并冻结快照，消除业务参数写回。
- R3：来源与保存预检显式交接，避免新分组导致隐式默认。
- R4：同步任务及参考消费者，缺比较条件明确失败。

### 文件改动

```text
recipes/aero_cfd/
  configuration.py                    新增：五段加载与参数提取（R1）
  config.yaml                         修改：分组与插值（R1）
  datapre.py → rawprep.py              移动：案例入口，库方法不变（R1）
  pipeline.py、trainprep.py、train.py、post.py
                                      修改：配置加载及阶段调用（R1）
  task-entry.json                     修改：输入及指标路径（R4）
  README.md                           修改：使用与快照说明
packages/ai4e-core/
  run/session.py、training.py          修改：通用加载与冻结配置（R2）
  run/dataset.py                      修改：来源报告与显式预检参数（R3）
  applications/aero_cfd/configuration.py
                                      新增：旧路径解析兼容入口（R2）
  applications/aero_cfd/train/fitting.py、pointfield_workflow.py、post/stage.py
                                      修改：移除内部配置写回（R2）
packages/ai4e-task/versions/compare.py  修改：已声明条件缺失保护（R4）
tools/verification/
  recipe_config.py                    新增：参考实验读取（R4）
  compare_datapre.py、compare_trainprep.py、compare_full_updates.py
                                      修改：新案例接入（R4）
  run_noether_reference.py、run_noether_post.py
                                      修改：实际实验参数（R4）
tests/integration/
  test_recipe_configuration.py         新增：A 与预检交接
  test_run_config_snapshot.py          新增：B 与通用加载
  test_verification_config.py          新增：D 的参考参数
  相关案例、恢复、后处理、任务测试      修改：C/D 回归
AGENTS.md、.context/                   修改：入口、职责和验收导航
.context/mvp/config-regroup-acceptance.md
                                      新增：验收记录
.context/mvp/config-regroup-results/   新增：测试、配置和运行证据
docs/PRD/recipes、ai4e-core、ai4e-task  修改：相关模块现行行为
docs/AI4E_Dojo_ARCHITECTURE (1).md     修改：唯一架构中的配置职责
```

### 实施步骤

1. 固定源码和加载位置 → 可核对本轮真实影响。
2. 完成配置模块 → A1—A3 通过。
3. 完成加载回调和快照冻结 → B1—B2 通过。
4. 清理来源写回并显式交接预检参数 → B3 与 C3 通过。
5. 完成案例改名和恢复交接 → C1—C2 通过。
6. 更新消费者 → D1—D3 通过。
7. 同步说明及索引 → E 通过。
8. 安装并执行真实案例 → F 通过后汇总结果。

### 测试用例

- A1：新旧键及混用加载 → 正确映射或明确拒绝；配置测试。
- A2：跨启动目录、覆盖和默认展开 → 路径与值正确；配置测试。
- A3：两类模型配置提取 → 保持原输入顺序和值；配置测试。
- B1：两种任意配置布局通过自定义加载函数启动 → run 无五段判断；快照测试。
- B2：业务副本变更及检查点保存 → 输入不变且检查点一致；快照测试。
- B3：发现来源和分片 → 报告完整，输入快照不改写；快照及来源测试。
- C1：独立原始处理和流水线 → 产物契约一致；数据集案例测试。
- C2：新准备、训练、续训及网格补跑 → 正确交接与覆盖保护；恢复和后处理测试。
- C3：干跑、仅测试分片参考统计、错误阶段和样本失败 → 不误用拟合统计，诊断与部分产物保留；配置、阶段、日志及框架正确性测试。
- D1：新任务模板绑定输入并提取两个指标条件 → 新路径可读取；任务案例测试。
- D2：非默认种子和预算传入参考入口 → 值一致，缺必要参数拒绝；参考配置测试。
- D3：双方缺少已声明采样条件 → 不能因空值相同判可比；任务契约测试。
- E：检查链接、命令和职责说明 → 当前文档一致，历史证据保留；文档检查。
- F：实际安装后复制正式案例 → MPS 两轮训练及同进程后处理成功；安装测试与实跑记录。

### 修改与验收

1. **上下游**：用户配置 → 案例映射 → 原业务接口 → 准备、训练、后处理 → 运行报告与对照工具。任何错误保留原失败边界，预检参数不得从用户快照猜测。
2. **带齐更新**：代码、AGENTS、模块索引、相关六节 PRD 和测试同步；不修改历史产物版本和模型计算。
3. **相关验收**：所有 Python、测试、构建及静态检查使用 uv run（项目环境入口）。先过相关用例，再安装和实跑，不以全仓测试冒充覆盖。正式复制案例使用 889 样本、默认双域预算、两轮、块长 16384，仅改路径及 MPS 设备；验证全部测试预测、默认完整表面和体积网格、快照与检查点一致，并单独补跑网格。必要失败、硬件不可用或必要跳过均不得宣布完成。结果以验收文档实际证据为准。

实际验收已完成，测试分组、正式 MPS 运行及数值比较边界见 `.context/mvp/config-regroup-acceptance.md`。
