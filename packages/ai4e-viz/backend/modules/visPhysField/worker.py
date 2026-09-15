"""工作进程主线程拥有全部 VTK 对象，Trame 和 IPC 共用事件循环。"""

import asyncio


def run(connection, bindings: list, spec: dict, port: int, secret: str) -> None:
    """启动独立工作区；初始化失败通过 IPC 明确返回。"""
    try:
        from trame.app import get_server

        from .scene import Scene
        from .trameUI.layout import build_ui

        scene = Scene(bindings, spec)
        if spec.get("renderer") == "remote":
            import vtk

            # 远程浏览器发送交互事件，服务端窗口必须拥有真实 interactor。
            interactor = vtk.vtkRenderWindowInteractor()
            interactor.SetRenderWindow(scene.window)
            interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
            interactor.Initialize()
        server = get_server(client_type="vue2")
        server.cli.set_defaults(authKey=secret)
        ui = build_ui(server, scene)

        async def service():
            """执行当前工作区的异步回调，保持所属操作的生命周期。"""
            while True:
                if connection.poll():
                    request = connection.recv()
                    try:
                        ui.stash()
                        result = (ui.visibility(request["body"].get("visible"))
                                  if request["body"]["operation"] == "visibility"
                                  else scene.command(request["body"]))
                        if request["body"]["operation"] not in {"snapshot", "visibility"}:
                            ids = [v["id"] for v in scene.spec["views"]]
                            if server.state.active_view not in ids:
                                server.state.active_view = ids[0]
                            if not ui.object():
                                server.state.selected = (
                                    scene.spec["pipeline"][0]["id"]
                                    if scene.spec["pipeline"]
                                    else ""
                                )
                            ui.hydrate()
                            ui.refresh()
                        response = {"request_id": request["request_id"], "result": result}
                    except Exception as exc:  # noqa: BLE001 - 进程和界面边界必须返回可见失败，不能吞掉请求。
                        response = {"request_id": request["request_id"], "error": str(exc)}
                    connection.send(response)
                await asyncio.sleep(0.02)

        @server.controller.add("on_server_ready")
        def ready(**kwargs):
            """执行当前工作区的异步回调，保持所属操作的生命周期。"""
            # 初始视图同步成功之后才发布会话，避免返回已就绪但页面无法连接。
            ui.refresh()
            connection.send({"result": scene.snapshot()})
            asyncio.create_task(service())

        server.start(
            host="127.0.0.1", port=port, open_browser=False, show_connection_info=False, timeout=0
        )
    except Exception as exc:  # noqa: BLE001 - 进程和界面边界必须返回可见失败，不能吞掉请求。
        connection.send({"error": str(exc)})
    finally:
        connection.close()
