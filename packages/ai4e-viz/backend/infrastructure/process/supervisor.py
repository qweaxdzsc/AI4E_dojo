"""子进程退出、终止和强制回收的统一技术实现。"""
import socket


def available_port() -> int:
    """分配回环临时端口，启动失败仍需由调用方处理。"""
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


def stop_process(process) -> None:
    """有界回收进程，避免僵尸与后台孤儿。"""
    if process.is_alive():
        process.terminate()
    process.join(3)
    if process.is_alive():
        process.kill()
        process.join(3)
