"""按完整更新边界响应信号，避免把半步优化状态作为可恢复状态。"""

import signal
import threading
from contextlib import contextmanager


@contextmanager
def cancellation():
    """主线程临时接管 SIGINT/SIGTERM；退出后恢复调用方处理器。"""
    stopped = False
    previous = {}

    def stop(*_):
        nonlocal stopped
        stopped = True

    try:
        if threading.current_thread() is threading.main_thread():
            for name in (signal.SIGINT, signal.SIGTERM):
                previous[name] = signal.signal(name, stop)
        yield lambda: stopped
    finally:
        for name, handler in previous.items():
            signal.signal(name, handler)
