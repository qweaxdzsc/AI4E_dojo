# SafeDiffCon 参考复现入口

当前按每案例累计三小时执行模型接入。长训练已停止；缩小实验不等于论文精度复现。完整实施顺序及验收见
[实施计划](../../../.cursor/plans/safediffcon-integration.plan.md)；实际证据见
[专项记录](../../../.context/mvp/safediffcon-acceptance.md)。

## 数据与源码核验

从 Dojo 仓库执行，输出目录必须不存在；不会向原数据或原仓库写入：

```bash
uv run --no-sync python tools/verification/safediffcon/admission.py \
  --source /Users/zonghui/work/new_code_project/SafeDiffCon \
  --burgers '/Users/zonghui/work/datasets/1D_burger/1D Burgers_' \
  --tokamak /Users/zonghui/work/datasets/tokamak \
  --output /Users/zonghui/work/project_simulation/dojo_train/safediffcon/admission/NEW_RUN
```

`admission.json` 的数据通过不代表科学口径通过。原始 Tokamak `targets` 与源码使用的
`outputs` 分别统计，不合并成同一个目标。源码快照只包含两个案例的跟踪文件与资源，
同时保存实际修改补丁；未跟踪文件仅登记，不自动执行。

## 独立环境

参考训练用 Python 3.12，KSTAR 用 Python 3.9。两个环境的依赖分别由本目录
`reference_env/pyproject.toml` 与 `kstar/pyproject.toml` 声明。使用 `uv venv` 建立环境，
用 `uv pip install --python <独立环境>/bin/python -r <对应清单>` 安装，不同步主环境。
实际包版本写入每次探针或训练记录。macOS ARM 使用官方 `tensorflow-macos` 分发，
TensorFlow/Keras 2.13.1、NumPy 1.22.4、SciPy 1.7.3 保持原仓库版本。

执行独立解释器时必须使用 `uv run --no-project --python <独立解释器> python ...`；
省略 `--no-project` 可能重新选择当前 Dojo 的环境。`PYTHONDONTWRITEBYTECODE=1` 保证
运行不向参考快照写字节码；`MPLBACKEND=Agg` 避免弹出绘图窗口。

## 限时参考与 Dojo

`compare.py --config <quick.yaml> --snapshot <冻结源码> --side reference|dojo --output <新目录>` 消费两案例配置。
每次外层必须通过 `tools/verification/gencp/budget.py --ledger <同一案例账本> -- <计算命令>`；失败与重试计入累计，175分钟软停止、180分钟硬终止。
参考侧执行原网络和原 Trainer，使用与Dojo相同的可恢复批次流，消除抽样差异。后续控制阶段共用领域连接；`numerics.py`另对原采样、引导及校准定义验证，避免把共同实现自比较冒充独立参考。

继续切片使用 `--independent-stages`：参考侧直接执行冻结原校准类、原加权训练步与适配步，并用原网络采样，不调用 Dojo 后训练或推理编排。共享边界是准备数组/批次流、检查点容器、响应求解及指标/结果存储。每轮开始校准、阶段权重交接和实际适配数属于披露的修正，不是原脚本原样运行。省略开关保留历史共享编排入口。

`inputs.train.resume` 使用各侧已验完整预训练权重，`train.updates` 是包含历史的总目标。原 Trainer 连接恢复优化器、调度器及步数，随机量和流由已有容器恢复；无这些状态的作者权重不能精确恢复。正式增加步数前须以同一恢复状态完成数值检查。

阶段预算入口：`uv run --no-sync python -m tools.verification.safediffcon.budget --ledger <已有账本> --seconds <阶段秒数> --reserve <最终评价预留秒数> -- <计算命令>`。只接受已有账本，最大仍为累计180分钟；配置的20000总步数上限不能替代实际计时。

`acceptance.py` 默认要求完整50样本；`--diagnostic-samples` 只用于固定小样本数值诊断，并在输出明确标识 `diagnostic_only`，不能记为正式评价。

`short_probe.py` 实测更新和采样开销；`reference.py` 是保留的历史诊断入口，必须显式填写1–4000步，禁止启动200000步。当前模型/预算真源是 `examples/safediffcon/{burgers,tokamak}/quick.yaml`。
所有执行需要显式把 `run_root`、`data_root` 指向外部实验目录。配置加载器解析相对路径；运行报告与数据分目录。

## 响应探针

`probe.py burgers` 接收原 HDF5 目录，回放全部测试控制并诊断两个原类构造。
`probe.py kstar` 接收仅含数值的 NPZ（actions、outputs），在独立环境加载原 KSTAR
模型，输出逐场差值与完整响应 NPY。KSTAR 仅修正原模块通过 argv[0] 查找资源的位置，
不改变控制裁剪、取整、重置或递推。CLI 非零退出表示失败或不一致，应读取 JSON 原因。

## 本切片验收

```bash
uv run --no-sync pytest tests/integration/test_safediffcon_admission.py tests/integration/test_safediffcon_reference.py -q
```

这些测试覆盖输入完整性和启动门禁。它们不替代完整训练、论文指标、Dojo 数值迁移及安装验收。


## 当前公共约定验收

`public_conventions.py --case burgers|tokamak --output <新目录>` 复制完整example，经实际安装包执行原读取器的8/4/2原分片前缀、六阶段Task、相同准备的直接流程、2→3恢复、独立阶段、结果共享及fork后post。`--template`另验Burgers公共模板。加入模型包装与energy派生/独立audit步骤并读回；不改科学默认配置。

`task_acceptance.py` 显式转换旧冻结配置为内存新副本，从历史5000/8000状态各续训一次并执行真实响应。历史报告不覆盖。`continue_case.py` 核验旧配置摘要后生成新的public配置，安装环境由调用者显式选择，不回到历史安装副本；该工具仍为较长研究续接，不属于本轮短验收命令。

以上计算均须由原累计账本包装。正常训练通过、故意缺输入失败、固定post隔离、论文未达标分开报告。研究入口及最新实际数字以专项记录为准。

`release_replay.py --root <实验根> --case burgers|tokamak` 使用已交付 `public-conventions/run.sh`，经CLI新建模板与案例任务；只运行历史固定结果post，核对历史数组未改和worker实际安装来源。外层仍需原账本监督。
