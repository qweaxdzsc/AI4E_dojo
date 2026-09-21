<!-- dojo-help: {"topic_id": "capability:sampling", "title": "几何与采样", "kind": "tutorial", "layer": "capability", "domain": "sampling", "summary": "网格、坐标、法向、距离和一致采样，保留实体身份", "tasks": ["网格采样", "下采样", "几何"], "symbols": ["ai4e_core.abilities.sampling.structured_grid.sample_grid", "ai4e_core.abilities.sampling.structured_grid.grid_faces"], "navigation_order": 2} -->
# 几何与采样

规则网格用 sample_grid 获取采样数组、原始实体 ID 和新形状，坐标与标签必须共用相同 ID。曲面法向和距离进入 geometry 对应 API，不能把任意体网格当作二维曲面。

下面输入是 C 序展平的 [N,C]；返回值不是自动插值或物理网格重建。改变分辨率必须登记，评价时仍需返回协议规定的网格。

## 直接入口

- `ai4e_core.abilities.sampling.structured_grid.sample_grid`
- `ai4e_core.abilities.sampling.structured_grid.grid_faces`

使用 `ai4e_task.describe_help_symbol` 核对当前安装版本的签名和源码；这里的例子验证调用，不代表生产精度。

## 可执行小例子

将代码保存到独立研究目录的 `source/demo.py`，从研究目录启动；不同例子用不同工作目录。

```python
import numpy as np
from ai4e_core.abilities.sampling.structured_grid import sample_grid, grid_faces

values = np.arange(32).reshape(16, 2)
sampled, ids, shape = sample_grid(values, (4, 4), (2, 2))
assert shape == (2, 2)
np.testing.assert_array_equal(sampled, values[ids])
assert len(grid_faces(shape)) == 5
```

## 继续阅读

[接入细节](../user-components/sampling.md) · [帮助首页](../index.md)
