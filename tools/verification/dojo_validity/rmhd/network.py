"""主控公网代理：解析后只连接公网 IP，TLS 隧道只记录目标而不读取凭据。"""

import ipaddress
import json
import select
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen


def public_addresses(host, port):
    """检查所有 DNS 地址，连接已检查的数值地址，避免解析重绑定。"""
    if not 1 <= port <= 65535:
        raise ValueError("非法端口")
    answers = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    # 本机 VPN 可能返回 198.18/15 合成地址；不能把该保留段当公网放行。
    # 仅这种情况通过固定 HTTPS 公共 DNS 解析，仍连接核过的真实公网数值地址。
    if answers and all(
        ipaddress.ip_address(a[4][0]) in ipaddress.ip_network("198.18.0.0/15") for a in answers
    ):
        request = Request(
            "https://cloudflare-dns.com/dns-query?" + urlencode({"name": host, "type": "A"}),
            headers={"accept": "application/dns-json"},
        )
        with urlopen(request, timeout=15) as response:
            records = json.loads(response.read(65536))
        answers = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", (row["data"], port))
            for row in records.get("Answer", [])
            if row.get("type") == 1
        ]
    if not answers or any(not ipaddress.ip_address(a[4][0]).is_global for a in answers):
        raise ValueError("仅允许公网目标")
    return answers


class PublicProxy:
    """每个 CLI 调用一个受主控管理的代理；退出自动关闭。"""

    def __init__(self, log):
        self.log = log
        self.lock = threading.Lock()
        self.stopping = threading.Event()
        owner = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, *args):
                pass

            def connect_public(self, host, port):
                addresses = public_addresses(host, port)
                last = None
                for family, socktype, proto, _, address in addresses:
                    connection = socket.socket(family, socktype, proto)
                    try:
                        connection.settimeout(30)
                        connection.connect(address)
                        owner.record(host, port, address[0], "connected")
                        return connection
                    except OSError as error:
                        last = error
                        connection.close()
                raise last or OSError("公网连接失败")

            def do_CONNECT(self):
                try:
                    parsed = urlsplit("//" + self.path)
                    upstream = self.connect_public(parsed.hostname, parsed.port or 443)
                except (OSError, ValueError, TypeError) as error:
                    owner.record(self.path, None, None, type(error).__name__)
                    self.send_error(403, "Public destinations only")
                    return
                self.send_response(200, "Connection established")
                self.end_headers()
                self.wfile.flush()
                self.close_connection = True
                with upstream:
                    sockets = [self.connection, upstream]
                    while not owner.stopping.is_set():
                        ready, _, _ = select.select(sockets, [], [], 1)
                        if not ready:
                            # 长推理可能没有响应字节；静默不是断连，不能人为触发模型重试。
                            continue
                        for source in ready:
                            try:
                                data = source.recv(65536)
                                if not data:
                                    return
                                (
                                    upstream if source is self.connection else self.connection
                                ).sendall(data)
                            except OSError as error:
                                owner.record(
                                    parsed.hostname, parsed.port or 443, None, type(error).__name__
                                )
                                return

            def do_GET(self):
                self.forward_http()

            def do_HEAD(self):
                self.forward_http()

            def do_POST(self):
                self.forward_http()

            def forward_http(self):
                try:
                    parsed = urlsplit(self.path)
                    if (
                        parsed.scheme != "http"
                        or not parsed.hostname
                        or self.headers.get("Transfer-Encoding")
                    ):
                        raise ValueError("HTTP requires absolute URL and content length")
                    upstream = self.connect_public(parsed.hostname, parsed.port or 80)
                except (OSError, ValueError, TypeError):
                    self.send_error(403, "Public destinations only")
                    return
                self.close_connection = True
                path = parsed.path or "/"
                if parsed.query:
                    path += "?" + parsed.query
                with upstream:
                    headers = [f"{self.command} {path} HTTP/1.1"]
                    headers.extend(
                        f"{k}: {v}"
                        for k, v in self.headers.items()
                        if k.lower()
                        not in {"proxy-authorization", "proxy-connection", "connection"}
                    )
                    headers.append("Connection: close")
                    upstream.sendall(("\r\n".join(headers) + "\r\n\r\n").encode("latin1"))
                    remaining = int(self.headers.get("Content-Length", 0))
                    while remaining:
                        data = self.rfile.read(min(65536, remaining))
                        if not data:
                            return
                        upstream.sendall(data)
                        remaining -= len(data)
                    while data := upstream.recv(65536):
                        self.wfile.write(data)

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.daemon_threads = True
        self.port = self.server.server_address[1]

    def record(self, host, port, address, status):
        """仅记录目标与状态；不记录认证头或 TLS 内容。"""
        with self.lock, self.log.open("a") as stream:
            stream.write(
                json.dumps(
                    {
                        "time": time.monotonic(),
                        "host": host,
                        "port": port,
                        "address": address,
                        "status": status,
                    }
                )
                + "\n"
            )

    def __enter__(self):
        self.log.parent.mkdir(parents=True, exist_ok=True)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *args):
        self.stopping.set()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
