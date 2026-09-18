# ai4e-contrib 模块索引
## 当前职责与本轮变更

ability 中的模型/方程与 application 中的数据适配、模型专属配置和局部连接。

- `packages/ai4e-contrib/application/aero_cfd/configuration.py`：官方配置分组转换和本地扩展参数连接。
- `packages/ai4e-contrib/application/aero_cfd/abupt.py`：AB-UPT 默认布局和专属参数校验。
- `packages/ai4e-contrib/application/aero_cfd/transolver3.py`：Transolver-3 专属配置连接。
- `packages/ai4e-contrib/application/aero_cfd/loader_adapter.py`：显式旧外流加载适配，不反向转导出通用 run。
- `packages/ai4e-contrib/application/parametric_pde/pibsnet.py`：PDE 准备参数连接，不约束其他组件。
- 本轮文件与回归清单：`.context/mvp/architecture-alignment-acceptance.md`。


- [Ability 五类简表](../../docs/abilities-summary.md)：简表中的模型构建及专用数据准备/推理包含已有贡献模型路线，不表示任意模型配置均受支持。

- [Ability 源码盘点表](../../docs/abilities-inventory.md)：贡献模型与 core 通用能力分列，包含完整网络、专用准备、推理及内部组件。
- [合并后的 Ability 清单](../../docs/abilities-merged.md)：v2 明确列出位置编码、池化、条件调制、域/物理切片注意力及输出映射等模型内计算单元，区别于薄包装；保留专用准备/推理与源码对照。

已实现可安装、可 import 的共享数据集适配；不实现平台上传。仅使用 core/spec 的公开接口。

- `packages/ai4e-contrib/pyproject.toml`：workspace 包和资源打包。
- `packages/ai4e-contrib/application/datasets/shapenet_car/adapter.py`：按 manifest 选择样本与分片，不加载网格。`unsplit` 把官方名单收成单一训练宇宙，供平台原始处理不按 train/test 落盘。
- `packages/ai4e-contrib/application/datasets/shapenet_car/manifest.yaml`：数据结构、字段分量/归属、未知单位、输出契约；能力与默认均打开 VTKHDF；默认写出 `formats: [pt]`。
- 同目录 `partition.yaml`：官方 train/test 稳定样本名单；`statistics.yaml`：显式选择的参考统计。
- `packages/ai4e-contrib/application/datasets/nasa_crm/manifest.yaml`：NASA 未接入 VTKHDF，默认关闭；默认写出 `formats: [pt]`。
- `docs/PRD/ai4e-contrib/application/PRD.md`：适配器复用、复制修改和失败规则；SafeDiffCon 的参考数据准入与正式适配交付边界。现已新增控制算法与案例，验收范围见专项记录。
- `tests/integration/test_dataset_recipe.py`：安装、复制与自定义 manifest 交接。

## 本次实施定位（2026-09-08）

- `ability/model/abupt/`：network.py 与 modules 保留完整网络，model.py 为构造/输出入口；sampling.py 与 batch.py 声明模型布局。超节点半径检索在 MPS 上先回 CPU 再搬回边索引；复数旋转保持 MPS，已验前后向。scatter_reduce 的 MPS 非确定性仍限制严格复现。
- `ability/model/abupt/README.md、LICENSE、source.json`：来源、许可和源码摘要。Notice 在包根统一打包。
- `pyproject.toml`：abupt 可选依赖；使用已验证镜像，uv.lock 已锁定可选依赖；PyG 固定 2.6.1，图扩展复用当前 Torch 构建。
- `docs/PRD/ai4e-contrib/ability/PRD.md`：贡献模型说明。

## 多域模型变更

`ability/model/abupt/domains.py`：有序域、字段、特征和条件布局。`network.py` 与 `modules/blocks/domain.py`：唯一多域网络、条件调制与逐层 K/V；无条件路径经模块 `forward` 进入 `forward_domains`，供结构跟踪收成模块盒。`inference.py`：缓存验证、上下文释放与查询分块。`sampling.py`/`batch.py`：按声明绑定和嵌套收批。

验收导航：`.context/mvp/abupt-multidomain-acceptance.md`。

network 输入错误保留 ValueError 并拆分实际/期望约束；sampling 元信息提供分片下标。相关测试见 test_framework_correctness.py。

## 双模型组件入口

- `application/aero_cfd/`：全限定组件加载及缺省汽车组件选择；不代表兼容旧公开配置树。`loader_adapter.py` 是显式旧外流加载适配；通用运行器不解释业务键。`operations.py` 的 inspect 对现行公共键做输入绑定；历史旧键仍走原检查门面，不改写任务 YAML。
- `application/datasets/nasa_crm/`：HDF5/NPY 视图、字段声明、拓扑适配。
- `ability/model/{abupt,transolver3}/component.py`：组件出口；AB-UPT 声明可配置点/锚点/查询采样，Transolver-3 声明抽稀步长只读的采样与固定 MSE。
- `ability/model/transolver3/`：独立训练网络、缓存解码、适配与来源摘要。

历史数值对标及其范围见 `.context/mvp/transolver3-acceptance.md`；当前公开入口和兼容边界见 `.context/mvp/architecture-alignment-acceptance.md`，不迁移历史任务。

NASA 的 `SOURCE_PATH_FIELDS` 声明来源路径，复制 recipe 按配置目录解析；contrib transolver3 extra 依赖 core 的 hdf5 extra，HDF5 导出依赖由 core 唯一清单管理。

## 物理数据跨模型实验

datasets/{nasa_crm,shapenet_car}/physical.py：物理字段与原拓扑适配；ability/model/{abupt,transolver3}/preparation.py：模型专用输入及完整推理。

状态与圈定测试见 `.context/mvp/cross-model-acceptance.md`。

- `application/datasets/{shapenet_car,nasa_crm}/inspection.py`：样本依赖和真实字段目录，供平台检查门面调用。
- `ability/model/{abupt,transolver3}/component.py`：公开损失与训练限制描述；平台依据真实组件约束显示优化器、采样与学习目标。

## 显式 Recipe 组件适配

`application/aero_cfd/__init__.py` 的配置默认解析只选择数据/模型，旧 load/workflow 调用兼容保留；新模板和五例直接使用公开业务步骤。用户字段与采样例在 `examples/recipe_extensions/`，入口及验收见 recipes 模块索引和 `.context/mvp/recipe-explicit-acceptance.md`。


## PI-BSNet 与物理数据

- `packages/ai4e-contrib/ability/model/pibsnet/`：model 网络、spline 物理样条、component 准备/求值/训练步、README 来源与修正。
- `packages/ai4e-contrib/ability/constraint/equations/`：普通张量方程函数，包括二维 NS。
- `packages/ai4e-contrib/application/datasets/parametric.py`：独立生成清单、身份校验及读取器。
- `packages/ai4e-contrib/application/datasets/{convection_diffusion,neumann_diffusion,advection,burgers,diffusion_trapezoid}/generate.py`：五例各自生产算法和入口。
- `docs/PRD/ai4e-contrib/ability/PRD.md`、`docs/PRD/ai4e-contrib/application/PRD.md`：长期功能正文。
- `.context/mvp/pibsnet-acceptance.md`：实际证据和未验收边界。

- `tools/verification/pibsnet/reference_advection.py`：摘要锁定原 Advection 训练循环，同数据独立参考；`test_pibsnet_reference_protocol.py` 验证执行与配点协议。

## 声明驱动原始处理

数据集 shapenet_car/nasa_crm 的 descriptor.py 提供 describe_rawprep；manifest.yaml 提供默认值、绑定槽位、本机识别规则（目录标记或三文件名）、输出及能力依赖，inspection.py 返回样本范围、检查覆盖与缺项。平台 `sample_scope` 检查用官方/自身分片作输入宇宙，回传 `sample_universe`。

圈定验收入口：`.context/mvp/manifest-rawprep-acceptance.md`。

## 原案例迁移

source_cases.py装配原Neumann/Advection；neumann_numerics.py/advection_numerics.py保留各案例不同数值定义；对应generate.py生产原FP32/连续流数据。

## 独立推理参数

- `ability/model/abupt/preparation.py`：原生 infer 的查询参数交接；旧 post 路线独立保留。Transolver 专用状态汇总不改。
- 长期正文 `docs/PRD/ai4e-contrib/ability/PRD.md`；数值验收 `tests/integration/test_infer_stage.py`。

## 推理工作台选择与统计

`ability/model/transolver3/{inference,preparation,component}.py`：缓存后解码查询块；`application/datasets/{shapenet_car,nasa_crm}/{physical,__init__}.py`：字段、分量、单位描述。

专项状态与证据见 `.context/mvp/inference-ui-acceptance.md`，不沿用旧验收结论。

共享数据兼容：`application/aero_cfd/loader_adapter.py` 隔离旧加载器不认识的并行与多格式键，仅本次托管运行生效，冻结脚本不改写；验收见 Task 共享专项。

## GenCP

`ability/model/gencp/`：cno、sit_fno、adapters、原模型 modules、source.json 与许可证。`ability/transform/gencp/`：normalization/preprocessing/state/conditions/boundaries；`constraint/gencp/objective.py`、`inference/gencp/velocity.py`、`postproc/gencp/reference.py` 各司数值职责。`application/datasets/gencp/` 为 fsi/ntcouple 读取描述及 manifests；`application/coupled_physics/gencp/` 为 configuration、cases、validation。模块长期说明归现有 ability/application PRD，实际验收见 [GenCP](../mvp/gencp-acceptance.md)。

## SafeDiffCon 限时集成

- `ability/model/safediffcon/`：两种原UNet与构造器，LICENSE/source.json覆盖迁入数值定义。
- `ability/{constraint,inference,training,transform,eval,postproc}/safediffcon/`：原扩散/残差、校准与重权、EMA、原生缩放、物理指标和Burgers/KSTAR响应；KSTAR在隔离解释器运行。
- `application/datasets/safediffcon/arrays.py`：HDF5/Arrow和ZIP原数据读取。
- `application/pde_control/safediffcon/{configuration,migration,handoff,stream,training,inference,solver}.py`：公共/内部配置边界、只生成新配置的迁移、数组/指标与阶段权重登记、尾批游标、训练与推理局部连接。求解器解释器保留虚拟环境路径。
- `configuration.py` 的预训练总更新目标默认4000、短实验上限20000；恢复历史包含在总数内。墙钟预算由工具层持久账本负责，旧准备和配置继续兼容。
- `docs/PRD/ai4e-contrib/{ability,application}/PRD.md`第三章：算法与案例功能；当前范围见`.context/mvp/safediffcon-acceptance.md`。

WDNO 的原版历史切片与当前缩小范围迁移分开记录；可安装基础能力和连接见下方，执行与数值验收见 `.context/mvp/wdno-acceptance.md`。

## WDNO 基础预测与共享EMA

- `ability/model/wdno/{unet,schedules}.py`：作者二维网络、辅助算子与噪声日程；`source.json` 为抽取位置及完整摘要。
- `ability/constraint/wdno/objective.py`：原条件噪声目标；`ability/inference/wdno/{diffusion,predict}.py`：原扩散采样与物理预测函数。
- `ability/transform/wdno/{layout,multiscale,preparation,burgers}.py`：原系数布局、保留的辅助定义、模型准备及基础物理正逆变换；多尺度分支保留源码不等于超分闭环已支持。
- `ability/eval/wdno/{metrics,physical}.py`：原MSE及固定场评价绑定。
- `ability/training/moving_average.py`：WDNO/SafeDiffCon共享原EMA适配，旧SafeDiffCon路径保留门面。
- `application/spatiotemporal_pde/wdno/{data,configuration,model,training,inference,stream,provenance}.py`：原始Torch来源、严格配置与路径、网络/条件连接、优化/恢复、独立采样、可恢复原随机批次顺序、实际组件身份及研究目录源码归档。
- 功能正文：贡献ability第四章、application第四章；依赖`wdno` extra；不注册平台。
- 验收：`test_wdno_migration.py`、`test_wdno_recipe.py`、真实对照工具 `tools/verification/wdno/migration.py`。

- `tests/integration/test_wdno_migration_acceptance.py`：显式真实两侧2000步、64/128预测和独立安装产物门槛；无真实产物不能记通过。

WDNO公共约定调整：`application/spatiotemporal_pde/wdno/handoff.py`连接分片输入冲突、资产依赖及MSE语义；`migration.py`仅显式转换旧用户配置副本。configuration读取公共inputs/data_root，训练和推理不读旧用户路径键。数值与冻结合同不变；验收test_wdno_task.py及专项记录。

公共研究配置：`application/aero_cfd/inputs.py` 只在领域边界展开输入路径；`operations.py` 的检查与推理检查共用该连接，管理层不解释模型配置。GenCP训练片段参数校验、条件扩展及直接/Task证据见Recipe/Task专项。

## WDNO最新公共约定补验（2026-09-17）

WDNO handoff.py共用数组依赖解析；指标绑定清单与全部数组，资产保留bundle_root；test_wdno_public_metrics覆盖篡改、缺失、越界和科学口径。无需修改公共索引格式。 当前结果以 `.context/mvp/wdno-acceptance.md` 为准。

## WDNO 局部训练策略

`application/spatiotemporal_pde/wdno/{training,configuration}.py` 接收可选优化器/调度器/更新函数并记录来源；未选择保持原合同。`inference.py` 对固定权重忽略新增训练策略身份，原模型/数据/目标身份仍严格检查，完整续训不忽略策略。示例与验收从 [研究任务导航](../tasks/research.md) 进入。
