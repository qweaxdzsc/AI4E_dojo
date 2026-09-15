"""旧示例服务兼容入口；仅显式启动时创建九类场景。"""
import asyncio
from trame.app import get_server
from trame.ui.vuetify2 import SinglePageLayout
from trame.widgets import html, vuetify2
from trame_client.widgets import trame
from trame_vtk.widgets.vtk import VtkLocalView
from trame_server.utils import asynchronous
from .exampleScenes import *
from .exampleScenes import _ensure_data


def main():
    """保留原九类示例界面，导入模块不会启动场景或全局播放。"""
    # ---------------------------------------------------------------- server
    _ensure_data()
    print("[trame] building scenes (client-side rendering)…", flush=True)
    MILLER_ANIMATION = build_miller_field_scene()
    SCENES = {
        "raster": build_raster_scene(),
        "raster_vector": build_raster_vector_scene(),
        "volume": build_volume_scene(),
        "volume_vector": build_volume_vector_scene(),
        "field": build_field_scene(),
        "field_vector": build_field_vector_scene(),
        "miller_field": MILLER_ANIMATION.render_window,
        "points": build_points_scene(),
        "trajectory": build_trajectory_scene(),
    }
    print("[trame] scenes ready", flush=True)

    server = get_server(client_type="vue2")
    state, ctrl = server.state, server.controller
    state.trame__title = "AI4E VizReport · trame 3D"
    state.setdefault("view", "volume")
    state.setdefault("view_ready", False)
    state.setdefault("miller_frame", MILLER_ANIMATION.current_frame)
    state.setdefault("miller_playing", False)
    state.setdefault("miller_speed", 1.0)
    state.setdefault("miller_loop", True)
    state.setdefault("miller_time", float(MILLER_ANIMATION.times[MILLER_ANIMATION.current_frame]))
    state.setdefault("miller_frame_count", MILLER_ANIMATION.frame_count)
    state.setdefault("miller_fps", MILLER_ANIMATION.fps)
    # `view` belongs to a browser tab, not to the shared Python server state.  The
    # stock trame client keeps URL parameters in the wslink connection config; it
    # does not merge arbitrary parameters into application state.  Marking this
    # key client-only prevents different cases opened in multiple tabs from
    # changing each other's active scene.
    state.client_only("view", "view_ready")


    def _push_miller_frame(index):
        meta = MILLER_ANIMATION.set_frame(index)
        with state:
            state.miller_frame = meta["index"]
            state.miller_time = meta["time"]
            state.miller_minimum = meta["minimum"]
            state.miller_maximum = meta["maximum"]
        ctrl.miller_field_view_update()


    @state.change("miller_frame")
    def on_miller_frame(miller_frame, **_kwargs):
        """响应前端帧定位并原位更新Miller标量。"""

        _push_miller_frame(miller_frame)


    MILLER_PLAY_TOKEN = 0
    MILLER_PLAY_TASK = None
    MILLER_PLAY_ACTIVE = False
    MILLER_PLAY_SPEED = 1.0
    MILLER_PLAY_LOOP = True


    @state.change("miller_speed")
    def on_miller_speed(miller_speed, **_kwargs):
        """响应Miller时序播放速度变化。"""

        global MILLER_PLAY_SPEED

        MILLER_PLAY_SPEED = max(0.25, min(4.0, float(miller_speed or 1.0)))


    @state.change("miller_loop")
    def on_miller_loop(miller_loop, **_kwargs):
        """响应Miller时序循环播放开关。"""

        global MILLER_PLAY_LOOP

        MILLER_PLAY_LOOP = bool(miller_loop)


    async def _play_miller_field(token):
        global MILLER_PLAY_ACTIVE

        loop = asyncio.get_running_loop()
        last_tick = loop.time()
        frame_fraction = 0.0
        # Trame scopes state reads to the active websocket callback.  Once this
        # coroutine crosses an await it may otherwise see the server's default
        # state rather than the session that pressed Play.  The scene is already a
        # single shared VTK object, so keep its playback clock server-side and use
        # Trame state only to publish the result.
        while MILLER_PLAY_ACTIVE and token == MILLER_PLAY_TOKEN:
            await asyncio.sleep(0.02)
            if not MILLER_PLAY_ACTIVE or token != MILLER_PLAY_TOKEN:
                break
            now = loop.time()
            frame_fraction += max(0.0, now - last_tick) * MILLER_ANIMATION.fps * MILLER_PLAY_SPEED
            last_tick = now
            advance = int(frame_fraction)
            if advance < 1:
                continue
            frame_fraction -= advance
            if not MILLER_PLAY_ACTIVE or token != MILLER_PLAY_TOKEN:
                break
            # Scene serialization may be slower than the source 24 fps. Skip to the
            # wall-clock-correct frame instead of slowing a 10 s dataset to 40 s.
            next_frame = MILLER_ANIMATION.current_frame + advance
            if next_frame >= MILLER_ANIMATION.frame_count:
                if MILLER_PLAY_LOOP:
                    next_frame %= MILLER_ANIMATION.frame_count
                else:
                    MILLER_PLAY_ACTIVE = False
                    state.miller_playing = False
                    state.flush()
                    break
            _push_miller_frame(next_frame)


    def toggle_miller_animation():
        """切换Miller时序播放与暂停状态。"""

        global MILLER_PLAY_ACTIVE, MILLER_PLAY_TASK, MILLER_PLAY_TOKEN

        MILLER_PLAY_TOKEN += 1
        if MILLER_PLAY_TASK is not None and not MILLER_PLAY_TASK.done():
            MILLER_PLAY_TASK.cancel()
        MILLER_PLAY_TASK = None
        MILLER_PLAY_ACTIVE = not MILLER_PLAY_ACTIVE
        state.miller_playing = MILLER_PLAY_ACTIVE
        if MILLER_PLAY_ACTIVE:
            # asyncio only keeps weak references to tasks.  Retain the playback
            # task explicitly so a long-lived Trame session cannot lose its
            # animation loop after the first await.
            MILLER_PLAY_TASK = asynchronous.create_task(_play_miller_field(MILLER_PLAY_TOKEN))


    def step_miller_frame(delta):
        """按给定步长前进或后退Miller帧。"""

        global MILLER_PLAY_ACTIVE, MILLER_PLAY_TASK, MILLER_PLAY_TOKEN

        MILLER_PLAY_TOKEN += 1
        if MILLER_PLAY_TASK is not None and not MILLER_PLAY_TASK.done():
            MILLER_PLAY_TASK.cancel()
        MILLER_PLAY_TASK = None
        MILLER_PLAY_ACTIVE = False
        state.miller_playing = False
        _push_miller_frame((int(state.miller_frame or 0) + int(delta)) % MILLER_ANIMATION.frame_count)


    def previous_miller_frame():
        """切换到上一帧Miller物理场。"""

        step_miller_frame(-1)


    def next_miller_frame():
        """切换到下一帧Miller物理场。"""

        step_miller_frame(1)


    with SinglePageLayout(server) as layout:
        layout.title.set_text("AI4E VizReport · trame")
        # The embedded viewer can be as narrow as a 390 px phone viewport.  Keep
        # every scientific control reachable with a horizontal swipe instead of
        # clipping the controls beyond the app bar.
        layout.toolbar.style = "overflow-x:auto; overflow-y:hidden; overscroll-behavior-x:contain;"

        # Resolve `?view=` inside the actual browser that owns this view.  Invalid
        # values deliberately fall back to the volume scene and no code is
        # evaluated from the URL.
        trame.ClientStateChange(
            value="new URLSearchParams(window.location.search).get('view') || 'volume'",
            trigger_on_create=True,
            change=(
                "view = ['raster', 'raster_vector', 'volume', 'volume_vector', 'field', 'field_vector', 'miller_field', 'points', 'trajectory'].includes($event) ? $event : 'volume'; "
                "view_ready = true"
            ),
        )

        with layout.toolbar:
            vuetify2.VSpacer()
            vuetify2.VSelect(
                label="数据视图",
                v_model=("view", "volume"),
                items=(
                    "items",
                    [
                        {"text": "FLD · 二维标量栅格", "value": "raster"},
                        {"text": "FLD · 二维矢量栅格", "value": "raster_vector"},
                        {"text": "FLD · 燃烧室温度体数据", "value": "volume"},
                        {"text": "FLD · 三维矢量体", "value": "volume_vector"},
                        {"text": "FLD · 涡轮叶片压力场", "value": "field"},
                        {"text": "FLD · 近壁矢量场", "value": "field_vector"},
                        {"text": "FLD · Miller 托卡马克静电势场", "value": "miller_field"},
                        {"text": "ENT · 空间点集", "value": "points"},
                        {"text": "ENT · 羽流粒子轨迹", "value": "trajectory"},
                    ],
                ),
                dense=True,
                hide_details=True,
                style="max-width: 300px",
            )
            vuetify2.VBtn(
                "重置视角",
                v_if="view_ready && view === 'raster'",
                click="$refs.raster_view.resetCamera()",
                small=True,
                class_="ml-2",
            )
            vuetify2.VBtn("重置视角", v_if="view_ready && view === 'raster_vector'", click="$refs.raster_vector_view.resetCamera()", small=True, class_="ml-2")
            vuetify2.VBtn(
                "重置视角",
                v_if="view_ready && view === 'volume'",
                click="$refs.volume_view.resetCamera()",
                small=True,
                class_="ml-2",
            )
            vuetify2.VBtn("重置视角", v_if="view_ready && view === 'volume_vector'", click="$refs.volume_vector_view.resetCamera()", small=True, class_="ml-2")
            vuetify2.VBtn(
                "重置视角",
                v_if="view_ready && view === 'points'",
                click="$refs.points_view.resetCamera()",
                small=True,
                class_="ml-2",
            )
            vuetify2.VBtn("重置视角", v_if="view_ready && view === 'field_vector'", click="$refs.field_vector_view.resetCamera()", small=True, class_="ml-2")
            vuetify2.VBtn("重置视角", v_if="view_ready && view === 'miller_field'", click="$refs.miller_field_view.resetCamera()", small=True, class_="ml-2")
            vuetify2.VBtn(
                "{{ (typeof miller_playing !== 'undefined' && miller_playing) ? '暂停' : '播放' }}",
                v_if="view_ready && view === 'miller_field'",
                click=toggle_miller_animation,
                small=True,
                class_="ml-2",
                aria_label="播放或暂停时序物理场",
            )
            vuetify2.VBtn("上一帧", v_if="view_ready && view === 'miller_field'", click=previous_miller_frame, small=True, text=True, aria_label="上一帧")
            vuetify2.VBtn("下一帧", v_if="view_ready && view === 'miller_field'", click=next_miller_frame, small=True, text=True, aria_label="下一帧")
            # A native range input keeps the time locator genuinely keyboard
            # operable. Vuetify 2 renders its slider role on a transformed thumb
            # div, which is visually present but reported hidden by browsers when
            # this toolbar is embedded in a narrower report iframe.
            with html.Div(
                v_if="view_ready && view === 'miller_field'",
                style="display:flex; align-items:center; gap:6px; min-width:190px; margin-left:8px;",
            ):
                # trame's HTML Label exposes the literal ``for`` attribute (not
                # the Python-style ``for_`` alias).  Passing it through kwargs
                # keeps the native range input correctly named in the browser's
                # accessibility tree.
                html.Label(
                    "Miller 时序帧",
                    style="font-size:12px; white-space:nowrap;",
                    **{"for": "miller-frame-range"},
                )
                html.Input(
                    id="miller-frame-range",
                    type="range",
                    v_model=("miller_frame", MILLER_ANIMATION.current_frame),
                    min=0,
                    max=MILLER_ANIMATION.frame_count - 1,
                    step=1,
                    style="width:120px; accent-color:#1677ff;",
                )
            vuetify2.VSelect(
                v_if="view_ready && view === 'miller_field'",
                label="播放速度",
                v_model=("miller_speed", 1.0),
                items=("miller_speed_items", [0.25, 0.5, 1.0, 2.0, 4.0]),
                suffix="×",
                hide_details=True,
                dense=True,
                style="max-width:82px; margin-left:8px",
            )
            vuetify2.VCheckbox(
                v_if="view_ready && view === 'miller_field'",
                v_model=("miller_loop", True),
                label="循环",
                hide_details=True,
                dense=True,
                class_="ml-2",
            )
            vuetify2.VBtn(
                "重置视角",
                v_if="view_ready && view === 'trajectory'",
                click="$refs.trajectory_view.resetCamera()",
                small=True,
                class_="ml-2",
            )
            vuetify2.VBtn(
                "重置视角",
                v_if="view_ready && view === 'field'",
                click="$refs.field_view.resetCamera()",
                small=True,
                class_="ml-2",
            )

        with layout.content:
            with html.Div(style="position: relative; height: 100%;"):
                # 仅挂载当前激活视图（v-if），由 vtk.js 在客户端渲染
                # Explicit keys force Vue to mount the matching vtk-local-view
                # instead of reusing the first conditional component instance.
                with html.Div(key="'raster-scene'", v_if="view_ready && view === 'raster'", style="position:absolute; inset:0;"):
                    VtkLocalView(SCENES["raster"], ref="raster_view")
                with html.Div(key="'raster-vector-scene'", v_if="view_ready && view === 'raster_vector'", style="position:absolute; inset:0;"):
                    VtkLocalView(SCENES["raster_vector"], ref="raster_vector_view")
                with html.Div(key="'volume-scene'", v_if="view_ready && view === 'volume'", style="position:absolute; inset:0;"):
                    VtkLocalView(SCENES["volume"], ref="volume_view")
                with html.Div(key="'volume-vector-scene'", v_if="view_ready && view === 'volume_vector'", style="position:absolute; inset:0;"):
                    VtkLocalView(SCENES["volume_vector"], ref="volume_vector_view")
                with html.Div(key="'field-scene'", v_if="view_ready && view === 'field'", style="position:absolute; inset:0;"):
                    VtkLocalView(SCENES["field"], ref="field_view")
                with html.Div(key="'field-vector-scene'", v_if="view_ready && view === 'field_vector'", style="position:absolute; inset:0;"):
                    VtkLocalView(SCENES["field_vector"], ref="field_vector_view")
                with html.Div(key="'miller-field-scene'", v_if="view_ready && view === 'miller_field'", style="position:absolute; inset:0;"):
                    miller_local_view = VtkLocalView(SCENES["miller_field"], ref="miller_field_view")
                    ctrl.miller_field_view_update = miller_local_view.update
                with html.Div(key="'points-scene'", v_if="view_ready && view === 'points'", style="position:absolute; inset:0;"):
                    VtkLocalView(SCENES["points"], ref="points_view")
                with html.Div(key="'trajectory-scene'", v_if="view_ready && view === 'trajectory'", style="position:absolute; inset:0;"):
                    VtkLocalView(SCENES["trajectory"], ref="trajectory_view")

                with html.Div(
                    style=(
                        "position:absolute; left:12px; bottom:12px; z-index:5; max-width:420px;"
                        "background:rgba(13,17,23,0.82); color:#dbe3ee; border:1px solid rgba(255,255,255,0.14);"
                        "border-radius:8px; padding:8px 12px; font:11.5px/1.6 -apple-system,'PingFang SC',sans-serif;"
                    )
                ):
                    for view_name, meta in VIEW_META.items():
                        with html.Div(v_if=f"view_ready && view === '{view_name}'", data_artifact=meta["artifact"]):
                            html.Div(meta["title"], style="font-weight:600; font-size:12.5px;")
                            html.Div(f"Artifact: {meta['artifact']} · 引擎: {meta['engine']}")
                            html.Div(f"文件: {meta['file']}", style="opacity:0.8;")
                            html.Div(meta["note"], style="opacity:0.65;")
                            html.Div(
                                "帧 {{ miller_frame + 1 }}/{{ miller_frame_count }} · t={{ Number(miller_time).toFixed(3) }} R/vti · {{ miller_speed }}×",
                                v_if="view === 'miller_field'",
                                style="margin-top:3px; color:#72d6cf; font-variant-numeric:tabular-nums;",
                            )


    server.start(host="127.0.0.1", open_browser=False, timeout=0)


if __name__ == "__main__":
    main()
