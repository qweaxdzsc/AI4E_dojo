# aero_cfd 双模型实施与验收

当前状态（2026-09-10）：双案例功能已实现，Transolver 正式规模数值对标通过；旧版公开 YAML 的兼容政策仍待确认，因此不宣称用户计划 A—F 全部完成。当前案例采用仓库现行 rawprep → trainprep → train → post 入口，以及 rawprep/trainprep/model/train/post 五段配置。无 components 的汽车配置仍选择原组件，但旧顶层 sampling/normalization 与旧 datapre 阶段名被当前配置入口拒绝。历史冻结产物的语义兼容与公开 YAML 迁移是两件事。

## 正式规模结果

原始参考仓库只读。双方使用相同 MPS、fp32、Python 3.12.14、torch 2.14.0、numpy 2.5.3、h5py 3.16.0、VTK 9.7.0；参考网格包装使用 PyVista 0.49.0，Dojo 使用原生 VTK。模型为 256 宽、24 层、8 头、64 切片，激活检查点开启。数据分片种子 42，训练种子 2，84/21/44 分片，每样本 454,404 点；两轮周期为 2 的余弦调度，AdamW、标准化四通道 MSE，无 EMA。

固定容差为 rtol=1e-5 / atol=1e-6；整数、字段、样本、点序与拓扑严格一致；非有限值不能通过。下面各项均来自真实运行，所有逐元素比较的超差数量和最大绝对误差均为 0：

- `transolver3-results/full-data.json`：149 样本、12,069 个 NPY 数组。工况统计计数 84，标签统计计数 38,169,936；训练与验证及独立测试分片一致。
- `reference-repeat.json`：原参考独立完整两轮重复，模型、优化器、调度器与数值历史一致。
- `formal-training.json`、`formal-inputs.json`：Dojo 与原参考各自初始化并独立训练两轮，初始化与全部 168 个实际训练批次摘要一致，最终状态及历史一致；没有共享最终权重绕过训练比较。
- `formal-model-paired.json`：正式网络同批前向、反向与参数更新；`formal-device-probe.json` 仅是前置单批硬件证据。
- `formal-resume.json`、`formal-resume-best.json`、`formal-resume-inputs.json`：双方从实际第一轮检查点恢复，第二轮 84 个实际批次、模型及训练状态、此前最佳权重均一致。恢复独立匹配参考重建数据生成器的行为，不声称恢复等于不中断。
- `formal-cache.json`：完整单样本 24 层全表面缓存与 20 个解码预测块一致。比较观察的是原入口实际 `_infer_sample` 返回的缓存，不是替代推理。
- `full-topology.json`：454,404 点、1,792 三角形、453,512 四边形、909,700 边、Euler 特征 8，拓扑严格一致。
- `formal-post.json`：全部 44 样本、19,993,776 点的预测块、HDF5 数组及属性、VTP 点/连接/偏移/点场/全局字段、CSV/JSON 指标一致；包含四通道与摩擦系数模长指标。未以平均误差掩盖局部差异。

上述省略目录的文件均位于 `transolver3-results/`。`coverage.json` 保留 Excel Sheet1 全部 100 项的名称、原来源、Dojo 路径、功能叶子和证据；正常全量路径、故障用例和入口格式差异分别说明。ParaView 的交付为真实 VTP 数值与拓扑，不宣称人工 GUI 浏览验收。

## 功能叶子与圈定测试

- A1/A2：`test_aero_cfd_examples.py`，模型默认值隔离、复制案例、来源相对路径、四个独立阶段与整条流水线一致。A3 的既有汽车行为回归已通过，旧公开 YAML 自动兼容未交付。
- B1/B2/B3：`test_nasa_crm_data.py`，真实 HDF5 字段/形状/工况/非有限值/跨来源点数、训练独占统计、字段顺序、仅公开协议视图消费、冻结摘要、坏块重建和不完整提交标记。
- C1/C3/C4：`test_transolver_training.py`，前后向及非零权重衰减、指纹、相等选优、恢复后没有改善仍保留原最佳、缺最佳拒绝恢复。归一化算术归 transform ability，application 保留兼容导入。
- C2/C4/E1/E2：`test_transolver_reference.py`，原仓库独立完整小数据流程及恢复实际批次配对、缺证据门禁、局部扰动和非有限比较反例。
- D1—D4：`test_transolver_post.py`，真实缓存和 VTP、部分交付、预检、实际第二个 HDF5 写入失败及补跑；完整数据结果由正式工具额外验证。
- E3：`tools/verification/transolver3/` 中 reference/dojo/trace 运行真实入口，compare_data/training/cache/post 执行逐层与最终比较；formal_probe 仅作硬件前置检查。
- F：`test_aero_cfd_documents.py` 检查 100 项真实路径、模块导航、复制脚本一致和正式包引用边界。

已保存回归证据：`core-regression.xml` 75 通过、1 跳过；`workflow-regression.xml` 110 通过、5 跳过；`abupt-formal-regression.xml` 真实 MPS 正式 AB-UPT 两轮 1 通过（约 181 秒）。跳过不作为硬件验收，MPS 正式实跑单列。本轮新增用例 37 通过；增量回归 92 通过、3 跳过；最新新增测试与增量回归数量以 `new-suite.xml` 和 `incremental-regression.xml` 为准，检查摘要见 `delivery-checks.json`：76 文件格式与 Ruff 静态检查通过，导入边界及安装副本一致；mypy 因离线缓存缺少工具未执行。未运行全仓测试；未用局部测试或静态检查替代正式规模对标。

验证使用独立环境 `/private/tmp/dojo-transolver-env`，三个 framework wheel 先重新安装，避免另一任务重装共享环境导致加载到旧实现。命令模板：

```bash
OMP_NUM_THREADS=1 UV_PROJECT_ENVIRONMENT=/private/tmp/dojo-transolver-env UV_CACHE_DIR=/private/tmp/dojo-analysis-uv uv run --no-sync python -m pytest tests/integration/test_aero_cfd_examples.py tests/integration/test_nasa_crm_data.py tests/integration/test_transolver_training.py tests/integration/test_transolver_post.py tests/integration/test_transolver_reference.py tests/integration/test_aero_cfd_documents.py
```

## 原参考恢复的已披露修正

原参考将整个 checkpoint 加载到 MPS 后，把 MPS RNG 张量交给 CPU generator，真实恢复报 `TypeError: RNG state must be a torch.ByteTensor`。verification 的加载包装只将 `torch_random_state` 搬回 CPU，记录 `torch_random_state_to_cpu`；参考源码未改，模型数学与随机消费顺序未变。原参考恢复到新目录且验证不改善时还需携带此前 best；工具校验后复制已有最佳权重，Dojo 在 checkpoint 中保存并恢复选择记录。

人工复制的 `reference-checkpoints/epoch-1.pt` 曾与运行竞争，其内容实际已是第二轮，不能用于恢复验收。最终使用 `reference-repeat-checkpoints/epoch-1.pt`（参考内部 epoch=0）与 `dojo-epoch-snapshots/2026-09-09T18-05-16_a9ed7e/epoch-1.pt`（Dojo epoch=1）。工具现在验证内容轮次并拒绝无更新的伪恢复。失败及无效尝试未计入最终证据。

## 产物位置、重用与边界

全量数据、权重、预测和运行源码快照位于 `/private/tmp/dojo-transolver-formal`，没有进入源码包。此位置是本地临时存储，轻量记录中的绝对引用依赖这些文件仍存在；长期归档需另选持久目录。

- 连续 Dojo：`dojo-runs/2026-09-09T18-05-16_a9ed7e`；参考：`reference-checkpoints`；参考重复：`reference-repeat-checkpoints`。
- 恢复 Dojo：`dojo-resume-fixed-runs/2026-09-09T18-47-35_33eed7`；参考：`reference-resume-final-checkpoints`。
- Dojo 输出：`dojo-data/predictions/test`、`dojo-data/post/test`；参考输出：`reference-predictions/test`、`reference-post/test`。
- `transolver3-results/provenance.json` 保存锁定配置、来源确认与产物定位；实际训练源码以对应 run 的代码快照为准。后续默认参数补齐、归一化模块归位及错误身份改动不修改已生成的历史记录。

训练来源与测试来源可重复 Sample 编号，唯一身份是来源/分片/样本。同一训练来源内 train/validation 不重叠。TOML/命令行由 YAML/阶段入口表达；文件容器压缩、运行路径、日志格式、耗时和源码布局不纳入数值相等。

预测复用绑定数据、权重、变换、推理设置与模型组件源码；后续源码变化导致历史缓存被拒绝属于预期，不重写旧提交标记冒充当前来源。完整模型的来源摘要已保存；原检出未发现许可文件，不虚构许可。正式包不依赖原仓库或 user_project。

待决政策：批准计划要求旧汽车配置兼容，而并行更新的 AGENTS/配置入口要求拒绝旧键。已就此询问用户，未收到选择；保留当前新入口且不覆盖并行修改。这个未决项不影响上述数值结果，但阻止宣布整体计划全部完成。
