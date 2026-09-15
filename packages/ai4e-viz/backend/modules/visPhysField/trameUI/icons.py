"""工作台统一线性图标；直接绘制 SVG，避免字体图标的字形和尺寸差异。"""

from base64 import b64encode

from trame.widgets import html

PATHS = {
    "glyph": '<path d="M7 25L25 7M7 7l18 18M5 18l2 7 7-2M18 5l7 2-2 7"/><path d="m7 7 1 7m-1-7 7 1m11 17-1-7m1 7-7-1"/>',
    "slice": '<path d="m8 8 13-4v21l-13 4zM13 5l13-3v21l-5 2"/>',
    "clip": '<path d="m8 8 13-4v21l-13 4z" fill="currentColor" fill-opacity=".14"/><path d="m13 5 13-3v21l-5 2M16 3v27"/>',
    "streamline": '<path d="M3 9c7-9 14 9 26-2M3 16c7-9 14 9 26-2M3 23c7-9 14 9 26-2"/>',
    "isosurface": '<circle cx="12" cy="13" r="8" fill="currentColor" fill-opacity=".5"/><circle cx="22" cy="15" r="7" fill="currentColor" fill-opacity=".7"/><circle cx="15" cy="23" r="6" fill="currentColor" fill-opacity=".9"/>',
    "contour": '<circle cx="16" cy="16" r="12"/><circle cx="16" cy="16" r="8"/><circle cx="16" cy="16" r="4"/>',
    "probe": '<path d="M16 29s9-11 9-18a9 9 0 0 0-18 0c0 7 9 18 9 18z" fill="currentColor" fill-opacity=".1"/><circle cx="16" cy="11" r="3"/>',
    "select": '<path d="m7 3 20 15-10 1-5 10z" fill="currentColor" stroke-width="1"/>',
    "rotate": '<circle cx="16" cy="16" r="9"/><path d="M16 2v7m0 14v7M2 16h7m14 0h7m-2-8-4 1 1-4"/>',
    "pan": '<path d="M10 16V7a2 2 0 0 1 4 0v8-11a2 2 0 0 1 4 0v11-9a2 2 0 0 1 4 0v10-5a2 2 0 0 1 4 0v10c0 11-13 11-17 5l-5-8c-2-4 3-5 6-2z"/>',
    "zoom": '<circle cx="13" cy="13" r="8"/><path d="m19 19 10 10M9 13h8m-4-4v8"/>',
    "fit": '<path d="M3 12V3h9m8 0h9v9m0 8v9h-9m-8 0H3v-9" stroke-dasharray="4 2"/>',
    "axes": '<path d="M8 25V4m0 21h20m-20 0L2 30M5 8l3-4 3 4m13 14 4 3-4 3"/>',
    "cube": '<path d="m16 3 11 6v14l-11 6-11-6V9zM5 9l11 7 11-7M16 16v13M16 3v13"/>',
    "legend": '<path d="M10 3h6v26h-6z" fill="url(#phys-spectrum)" stroke="none"/><path d="M20 4h4m-4 6h3m-3 6h4m-4 6h3m-3 6h4"/>',
    "opacity": '<path d="M4 4h8v8H4zm16 0h8v8h-8zm-8 8h8v8h-8zm-8 8h8v8H4zm16 0h8v8h-8z" fill="currentColor" stroke="none"/>',
    "light": '<circle cx="16" cy="16" r="6"/><path d="M16 2v5m0 18v5M2 16h5m18 0h5M6 6l4 4m12 12 4 4M6 26l4-4M22 10l4-4"/>',
    "movie": '<circle cx="16" cy="16" r="12"/><circle cx="16" cy="16" r="8" fill="currentColor" stroke="none"/>',
}


def icon(name, **kwargs):
    """通过隐藏于无障碍树的 SVG 装饰已命名的真实按钮。"""
    content = PATHS.get(name, PATHS["cube"])
    defs = (
        '<defs><linearGradient id="phys-spectrum" x2="0" y2="1"><stop stop-color="#f00"/><stop offset=".3" stop-color="#ff0"/><stop offset=".5" stop-color="#0f8"/><stop offset=".7" stop-color="#00cfff"/><stop offset="1" stop-color="#23f"/></linearGradient></defs>'
        if name == "legend"
        else ""
    )
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" '
        'fill="none" stroke="currentColor" stroke-width="1.8" '
        f'stroke-linecap="round" stroke-linejoin="round">{defs}{content}</svg>'
    ).replace("currentColor", "#fa1727" if name == "movie" else "#066bff")
    return html.Img(
        src="data:image/svg+xml;base64," + b64encode(svg.encode()).decode(),
        classes="phys-icon",
        alt="",
        aria_hidden="true",
        **kwargs,
    )
