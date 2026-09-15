"""单 Layout 多窗体：每个窗口左上角是标签，新增标签即新增窗口。"""

# ruff: noqa: SIM117 - Trame 布局按 DOM 层级书写，保持窗体与标签嵌套。
from trame.widgets import html, vtk
from trame.widgets import vuetify as v


def viewport_grid(ui):
    """窗口与标签叠在同一位置；工具条只保留全体相机联动和增减。"""
    with html.Div(classes="phys-window-toolbar"):
        with v.VBtn(
            icon=True,
            small=True,
            title="新建窗口",
            disabled=("view_items.length >= 4",),
            click=lambda: ui.view_action("view_create"),
        ):
            v.VIcon("mdi-plus")
        v.VCheckbox(
            v_model=("link_cameras",),
            label="相机联动",
            dense=True,
            hide_details=True,
            change=(ui.link, "[$event]"),
        )
        for title, icon, direction in [
            ("左右分割", "mdi-view-split-vertical", "horizontal"),
            ("上下分割", "mdi-view-split-horizontal", "vertical"),
        ]:
            with v.VBtn(
                icon=True,
                small=True,
                title=title,
                disabled=("view_items.length >= 4",),
                click=lambda d=direction: ui.view_action("view_create", d),
            ):
                v.VIcon(icon)
        with v.VMenu(offset_y=True, attach="body", allow_overflow=True, close_on_content_click=False):
            with v.Template(v_slot_activator="{ on, attrs }"):
                v.VBtn(
                    "比例",
                    text=True,
                    x_small=True,
                    v_bind="attrs",
                    v_on="on",
                    disabled=("view_items.length === 1",),
                )
            with v.VCard(classes="pa-3", width=240):
                v.VSlider(
                    v_model=("ratio",),
                    label="当前分割比例",
                    min=0.1,
                    max=0.9,
                    step=0.05,
                    thumb_label=True,
                    change=(ui.layout_ratio, "[$event]"),
                )
        with v.VBtn(icon=True, small=True, title="最大化 / 恢复", click=ui.maximize):
            v.VIcon("mdi-fullscreen")
    with html.Div(
        classes="phys-viewport",
        id="phys-viewport",
        mousedown=(
            ui.plane_press,
            "[$event.offsetX/$event.currentTarget.clientWidth,1-$event.offsetY/$event.currentTarget.clientHeight,$event.currentTarget.clientWidth,$event.currentTarget.clientHeight]",
        ),
        mousemove=(
            ui.plane_move,
            "[$event.offsetX/$event.currentTarget.clientWidth,1-$event.offsetY/$event.currentTarget.clientHeight,$event.currentTarget.clientWidth,$event.currentTarget.clientHeight]",
        ),
        mouseup=ui.plane_release,
        click=(
            ui.pick_screen,
            "[$event.offsetX/$event.currentTarget.clientWidth,1-$event.offsetY/$event.currentTarget.clientHeight,$event.currentTarget.clientWidth,$event.currentTarget.clientHeight]",
        ),
    ):
        common = {"ref": "physical_view", "style": "width:100%;height:100%"}
        if ui.scene.spec.get("renderer") == "remote":
            ui.view = vtk.VtkRemoteView(
                ui.scene.window,
                interactive_ratio=1,
                interactor_events=("remote_events", ["EndAnimation"]),
                EndAnimation=ui.remote_end,
                **common,
            )
        else:
            with vtk.VtkLocalView(
                ui.scene.window,
                interactor_settings=(
                    "interaction_settings",
                    [
                        {"button": 1, "action": "Rotate"},
                        {"button": 2, "action": "Pan"},
                        {"button": 3, "action": "Zoom", "scrollEnabled": True},
                    ],
                ),
                picking_modes=("picking_modes", []),
                after_scene_loaded="window.dispatchEvent(new Event('phys-scene-ready'))",
                interactor_events=("events", ["EndAnimation"]),
                **common,
            ) as local_view:
                from trame_client.widgets.core import AbstractElement

                AbstractElement(
                    "phys-camera-tracker",
                    view_ids=("view_ids",),
                    cameras=("render_cameras",),
                    plane_widget=("plane_widget",),
                    camera_change=(ui.camera_event, "[$event]"),
                    view_resize=(ui.resize, "[$event]"),
                    plane_press=(
                        ui.plane_press,
                        "[$event.x,$event.y,$event.width,$event.height]",
                    ),
                    plane_move=(
                        ui.plane_move,
                        "[$event.x,$event.y,$event.width,$event.height]",
                    ),
                    plane_release=ui.plane_release,
                    __properties=[
                        ("view_ids", "viewIds"),
                        "cameras",
                        ("plane_widget", "planeWidget"),
                    ],
                    __events=[
                        ("camera_change", "camera-change"),
                        ("view_resize", "view-resize"),
                        ("plane_press", "plane-press"),
                        ("plane_move", "plane-move"),
                        ("plane_release", "plane-release"),
                    ],
                )
            ui.view = local_view
        with html.Div(classes="phys-window-layer"):
            with html.Div(
                v_for="frame in view_frames",
                key="frame.id",
                classes=(
                    "frame.id === active_view ? 'phys-window is-active' : 'phys-window'",
                ),
                style=("frame.css",),
            ):
                with html.Div(
                    classes=(
                        "frame.id === active_view ? 'phys-tab active' : 'phys-tab'",
                    ),
                ):
                    html.Span("{{ frame.name }}", click=(ui.view_select, "[frame.id]"))
                    with v.VBtn(
                        icon=True,
                        x_small=True,
                        title="关闭窗口",
                        disabled=("view_items.length === 1",),
                        click=(
                            lambda identity: (
                                ui.view_select(identity),
                                ui.view_action("view_close"),
                            ),
                            "[frame.id]",
                        ),
                    ):
                        v.VIcon("mdi-close", small=True)
