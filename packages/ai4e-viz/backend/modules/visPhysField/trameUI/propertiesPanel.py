"""与参考图对齐的紧凑属性行；坐标三分量独立输入，计算仍需应用。"""

# ruff: noqa: SIM117 - Trame 布局按 DOM 层级书写。

from trame.widgets import html
from trame.widgets import vuetify as v

from .icons import icon


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
            change=(
                lambda value, identity: ui.set_parameter(key, value, identity),
                "[$event, selected]",
            ),
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
                    # 等待最终拖动位置提交，避免晚到的拖动回填覆盖刚输入的坐标。
                    disabled=("plane_dragging !== ''",),
                    dense=True,
                    outlined=True,
                    hide_details=True,
                    change=(
                        lambda value, identity, i=index: ui.set_coordinate(key, i, value, identity),
                        "[$event, selected]",
                    ),
                )


def choices(ui, key, label, items, *, display=False):
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
                    click=(
                        lambda identity, selected=value: (
                            ui.edit_display(key, selected, identity)
                            if display
                            else ui.set_parameter(key, selected, identity)
                        ),
                        "[selected]",
                    ),
                )


def select(ui, key, label, items, *, display=False, chart=False, **kwargs):
    """计算、显示或折线图轴分别编辑。"""
    condition = kwargs.pop("v_if", "true")
    with row(label, v_if=condition):
        v.VSelect(
            v_model=(key,),
            items=items,
            __properties=[("aria_label", "aria-label"), ("aria_pressed", "aria-pressed")],
            aria_label=label,
            dense=True,
            outlined=True,
            hide_details=True,
            change=(
                lambda value, identity: (
                    ui.set_chart_axis(key, value, identity)
                    if chart
                    else ui.edit_display(key, value, identity)
                    if display
                    else ui.set_parameter(key, value, identity)
                ),
                "[$event, selected]",
            ),
            **kwargs,
        )


def legend_popup(ui):
    """色标属于当前对象；打开时回填该对象，点应用才写入。"""
    with v.VMenu(
        offset_y=True,
        left=True,
        allow_overflow=True,
        close_on_content_click=False,
        content_class="phys-legend-popup",
    ):
        with v.Template(v_slot_activator="{ on, attrs }"):
            with v.VBtn(
                icon=True,
                small=True,
                text=True,
                title="色标",
                classes="phys-legend-trigger",
                __properties=[
                    ("aria_label", "aria-label"),
                    ("aria_pressed", "aria-pressed"),
                ],
                aria_label="色标",
                aria_pressed=("legend",),
                disabled=("!kind || kind === 'probe'",),
                v_bind="attrs",
                v_on="on",
                click=(ui.prepare_legend, "[selected]"),
            ):
                icon("legend")
        with v.VCard(classes="phys-legend-menu", width=268, outlined=True, elevation=0):
            html.Div("色标 · {{ object_name }}", classes="phys-legend-heading")
            with row("显示色标"):
                v.VCheckbox(
                    v_model=("legend",),
                    dense=True,
                    hide_details=True,
                    change=(
                        lambda x, identity: ui.edit_display("legend", x, identity),
                        "[$event, selected]",
                    ),
                )
            with row("方向"):
                with html.Div(classes="phys-choice"):
                    for value, text in (("vertical", "纵向"), ("horizontal", "横向")):
                        v.VBtn(
                            text,
                            small=True,
                            outlined=True,
                            depressed=(f"legend_orientation === '{value}'",),
                            __properties=[
                                ("aria_label", "aria-label"),
                                ("aria_pressed", "aria-pressed"),
                            ],
                            aria_label=f"方向 {text}",
                            click=(
                                lambda identity, selected=value: ui.edit_display(
                                    "legend_orientation", selected, identity
                                ),
                                "[selected]",
                            ),
                        )
            with row("长度比例"):
                v.VTextField(
                    v_model=("legend_length",),
                    type="number",
                    dense=True,
                    outlined=True,
                    hide_details=True,
                    aria_label="长度比例",
                    change=(
                        lambda x, identity: ui.edit_display(
                            "legend_length", x, identity
                        ),
                        "[$event, selected]",
                    ),
                )
            with row("厚度"):
                v.VTextField(
                    v_model=("legend_thickness",),
                    type="number",
                    dense=True,
                    outlined=True,
                    hide_details=True,
                    aria_label="厚度",
                    change=(
                        lambda x, identity: ui.edit_display(
                            "legend_thickness", x, identity
                        ),
                        "[$event, selected]",
                    ),
                )
            with row("标题字号"):
                v.VTextField(
                    v_model=("legend_title_size",),
                    type="number",
                    dense=True,
                    outlined=True,
                    hide_details=True,
                    aria_label="标题字号",
                    change=(
                        lambda x, identity: ui.edit_display(
                            "legend_title_size", x, identity
                        ),
                        "[$event, selected]",
                    ),
                )
            with row("刻度字号"):
                v.VTextField(
                    v_model=("legend_label_size",),
                    type="number",
                    dense=True,
                    outlined=True,
                    hide_details=True,
                    aria_label="刻度字号",
                    change=(
                        lambda x, identity: ui.edit_display(
                            "legend_label_size", x, identity
                        ),
                        "[$event, selected]",
                    ),
                )
            with row("位置"):
                v.VSelect(
                    v_model=("legend_position",),
                    items=(
                        [
                            {"text": "右侧", "value": "right"},
                            {"text": "左侧", "value": "left"},
                            {"text": "顶部", "value": "top"},
                            {"text": "底部", "value": "bottom"},
                            {"text": "自定义", "value": "custom"},
                        ],
                    ),
                    dense=True,
                    outlined=True,
                    hide_details=True,
                    aria_label="位置",
                    change=(
                        lambda x, identity: ui.edit_display(
                            "legend_position", x, identity
                        ),
                        "[$event, selected]",
                    ),
                )
            with row("位置 X", v_if="legend_position === 'custom'"):
                v.VTextField(
                    v_model=("legend_x",),
                    type="number",
                    dense=True,
                    outlined=True,
                    hide_details=True,
                    aria_label="位置 X",
                    change=(
                        lambda x, identity: ui.edit_display("legend_x", x, identity),
                        "[$event, selected]",
                    ),
                )
            with row("位置 Y", v_if="legend_position === 'custom'"):
                v.VTextField(
                    v_model=("legend_y",),
                    type="number",
                    dense=True,
                    outlined=True,
                    hide_details=True,
                    aria_label="位置 Y",
                    change=(
                        lambda x, identity: ui.edit_display("legend_y", x, identity),
                        "[$event, selected]",
                    ),
                )
            with html.Div(classes="phys-legend-actions"):
                v.VBtn(
                    "取消",
                    small=True,
                    text=True,
                    click=(ui.cancel_legend, "[selected]"),
                )
                v.VBtn(
                    "应用",
                    small=True,
                    color="primary",
                    depressed=True,
                    click=(ui.apply_legend, "[selected]"),
                    disabled=("busy || !kind || kind === 'probe'",),
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
            html.Div("计算参数", classes="phys-section-title", v_if="kind && kind !== 'surface'")
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
                v.VCheckbox(
                    v_model=("crinkle_slice",),
                    label="皱折切面",
                    dense=True,
                    hide_details=True,
                    change=(lambda x: ui.set_parameter("crinkle_slice", x), "[$event]"),
                )
                v.VCheckbox(
                    v_if="kind === 'slice'",
                    v_model=("triangulate_slice",),
                    label="三角化切面",
                    dense=True,
                    hide_details=True,
                    change=(lambda x: ui.set_parameter("triangulate_slice", x), "[$event]"),
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
            with html.Div(v_if="kind === 'contour'"):
                field(ui, "level_count", "等值级别数", type="number", min=1, max=256)
                field(ui, "level_min", "范围下限", placeholder="自动")
                field(ui, "level_max", "范围上限", placeholder="自动")
            with html.Div(v_if="kind === 'isosurface'"):
                with row("等值滑条"):
                    v.VSlider(
                        v_model=("iso_slider",),
                        min=("iso_field_min",),
                        max=("iso_field_max",),
                        step=0,
                        dense=True,
                        hide_details=True,
                        thumb_label=True,
                        __properties=[
                            ("aria_label", "aria-label"),
                            ("aria_pressed", "aria-pressed"),
                        ],
                        aria_label="等值滑条，范围为当前物理量",
                        change=(lambda value: ui.set_iso_slider(value), "[$event]"),
                    )
                html.Div("{{ iso_range_text }}", classes="text-caption", v_if="iso_range_text")
                html.Div(
                    "{{ iso_range_hint }}",
                    classes="text-caption error--text",
                    v_if="iso_range_hint",
                )
                field(ui, "iso_values", "等值（可越界）")
            with html.Div(v_if="kind === 'plot_over_line'"):
                xyz(ui, "line_start", "起点", "线段起点")
                xyz(ui, "line_end", "终点", "线段终点")
                field(ui, "line_resolution", "分辨率", type="number", min=2, max=20000)
                html.Div("折线图显示", classes="phys-section-title")
                select(
                    ui,
                    "chart_x_array",
                    "X 轴",
                    ("chart_x_items",),
                    chart=True,
                )
                select(
                    ui,
                    "chart_y_arrays",
                    "Y 轴物理量",
                    ("chart_y_items",),
                    chart=True,
                    multiple=True,
                )
            with html.Div(v_if="kind === 'glyph'"):
                choices(
                    ui,
                    "glyph_shape",
                    "符号形状",
                    (("arrow", "箭头"), ("cone", "圆锥"), ("line", "线段")),
                )
                choices(
                    ui,
                    "glyph_scale_mode",
                    "大小方式",
                    (("constant", "固定"), ("quantity", "物理量")),
                )
                select(
                    ui,
                    "glyph_scale_field",
                    "大小物理量",
                    ("scale_field_items",),
                    v_if="glyph_scale_mode === 'quantity'",
                )
                field(ui, "vector_scale", "箭头比例", type="number")
                choices(
                    ui,
                    "glyph_sampling",
                    "采样方式",
                    (("nodes", "节点间隔"), ("spatial", "空间均匀")),
                )
                with html.Div(v_if="glyph_sampling === 'nodes'"):
                    field(ui, "vector_stride", "采样间隔", type="number")
                with html.Div(v_if="glyph_sampling === 'spatial'"):
                    field(ui, "glyph_spacing", "空间间距", type="number")
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
                v.VBtn(
                    "{{ seed_preview ? '隐藏预览' : '预览种子' }}",
                    v_if="can_preview_seeds",
                    small=True,
                    outlined=True,
                    color="primary",
                    classes="phys-preview-button",
                    click=ui.toggle_seed_preview,
                )
                v.VCheckbox(
                    v_if="!can_preview_seeds",
                    v_model=("seeds_visible", True),
                    label="显示种子",
                    dense=True,
                    hide_details=True,
                    change=(
                        lambda value, identity: ui.set_display("seeds_visible", value, identity),
                        "[$event, selected]",
                    ),
                )
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
                with row("点选拾取"):
                    with html.Div(classes="phys-probe-pick"):
                        v.VSwitch(
                            v_model=("probe_pick_enabled", False),
                            dense=True,
                            hide_details=True,
                            inset=True,
                            color="primary",
                            __properties=[
                                ("aria_label", "aria-label"),
                                ("aria_pressed", "aria-pressed"),
                            ],
                            aria_label="点选拾取",
                            aria_pressed=("probe_pick_enabled",),
                            change=(ui.set_probe_pick, "[$event]"),
                        )
                with html.Div(classes="phys-probe-actions"):
                    v.VCheckbox(
                        v_model=("probe_label",),
                        label="显示标签",
                        dense=True,
                        hide_details=True,
                        change=(ui.probe_label, "[$event]"),
                    )
            with html.Div(
                classes="phys-section-title phys-legend-section",
                v_if="kind && kind !== 'probe'",
            ):
                html.Span("显示设置")
                legend_popup(ui)
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
                        change=(
                            lambda x, identity: ui.edit_display("coloring", x, identity),
                            "[$event, selected]",
                        ),
                    )
                    v.VSelect(
                        v_model=("component",),
                        items=("components", [{"text": "模长", "value": "magnitude"}, 0, 1, 2]),
                        v_if="coloring",
                        __properties=[("aria_label", "aria-label")],
                        aria_label="分量",
                        dense=True,
                        outlined=True,
                        hide_details=True,
                        classes="phys-component",
                        change=(
                            lambda x, identity: ui.edit_display("component", x, identity),
                            "[$event, selected]",
                        ),
                    )
                with row("颜色", v_if="!coloring"):
                    v.VTextField(
                        v_model=("solid_color",),
                        __properties=[("aria_label", "aria-label")],
                        aria_label="纯色",
                        type="color",
                        dense=True,
                        outlined=True,
                        hide_details=True,
                        classes="phys-solid-color",
                        change=(
                            lambda x, identity: ui.edit_display("solid_color", x, identity),
                            "[$event, selected]",
                        ),
                    )
                with html.Div(v_if="coloring"):
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
                            change=(
                                lambda x, identity: ui.edit_display("palette", x, identity),
                                "[$event, selected]",
                            ),
                        )
                    with row("范围模式"):
                        v.VSelect(
                            v_model=("range_mode",),
                            __properties=[("aria_label", "aria-label")],
                            aria_label="范围模式",
                            items=(
                                [
                                    {"text": "自动", "value": "automatic"},
                                    {"text": "自定义", "value": "custom"},
                                ],
                            ),
                            dense=True,
                            outlined=True,
                            hide_details=True,
                            change=(
                                lambda value, identity: ui.edit_display(
                                    "range_mode", value, identity
                                ),
                                "[$event, selected]",
                            ),
                        )
                    with row("自动范围", v_if="range_mode === 'automatic'"):
                        html.Span("{{ automatic_range_text }}", classes="phys-range-value")
                    with row("显示范围", v_if="range_mode === 'custom'"):
                        with html.Div(classes="phys-range-inputs"):
                            for key, label in [
                                ("range_min", "范围下限"),
                                ("range_max", "范围上限"),
                            ]:
                                v.VTextField(
                                    v_model=(key,),
                                    __properties=[
                                        ("aria_label", "aria-label"),
                                        ("aria_pressed", "aria-pressed"),
                                    ],
                                    aria_label=label,
                                    dense=True,
                                    outlined=True,
                                    hide_details=True,
                                    change=(
                                        lambda value, identity, k=key: ui.edit_display(
                                            k, value, identity
                                        ),
                                        "[$event, selected]",
                                    ),
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
                            change=(
                                lambda x, identity: ui.edit_display("bands", x, identity),
                                "[$event, selected]",
                            ),
                        )
                with row("透明度"):
                    v.VSlider(
                        v_model=("opacity",),
                        __properties=[
                            ("aria_label", "aria-label"),
                            ("aria_pressed", "aria-pressed"),
                        ],
                        aria_label="透明度",
                        min=0,
                        max=1,
                        step=0.01,
                        dense=True,
                        hide_details=True,
                        change=(
                            lambda x, identity: ui.edit_display("opacity", x, identity),
                            "[$event, selected]",
                        ),
                    )
                    html.Span("{{ Number(opacity).toFixed(3) }}", classes="phys-opacity-value")
                with html.Div(v_if="display_mode === 'surface_lic'"):
                    html.Div("Surface LIC", classes="phys-section-title")
                    field(ui, "lic_steps", "步数", type="number")
                    field(ui, "lic_step_size", "步长", type="number")
                    field(ui, "lic_intensity", "LIC 强度", type="number")
                    v.VCheckbox(
                        v_model=("lic_enhanced", True),
                        label="增强 LIC",
                        dense=True,
                        hide_details=True,
                        change=(
                            lambda value, identity: ui.set_display("lic_enhanced", value, identity),
                            "[$event, selected]",
                        ),
                    )
                    choices(
                        ui,
                        "lic_contrast",
                        "对比增强",
                        (("off", "关"), ("lic", "LIC"), ("color", "颜色"), ("both", "两者")),
                    )
                    choices(
                        ui,
                        "lic_color_mode",
                        "颜色模式",
                        (("blend", "混合"), ("lic", "LIC")),
                    )
                with row("线宽", v_if="kind === 'contour'"):
                    v.VTextField(
                        v_model=("line_width",),
                        __properties=[("aria_label", "aria-label")],
                        aria_label="线宽",
                        type="number",
                        min=1,
                        max=20,
                        dense=True,
                        outlined=True,
                        hide_details=True,
                        change=(
                            lambda x, identity: ui.edit_display("line_width", x, identity),
                            "[$event, selected]",
                        ),
                    )
                with html.Div(v_if="kind === 'streamline'"):
                    choices(
                        ui,
                        "streamline_shape",
                        "形状",
                        (("line", "线"), ("tube", "圆管")),
                        display=True,
                    )
                    with row("粗细"):
                        v.VTextField(
                            v_model=("streamline_thickness",),
                            __properties=[("aria_label", "aria-label")],
                            aria_label="流线粗细",
                            type="number",
                            min=0.001,
                            dense=True,
                            outlined=True,
                            hide_details=True,
                            change=(
                                lambda x, identity: ui.edit_display(
                                    "streamline_thickness", x, identity
                                ),
                                "[$event, selected]",
                            ),
                        )
                    html.Div(
                        "线为像素线宽，部分 OpenGL 上限为 1；更粗请改圆管。圆管粗细为模型坐标半径。",
                        classes="text-caption",
                    )
                    with row("圆的面数", v_if="streamline_shape === 'tube'"):
                        v.VTextField(
                            v_model=("streamline_sides",),
                            __properties=[("aria_label", "aria-label")],
                            aria_label="圆管圆周面数 3–64",
                            type="number",
                            min=3,
                            max=64,
                            dense=True,
                            outlined=True,
                            hide_details=True,
                            change=(
                                lambda x, identity: ui.edit_display(
                                    "streamline_sides", x, identity
                                ),
                                "[$event, selected]",
                            ),
                        )
            with html.Div(v_if="kind === 'slice' || kind === 'clip'"):
                html.Div("辅助显示", classes="phys-section-title")
                v.VCheckbox(
                    v_model=("plane_visible", True),
                    label="显示辅助平面",
                    dense=True,
                    hide_details=True,
                    change=(
                        lambda value, identity: ui.set_display("plane_visible", value, identity),
                        "[$event, selected]",
                    ),
                )
            with html.Div(classes="phys-property-footer"):
                v.VBtn("取消修改", v_if="pending", small=True, text=True, click=ui.cancel_selected)
                html.Span("{{ status_text }}", classes="phys-status")
                v.VBtn(
                    "应用",
                    v_if="kind",
                    color="primary",
                    small=True,
                    depressed=True,
                    click=ui.apply_selected,
                    disabled=("busy",),
                )
