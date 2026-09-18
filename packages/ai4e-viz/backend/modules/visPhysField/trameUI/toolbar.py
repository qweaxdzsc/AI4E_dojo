"""参考图的图标工具带：分析创建与活动视图显示分成两行。"""

# ruff: noqa: SIM117 - Trame 布局按 DOM 层级书写。

from trame.widgets import html
from trame.widgets import vuetify as v

from .controller import LABELS
from .icons import icon
from .timelinePanel import timeline


def tool(label, glyph, click, *, caption=False, **kwargs):
    """按钮保留明确名称、提示和选中状态，图标不代替业务操作。"""
    with v.VBtn(
        text=True,
        click=click,
        title=label,
        aria_label=label,
        __properties=[("aria_label", "aria-label"), ("aria_pressed", "aria-pressed")],
        **kwargs,
    ):
        icon(glyph)
        if caption:
            html.Span(label, classes="phys-tool-caption")


def creation_bar(ui):
    """大图标加名称的分析工具带，不创建任何占位资产。"""
    with html.Div(classes="phys-creation"):
        tools = [
            "glyph",
            "slice",
            "clip",
            "streamline",
            "isosurface",
            "contour",
            "probe",
            "plot_over_line",
        ]
        for kind in tools:
            disabled = "busy || !can_create" + (
                " || !can_vector"
                if kind in ("glyph", "streamline")
                else " || !can_iso"
                if kind == "isosurface"
                else " || !can_contour"
                if kind == "contour"
                else ""
            )
            with html.Div(classes="phys-analysis-cell"):
                tool(
                    LABELS[kind],
                    kind,
                    lambda k=kind: ui.begin(k),
                    caption=True,
                    disabled=(disabled,),
                    classes="phys-analysis-main",
                )
        with v.VMenu(offset_y=True, attach="body", allow_overflow=True):
            with v.Template(v_slot_activator="{ on, attrs }"):
                v.VBtn(
                    "更多分析", text=True, classes="phys-analysis-more", v_bind="attrs", v_on="on"
                )
            with v.VList(dense=True):
                for kind in tools:
                    disabled = "busy || !can_create" + (
                        " || !can_vector"
                        if kind in ("glyph", "streamline")
                        else " || !can_iso"
                        if kind == "isosurface"
                        else " || !can_contour"
                        if kind == "contour"
                        else ""
                    )
                    with v.VListItem(disabled=(disabled,), click=lambda k=kind: ui.begin(k)):
                        v.VListItemTitle(LABELS[kind])
        timeline(ui)
        tool(
            "动画",
            "movie",
            lambda: ui.request("animation"),
            caption=True,
            disabled=("!time_values.length",),
            classes="phys-animation",
        )


def view_bar(ui):
    """图标化相机手势与显示操作，字段选择保留独立入口。"""
    with html.Div(classes="phys-viewbar"):
        with html.Div(classes="phys-tool-group phys-navigation-tools"):
            for label, mode in [
                ("选择", "select"),
                ("旋转", "rotate"),
                ("平移", "pan"),
                ("缩放", "zoom"),
            ]:
                tool(
                    label,
                    mode,
                    lambda m=mode: ui.mode(m),
                    classes=(
                        f"interaction_mode === '{mode}' ? 'phys-tool selected' : 'phys-tool'",
                    ),
                    aria_pressed=(f"interaction_mode === '{mode}'",),
                )
            tool("适窗", "fit", ui.camera, classes="phys-tool")
            tool(
                "坐标轴",
                "axes",
                lambda: ui.view_setting("axes", not ui.server.state.axes),
                classes=("axes ? 'phys-tool toggled' : 'phys-tool'",),
                aria_pressed=("axes",),
            )
        with html.Div(classes="phys-tool-group phys-directions"):
            for label, direction in [
                ("正", "-y"),
                ("后", "+y"),
                ("左", "-x"),
                ("右", "+x"),
                ("顶", "+z"),
                ("底", "-z"),
                ("轴测", "iso"),
            ]:
                tool(
                    label,
                    "cube",
                    lambda d=direction: ui.camera(d),
                    caption=True,
                    classes="phys-direction",
                )
        with v.VMenu(offset_y=True, attach="body", allow_overflow=True):
            with v.Template(v_slot_activator="{ on, attrs }"):
                v.VBtn("视角", text=True, classes="phys-direction-more", v_bind="attrs", v_on="on")
            with v.VList(dense=True):
                for label, direction in [
                    ("正", "-y"),
                    ("后", "+y"),
                    ("左", "-x"),
                    ("右", "+x"),
                    ("顶", "+z"),
                    ("底", "-z"),
                    ("轴测", "iso"),
                ]:
                    with v.VListItem(click=lambda d=direction: ui.camera(d)):
                        v.VListItemTitle(label)
        with html.Div(classes="phys-toolbar-field"):
            icon("legend")
            v.VSelect(
                v_model=("coloring",),
                items=("field_items",),
                __properties=[("aria_label", "aria-label"), ("aria_pressed", "aria-pressed")],
                aria_label="着色物理量",
                placeholder="着色物理量",
                dense=True,
                hide_details=True,
                outlined=True,
                disabled=("!kind || kind === 'probe'",),
                change=(lambda value, identity: ui.set_display("coloring", value, identity), "[$event, selected]"),
            )
        with html.Div(classes="phys-tool-group phys-display-tools"):
            with v.VMenu(offset_y=True, attach="body", allow_overflow=True, close_on_content_click=False):
                with v.Template(v_slot_activator="{ on, attrs }"):
                    with v.VBtn(
                        text=True,
                        title="透明度",
                        __properties=[
                            ("aria_label", "aria-label"),
                            ("aria_pressed", "aria-pressed"),
                        ],
                        aria_label="透明度",
                        classes="phys-tool",
                        v_bind="attrs",
                        v_on="on",
                    ):
                        icon("opacity")
                with v.VCard(classes="pa-4", width=260):
                    v.VSlider(
                        v_model=("opacity",),
                        label="不透明度",
                        min=0,
                        max=1,
                        step=0.01,
                        thumb_label=True,
                        change=(lambda x, identity: ui.set_display("opacity", x, identity), "[$event, selected]"),
                    )
            with v.VMenu(offset_y=True, attach="body", allow_overflow=True):
                with v.Template(v_slot_activator="{ on, attrs }"):
                    with v.VBtn(
                        text=True,
                        title="显示模式",
                        __properties=[
                            ("aria_label", "aria-label"),
                            ("aria_pressed", "aria-pressed"),
                        ],
                        aria_label="显示模式",
                        classes="phys-tool",
                        v_bind="attrs",
                        v_on="on",
                    ):
                        icon("cube")
                with v.VList(dense=True):
                    for label, mode in [
                        ("表面", "surface"),
                        ("网格", "wireframe"),
                        ("表面+网格", "surface_edges"),
                        ("Surface LIC", "surface_lic"),
                    ]:
                        with v.VListItem(click=lambda m=mode: ui.set_display("display_mode", m)):
                            v.VListItemTitle(label)
            with v.VMenu(offset_y=True, attach="body", allow_overflow=True, close_on_content_click=False):
                with v.Template(v_slot_activator="{ on, attrs }"):
                    with v.VBtn(
                        text=True,
                        title="光照设置",
                        __properties=[
                            ("aria_label", "aria-label"),
                            ("aria_pressed", "aria-pressed"),
                        ],
                        aria_label="光照设置",
                        classes="phys-tool",
                        v_bind="attrs",
                        v_on="on",
                    ):
                        icon("light")
                with v.VCard(classes="pa-4", width=230):
                    v.VCheckbox(
                        v_model=("lighting",),
                        label="光照",
                        dense=True,
                        hide_details=True,
                        change=(lambda x, identity: ui.set_display("lighting", x, identity), "[$event, selected]"),
                    )
                    v.VCheckbox(
                        v_model=("shadows",),
                        label="阴影",
                        dense=True,
                        hide_details=True,
                        disabled=("!can_shadow",),
                        title="默认关闭，与 ParaView 一致；仅 Linux 远程可开",
                        change=(lambda x: ui.view_setting("shadows", x), "[$event]"),
                    )
