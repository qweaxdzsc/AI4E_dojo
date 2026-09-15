"""与参考图对齐的紧凑属性行；坐标三分量独立输入，计算仍需应用。"""

# ruff: noqa: SIM117 - Trame 布局按 DOM 层级书写。

from trame.widgets import html
from trame.widgets import vuetify as v


def row(label, **kwargs):
    """属性标签与输入横向对齐，不使用占高的浮动标签。"""
    wrapper = html.Div(classes="phys-property-row", **kwargs)
    wrapper.__enter__()
    html.Span(label, classes="phys-property-label")
    wrapper.__exit__(None, None, None)
    return wrapper


def field(ui, key, label, **kwargs):
    """普通计算参数只写草稿。"""
    with row(label):
        v.VTextField(
            v_model=(key,),
            __properties=[("aria_label", "aria-label"), ("aria_pressed", "aria-pressed")],
            aria_label=label,
            dense=True,
            outlined=True,
            hide_details=True,
            change=(lambda value: ui.set_parameter(key, value), "[$event]"),
            **kwargs,
        )


def xyz(ui, key, label, accessible):
    """三个坐标共用已有声明式参数，不另建业务配置。"""
    with row(label):
        with html.Div(classes="phys-xyz"):
            for index, axis in enumerate("XYZ"):
                v.VTextField(
                    v_model=(f"{key}_{index}", "0"),
                    __properties=[("aria_label", "aria-label"), ("aria_pressed", "aria-pressed")],
                    aria_label=f"{accessible} {axis}",
                    title=axis,
                    dense=True,
                    outlined=True,
                    hide_details=True,
                    change=(lambda value, i=index: ui.set_coordinate(key, i, value), "[$event]"),
                )


def choices(ui, key, label, items):
    """紧凑单选按钮，避免为两三个选项再开下拉。"""
    with row(label):
        with html.Div(classes="phys-choice"):
            for value, text in items:
                v.VBtn(
                    text,
                    small=True,
                    outlined=True,
                    depressed=(f"{key} === '{value}'",),
                    __properties=[("aria_label", "aria-label"), ("aria_pressed", "aria-pressed")],
                    aria_label=f"{label} {text}",
                    click=lambda selected=value: ui.set_parameter(key, selected),
                )


def select(ui, key, label, items, *, display=False, **kwargs):
    """计算与显示字段保持独立，显示设置即时提交。"""
    with row(label):
        v.VSelect(
            v_model=(key,),
            items=items,
            __properties=[("aria_label", "aria-label"), ("aria_pressed", "aria-pressed")],
            aria_label=label,
            dense=True,
            outlined=True,
            hide_details=True,
            change=(
                lambda value: (
                    ui.set_display(key, value) if display else ui.set_parameter(key, value)
                ),
                "[$event]",
            ),
            **kwargs,
        )


def properties_panel(ui):
    """单对象属性以表格式布局展示，避免大面积空白与重复工具。"""
    with html.Div(classes="phys-properties"):
        with html.Div(classes="phys-panel-heading"):
            html.H3("属性 / 配置")
            v.VIcon("mdi-pin-outline", small=True, aria_hidden="true")
        with html.Div(classes="phys-property-content"):
            with row("当前对象"):
                html.Span("{{ object_name }}", classes="phys-object-title")
                html.Span("未应用", v_if="pending", classes="phys-draft-badge")
            with html.Div(v_if="kind === 'slice' || kind === 'clip'"):
                with row("切面类型"):
                    html.Div("平面", classes="phys-static-select")
                with row("剖切方向"):
                    with html.Div(classes="phys-xyz"):
                        for axis, label in (("x", "X"), ("y", "Y"), ("z", "Z")):
                            v.VBtn(
                                label,
                                small=True,
                                outlined=True,
                                aria_label=f"对齐{label}方向",
                                click=lambda a=axis: ui.align_plane_axis(a),
                            )
                xyz(ui, "plane_origin", "原点", "原点")
                xyz(ui, "plane_normal", "法向", "法向（无量纲）")
                v.VCheckbox(
                    v_if="kind === 'clip'",
                    v_model=("inside_out",),
                    label="保留平面反侧",
                    dense=True,
                    hide_details=True,
                    change=(lambda x: ui.set_parameter("inside_out", x), "[$event]"),
                )
            with html.Div(v_if="['glyph','streamline','isosurface','contour'].includes(kind)"):
                select(ui, "compute_field", "计算物理量", ("compute_items",))
                select(
                    ui,
                    "compute_component",
                    "计算分量",
                    ("compute_components", ["magnitude", 0, 1, 2]),
                    v_if="kind === 'isosurface' || kind === 'contour'",
                )
            with html.Div(v_if="kind === 'isosurface' || kind === 'contour'"):
                field(ui, "iso_values", "等值列表")
            with html.Div(v_if="kind === 'glyph'"):
                field(ui, "vector_scale", "箭头比例", type="number")
                field(ui, "vector_stride", "采样间隔", type="number")
            with html.Div(v_if="kind === 'streamline'", classes="phys-seed-block"):
                choices(
                    ui,
                    "seed_type",
                    "起点类型",
                    (
                        ("line", "线段"),
                        ("sphere", "球体"),
                        ("plane", "平面"),
                        ("surface", "命名面"),
                    ),
                )
                with html.Div(v_if="seed_type === 'line'"):
                    xyz(ui, "seed_start", "起点", "种子起点")
                    xyz(ui, "seed_end", "终点", "种子终点")
                with html.Div(v_if="seed_type === 'sphere'"):
                    xyz(ui, "seed_center", "球心", "球心")
                    field(ui, "seed_radius", "半径", type="number")
                with html.Div(v_if="seed_type === 'plane'"):
                    xyz(ui, "seed_origin", "原点", "平面原点")
                    xyz(ui, "seed_normal", "法向", "平面法向")
                    field(ui, "seed_width", "宽度", type="number")
                    field(ui, "seed_height", "高度", type="number")
                select(
                    ui,
                    "seed_surface",
                    "命名面",
                    ("seed_surface_items",),
                    v_if="seed_type === 'surface' && seed_surface_items.length",
                )
                html.Span(
                    "当前没有可用命名面，可改用线段、球体或平面。",
                    v_if="seed_type === 'surface' && !seed_surface_items.length",
                    classes="phys-seed-hint",
                )
                field(ui, "seed_count", "种子数", type="number")
                field(ui, "flow_length", "积分长度", type="number")
                choices(
                    ui,
                    "flow_direction",
                    "积分方向",
                    (("both", "双向"), ("forward", "正向"), ("backward", "反向")),
                )
            with html.Div(v_if="kind === 'probe'"):
                xyz(ui, "probe_position", "空间坐标", "空间坐标")
                select(
                    ui,
                    "probe_fields",
                    "标签物理量（空为全部）",
                    ("probe_field_items",),
                    multiple=True,
                )
                with html.Div(classes="phys-probe-actions"):
                    v.VBtn(
                        "在模型上拾取位置",
                        small=True,
                        text=True,
                        color="primary",
                        click=lambda: ui.mode("probe"),
                    )
                    v.VCheckbox(
                        v_model=("probe_label",),
                        label="显示标签",
                        dense=True,
                        hide_details=True,
                        change=(ui.probe_label, "[$event]"),
                    )
            with html.Div(v_if="kind && kind !== 'probe'"):
                with row("着色变量"):
                    v.VSelect(
                        v_model=("coloring",),
                        items=("field_items",),
                        __properties=[("aria_label", "aria-label")],
                        aria_label="着色变量",
                        dense=True,
                        outlined=True,
                        hide_details=True,
                        change=(lambda x: ui.set_display("coloring", x), "[$event]"),
                    )
                    v.VSelect(
                        v_model=("component",),
                        items=("components", [{"text": "模长", "value": "magnitude"}, 0, 1, 2]),
                        __properties=[("aria_label", "aria-label")],
                        aria_label="分量",
                        dense=True,
                        outlined=True,
                        hide_details=True,
                        classes="phys-component",
                        change=(lambda x: ui.set_display("component", x), "[$event]"),
                    )
                with row("颜色映射"):
                    html.Span(
                        classes=(
                            "'phys-palette-swatch palette-' + palette.toLowerCase().replaceAll(' ', '-')",
                        )
                    )
                    v.VSelect(
                        v_model=("palette",),
                        items=(
                            "palettes",
                            [
                                "Rainbow",
                                "Jet",
                                "Turbo",
                                "Cool to Warm",
                                "viridis",
                                "plasma",
                                "gray",
                            ],
                        ),
                        __properties=[
                            ("aria_label", "aria-label"),
                            ("aria_pressed", "aria-pressed"),
                        ],
                        aria_label="颜色映射",
                        dense=True,
                        outlined=True,
                        hide_details=True,
                        change=(lambda x: ui.set_display("palette", x), "[$event]"),
                    )
                with row("显示范围"):
                    with html.Div(classes="phys-range-inputs"):
                        for key, label in [
                            ("range_min", "范围下限（空为自动）"),
                            ("range_max", "范围上限"),
                        ]:
                            v.VTextField(
                                v_model=(key,),
                                __properties=[
                                    ("aria_label", "aria-label"),
                                    ("aria_pressed", "aria-pressed"),
                                ],
                                aria_label=label,
                                placeholder="自动",
                                dense=True,
                                outlined=True,
                                hide_details=True,
                                change=(lambda value, k=key: ui.set_display(k, value), "[$event]"),
                            )
                            if key == "range_min":
                                html.Span("～")
                with row("颜色层数"):
                    v.VTextField(
                        v_model=("bands",),
                        __properties=[
                            ("aria_label", "aria-label"),
                            ("aria_pressed", "aria-pressed"),
                        ],
                        aria_label="颜色层数 2–256",
                        type="number",
                        min=2,
                        max=256,
                        dense=True,
                        outlined=True,
                        hide_details=True,
                        classes="phys-bands",
                        change=(lambda x: ui.set_display("bands", x), "[$event]"),
                    )
                    v.VCheckbox(
                        v_model=("legend",),
                        label="色标",
                        dense=True,
                        hide_details=True,
                        change=(lambda x: ui.set_display("legend", x), "[$event]"),
                    )
                    v.VSlider(
                        v_model=("opacity",),
                        __properties=[
                            ("aria_label", "aria-label"),
                            ("aria_pressed", "aria-pressed"),
                        ],
                        aria_label="不透明度",
                        min=0,
                        max=1,
                        step=0.01,
                        dense=True,
                        hide_details=True,
                        change=(lambda x: ui.set_display("opacity", x), "[$event]"),
                    )
                    html.Span("{{ Number(opacity).toFixed(3) }}", classes="phys-opacity-value")
            with html.Div(classes="phys-property-footer"):
                html.Span("{{ status_text }}", classes="phys-status")
                v.VBtn(
                    "应用",
                    v_if="kind && kind !== 'surface'",
                    color="primary",
                    small=True,
                    depressed=True,
                    click=ui.apply_selected,
                    disabled=("busy",),
                )
