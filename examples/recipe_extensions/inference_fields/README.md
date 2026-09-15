# 独立推理派生字段扩展

复制任一 `examples/aero_cfd` 目录到仓库外，再将本目录 `fields.py` 复制到案例目录。
在 `infer.py` 的物理输出步骤之后、保存步骤之前插入：

```python
from fields import absolute_error
job = infer_stage.configure_derived_fields(
    job, name="pressure_error", domain="surface", unit=None,
    inputs={"prediction": "surface.pressure.prediction", "truth": "surface.pressure.truth"},
    operation=absolute_error,
)
```

上例适用于 ShapeNet pressure 字段；NASA 使用实际配置的 pressure_coefficient 名称。
`unit=None` 表示原始数据未声明单位，明确有单位时填写同一物理单位。
同样可用 `settings={"target": "fields.absolute_error"}` 替换直接传入函数，二者互斥。

执行独立 infer 后，新增数组写入样本清单并随真实 VTP 输出；
使用 `infer.read_sample(manifest)` 可读回 `surface.pressure_error`。
新增字段只共享原域实体 ID，不生成新数据集，不修改原训练目标。

派生字段须在 `configure_selection` 前登记，可用 `surface:pressure_error:scalar` 精确选择。未选派生字段不保存；没有独立真值的派生字段保留数组及不可评价原因，不用误差场自身充当真值。字段与普通用户评价一起通过 `test_infer_extensions.py` 外部复制、真实运行、读回和VTK验收。
