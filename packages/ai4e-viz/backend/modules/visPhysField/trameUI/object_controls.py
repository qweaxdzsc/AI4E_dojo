"""物理场工作台对象控制；共享原工作台状态。"""

from copy import deepcopy


class ObjectControls:
    """通过显式工作台引用访问共享场景，不创建第二份会话。"""

    def __init__(self, workbench):
        self.workbench = workbench

    def descendants(self, identity):
        """委托领域依赖遍历，UI 不复制删除规则。"""
        from ..commands import descendants

        return descendants(self.workbench.scene.spec, identity)

    def visible(self, identity, enabled=None):
        """显隐仅作用于单对象当前视图；失败恢复旧画面，并向用户返回原因。"""
        state = self.workbench.server.state
        if identity in [source["id"] for source in self.workbench.scene.spec["sources"]]:
            return  # 来源分组没有显示实例，不能解释成批量显隐。
        view = next(
            (
                item
                for item in self.workbench.scene.spec["views"]
                if item["id"] == state.active_view
            ),
            {},
        )
        node = next(
            (item for item in self.workbench.scene.spec["pipeline"] if item["id"] == identity),
            None,
        )
        if view.get("type") == "line_chart" and (node or {}).get("type") != "plot_over_line":
            state.error = "折线图窗只能显示线段提取"
            return
        if self.workbench.drafts.get(identity, {}).get("new"):
            state.error = "请先应用此对象的计算参数"
            return
        layer = next(
            (
                l
                for l in self.workbench.scene.spec["layers"]
                if l["input"] == identity and l["view"] == state.active_view
            ),
            None,
        )
        probe = next((p for p in self.workbench.scene.spec["probes"] if p["id"] == identity), None)
        if layer is None and probe is None and identity not in self.workbench.scene.datasets:
            state.error = "对象数据当前不可用"
            return
        # 在其他窗口新建的对象首次显示时才建立本窗口实例，输入与计算结果仍共享。
        previous = deepcopy(self.workbench.scene.spec) if layer is None and probe is None else None
        old = (
            probe.get("views", {}).get(str(state.active_view), {}).get("visible", False)
            if probe
            else (layer.get("visible", True) if layer else False)
        )
        target = not old if enabled is None else bool(enabled)
        tree = deepcopy(state.tree_nodes or [])
        body = {
            "operation": "probe_visibility" if probe else "display",
            "id": identity,
            "view": state.active_view,
            "visible": target,
        }
        try:
            self.workbench.scene.command(body)
            self.workbench._sync_tree_visible({identity}, target)
            # 选中的切面隐藏时撤下从属手柄，不能把仍可见的子分析一起隐藏。
            self.workbench.scene.show_selection(state.selected, state.active_view)
            self.workbench.sync_plane_widget()
            self.workbench._push_visibility_view()
            state.error = ""
        except Exception as exc:  # noqa: BLE001 - 覆盖计算以外的树同步和视口推送。
            state.tree_nodes = tree
            try:
                if previous is not None:
                    self.workbench.scene.apply(previous)
                else:
                    self.workbench.scene.command({**body, "visible": old})
                self.workbench.sync_plane_widget()
                self.workbench._push_visibility_view()
            except Exception as recovery:  # noqa: BLE001 - 推送也失败时必须明确失联。
                state.error = f"{exc}；画面同步失败：{recovery}，请重新连接"
            else:
                state.error = str(exc)

    def _sync_tree_visible(self, identities, enabled):
        """对象树眼睛只改标记，不重新画像数据集。"""
        found = set(identities)

        def walk(nodes):
            """复制树标记，仅改明确指定的对象。"""
            updated = []
            for node in nodes or []:
                item = dict(node)
                if item.get("id") in found:
                    item["visible"] = enabled
                children = item.get("children") or []
                if children:
                    item["children"] = walk(children)
                updated.append(item)
            return updated

        self.workbench.server.state.tree_nodes = walk(self.workbench.server.state.tree_nodes or [])

    def _push_visibility_view(self):
        """把已有 actor 显隐推到客户端，不走 snapshot/refresh，不推相机位姿。"""
        if not self.workbench.view:
            return
        if self.workbench.scene.spec.get("renderer") != "remote":
            from ..rendering import install_local_serializers

            install_local_serializers()
        self.workbench.view.update()

    def rename(self):
        """名称更新不改变对象身份。"""
        if self.workbench.command(
            {
                "operation": "object_rename",
                "id": self.workbench.server.state.selected,
                "name": self.workbench.server.state.object_name,
            }
        ):
            self.workbench.server.state.rename_dialog = False
            self.workbench.refresh()

    def delete(self):
        """用户确认后级联移除对象，源文件保持不变。"""
        state = self.workbench.server.state
        parent = (self.workbench.object() or {}).get("input")
        affected = self.workbench.descendants(state.selected)
        # 草稿尚未进入正式依赖图，也要随父对象一起移除。
        while any(
            d["node"]["input"] in affected and k not in affected
            for k, d in self.workbench.drafts.items()
        ):
            affected.update(
                k for k, d in self.workbench.drafts.items() if d["node"]["input"] in affected
            )
        op = (
            "source_remove"
            if state.selected in [s["id"] for s in self.workbench.scene.spec["sources"]]
            else "object_delete"
        )
        if self.workbench.command({"operation": op, "id": state.selected, "cascade": True}):
            self.workbench.drafts = {
                k: d for k, d in self.workbench.drafts.items() if k not in affected
            }
            state.selected = (
                parent
                if any(n["id"] == parent for n in self.workbench.scene.spec["pipeline"])
                else ""
            )
            state.delete_dialog = False
            self.workbench.hydrate()
            self.workbench.refresh()
