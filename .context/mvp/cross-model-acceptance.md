# aero_cfd 物理数据跨模型验收

当前状态：本期约定的五组正式 MPS/fp32 单轮训练、固定五样本全点评价与两份报告已交付。圈定回归 163 项通过，沙箱内跳过的两项 MPS 回归已在真实设备补跑通过；最终交付检查 11 项通过。范围和工具限制见下文。

## 输入和执行

独立数据与运行根：`/private/tmp/dojo-cross-model`。`training-runs.json` 和 `post-runs.json` 登记本次明确创建的运行，不根据历史目录猜测成功。

NASA：84 训练、21 验证、44 测试来源，每样本 454404 点；物理 PT 直接来自原 HDF5。汽车：复用 `/private/tmp/dojo-regroup-20260909/data/manifest.json` 的 789 训练和 100 测试，未改写张量。两套测试名单各从排序后的名单用独立 NumPy default_rng(42) 选五样本，前三个出图；名单保存 `selection.json`。

五例均单实例、单轮、最后权重，训练期间不评价测试集。NASA AB-UPT 为单表面域，原 c 跨域块不能用于单域，明确改为已有 s 自注意力块，宽度与块数保留；汽车 AB-UPT 保留联合模型。Transolver NASA/汽车表面为 24 层，汽车体积为 16 层，均宽 256、8 头、64 切片。

NASA 的全部跨步块参与逐层缓存及解码；全点评价没有用训练抽样替代。NASA 正侧半展长从对称中面至正 Y 翼尖，20/50/80% 截面保留真实物理坐标；汽车使用中间 Y/Z 面，缺少有效顶点的单元排除，不填零。

## 功能与测试导航

- A1/A2：`test_physical_dataset_contract.py`；物理视图、样本条件、旧 PT 不变性。
- A3：`test_model_preparation_contract.py`；准备来源和随机流隔离。
- B1/B4：`test_cross_model_recipe.py`；五例共享脚本、复制四阶段、独立后处理。
- B2/B3：`test_cross_model_training.py`；三种维度真实前后向、AB-UPT 条件和异常身份。
- C1/C3：`test_cross_model_comparison.py`；身份对齐、加权指标、非有限及零分母。
- C2：`test_comparison_visualization.py`；解析场的切面与共同插值。
- D：`test_cross_model_acceptance.py`；显式本次真实运行、更新数、完整预测复算、图像和导航。环境未指定时 skip 不算正式验收。

新增源码位置见各模块索引。参考 NPY 算法回归使用 `tests/fixtures/transolver3/reference-example.yaml`，不以迁移后的公共 example 改写原参考测试。

## 结果与边界

两份离线报告在 `/private/tmp/dojo-cross-model/reports/{nasa,shapenet}/index.html`，逐样本和总体数值在 `comparison/{数据集}/{域}/comparison.json`。报告含 NASA 24 张与汽车 9 张图像，图像不进入仓库。

这是一轮实验的组装与数据复用验收，不证明模型精度上限或不同硬件数值等价。原 Transolver 全量两轮对标不重跑；旧算法范围按相关回归检查。公共物理训练路径当前支持 batch=1、workers=0、fp32 和独立 post 评价，其余执行设置仍使用既有工作流。

## 交付证据

- `cross-model-results/selection.json`：训练前冻结的五样本名单。
- `cross-model-results/training-runs.json`、`post-runs.json`：实际运行、检查点与预测定位。
- `cross-model-results/experiments.json`：正式参数规模、采样策略、更新数和耗时。
- `cross-model-results/metrics.json`：两数据集逐样本和总体物理指标。
- `cross-model-results/scoped-tests.xml`、`mps-regression.xml`、`final-contracts.xml`、`final-delivery.xml`：圈定用例、真实 MPS 补跑和最后交付检查。
- `cross-model-results/source.json`、`checks.json`：当前代码摘要、格式与静态边界检查。训练时实际代码快照另在每个运行自身的 code.tar.gz，不将当前代码摘要冒充训练时版本。

逐字段 MSE/MAE/相对 L2 的关键结果（AB-UPT / Transolver-3）：

- NASA Cp：0.12366367 / 0.13272174；0.23166239 / 0.23089948；0.96554442 / 1.00028146。
- NASA Cf 模长：1.36989735e-6 / 1.43140701e-6；0.00079384 / 0.00080804；0.55449729 / 0.56680932。
- 汽车表面压力：246.34068029 / 830.17301351；8.93202589 / 20.56690859；0.26548095 / 0.48735968。
- 汽车体速度（三分量合计）：1.25482079 / 0.99064940；0.60208618 / 0.48955619；0.10496393 / 0.09326296。

NASA 每模型评价 2,272,020 个表面点；汽车每模型对应域评价 17,930 个表面点、142,520 个体积点。比较指标逐元素独立复算通过。NASA 压力预测在一轮后较粗糙，不能据此推断模型精度上限。

相关用例均按本文件圈定范围运行，未用全仓测试替代；实际命令使用 uv run 和独立已安装 wheel 环境 `/private/tmp/dojo-transolver-env`。Ruff 只读检查和包依赖 AST 检查通过。mypy 本地不可用且离线缓存缺包，未执行，不宣称类型检查通过。
