"""参考图的独立播放按钮组与两行实际时间读数。"""

from trame.widgets import html
from trame.widgets import vuetify as v


def timeline(ui):
    """停止回首帧；不将帧序号当作物理时间。"""
    with html.Div(classes="phys-timeline"):
        with html.Div(classes="phys-playback"):
            for title, glyph, fn in [
                ("上一帧", "mdi-skip-previous", lambda: ui.step(-1)),
                ("反向播放", "mdi-rewind", lambda: ui.play(-1)),
                ("播放", "mdi-play", ui.play),
                ("暂停", "mdi-pause", ui.pause),
                ("停止", "mdi-stop", ui.stop),
                ("下一帧", "mdi-skip-next", lambda: ui.step(1)),
            ]:
                with v.VBtn(
                    text=True,
                    title=title,
                    __properties=[("aria_label", "aria-label"), ("aria_pressed", "aria-pressed")],
                    aria_label=title,
                    click=fn,
                    disabled=("!time_values.length",),
                    classes="phys-play-button",
                ):
                    v.VIcon(glyph)
        with html.Div(classes="phys-time-readout"):
            v.VSelect(
                v_model=("time_index",),
                items=("time_items",),
                dense=True,
                hide_details=True,
                __properties=[("aria_label", "aria-label"), ("aria_pressed", "aria-pressed")],
                aria_label="时间步 / 物理时间",
                change=(ui.seek, "[$event]"),
                disabled=("!time_values.length",),
            )
            html.Span(
                "{{ time_values.length ? 't = ' + Number(time_values[time_index]).toPrecision(4) : '静态结果' }}",
                classes="phys-time-value",
            )
