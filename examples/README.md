# 可复制研究案例

研究 Agent 先从 [`docs/agent-help/index.md`](../docs/agent-help/index.md) 按任务检索 workflow、API 和案例主题；每个清单案例的稳定主题 ID 为 `case:<案例ID>`。支持安装资源 API 时调用 `search_help`、`read_help_topic` 和 `describe_help_symbol`，不要只凭目录名猜输入或调用签名。

Dojo 将案例分成两种类型：

- `standalone` 是完整、可独立运行的研究目录，也是 Agent 的主要起点。
- `extension` 是依附 `base_case` 的参考变体，展示替换网络、损失、字段、采样、训练策略或 post 输出的方式。

所有 standalone 遵循 `example_contract_version=1` 与 `recipe_contract_version=1`。目录至少包含 `README.md`、`config.yaml`、`configuration.py` 和 `pipeline.py`，领域阶段文件在清单中明确声明。Python 文件表达顺序和普通值交接，YAML 只保存参数、路径和能力选择；`inputs.*`、`run_root`、`data_root` 是跨阶段路径边界。

Agent 从目录外通过 `python <case>/pipeline.py` 或单阶段脚本开始研究。需要任务版本、代码和配置快照、资产、后台执行、停止、恢复或比较时，将同一个目录交给 `ai4e_task` Python API。CLI 只提供资源发现、复制和 smoke 数据等便利操作，不能替代 direct-core 或 Task 运行证据。

复制 extension 时，资源门面会先复制 `base_case` 的完整 standalone，再叠加清单 `override_files`，遇到未声明冲突、缺基案例或非空目标直接失败，并写出 `.dojo-provenance.json`。物化后的目录才是可运行和可继续修改的研究分支。

机器可读清单是 `case-manifest.json`。它声明案例 ID、类型、模型、数据集、用途、入口、阶段、依赖、维护源标识、公共脚本和验证证据；验证证据描述测试事实，不是第三种案例类型或发布状态。清单和案例不依赖仓库内部导航、隐藏任务描述或本机绝对路径。

- `aero_cfd/shapenet_car_meshgraphnet`：PT+VTKHDF 双域图准备，分别预测表面压力与体积速度。
- `aero_cfd/nasa_crm_meshgraphnet`：NASA 表面 VTKHDF、大图核心分区与 halo 推理，预测 Cp/Cf。

## PCNO 地热研究

`geothermal/pcno` 是完整双场案例；`recipe_extensions/pcno` 在完整副本上替换网络并插入温降分析。发布24例用于集成验证，不代表论文完整复现。
