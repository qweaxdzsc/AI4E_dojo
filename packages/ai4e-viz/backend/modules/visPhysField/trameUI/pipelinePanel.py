"""结果来源与用户创建对象树，行内删除打开级联确认，不创建物理量占位节点。"""

from trame.widgets import html
from trame.widgets import vuetify as v


def pipeline_panel(ui):
    """树选择、来源分组、搜索和活动视图显隐。"""
    with html.Div(classes="phys-tree"):
        with html.Div(classes="phys-panel-heading"):
            html.H3("可视化资产")
            v.VIcon("mdi-pin-outline", small=True, aria_hidden="true")
        with html.Div(classes="phys-menus"):
            for title, items in [
                (
                    "文件",
                    [
                        ("导入结果", "import"),
                        ("保存配置", "save"),
                        ("打开已保存配置", "open"),
                        ("应用外部配置", "configuration"),
                    ],
                ),
                ("对象", [("重命名", "rename"), ("复制", "copy"), ("删除", "delete")]),
                (
                    "导出",
                    [
                        ("图片 / 数据", "export"),
                        ("时序动画", "animation"),
                        ("录制实际操作", "record"),
                    ],
                ),
            ]:
                with v.VMenu(offset_y=True, attach="body", allow_overflow=True):
                    with v.Template(v_slot_activator="{ on, attrs }"):
                        v.VBtn(
                            title,
                            text=True,
                            small=True,
                            aria_label=title,
                            __properties=[("aria_label", "aria-label")],
                            v_bind="attrs",
                            v_on="on",
                        )
                    with v.VList(dense=True):
                        for label, action in items:
                            with v.VListItem(click=lambda a=action: ui.menu(a)):
                                v.VListItemTitle(label)
            with v.VMenu(offset_y=True, attach="body", allow_overflow=True):
                with v.Template(v_slot_activator="{ on, attrs }"):
                    v.VBtn(
                        "视图",
                        text=True,
                        small=True,
                        aria_label="视图",
                        __properties=[("aria_label", "aria-label")],
                        v_bind="attrs",
                        v_on="on",
                    )
                with v.VList(dense=True):
                    for label, callback in [
                        ("适合窗口", ui.camera),
                        ("左右分割", lambda: ui.view_action("view_create", "horizontal")),
                        ("上下分割", lambda: ui.view_action("view_create", "vertical")),
                        ("最大化 / 恢复", ui.maximize),
                    ]:
                        with v.VListItem(click=callback):
                            v.VListItemTitle(label)
        v.VTextField(
            v_model=("search",),
            placeholder="搜索对象…",
            prepend_inner_icon="mdi-magnify",
            outlined=True,
            dense=True,
            hide_details=True,
            classes="phys-tree-search",
        )
        with (
            v.VTreeview(
                items=("tree_nodes",),
                open=("tree_open",),
                search=("search",),
                dense=True,
                item_key="id",
                open_on_click=False,
            ),
            v.Template(v_slot_label="{ item }"),
            html.Div(classes=("item.id === selected ? 'phys-node selected' : 'phys-node'",)),
        ):
            with v.VBtn(icon=True, x_small=True, click=(ui.visible, "[item.id]")):
                v.VIcon(
                    '{{ item.source ? "mdi-tag" : (item.probe ? "mdi-map-marker-outline" : (item.visible ? "mdi-eye-outline" : "mdi-eye-off-outline")) }}',
                    small=True,
                )
            html.Span(
                "{{ item.name }}",
                click=(ui.select, "[item.id]"),
                style="flex:1;cursor:pointer",
            )
            with v.VBtn(
                icon=True,
                x_small=True,
                title=(" '删除 ' + item.name ",),
                aria_label=(" '删除 ' + item.name ",),
                __properties=[("aria_label", "aria-label")],
                classes="phys-delete",
                click=(ui.request_delete, "[item.id]"),
            ):
                v.VIcon("mdi-delete-outline", small=True)
