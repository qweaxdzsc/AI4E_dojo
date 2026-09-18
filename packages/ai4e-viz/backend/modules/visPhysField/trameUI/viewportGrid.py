"""单 Layout 多窗体：每个窗口左上角是标签，新增标签即新增窗口。"""

# ruff: noqa: SIM117 - Trame 布局按 DOM 层级书写，保持窗体与标签嵌套。
from trame.widgets import html, vtk
from trame.widgets import vuetify as v


def viewport_grid(ui):
    """窗口与标签叠在同一位置；工具条只保留全体相机联动和增减。"""
    with html.Div(classes="phys-window-toolbar", id="phys-window-toolbar"):
        with v.VMenu(offset_y=True, close_on_content_click=False):
            with v.Template(v_slot_activator="{ on, attrs }"):
                v.VBtn("视图设置", text=True, small=True, v_bind="attrs", v_on="on")
            with v.VCard(style="padding:12px;min-width:220px"):
                v.VTextField(
                    label="背景颜色",
                    v_model=("background_hex", "#24364a"),
                    type="color",
                    hide_details=True,
                    input=(ui.set_background, "[$event]"),
                )
                v.VBtn(
                    "恢复默认背景",
                    text=True,
                    small=True,
                    click=lambda: ui.set_background("#24364a"),
                )
        with v.VMenu(offset_y=True, attach="#phys-window-toolbar", allow_overflow=True):
            with v.Template(v_slot_activator="{ on, attrs }"):
                with v.VBtn(
                    icon=True,
                    small=True,
                    title="新建窗口",
                    disabled=("view_items.length >= 4",),
                    v_bind="attrs",
                    v_on="on",
                ):
                    v.VIcon("mdi-plus")
            with v.VList(dense=True):
                with v.VListItem(click=lambda: ui.view_action("view_create", view_type="render")):
                    v.VListItemTitle("三维渲染")
                with v.VListItem(
                    click=lambda: ui.view_action("view_create", view_type="line_chart")
                ):
                    v.VListItemTitle("折线图")
        v.VCheckbox(
            v_model=("link_cameras",),
            label="相机联动",
            dense=True,
            hide_details=True,
            change=(ui.link, "[$event]"),
        )
        html.Span(
            "{{ link_notice }}",
            classes="text-caption phys-link-notice",
            v_show="link_notice",
        )
        for title, icon, direction in [
            ("左右分割", "mdi-view-split-vertical", "horizontal"),
            ("上下分割", "mdi-view-split-horizontal", "vertical"),
        ]:
            with v.VMenu(offset_y=True, attach="#phys-window-toolbar", allow_overflow=True):
                with v.Template(v_slot_activator="{ on, attrs }"):
                    with v.VBtn(
                        icon=True,
                        small=True,
                        title=title,
                        disabled=("view_items.length >= 4",),
                        v_bind="attrs",
                        v_on="on",
                    ):
                        v.VIcon(icon)
                with v.VList(dense=True):
                    with v.VListItem(
                        click=lambda d=direction: ui.view_action("view_create", d, view_type="render")
                    ):
                        v.VListItemTitle("三维渲染")
                    with v.VListItem(
                        click=lambda d=direction: ui.view_action(
                            "view_create", d, view_type="line_chart"
                        )
                    ):
                        v.VListItemTitle("折线图")
        with v.VMenu(
            offset_y=True,
            attach="#phys-window-toolbar",
            allow_overflow=True,
            close_on_content_click=False,
        ):
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
        classes=("['phys-viewport', remote_handoff ? 'phys-remote-handoff' : '']",),
        id="phys-viewport",
        click=(
            ui.pick_screen,
            "[$event.offsetX/$event.currentTarget.clientWidth,1-$event.offsetY/$event.currentTarget.clientHeight,$event.currentTarget.clientWidth,$event.currentTarget.clientHeight]",
        ),
    ):
        common = {"style": "width:100%;height:100%"}
        with html.Div(
            style=(
                "use_remote_view ? 'display:none;width:100%;height:100%' : 'width:100%;height:100%'",
            )
        ):
            with vtk.VtkLocalView(
                ui.scene.window,
                ref="physical_local_view",
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
                interaction_tracker(ui)
            ui.local_view = local_view
        with html.Div(
            style=(
                "use_remote_view ? 'width:100%;height:100%' : 'display:none;width:100%;height:100%'",
            )
        ):
            ui.remote_view = vtk.VtkRemoteView(
                ui.scene.window,
                ref="physical_remote_view",
                interactive_ratio=1,
                interactor_events=("remote_events", ["EndAnimation"]),
                EndAnimation=ui.remote_end,
                **common,
            )
            interaction_tracker(ui)
        persisted_remote = ui.scene.spec.get("renderer") == "remote"
        ui.server.state.use_remote_view = persisted_remote
        ui.server.state.remote_ready = persisted_remote
        ui.server.state.remote_handoff = False
        ui.view = ui.remote_view if persisted_remote else ui.local_view
        with html.Div(classes="phys-window-layer"):
            with html.Div(
                v_for="frame in view_frames",
                key="frame.id",
                classes=(
                    "(frame.id === active_view ? 'phys-window is-active' : 'phys-window') + (frame.view_type === 'line_chart' ? ' is-chart' : '')",
                ),
                style=("frame.css",),
            ):
                with html.Div(
                    classes=("frame.id === active_view ? 'phys-tab active' : 'phys-tab'",),
                ):
                    html.Span("{{ frame.name }}", click=(ui.activate_view, "[frame.id]"))
                    with v.VBtn(
                        icon=True,
                        x_small=True,
                        title="关闭窗口",
                        disabled=("view_items.length === 1",),
                        click=(
                            lambda identity: (
                                ui.activate_view(identity),
                                ui.view_action("view_close"),
                            ),
                            "[frame.id]",
                        ),
                    ):
                        v.VIcon("mdi-close", small=True)
                with html.Div(
                    v_if="frame.view_type === 'line_chart'",
                    classes="phys-line-chart-view",
                    click=(ui.activate_view, "[frame.id]"),
                ):
                    html.Div(
                        v_if="frame.has_chart",
                        v_html=("frame.chart_html",),
                        classes="phys-line-chart-canvas",
                    )
                    html.Div(
                        "选择线段提取对象并应用后，将在此显示折线图",
                        v_if="!frame.has_chart",
                        classes="phys-line-chart-empty",
                    )
                    v.VBtn(
                        "导出 CSV",
                        v_if="frame.has_chart",
                        small=True,
                        text=True,
                        classes="phys-line-chart-export",
                        click=(ui.export_chart_view, "[frame.id]"),
                    )


def interaction_tracker(ui):
    """本地和远程共享指针捕获、命中和事件身份。"""
    from trame_client.widgets.core import AbstractElement

    AbstractElement(
        "phys-camera-tracker",
        view_ids=("view_ids",),
        cameras=("render_cameras",),
        plane_widget=("plane_widget",),
        plane_dragging=("plane_dragging",),
        wheel_zooming=("wheel_zooming", False),
        camera_navigating=("camera_navigating", False),
        remote_handoff=("remote_handoff", False),
        use_remote_view=("use_remote_view", False),
        remote_ready=("remote_ready", False),
        camera_change=(ui.camera_event, "[$event]"),
        view_activate=(ui.activate_view, "[$event]"),
        view_resize=(ui.resize, "[$event]"),
        wheel_zoom=(ui.wheel_zoom, "[$event]"),
        camera_navigate=(ui.camera_navigate, "[$event]"),
        plane_press=(
            ui.plane_press,
            "[$event.x,$event.y,$event.width,$event.height,$event.identity,$event.token,$event.handle,$event.view]",
        ),
        plane_move=(
            ui.plane_move,
            "[$event.x,$event.y,$event.width,$event.height,$event.identity,$event.token]",
        ),
        plane_release=(ui.plane_release, "[$event.identity,$event.token]"),
        plane_hover=(ui.plane_hover, "[$event.handle,$event.identity]"),
        __properties=[
            ("view_ids", "viewIds"),
            "cameras",
            ("plane_widget", "planeWidget"),
            ("plane_dragging", "planeDragging"),
            ("wheel_zooming", "wheelZooming"),
            ("camera_navigating", "cameraNavigating"),
            ("remote_handoff", "remoteHandoff"),
            ("use_remote_view", "useRemoteView"),
            ("remote_ready", "remoteReady"),
        ],
        __events=[
            ("camera_change", "camera-change"),
            ("view_activate", "view-activate"),
            ("view_resize", "view-resize"),
            ("wheel_zoom", "wheel-zoom"),
            ("camera_navigate", "camera-navigate"),
            ("plane_press", "plane-press"),
            ("plane_move", "plane-move"),
            ("plane_release", "plane-release"),
            ("plane_hover", "plane-hover"),
        ],
    )
