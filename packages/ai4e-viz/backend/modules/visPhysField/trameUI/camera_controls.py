"""物理场工作台相机控制；共享原工作台状态。"""


class CameraControls:
    """通过显式工作台引用访问共享场景，不创建第二份会话。"""

    def __init__(self, workbench):
        self.workbench = workbench

    def camera(self, direction=None):
        """相机命令只作用于活动视图及其联动组。"""
        self.workbench.command(
            {
                "operation": "camera",
                "view": self.workbench.server.state.active_view,
                **({"direction": direction} if direction else {}),
            }
        )
        self.workbench.refresh(push_cameras=True)

    def view_setting(self, key, value):
        """视图级开关与对象属性独立保存。"""
        self.workbench.command(
            {
                "operation": "view_update",
                "view": self.workbench.server.state.active_view,
                "settings": {key: value},
            }
        )
        self.workbench.refresh()

    def link(self, value):
        """开启后全体窗口共用相机，不要求共同坐标空间。"""
        self.workbench.command(
            {
                "operation": "link_views",
                "views": [v["id"] for v in self.workbench.scene.spec["views"]] if value else [],
            }
        )
        self.workbench.refresh(push_cameras=True)

    def remote_end(self, *_):
        """远程交互结束后只重定位注记，不把服务端旧相机推回客户端。"""
        if not getattr(self.workbench, "_remote_interaction_ready", lambda: True)():
            return
        self.workbench.scene.add_annotations()
        if self.workbench.view:
            self.workbench.view.update()

    def resize(self, size):
        """容器尺寸变化只重定位注记，不刷新对象树、不重读网格。"""
        width, height = int(size["width"]), int(size["height"])
        if min(width, height) < 1 or self.workbench.scene.window.GetSize() == (width, height):
            return
        state = self.workbench.server.state
        if getattr(state, "use_remote_view", False) and not getattr(state, "remote_ready", False):
            return
        self.workbench.scene.window.SetSize(width, height)
        self.workbench.scene.add_annotations()
        if self.workbench.view:
            if self.workbench.scene.spec.get("renderer") != "remote":
                from ..rendering import install_local_serializers

                install_local_serializers()
            self.workbench.view.update()

    def camera_event(self, event):
        """交互结束只回写活动相机，不走整屏 refresh，避免再次读盘和推场景。"""
        views = self.workbench.scene.spec["views"]
        if event.get("view") not in [v["id"] for v in views]:
            return
        index = next(i for i, v in enumerate(views) if v["id"] == event["view"])
        import numpy as np

        from ..modules.fieldVisualization.view import camera_spec, set_camera

        camera = self.workbench.scene.renderers[index].GetActiveCamera()
        current = camera_spec(camera)
        incoming = event.get("camera") or {}
        if incoming and all(
            k in current and np.allclose(current[k], value, rtol=1e-4, atol=1e-5)
            for k, value in incoming.items()
        ):
            return
        if incoming:
            set_camera(camera, incoming)
        views[index]["camera"] = camera_spec(camera)
        if event["view"] != self.workbench.server.state.active_view:
            self.workbench.activate_view(event["view"])

    def camera_changed(self, value, pointer):
        """回传实际相机，固定修订导出与屏幕视角一致。"""
        from ..modules.fieldVisualization.view import set_camera

        mapping = {
            "position": "position",
            "focalPoint": "focal_point",
            "viewUp": "view_up",
            "parallelScale": "parallel_scale",
            "parallelProjection": "parallel_projection",
        }
        translated = {
            target: value[source] for source, target in mapping.items() if source in value
        }
        for i, r in enumerate(self.workbench.scene.renderers):
            x0, y0, x1, y1 = r.GetViewport()
            if x0 <= pointer[0] <= x1 and y0 <= pointer[1] <= y1:
                set_camera(r.GetActiveCamera(), translated)
                self.workbench.activate_view(self.workbench.scene.spec["views"][i]["id"])
                break
        if self.workbench.scene.spec.get("link_groups"):
            self.workbench.refresh(push_cameras=True)
