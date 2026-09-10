
# Recipe、Dataset 与前处理重构方案

## 1. 可复制的运行代码与可安装的共享能力

将 `packages/ai4e-recipes` 改为普通 `recipes/` 模板集合，移除其安装配置、workspace 成员和 `ai4e_recipes` 导入依赖。

```text
recipes/aero_cfd/
├── README.md
├── config.yaml
├── pipeline.py
└── pre.py
```

删除 recipe 内的 `__init__.py`、`__main__.py` 和已有 `__pycache__`；脚本入口禁止后续本地模块导入生成字节码缓存。

- `uv run python pipeline.py`：按配置串接阶段，默认仅 pre。
- `uv run python pre.py`：独立执行前处理。
- 默认读取脚本旁的配置，支持 `--config`。
- pipeline 不展开 pre 内部步骤；调用 pre 时共用一次运行上下文，不重复创建运行记录。
- 代码、运行记录、数据分别定位，没有强制父子关系。

将 contrib 建成可安装、可直接 import 的包，共享数据集组织为：

```text
contrib/application/datasets/shapenet_car/
├── manifest.yaml
└── adapter.py
```

用户可以引用或复制修改。recipe 不预建组件目录；server/web 上传、task new/fork 暂不实现。

## 2. Dataset 分层与 pre 写法

- **Manifest**：描述文件布局、样本身份、字段来源、point/cell 归属、分量数、已知单位和官方划分。
- **Adapter**：解释 manifest，完成样本发现、选择、划分和数据集特有处理；通用算法调用 core。
- **Recipe**：明确选择样本、字段、维度要求、处理方法与参数。
- **Dataset**：使用体验接近内存对象，实际按需加载；执行时逐样本完成整条链并提交，不把整批网格保存在内存。

`pre.py` 只公开一个 `preprocess(cfg)`，所有参数直接使用 `cfg.xxx`：

```python
def preprocess(cfg):
    dataset = shapenet_car.open_dataset(
        root=cfg.dataset.root,
        manifest=cfg.dataset.manifest,
        samples=cfg.dataset.samples,
        partition=cfg.dataset.partition,
    )

    data = pre.read(dataset, sources=cfg.sources)
    data = pre.extract_fields(data, fields=cfg.fields)
    data = pre.derive_geometry(data, features=cfg.geometry)
    data = pre.select_fields(data, fields=cfg.save_fields)
    data = pre.validate_fields(data)
    data = pre.filter_points(data, filters=cfg.filters)
    data = pre.validate_fields(data)
    data = pre.to_tensors(data)

    results = run.execute(
        data,
        save=pre.save_sample,
        output=cfg.paths.datasets,
    )

    dataset = pre.publish_dataset(results)
    pre.compute_statistics(dataset, cfg.statistics)

    return dataset
```

上述为待实现接口。步骤声明形成按需执行的数据流，`run.execute` 才触发实际处理。复用顺序执行机制，不引入 DAG；run 负责循环和汇总，保存策略解释业务输出，application 不反向导入 run。

## 3. 显式路径插值、统计与运行配置

所有默认路径均明确写出组成关系，不再隐式追加目录名：

```yaml
# 原始数据、处理产物和运行记录分别指定。
dataset:
  root: /shared/raw/shapenet_car

data_root: /shared/datasets/car_experiment
run_root: /shared/runs/car_experiment

paths:
  datasets:
    root: ${data_root}
    train: ${data_root}/train
    eval: ${data_root}/eval
    test: ${data_root}/test

    normalize:
      root: ${data_root}/normalize
      train: ${paths.datasets.normalize.root}/train
      eval: ${paths.datasets.normalize.root}/eval
      test: ${paths.datasets.normalize.root}/test
```

支持任意配置变量的 `${...}` 引用；例如可以单独将 test 改为另一块磁盘：

```yaml
test_root: /other_disk/car_test

paths:
  datasets:
    test: ${test_root}/test
```

路径处理顺序固定为：**合并配置与覆盖 → 展开变量 → 相对于配置文件解析相对路径 → 输出预检**。未知变量、循环引用直接报错；不能留下未展开的字符串进入运行。

- run_root 下创建唯一运行记录目录；不把数据自动放到该目录内。
- 未配置的分片不创建；本次不创建 normalize 目录。
- 统计参数从本次完整成功的训练分片计算，保存到其 `statistics.yaml`，由产物 manifest 引用。
- eval/test 不参与训练参数拟合；训练样本失败时不发布完整训练统计。
- 显式选用随 adapter 发布的参考统计时，记录其来源，不标为本次拟合。
- 产物 manifest 保存实际路径、分片、字段形状、物理/归一化状态和统计引用；训练读盘消费该清单。
- `inputs/` 仅保存一个最终生效的 `config.yaml`，变量已展开、路径已解析；计数和结果进入产物与摘要。

本次仅设计后续归一化的字段方法、参数、统计引用及路径机制，不实现 apply/inverse，也不生成归一化张量。后续以 Noether 实际行为为参考，不能默认为已归一化。

## 4. 日志规范与示例

`run.log` 保留实际执行的原子能力与工作流的开始、结束和耗时。批量或耗时操作报告内部进度；默认每 10 秒更新一次。无法取得完成比例时，只报告当前操作与已耗时。

下面是一份**日志节选示例**。其他样本也按同样规则记录，示例中省略了重复部分：

```text
09:00:00.000 INFO  [运行] 开始前处理
                  执行脚本=/work/experiments/car/pre.py
                  运行目录=/shared/runs/car_experiment/<run-id>
                  生效配置=inputs/config.yaml

09:00:00.010 INFO  [数据集/开始] 打开 ShapeNet-Car
                  原始数据=/shared/raw/shapenet_car
                  适配器=ai4e_contrib.application.datasets.shapenet_car
                  样本选择=全部；划分=官方划分

09:00:00.080 INFO  [数据集/结束] 选中 889 个样本
                  train=789；test=100；未配置 eval
                  物理场=表面压力(1分量)、体积速度(3分量)
                  耗时=0.07秒

09:00:00.090 INFO  [输出预检/开始] 检查目标路径与已有文件
09:00:00.110 INFO  [输出预检/结束] 目标可写，无覆盖冲突
                  train=/shared/datasets/car_experiment/train
                  test=/shared/datasets/car_experiment/test

09:00:00.120 INFO  [批量前处理/开始] 共 889 个样本；失败策略=首错停止

09:00:00.130 INFO  [读取/开始] 样本=param0/car_001；域=surface
                  文件=/shared/raw/shapenet_car/param0/car_001/quadpress_smpl.vtk
09:00:00.160 INFO  [读取/结束] 样本=param0/car_001；域=surface
                  点数=4000；单元数=3800；耗时=0.03秒

09:00:00.170 INFO  [字段提取/开始] 样本=param0/car_001
                  字段=surface_pressure；来源=PointData.point_scalars
09:00:00.175 INFO  [字段提取/结束] 样状=(4000, 1)；类型=float32；耗时=0.005秒

09:00:00.200 INFO  [几何派生/开始] 样本=param0/car_001
                  任务=体积点到表面网格的有符号距离；待处理点数=320000

09:00:10.200 INFO  [点到面距离/进度] 样本=param0/car_001
                  已处理=192000/320000；进度=60%；已耗时=10.0秒

09:00:16.800 INFO  [几何派生/结束] 样本=param0/car_001
                  已处理点数=320000；耗时=16.6秒

09:00:16.810 INFO  [字段校验/开始] 样本=param0/car_001
                  检查=来源、实体身份、数量、分量
09:00:16.820 INFO  [字段校验/结束] 全部通过；耗时=0.01秒

09:00:16.830 INFO  [筛选/开始] 样本=param0/car_001；域=volume
                  规则=排除与表面坐标重合的点；筛选前=320000
09:00:16.850 INFO  [筛选/结束] 保留=316000；删除=4000
                  字段与原始实体身份已同步；耗时=0.02秒

09:00:16.880 INFO  [张量编码/开始] 样本=param0/car_001；字段数=7
09:00:16.900 INFO  [张量编码/结束] 字段数=7；耗时=0.02秒

09:00:16.910 INFO  [样本提交/开始] 样本=param0/car_001
                  目标=/shared/datasets/car_experiment/test/param0/car_001
09:00:16.960 INFO  [样本提交/结束] 已提交文件=7；耗时=0.05秒

09:00:16.970 INFO  [批量前处理/进度] 完成=1/889；失败=0；未执行=888
                  当前样本耗时=16.84秒
```

上述 `样状` 字段在实现中统一命名为 `形状`。长操作的计数来自实际分块执行；如果底层一次性调用无法提供计数，则记录：

```text
09:00:10.200 INFO  [点到面距离/运行中] 样本=param0/car_001
                  已耗时=10.0秒；底层计算尚未返回
```

统计与整体结束记录示例：

```text
09:12:00.000 INFO  [批量前处理/结束] 成功=889；失败=0；未执行=0
                  耗时=11分59.88秒

09:12:00.010 INFO  [统计/开始] 分片=train；样本数=789
                  范围=本次成功提交的训练样本
                  方法=逐字段流式累计；标准差=总体标准差

09:12:10.010 INFO  [统计/进度] 字段=volume_velocity
                  已读取样本=420/789；已累计实体数=132720000

09:12:20.000 INFO  [统计/结束] 已完成全部指定字段
                  文件=/shared/datasets/car_experiment/train/statistics.yaml
                  耗时=19.99秒

09:12:20.020 INFO  [数据清单/结束] 已发布 manifest
                  数据状态=物理空间；未执行归一化

09:12:20.030 INFO  [运行/结束] 状态=成功；总耗时=12分20.03秒
                  数据清单=/shared/datasets/car_experiment/manifest.json
                  运行摘要=summary.json
```

失败示例：

```text
09:03:12.000 ERROR [字段提取/失败] 样本=param1/car_023；域=surface
                  文件=/shared/raw/shapenet_car/param1/car_023/surface.vtp
                  未找到 PointData 数组 Pressure
                  可用数组=p、wallShearStress
                  配置位置=fields.surface.pressure.array

09:03:12.010 ERROR [批量前处理/结束] 状态=失败
                  已成功=120；失败=1；未执行=768
                  已提交样本保留；训练统计与完整数据清单未发布
                  详细堆栈=logs/errors.log
```

原子能力发出事件，run/writer 统一写日志，不各自创建文件处理器。控制台展示工作流、进度和错误摘要；完整能力记录保存在 run.log。禁止打印数组、完整配置和整个批量结果字典。

## 5. 迁移与验收

同步更新 AGENTS、唯一架构文档、模块索引和相关 PRD；迁移 recipe 安装依赖、测试资源定位及旧训练读盘入口。

相关测试覆盖：

- 复制后的 recipe 无需安装即可运行；pipeline/pre 行为一致，不重复创建运行记录。
- contrib 安装、import、adapter 引用与复制修改。
- 样本、字段、划分选择及 point/cell 身份、维度校验。
- Dataset 按需读取与逐样本提交，不积累整批数组。
- 路径变量嵌套引用、单项覆盖、绝对/相对路径、未知变量及循环引用。
- 输出冲突、提交失败恢复、训练统计范围与参考统计来源。
- 产物 manifest 与训练读盘一致；不误报归一化完成。
- 原子能力和工作流的开始/结束日志、真实进度、失败摘要；inputs 只有一个 YAML。

仅运行受影响测试，使用 `uv run pytest <相关路径>` 验收，不以全仓测试替代相关链路验证。

