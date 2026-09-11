# ai4e-contrib 模块索引

- [Ability 五类简表](../../docs/abilities-summary.md)：简表中的模型构建及专用数据准备/推理包含已有贡献模型路线，不表示任意模型配置均受支持。

- [Ability 源码盘点表](../../docs/abilities-inventory.md)：贡献模型与 core 通用能力分列，包含完整网络、专用准备、推理及内部组件。
- [合并后的 Ability 清单](../../docs/abilities-merged.md)：v2 明确列出位置编码、池化、条件调制、域/物理切片注意力及输出映射等模型内计算单元，区别于薄包装；保留专用准备/推理与源码对照。

已实现可安装、可 import 的共享数据集适配；不实现平台上传。仅使用 core/spec 的公开接口。

- `packages/ai4e-contrib/pyproject.toml`：workspace 包和资源打包。
- `packages/ai4e-contrib/application/datasets/shapenet_car/adapter.py`：按 manifest 选择样本与分片，不加载网格。
- `packages/ai4e-contrib/application/datasets/shapenet_car/manifest.yaml`：数据结构、字段分量/归属、未知单位、输出契约。
- 同目录 `partition.yaml`：官方 train/test 稳定样本名单；`statistics.yaml`：显式选择的参考统计。
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
- `ability/model/{abupt,transolver3}/component.py`：组件出口。
- `ability/model/transolver3/`：独立训练网络、缓存解码、适配与来源摘要。

验收状态与相关测试见 `.context/mvp/transolver3-acceptance.md`，正式规模数值对标已通过，旧公开配置兼容政策仍待确认。

NASA 的 `SOURCE_PATH_FIELDS` 声明来源路径，复制 recipe 按配置目录解析；contrib transolver3 extra 依赖 core 的 hdf5 extra，HDF5 导出依赖由 core 唯一清单管理。

## 物理数据跨模型实验

datasets/{nasa_crm,shapenet_car}/physical.py：物理字段与原拓扑适配；ability/model/{abupt,transolver3}/preparation.py：模型专用输入及完整推理。

状态与圈定测试见 `.context/mvp/cross-model-acceptance.md`。

- `application/datasets/{shapenet_car,nasa_crm}/inspection.py`：样本依赖和真实字段目录，供平台检查门面调用。
- `ability/model/{abupt,transolver3}/component.py`：公开损失与训练限制描述；平台依据真实组件约束显示优化器、采样与学习目标。
