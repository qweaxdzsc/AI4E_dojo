> 2026-09-21 用户纠正与实施续接：N-001 是可选注意力能力候选，不是全局架构建议。本轮架构建议应计为 0。后续已按用户授权接入独立 core 组件，最新状态见 [组件验收](../../../../.context/mvp/flare-attention-acceptance.md)。以下保留首次只读调研正文，文中的“本轮未执行”只指当时调研，不代表后续实施状态。

# Dojo 每周训练框架借鉴：2026-09-21

本轮首次基线；核心建议 **1 项，待决定是否做局部实验**。没有安装、导入或执行第三方代码，没有训练或性能实测，没有修改 Dojo 框架、环境、正式服务、既有基线或历史证据。下文测试结论均指读到的断言，不代表本轮测试通过。

## 时间与工作区身份

- 窗口：北京时间 2026-09-14 05:00（含）至 2026-09-21 05:00（不含），对应 UTC 2026-09-13 21:00 至 2026-09-20 21:00。
- 检索/整理时间：2026-09-21T05:06:31.783220+08:00；各官方索引另存 retrieved_at。
- Git HEAD：`477c47bc4cba83fd1e903800034d7d58286ee6d8`。
- 跟踪及未忽略文件内容身份（排除本报告目录）：`636068ecc656d826f80c5e7c4bbb0636fded284354d3a54a9dc595c8035d10a9`，逐文件 SHA-256、porcelain 状态、采集时间见 [identity](2026-09-21-identity.json)。这是工作树身份，不能只用 HEAD 重建。
- 本自动化上次运行：无；不存在可以比较的历史周报。既有未提交内容不归因于本轮。已对照 `docs/reviews/archreview/2026-09-21.md` 的既有建议，未重复 Task/provider 资产边界或模型结构跟踪迁移建议。
- 写入范围：本 trend 目录与自动化 memory。按此次只调研授权，不改全仓索引、PRD 或测试；本报告不定义现行产品行为。

## 检索范围与新旧区分

读取官方 GitHub Releases 与默认分支窗口内 commits，覆盖 PhysicsNeMo、NeuralOperator、Lightning、Accelerate、Torchtune、PaddleScience、DeepXDE、Anemoi-core。窗口内分别为 9、0、5、2、0、0、0、15 条提交，均未达到每页 100 条上限；读取最近 10 个 release，其中这八个项目均未见窗口内发布。只代表这些官方源和默认分支，不能表述为全网无其他新闻。

PhysicsNeMo v2.2.2（9 月 11 日）、Lightning 2.6.6（9 月 10 日）、Accelerate v1.15.0（9 月 9 日）、Anemoi training-0.17.0（9 月 7 日）在窗口外，不伪装成本周新发布。PhysicsNeMo 本周合入的 FLARE++ 仍按开发分支 commit 审阅，不声称已进入 v2.2.2。

检索地址与完整返回见 evidence 中各 `组织--仓库.json`，[候选去重记录](candidates.json)保留 repo+commit 身份、窗口条目与评审状态。`pytorch/torchdata` API 返回 404，覆盖未知，不计入无更新项目；初查 `deepmodeling/deepxde` 404 后改查官方 `lululxvi/deepxde` 成功。旧 `ecmwf/anemoi-training` 的陈旧发布未作当前 Anemoi 证据，当前检索使用 anemoi-core。Experience 搜索为空，没有引用或归档 Experience 资产。

## N-001：复用 FLARE++ 动态路由，隔离模型上下文连接

**状态：有条件实验提案，不是集成承诺。** 价值是网络变体研究的局部复用；没有证据证明它提高 Dojo 精度、训练速度或降低总成本。若近期没有独立注意力/GeoTransolver 变体需求，可继续搁置。

### 发布身份与机制证据

[官方 PR #1940](https://github.com/NVIDIA/physicsnemo/pull/1940) 创建于 2026-08-19T23:52:36Z，合入于 **2026-09-18T19:22:10Z**（北京时间 9 月 19 日 03:22）；本周事件是合入，不是首次公开论文或 PR。锁定 commit `94dbdf829d1a4e93e3f31ecb77713392c471388e`。官方 [更新说明](https://github.com/NVIDIA/physicsnemo/blob/94dbdf829d1a4e93e3f31ecb77713392c471388e/CHANGELOG.md)及[模型文档](https://github.com/NVIDIA/physicsnemo/blob/94dbdf829d1a4e93e3f31ecb77713392c471388e/docs/api/models/geotransolver.rst)将独立 FLARE++ 与 `GALE_FPP` 分开。

[实际实现](https://github.com/NVIDIA/physicsnemo/blob/94dbdf829d1a4e93e3f31ecb77713392c471388e/physicsnemo/nn/module/flare_attention.py#L259)对输入做一次融合线性投影，分出 query K/V 与 physical K/V：学习 seed 先对输入合成 queries，queries 再 gather physical values，最后以 physical keys 作 query 将 latent values scatter 回 token。固定路由数时三次注意力的 token 维代价随 N 线性增长；这只是计算结构，不能推出实测更快。不同样本合成不同路由，而不是简单换已有 GALE 的激活函数或优化器。

[几何适配实现](https://github.com/NVIDIA/physicsnemo/blob/94dbdf829d1a4e93e3f31ecb77713392c471388e/physicsnemo/models/geotransolver/flare_plus_plus.py)仅另加 context K/V、交叉注意力与 weighted/concat_project 混合。上游以私有方法复用 mixer；Dojo 不应跨层照抄这种私有调用，需在局部组件组合中明确张量交接或把中立计算拆为普通函数，无须全仓协议。

### 已读测试及其限度

[注意力测试](https://github.com/NVIDIA/physicsnemo/blob/94dbdf829d1a4e93e3f31ecb77713392c471388e/test/nn/module/test_flare_attention.py)包含三次 SDPA 公式对照、输入条件路由、input/seed/projection 梯度有限、eval 不推进 RNG、参数拒绝及 fullgraph 编译对照。CPU 编译用 aot_eager，CUDA 用 inductor；不能据此推断 MPS 编译支持。

[GeoTransolver 适配测试](https://github.com/NVIDIA/physicsnemo/blob/94dbdf829d1a4e93e3f31ecb77713392c471388e/test/models/geotransolver/test_flare_plus_plus.py)包含无上下文时与 standalone 权重/输出对照、两类 context 混合、不同长度多流梯度、构造拒绝、固定输出等。[独立模型测试](https://github.com/NVIDIA/physicsnemo/blob/94dbdf829d1a4e93e3f31ecb77713392c471388e/test/models/flare/test_flare.py)另覆盖独立模型行为。固定输出辅助函数在参考缺失时会生成参考后报错；正式参考比较不能把这种生成行为当作通过或用来更新 Dojo 固定基线。本轮没有运行任何这些测试，也没有加载参考权重。

### Dojo 现状、缺口与最小接入点

已核对当前工作树：

- `packages/ai4e-core/abilities/modeling/modules/geometry_attention.py` 的 `_gale_forward_impl` 已负责 slice self-attention、context cross-attention 和混合，计算已可复用；`tests/integration/test_geotransolver_core.py::test_attention_without_contrib` 写有独立调用与梯度断言。
- `packages/ai4e-contrib/ability/model/geotransolver/network.py:350-353` 明确拒绝 activation checkpointing 与非 GALE attention；签名/长 docstring 出现 GALE_FA 不等于本地实现支持。当前没有 FLARE++ 的输入合成路由。
- `packages/ai4e-core/abilities/training/execution.py`、`iterations.py` 和 `tests/integration/test_training_strategy_extensions.py` 已有真实更新计数、局部策略/复制入口/恢复和固定产物读回设计，不能再建议“新增共享训练框架”。

现有 GALE 足以运行现有案例，却不能仅靠配置获得 FLARE++ 的四路投影及三次 SDPA 运算；因此缺的是一种可选计算组件，不是 Trainer、Task、YAML 工作流或全局注册系统。

如用户选择验证：先做独立 mixer 的上游公式/梯度对照；只有过关再考虑将中立数学放入 core modeling modules，GeoTransolver 构造与 context 连接留在 contrib，Python recipe 显式选局部变体。保留默认 GALE 和旧 checkpoint，不修改 Task、Web 或历史产物。初始验证仅普通 tensor、无 TE、无 token 分片。不要把 upstream 全套 Mesh/Hydra/Trainer 引入 Dojo。

**减少的重复劳动：** 独立点场网络和 GeoTransolver 上下文变体共用投影、路由、参数校验及数值测试；Agent 只需选择 mixer 与局部连接，不为两个模型分别复制训练循环、路由算法和保存恢复逻辑。这是结构性预期，尚未量化工时节省。

### 许可、维护与验证退出条件

源码文件 SPDX 与[上游 LICENSE.txt](https://github.com/NVIDIA/physicsnemo/blob/94dbdf829d1a4e93e3f31ecb77713392c471388e/LICENSE.txt)为 Apache-2.0；若实际迁移需保留版权/许可及修改说明，另核目标文件和依赖许可证。这不代表数据、论文图或权重获同样许可。代码明确拒绝 Transformer Engine 和 token-sharded 输入；不能沿用 GeoTransolver 其他后端的分布式支持声明。

建议的小范围验证（本轮均未执行）：

1. 锁定此 commit，普通 CPU 小张量检验三次 SDPA 的前向、输入/参数梯度、不同 N、无上下文对齐、有上下文两种混合与无效参数；先独立上游验证，再谈迁移。
2. 仓库外复制一个已有小案例，以相同 split、seed、预算比较原 GALE 与局部变体；保持原数据/物理字段含义。记录误差、峰值内存、完整训练和推理耗时，不只看单次 forward。
3. 如进入接入验收，再完成直接 core/Task、恢复、固定结果消费、真实安装复制及固定用户源码基线。只测组件不能算接入完成；论文复现另行立项。

退出条件：公式或梯度不一致即停；需改全仓协议、私有跨层访问或升级主环境才能跑则暂停；在预先固定容差与预算下无足够收益，或重复维护成本超过复用价值，则不纳入默认能力。不设未经测量的性能百分比承诺。

## 其余候选为何不形成建议

### C-002：外流坐标重复无量纲化修复

[官方 PR #1995](https://github.com/NVIDIA/physicsnemo/pull/1995)，创建 2026-09-15T22:19:01Z，合入 2026-09-17T14:06:52Z，commit `7bd00184c2f13510d68b4e10ff262828714c10e7`。[实现](https://github.com/NVIDIA/physicsnemo/blob/7bd00184c2f13510d68b4e10ff262828714c10e7/examples/cfd/external_aerodynamics/unified_external_aero_recipe/src/nondim.py)新增 `scale_geometry`，第二个 point/cell 字段变换实例关闭坐标缩放，避免重复除 L_ref。[测试](https://github.com/NVIDIA/physicsnemo/blob/7bd00184c2f13510d68b4e10ff262828714c10e7/examples/cfd/external_aerodynamics/unified_external_aero_recipe/tests/test_nondim.py)使用 L_ref=0.4，断言第二实例只缩放字段、正反链恢复。

这是配置链的显式控制，不是自动幂等算法。Dojo `abilities/transform/scale.py` 是给定张量的正反倍率，当前所读路径没有上游这种 Mesh 链；没有证据证明 Dojo 存在同一 bug，因此只记观察，不据外部缺陷修改本地。若后续出现共享几何的多字段无量纲化链，再按此触发复查。

### C-003：Anemoi 编译与 activation checkpointing

[官方 PR #1344](https://github.com/ecmwf/anemoi-core/pull/1344)，创建 2026-08-26T14:04:07Z，合入 2026-09-15T11:55:25Z，commit `10f8c259d417909ad78ae891509cbfb8e3bcf5fc`。[实现](https://github.com/ecmwf/anemoi-core/blob/10f8c259d417909ad78ae891509cbfb8e3bcf5fc/training/src/anemoi/training/utils/compile.py)设置线程数、在 checkpointing 时关闭 shape_padding，并按 PyTorch 版本调用私有 LRU 开关。[集成夹具](https://github.com/ecmwf/anemoi-core/blob/10f8c259d417909ad78ae891509cbfb8e3bcf5fc/training/tests/integration/conftest.py#L769)仍写 `cfg.model.compile = []` 且 TODO 调试 compile+checkpoint，不能把该修复视为组合已完整验收。

当前 Dojo GeoTransolver 构造拒绝 checkpointing，搜索 core/contrib 未发现实际 `torch.compile(...)` 接入；Transolver-3 已有非重入 checkpoint 调用，但不等于使用相同编译组合。该候选不形成可复用训练策略建议，不引入私有 PyTorch 开关或硬编码线程数。

## 本轮交付与后续比较

[候选账本](candidates.json)记录所有窗口内提交的筛选状态；[建议账本](recommendations.json)仅 N-001 一项。下次以 repo+commit 去重，建议以机制 identity 去重；只有状态变化、有效新证据或用户选择实验时再通知。首次运行无历史收益趋势可报告。

源码和测试均为静态阅读；没有 Dojo 性能、学习效果、论文精度或 Web 验收结论。需要用户关注的唯一事项：是否将 N-001 列入下一次网络变体小实验；当前没有必须处理的框架故障。
