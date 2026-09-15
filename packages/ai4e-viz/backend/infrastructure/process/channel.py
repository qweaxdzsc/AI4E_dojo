"""带请求身份的顺序 IPC，超时不让迟到响应污染下次命令。"""
from threading import Lock
from uuid import uuid4


class Channel:
    """同一工作进程的并发调用串行进入主事件循环。"""
    def __init__(self, connection):
        """绑定连接和互斥锁。"""
        self.connection = connection
        self.lock = Lock()

    def call(self, body: dict, timeout: float = 120) -> dict:
        """等待匹配响应；超时由监督器回收会话。"""
        with self.lock:
            identity = uuid4().hex
            self.connection.send({'request_id': identity, 'body': body})
            if not self.connection.poll(timeout):
                raise TimeoutError('phys_worker_timeout')
            result = self.connection.recv()
            if result.get('request_id') != identity:
                raise RuntimeError('phys_protocol_mismatch')
            if result.get('error'):
                raise ValueError(result['error'])
            return result['result']
