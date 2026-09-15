"""独立物理场工作台装配，具体交互由各 UI 功能组件承担。"""

# ruff: noqa: SIM117 - Trame 布局按 DOM 层级书写，保持结构可读。
from pathlib import Path

from trame.ui.vuetify import SinglePageLayout
from trame.widgets import client as trame
from trame.widgets import html
from trame.widgets import vuetify as v

from .controller import Workbench
from .extractionPanel import extraction_panel
from .pipelinePanel import pipeline_panel
from .propertiesPanel import properties_panel
from .toolbar import creation_bar, view_bar
from .viewportGrid import viewport_grid


def build_ui(server, scene):
    """构建同源可嵌入的完整工作台，不包含宿主平台导航。"""
    ui = Workbench(server, scene)
    client = Path(__file__).parent / "client"
    server.enable_module(
        {
            "serve": {"__phys_client": str(client)},
            "scripts": ["__phys_client/interaction.js"],
            "vue_use": ["PhysInteraction"],
        }
    )
    with SinglePageLayout(server) as layout:
        layout.toolbar.hide()
        layout.footer.hide()
        with layout.content:
            trame.Style((client / "workbench.css").read_text())
            trame.Script((client / "bridge.js").read_text())
            ui.bridge = trame.ClientTriggers(
                ref="phys_bridge",
                dispatch="window.ai4eVisBridge.request($event.action, $event.payload)",
            )
            with html.Div(classes="phys-workbench"):
                html.H2("三维物理场可视化", classes="phys-title")
                creation_bar(ui)
                with html.Div(classes="phys-body"):
                    with html.Div(classes="phys-sidebar"):
                        pipeline_panel(ui)
                        with html.Div(classes="phys-property-scroll"):
                            properties_panel(ui)
                            extraction_panel(ui)
                    with html.Div(classes="phys-main"):
                        view_bar(ui)
                        viewport_grid(ui)
                        html.Div(
                            "{{ error || missing_text }}",
                            classes="phys-error",
                            v_show="error || missing_text",
                        )
                with v.VDialog(v_model=("draft_dialog",), max_width=520, persistent=True):
                    with v.VCard():
                        v.VCardTitle("处理未应用参数")
                        v.VCardText("以下对象还有草稿：{{ dirty_names }}")
                        with v.VCardActions():
                            v.VBtn(
                                "全部应用", color="primary", click=lambda: ui.resolve_drafts(True)
                            )
                            v.VBtn("丢弃草稿", click=lambda: ui.resolve_drafts(False))
                            v.VBtn("取消", click="draft_dialog=false")
                with v.VDialog(v_model=("delete_dialog",), max_width=520):
                    with v.VCard():
                        v.VCardTitle("删除对象及下游依赖")
                        v.VCardText("{{ delete_names }}")
                        with v.VCardActions():
                            v.VBtn("确认删除", color="error", click=ui.delete)
                            v.VBtn("取消", click="delete_dialog=false")
                with v.VDialog(v_model=("rename_dialog",), max_width=400):
                    with v.VCard():
                        v.VCardTitle("重命名对象")
                        v.VTextField(v_model=("object_name",), label="名称", classes="mx-4")
                        with v.VCardActions():
                            v.VBtn("保存", click=ui.rename)
                            v.VBtn("取消", click="rename_dialog=false")
    # JS 通过 Trame 生命周期执行，HTML 中插入 script 不会由 Vue 执行。

    if scene.spec.get("renderer") != "remote":
        from ..rendering import install_local_serializers

        install_local_serializers()
    ui.refresh()
    return ui
