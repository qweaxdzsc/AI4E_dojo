# 平台配置合成与完整保存验收

日期：2026-09-16。当前切片已完成圈定验收：平台相关回归79 passed；原默认跳过的2项真实换模已显式补跑通过；最终编辑/兼容22项、真实五例及安装等结果如下。正式8000/5173未重启、未占用、未重装。

## 当前实现与边界

- Server stages/configuration.py 是平台编辑语义唯一新增实现；前端公共差异工具提交字符串数组路径，空值、删除与未编辑分别表达。路径重叠及越界拒绝，保存不产生参数合并确认。
- Task replace_configuration 完整保存，复用锁、修订、文件提交和共享资产维护；save_configuration 旧补丁语义保持。算法application、contrib和通用run没有因本次合并新增规则。
- 原始处理清理格式旧键及几何/字段依赖，数据准备删除字段不恢复、切换方法清理旧专属参数，模型采样迁移保留未编辑预算，换模沿用已有重置范围。
- 统一空间开启时现有共享坐标变换固定，方法只读；关闭后可改方法。不增加组合归一化算法。逐轮调度仅展示有效比例参数与固定调度说明，不更改调度算法。
- 真实实跑证明五个example的rawprep.py漏传formats，遂最小补齐五处参数透传；主recipe已支持，不修改历史冻结任务脚本。
- 旧接口请求仍适配；历史任意自定义脚本不因平台改造自动获得新算法能力。配置覆盖不授权物理数据覆盖，历史准备和检查点仍按原科学契约核验。

## 功能—文件—测试

- A1/A2：Server stages/configuration.py；test_web_configuration_composition.py 覆盖空值、列表、删除、字面点号键、旧别名、归一化、几何依赖及旧采样预算保留。
- A3：Task tasks/configuration.py；test_task_configuration.py 完整保存、旧修订拒绝、旧补丁兼容、版本身份。
- B1/B2/B3/B4：Web rawprep/trainprep/models/training/stages；configuration-composition、stage-consistency、model-picker、rawprep-consistency 浏览器用例；平台HTTP与旧recipe兼容回归。
- C1/C2：test_web_configuration_handoff.py 的HTTP保存、越界拒绝、真实Task运行、提交后编辑隔离及writer快照；既有test_task_execution.py。
- C3：test_recipe_explicit_equivalence.py 五案例固定源码、逐值权重/预测和恢复；test_task_installation.py 实际wheel与仓库外用户字段扩展；test_recipe_extensions.py 用户能力、参数、输出和下游消费。
- 真实CFD：test_web_configuration_handoff.py::test_real_five_case_configuration_consumption，以DOJO_CONFIGURATION_REAL=1显式启用。
- D：Task/Web文档检查、前端微领域门面检查、生成传输类型及目标Python静态检查。

## 已完成证据

- 最终补充边界与HTTP交接：22 passed（未编辑研究统计参数保留、旧请求新自定义变换参数保留），真实五例另跑，不把deselected计入通过。[日志](platform-configuration-results/final-edits-and-legacy.log)
- 原默认跳过的两个真实模型切换：DOJO_MODEL_PICKER_REAL=1 显式运行，2 passed；真实原始处理、旧准备拒绝、新准备消费及旧产物字节保持。[日志](platform-configuration-results/real-model-switch.log)。证据目录 `/Users/zonghui/work/project_simulation/dojo_train/platform-configuration-switch-evidence`。

- 平台最终相关回归：79 passed、2 skipped（同两项已在上述独立组显式通过）、1 deselected（真实五例另跑），无失败。[日志](platform-configuration-results/platform-regression.log)
- 新增完整保存API在实际wheel中执行赋值及删除后读回通过：1 passed。[日志](platform-configuration-results/wheel-complete-save.log)
- 配置与文档专项30 passed；物理数据、准备和训练参数契约6 passed。[文档日志](platform-configuration-results/documents.log)、[契约日志](platform-configuration-results/downstream-contracts.log)

- 五例真实CFD：1个参数循环用例通过，实际覆盖ShapeNet AB-UPT、NASA Transolver-3、NASA AB-UPT、ShapeNet Transolver-3表面与体场。平台合成与直接配置逐值一致；每例原始处理同时保存PT/Zarr，全部样本字段读回逐值一致；准备物化、CPU单轮训练、完整预测和post执行成功。
- 真实规模：ShapeNet每例1个训练样本、1个测试样本；NASA每例5个训练样本、1个验证样本、1个测试样本，模型宽度与采样预算缩小。单NASA训练样本会使工况标准差为零，最终使用分散的5个训练样本，不改归一化算法。仅证明交接，不代表生产精度。
- 真实产物：`/Users/zonghui/work/project_simulation/dojo_train/platform-configuration-20260916-real6/test_real_five_case_configurat0`；[五例检查点和预测路径](platform-configuration-results/real-evidence.json)。
- 浏览器：23 passed，使用既有5172测试入口和显式HTTP夹具；不把夹具浏览器结果称为真实生产服务验收。[日志](platform-configuration-results/browser.log)
- 固定源码五例等价、真实wheel安装和旧recipe兼容：11 passed。[日志](platform-configuration-results/installation-and-frozen-baseline.log)
- 用户扩展及配置/旧请求针对性回归：29 passed。[日志](platform-configuration-results/extensions.log)
- 前端构建、微领域公开门面检查通过；构建保留既有大包提示。[构建日志](platform-configuration-results/build.log)
- 各组有重叠，不累加为唯一测试总数；早期失败已修复的浏览器测试不计入最终失败。

## 运行方式

本仓库单层包的已安装副本与工作区可能不同。为避免重装干扰正式进程，本轮建立 `/tmp/dojo-config-source/ai4e_{spec,core,contrib,task,server,viz}` 符号链接指向当前 packages，令独立测试及其子进程通过 `PYTHONPATH=/tmp/dojo-config-source` 读取当前源码。wheel用例清除该变量并在独立环境安装实际构建包。

```bash
PYTHONPATH=/tmp/dojo-config-source uv run --no-sync pytest tests/integration/test_web_configuration_composition.py tests/integration/test_task_configuration.py tests/integration/test_web_stage_consistency.py tests/integration/test_web_rawprep.py tests/integration/test_recipe_configuration.py tests/integration/test_web_configuration_handoff.py -k 'not real_five' -q
PYTHONPATH=/tmp/dojo-config-source uv run --no-sync pytest tests/integration/test_recipe_explicit_equivalence.py tests/integration/test_task_installation.py tests/integration/test_web_recipe_compatibility.py -q
PYTHONPATH=/tmp/dojo-config-source uv run --no-sync pytest tests/integration/test_recipe_extensions.py tests/integration/test_web_design_documents.py tests/integration/test_task_documents.py -q
PYTHONPATH=/tmp/dojo-config-source DOJO_CONFIGURATION_REAL=1 uv run --no-sync pytest tests/integration/test_web_configuration_handoff.py::test_real_five_case_configuration_consumption --basetemp=/Users/zonghui/work/project_simulation/dojo_train/platform-configuration-20260916-real6 -q
```

复跑真实实验时使用新的basetemp目录，避免pytest清理已交付证据。Web目录执行 `DOJO_WEB_URL=http://127.0.0.1:5172 npm run test:e2e -- configuration-composition.spec.ts stage-consistency.spec.ts model-picker.spec.ts rawprep-consistency.spec.ts`。

## 验收中的问题与处理

- 旧阶段接口原始处理扩展被误作整段替换删除：区分旧阶段补丁与旧原始处理完整段接口，兼容回归已通过。
- 新浏览器测试挂载和控件定位错误：修复测试，最终23项通过。
- 文档已有架构标题变更，但PRD、导航与检查仍引用旧草案标题：更新导航锚点与现行架构检查，不改任何固定用户源码摘要。
- 初次源码回归发现reference统计目录断言失败；涉及已有统计落盘变更，本轮未修改该算法文件。后续读取现行源码时该统计路径已有独立变更，最终79项源码回归已通过；本轮不修改统计算法，也不拿旧安装包的通过代替源码验证。

## 公开接口变化

- `ai4e_task.replace_configuration(project, task_id, config, *, revision)`：接收完整映射，返回`revision/config`；根节点非映射抛TypeError，旧修订/归档/失效共享资产沿用ValueError。不新增版本，不迁移业务键。
- 阶段与原始处理保存请求新增可选`edited_paths/removed_paths`，形状为字符串数组的数组。路径相对所属阶段，字段中的点是普通字符。旧请求省略两项保持原接口语义。
- `stages.compose_configuration`公开给服务内其他模块复用，纯合成无写盘；越界、重叠、缺失赋值拒绝。普通Task补丁保存、recipe加载和执行签名不变。
- 新增目录及文件职责已写入模块索引；没有创建新的算法配置协议或组件注册表。

## 真实换模旧测试适配

旧测试按任务data拼接物理清单，并把缺字段负例写入共享内容目录，分别造成404和共享内容摘要变化。测试改用Task公开run_physical_manifest获取实际共享清单，负例写独立受控目录；没有修改共享数据算法或降低资产校验。最终两项实跑通过。

运行示例：`PYTHONPATH=/tmp/dojo-config-source DOJO_MODEL_PICKER_REAL=1 DOJO_MODEL_PICKER_EVIDENCE=/Users/zonghui/work/project_simulation/dojo_train/platform-configuration-switch-evidence uv run --no-sync pytest tests/integration/test_web_stage_consistency.py::test_model_switch_real_preparation_handoff`，实际运行另指定新的独立basetemp目录。
