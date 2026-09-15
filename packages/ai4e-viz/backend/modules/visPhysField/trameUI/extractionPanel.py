"""Probe 当前值与时间曲线。"""

from trame.widgets import html
from trame.widgets import vuetify as v


def extraction_panel(ui):
    """提取结果即时显示，文件只由显式导出生成。"""
    with html.Div(v_if="kind === 'probe'", classes="pa-2"):
        v.VBtn("当前数值", small=True, text=True, click=ui.query)
        v.VBtn(
            "时间曲线",
            small=True,
            text=True,
            click=lambda: ui.query("temporal"),
            disabled=("!time_values.length",),
        )
        v.VBtn("导出 CSV", small=True, text=True, click=ui.export_probe)
        html.Div(v_html=("query_curve",))
        v.VDataTable(
            headers=(
                "query_headers",
                [{"text": "物理量 / 状态", "value": "field"}, {"text": "数值", "value": "value"}],
            ),
            items=("query_table", []),
            dense=True,
            hide_default_footer=True,
            items_per_page=-1,
        )
