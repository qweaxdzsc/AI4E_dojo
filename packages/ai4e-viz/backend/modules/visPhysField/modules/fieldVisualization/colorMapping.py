"""颜色带、离散层级和范围映射业务规则。"""


def normalized_color_position(value: float, minimum: float, maximum: float) -> float:
    """把标量映射到0到1；常量场统一返回中点以保持稳定颜色。"""

    if minimum > maximum:
        raise ValueError("颜色范围下界不能大于上界")
    if minimum == maximum:
        return 0.5
    return min(1.0, max(0.0, (value - minimum) / (maximum - minimum)))


def build_color_mapping(array, color: dict):
    """离散颜色表、自动或固定显示范围，不改变归一化统计。"""
    import math

    import vtk

    limits = color.get("range") or list(array.GetRange())
    if len(limits) != 2 or not all(math.isfinite(x) for x in limits) or limits[0] > limits[1]:
        raise ValueError("invalid_color_range")
    if limits[1] - limits[0] <= 1e-12 * max(1.0, abs(limits[0]), abs(limits[1])):
        padding = max(abs(limits[0]) * 1e-6, 1e-12)
        limits = [limits[0] - padding, limits[0] + padding]
    from matplotlib import colormaps

    preset = color.get("preset", "viridis")
    preset = {"Rainbow": "rainbow", "Jet": "jet", "Turbo": "turbo", "Cool to Warm": "coolwarm"}.get(
        preset, preset
    )
    cmap = colormaps[preset]
    bands = int(color.get("bands", 256))
    if not 2 <= bands <= 256:
        raise ValueError("color_bands_out_of_range")
    lut = vtk.vtkLookupTable()
    lut.SetNumberOfTableValues(bands)
    lut.SetRange(limits)
    lut.Build()
    for j in range(bands):
        lut.SetTableValue(j, *cmap(j / (bands - 1)))
    return lut, limits, bands
