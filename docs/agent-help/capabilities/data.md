<!-- dojo-help: {"topic_id": "capability:data", "title": "数据读取、预处理与归一化", "kind": "tutorial", "layer": "capability", "domain": "data", "summary": "读取、字段提取、身份校验、筛选、保存、统计及正反归一化", "tasks": ["数据前处理", "归一化", "训练集统计", "读取 NumPy 数据"], "symbols": ["ai4e_core.abilities.data.stats.tensor_moments.tensor_moments", "ai4e_core.abilities.transform.standardization.Standardization", "ai4e_core.abilities.data.source.read.read_file", "ai4e_core.abilities.data.extract.time_windows.window_slices", "ai4e_core.abilities.data.filter.select.apply_aligned_mask", "ai4e_core.abilities.data.save.store.write_tensor_file", "ai4e_core.abilities.data.save.store.load_named_tensor"], "navigation_order": 1} -->
# 数据读取、预处理与归一化

适合已有数组需要训练集统计及冻结变换；文件读取按来源选择 data/source，实体对齐与筛选查 data/validate、data/filter，保存查 data/save。Dojo 不会自动理解任意新数据集的字段或分片。

输入为最后一轴是通道的张量；统计函数显式指定归约轴、精度及总体/样本标准差，返回 mean/std。Standardization 接受冻结参数并提供 apply/inverse，保留设备和梯度。只在训练分片拟合；验证和测试复用训练统计。坐标、单位、时间与样本 ID 由调用方保存。

## 按前处理工作继续分支

- **读文件**：`ai4e_core.abilities.data.source.read.read_file` 目前面向已登记 VTK/VTKHDF/NPY 格式并返回 VTK 对象；它不是任意 HDF5 表的读取器。新 HDF5 科学数据可由普通 h5py 适配，再接下游数组能力。
- **取时间窗口**：`ai4e_core.abilities.data.extract.time_windows.window_slices` 返回 history/future 两个 slice，明确 history、horizon、interval、gap、stride，并拒绝越界。
- **同步筛选**：`ai4e_core.abilities.data.filter.select.apply_aligned_mask` 将相同布尔 mask 应用于一组首维对齐数组，返回新映射；不能独自筛标签或坐标。
- **保存与读回**：`ai4e_core.abilities.data.save.store.write_tensor_file/load_named_tensor` 负责张量文件交付；覆盖显式选择，恢复用对应读接口。
- **统计与正反变换**：下面的 tensor_moments / Standardization；训练分片身份和冻结统计由研究代码登记。

## 直接入口

- `ai4e_core.abilities.data.stats.tensor_moments.tensor_moments`
- `ai4e_core.abilities.transform.standardization.Standardization`

使用 `ai4e_task.describe_help_symbol` 核对当前安装版本的签名和源码；这里的例子验证调用，不代表生产精度。

- `ai4e_core.abilities.data.source.read.read_file`
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
