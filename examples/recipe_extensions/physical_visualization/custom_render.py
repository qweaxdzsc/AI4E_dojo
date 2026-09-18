"""研究者自定义 PyVista 绘图：固定边线和背景，沿用公开图片契约。"""

from ai4e_core.abilities.postproc.visualization import render_field


def render_with_edges(mesh, **parameters):
    """普通函数无需继承；可继续使用原生 PyVista 修改显示副本。"""
    import pyvista as pv

    modified = pv.wrap(mesh).copy(deep=True)
    return render_field(modified, **{**parameters, "show_edges": True, "background": "white"})
