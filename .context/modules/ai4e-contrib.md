梯形所选实验：`ability/model/pibsnet/trapezoid.py` 负责完整输出/初边界覆盖/原数值训练步；`trapezoid_basis.py` 保留参数空间递推，非通用物理导数。`application/datasets/diffusion_trapezoid/generate.py` 为带协议标签的Euler独立生成。圈定 `tests/integration/test_pibsnet_trapezoid_alignment.py`，长期正文见本模块已有PRD。

# ai4e-contrib 模块索引

- [Ability 五类简表](../../docs/abilities-summary.md)：简表中的模型构建及专用数据准备/推理包含已有贡献模型路线，不表示任意模型配置均受支持。

- [Ability 源码盘点表](../../docs/abilities-inventory.md)：贡献模型与 core 通用能力分列，包含完整网络、专用准备、推理及内部组件。
- [合并后的 Ability 清单](../../docs/abilities-merged.md)：v2 明确列出位置编码、池化、条件调制、域/物理切片注意力及输出映射等模型内计算单元，区别于薄包装；保留专用准备/推理与源码对照。

已实现可安装、可 import 的共享数据集适配；不实现平台上传。仅使用 core/spec 的公开接口。

- `packages/ai4e-contrib/pyproject.toml`：workspace 包和资源打包。
- `packages/ai4e-contrib/application/datasets/shapenet_car/adapter.py`：按 manifest 选择样本与分片，不加载网格。
- `packages/ai4e-contrib/application/datasets/shapenet_car/manifest.yaml`：数据结构、字段分量/归属、未知单位、输出契约；能力与默认均打开 VTKHDF。
- 同目录 `partition.yaml`：官方 train/test 稳定样本名单；`statistics.yaml`：显式选择的参考统计。
- `packages/ai4e-contrib/application/datasets/nasa_crm/manifest.yaml`：NASA 未接入 VTKHDF，默认关闭。
- `docs/PRD/ai4e-contrib/application/PRD.md`：适配器复用、复制修改和失败规则。
- `tests/integration/test_dataset_recipe.py`：安装、复制与自定义 manifest 交接。

## 本次实施定位（2026-09-08）

- `ability/model/abupt/`：network.py 与 modules 保留完整网络，model.py 为构造/输出入口；sampling.py 与 batch.py 声明模型布局。超节点半径检索在 MPS 上先回 CPU 再搬回边索引；复数旋转保持 MPS，已验前后向。scatter_reduce 的 MPS 非确定性仍限制严格复现。
- `ability/model/abupt/README.md、LICENSE、source.json`：来源、许可和源码摘要。Notice 在包根统一打包。
- `pyproject.toml`：abupt 可选依赖；使用已验证镜像，uv.lock 已锁定可选依赖；PyG 固定 2.6.1，图扩展复用当前 Torch 构建。
- `docs/PRD/ai4e-contrib/ability/PRD.md`：贡献模型说明。

## 多域模型变更

`ability/model/abupt/domains.py`：有序域、字段、特征和条件布局。`network.py` 与 `modules/blocks/domain.py`：唯一多域网络、条件调制与逐层 K/V；旧双域 attention 模块已移除。`inference.py`：缓存验证、上下文释放与查询分块。`sampling.py`/`batch.py`：按声明绑定和嵌套收批。

验收导航：`.context/mvp/abupt-multidomain-acceptance.md`。

network 输入错误保留 ValueError 并拆分实际/期望约束；sampling 元信息提供分片下标。相关测试见 test_framework_correctness.py。

## 双模型组件入口

- `application/aero_cfd/`：全限定组件加载及缺省汽车组件选择；不代表兼容旧公开配置树。
- `application/datasets/nasa_crm/`：HDF5/NPY 视图、字段声明、拓扑适配。
- `ability/model/{abupt,transolver3}/component.py`：组件出口；AB-UPT 声明可配置点/锚点/查询采样，Transolver-3 声明抽稀步长只读的采样与固定 MSE。
- `ability/model/transolver3/`：独立训练网络、缓存解码、适配与来源摘要。

验收状态与相关测试见 `.context/mvp/transolver3-acceptance.md`，正式规模数值对标已通过，旧公开配置兼容政策仍待确认。

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

数据集 shapenet_car/nasa_crm 的 descriptor.py 提供 describe_rawprep；manifest.yaml 提供默认值、绑定槽位、本机识别规则（目录标记或三文件名）、输出及能力依赖，inspection.py 返回样本范围、检查覆盖与缺项。

圈定验收入口：`.context/mvp/manifest-rawprep-acceptance.md`。

## 原案例迁移

source_cases.py装配原Neumann/Advection；neumann_numerics.py/advection_numerics.py保留各案例不同数值定义；对应generate.py生产原FP32/连续流数据。

## 独立推理参数

- `ability/model/abupt/preparation.py`：原生 infer 的查询参数交接；旧 post 路线独立保留。Transolver 专用状态汇总不改。
- 长期正文 `docs/PRD/ai4e-contrib/ability/PRD.md`；数值验收 `tests/integration/test_infer_stage.py`。

## 推理工作台选择与统计

`ability/model/transolver3/{inference,preparation,component}.py`：缓存后解码查询块；`application/datasets/{shapenet_car,nasa_crm}/{physical,__init__}.py`：字段、分量、单位描述。

专项状态与证据见 `.context/mvp/inference-ui-acceptance.md`，不沿用旧验收结论。
