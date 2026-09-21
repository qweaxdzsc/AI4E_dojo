"""有版本约束的 HTTP 范围读取及完整 TFRecord 前缀下载，不接受整包回退。"""

import hashlib
import json
import struct
from pathlib import Path
from urllib.request import Request, urlopen

from .tfrecord import _masked_crc


def read_range(url, start, size, *, etag=None, timeout=60):
    """读取准确字节范围；拒绝整包响应、对象版本变化和截断。"""
    headers = {"Range": f"bytes={start}-{start + size - 1}"}
    if etag:
        headers["If-Match"] = etag
    with urlopen(Request(url, headers=headers), timeout=timeout) as response:
        content_range = response.headers.get("Content-Range", "")
        version = response.headers.get("ETag")
        if response.status != 206 or not content_range.startswith(
            f"bytes {start}-{start + size - 1}/"
        ):
            raise ValueError("来源未返回准确范围，拒绝整包下载")
        if not version or (etag is not None and version != etag):
            raise ValueError("来源版本缺失或已经变化")
        data = response.read(size + 1)
        if len(data) != size:
            raise ValueError("范围内容长度不符")
        return data, version


def download_record_prefix(url, directory, count):
    """下载前 count 条完整记录；每条原子提交，可按来源清单恢复。"""
    if type(count) is not int or count < 1:
        raise ValueError("记录数必须为正整数")
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    manifest = root / "source.json"
    state = (
        json.loads(manifest.read_text())
        if manifest.exists()
        else {"url": url, "etag": None, "records": [], "subset": True}
    )
    if state["url"] != url:
        raise ValueError("恢复来源不一致")
    offset = 0
    for item in state["records"]:
        data = (root / item["file"]).read_bytes()
        if hashlib.sha256(data).hexdigest() != item["sha256"] or len(data) != item["size"]:
            raise ValueError("本地已提交记录被改变")
        offset += len(data)
    for index in range(len(state["records"]), count):
        header, version = read_range(url, offset, 12, etag=state["etag"])
        size, crc = struct.unpack("<QI", header)
        if _masked_crc(header[:8]) != crc or size > 256 * 1024**2:
            raise ValueError("非法记录长度或长度CRC")
        body, _ = read_range(url, offset + 12, size + 4, etag=version)
        if _masked_crc(body[:-4]) != struct.unpack("<I", body[-4:])[0]:
            raise ValueError("记录内容CRC错误")
        data = header + body
        name = f"{index:06d}.tfrecord"
        partial = root / (name + ".partial")
        partial.write_bytes(data)
        partial.replace(root / name)
        state["etag"] = version
        state["records"].append(
            {
                "index": index,
                "offset": offset,
                "size": len(data),
                "file": name,
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
        temporary = manifest.with_suffix(".partial")
        temporary.write_text(json.dumps(state, indent=2) + "\n")
        temporary.replace(manifest)
        offset += len(data)
        print(f"record {index + 1}/{count}: {len(data)} bytes", flush=True)
    return state
