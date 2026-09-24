<!-- dojo-help: {"topic_id": "capability:data", "title": "数据读取、预处理与归一化", "kind": "tutorial", "layer": "capability", "domain": "data", "summary": "读取、身份校验、保存、统计、正反归一化及普通拟合状态读回", "tasks": ["数据前处理", "归一化", "训练集统计", "读取 NumPy 数据", "代理模型状态保存"], "symbols": ["ai4e_core.abilities.data.stats.tensor_moments.tensor_moments", "ai4e_core.abilities.transform.standardization.Standardization", "ai4e_core.abilities.data.source.read.read_file", "ai4e_core.abilities.data.extract.time_windows.window_slices", "ai4e_core.abilities.data.filter.select.apply_aligned_mask", "ai4e_core.abilities.data.save.store.write_tensor_file", "ai4e_core.abilities.data.save.store.load_named_tensor", "ai4e_core.abilities.data.source.array_read.read_array", "ai4e_core.abilities.data.stats.moments.accumulate_moments", "ai4e_core.abilities.data.stats.fit.fit_statistics", "ai4e_core.abilities.data.save.array_manifest.save_arrays", "ai4e_core.abilities.data.save.array_manifest.read_arrays", "ai4e_core.abilities.data.save.arrays.save_npy", "ai4e_core.abilities.data.save.arrays.save_json", "ai4e_core.abilities.data.validate.fingerprint.file_fingerprint", "ai4e_core.abilities.data.validate.fingerprint.source_fingerprint", "ai4e_core.abilities.data.save.surrogate.save_state", "ai4e_core.abilities.data.save.surrogate.read_state"], "navigation_order": 1} -->
# 数据读取、预处理与归一化

适合已有数组需要训练集统计及冻结变换；文件读取按来源选择 data/source，实体对齐与筛选查 data/validate、data/filter，保存查 data/save。Dojo 不会自动理解任意新数据集的字段或分片。

输入为最后一轴是通道的张量；统计函数显式指定归约轴、精度及总体/样本标准差，返回 mean/std。Standardization 接受冻结参数并提供 apply/inverse，保留设备和梯度。只在训练分片拟合；验证和测试复用训练统计。坐标、单位、时间与样本 ID 由调用方保存。

## 按前处理工作继续分支

- **读数值数组**：`ai4e_core.abilities.data.source.array_read.read_array(path, selection, key=...)` 支持具名 HDF5 数据集与 NPY 切片，返回独立有限数组。HDF5 字段组合、轨迹名单与 tar 成员选择仍由用户适配；不要因 VTK 读取器不支持 HDF5 就重写已有数组读取能力。
- **读网格对象**：`ai4e_core.abilities.data.source.read.read_file` 面向已登记 VTK/VTKHDF/NPY 格式并返回 VTK 对象；它与原生数组入口不同。
- **有序记录收批与尾批恢复**：`training.epoch_stream.EpochBatchStream` 接收用户生成的索引/窗口记录，保存轮内游标与独立 PCG64；支持保留尾批或显式丢尾。它不读取数据、不改变抽样分布、不预取下一轮，完整限制和示例见[训练能力](training.md)。
- **取时间窗口**：`ai4e_core.abilities.data.extract.time_windows.window_slices` 返回 history/future 两个 slice，明确 history、horizon、interval、gap、stride，并拒绝越界。
- **同步筛选**：`ai4e_core.abilities.data.filter.select.apply_aligned_mask` 将相同布尔 mask 应用于一组首维对齐数组，返回新映射；不能独自筛标签或坐标。
- **保存与读回**：具名数值数组可用 `data.save.array_manifest.save_arrays/read_arrays` 保存清单、形状、摘要并校验读回；`data.save.arrays.save_npy/save_json` 提供原子写入。PT 张量采用 `data.save.store.write_tensor_file/load_named_tensor`；数据写入数据目录，运行记录交给 writer。
- **流式总体统计**：`data.stats.moments.accumulate_moments` 消费 FP64 数组流，合并总体矩；`fit_statistics` 按具名字段组织。调用方转换实体/通道轴并选择训练分片，不必重写总体矩合并。
- **单数组统计与正反变换**：下面的 tensor_moments / Standardization；训练分片身份和冻结统计由研究组件登记。不同统计函数的零方差、稳定项与归约约定须按目标核对。
- **内容身份**：`data.validate.fingerprint.file_fingerprint/source_fingerprint` 提供文件流摘要和源码摘要；它们不替代样本分片和科学身份校验。

## 普通拟合状态与来源交接

[save_state / read_state](../api/core/abilities/data/save/surrogate.md) 保存 JSON 结构、校验数组及原生模型文本，不执行 pickle 或动态导入。`save_state(directory, state, context=...)` 拒绝覆盖并返回清单路径；`read_state(path)` 返回 `(state, context)`，预测对象由调用方显式重建。

context 由 application 声明并比较：训练数据身份、字段/特征顺序、归一化、POD 基等。文件摘要正确不意味着这些科学身份兼容。保存状态恢复的是拟合结果，不自动恢复优化轨迹；运行日志仍归 writer。最小读回闭环见[推理例子](inference.md)。

## 直接入口

- `ai4e_core.abilities.data.stats.tensor_moments.tensor_moments`
- `ai4e_core.abilities.transform.standardization.Standardization`

使用 `ai4e_task.describe_help_symbol` 核对当前安装版本的签名和源码；这里的例子验证调用，不代表生产精度。

- `ai4e_core.abilities.data.source.read.read_file`
- `ai4e_core.abilities.data.source.array_read.read_array`
- `ai4e_core.abilities.data.stats.moments.accumulate_moments`
- `ai4e_core.abilities.data.stats.fit.fit_statistics`
- `ai4e_core.abilities.data.save.array_manifest.save_arrays`
- `ai4e_core.abilities.data.save.array_manifest.read_arrays`
- `ai4e_core.abilities.data.save.arrays.save_npy`
- `ai4e_core.abilities.data.save.arrays.save_json`
- `ai4e_core.abilities.data.validate.fingerprint.file_fingerprint`
- `ai4e_core.abilities.data.validate.fingerprint.source_fingerprint`
- `ai4e_core.abilities.data.extract.time_windows.window_slices`
- `ai4e_core.abilities.data.filter.select.apply_aligned_mask`
- `ai4e_core.abilities.data.save.store.write_tensor_file`
- `ai4e_core.abilities.data.save.store.load_named_tensor`

## 可执行小例子

将代码保存到独立研究目录的 `source/demo.py`，从研究目录启动；不同例子用不同工作目录。

```python
import torch
from ai4e_core.abilities.data.stats.tensor_moments import tensor_moments
from ai4e_core.abilities.transform.standardization import Standardization

train = torch.arange(24, dtype=torch.float32).reshape(3, 4, 2)
mean, std = tensor_moments(train, axes=(0, 1), dtype=torch.float64, correction=0)
transform = Standardization(tuple(mean.tolist()), tuple(std.tolist()), arithmetic="divide")
encoded = transform.apply(train)
torch.testing.assert_close(transform.inverse(encoded), train)
assert encoded.shape == train.shape
```

## 继续阅读

[接入细节](../user-components/fields-and-transforms.md) · [帮助首页](../index.md)
