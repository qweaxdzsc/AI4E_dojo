"""物理场工作台会话播放控制；共享原工作台状态。"""

import asyncio


class SessionControls:
    """通过显式工作台引用访问共享场景，不创建第二份会话。"""

    def __init__(self, workbench):
        self.workbench = workbench

    def seek(self, value=None):
        """选择真实时间值，缺帧由场景报告。"""
        values = self.workbench.scene.times
        if values:
            self.workbench.command(
                {
                    "operation": "time",
                    "value": values[
                        int(self.workbench.server.state.time_index if value is None else value)
                    ],
                }
            )
            self.workbench.refresh()

    def step(self, direction):
        """逐帧有界前进/后退。"""
        if self.workbench.scene.times:
            self.workbench.seek(
                max(
                    0,
                    min(
                        len(self.workbench.scene.times) - 1,
                        int(self.workbench.server.state.time_index) + direction,
                    ),
                )
            )

    def visibility(self, visible):
        """隐藏暂停当前时间，返回只刷新视图，不清空对象或草稿。"""
        if not isinstance(visible, bool):
            raise ValueError("visibility_requires_boolean")  # noqa: TRY004 - 保持公开命令参数错误协议。
        if not visible:
            self.workbench.pause()
        elif self.workbench.view:
            self.workbench.view.update()
        return {"visible": visible}

    def pause(self):
        """使旧播放循环失效。"""
        self.workbench.playing += 1
        self.workbench.server.state.playing = False

    def stop(self):
        """停止并恢复第一时间步。"""
        self.workbench.pause()
        self.workbench.seek(0)

    def play(self, direction=1):
        """事件循环串行更新，避免跨线程访问 VTK。"""
        if not self.workbench.scene.times:
            return
        self.workbench.pause()
        token = self.workbench.playing
        self.workbench.server.state.playing = True

        async def run():
            """按实际时间索引连续播放，旧循环可失效。"""
            while token == self.workbench.playing:
                nxt = int(self.workbench.server.state.time_index) + direction
                if not 0 <= nxt < len(self.workbench.scene.times):
                    break
                self.workbench.seek(nxt)
                await asyncio.sleep(0.1)
            if token == self.workbench.playing:
                self.workbench.server.state.playing = False

        asyncio.create_task(run())
