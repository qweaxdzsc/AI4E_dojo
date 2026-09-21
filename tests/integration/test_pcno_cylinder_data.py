"""官方子集下载的完整性、版本和失败边界，不依赖公网测试。"""

import struct

import pytest

from ai4e_core.abilities.data.source import record_download as d
from ai4e_core.abilities.data.source.tfrecord import _crc32c, _masked_crc, iter_tfrecord


def record(payload):
    length = struct.pack("<Q", len(payload))
    return (
        length
        + struct.pack("<I", _masked_crc(length))
        + payload
        + struct.pack("<I", _masked_crc(payload))
    )


def test_crc_known_vector():
    assert _crc32c(b"123456789") == 0xE3069283


def test_resume_records_and_tampering(tmp_path, monkeypatch):
    data = record(b"first") + record(b"second")
    calls = []

    def read(url, start, size, *, etag=None, **kw):
        calls.append((start, size, etag))
        assert etag in (None, "version1")
        return data[start : start + size], "version1"

    monkeypatch.setattr(d, "read_range", read)
    d.download_record_prefix("source", tmp_path, 1)
    d.download_record_prefix("source", tmp_path, 2)
    assert list(iter_tfrecord(tmp_path / "000001.tfrecord")) == [b"second"]
    assert calls[2][0] == len(record(b"first")) and calls[2][2] == "version1"
    (tmp_path / "000000.tfrecord").write_bytes(b"changed")
    with pytest.raises(ValueError, match="改变"):
        d.download_record_prefix("source", tmp_path, 2)


def test_bad_crc_never_commits(tmp_path, monkeypatch):
    data = record(b"first")[:-1] + b"!"
    monkeypatch.setattr(
        d, "read_range", lambda url, start, size, **kw: (data[start : start + size], "v1")
    )
    with pytest.raises(ValueError, match="CRC"):
        d.download_record_prefix("source", tmp_path, 1)
    assert not (tmp_path / "source.json").exists()


@pytest.mark.parametrize("status,etag,length", [(200, "v1", 16), (206, "v2", 16), (206, "v1", 15)])
def test_reject_full_response_changed_version_truncation(monkeypatch, status, etag, length):
    class Response:
        def __init__(self):
            self.headers = {"ETag": etag, "Content-Range": "bytes 0-15/100"}

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def read(self, n):
            return b"x" * length

    r = Response()
    r.status = status
    monkeypatch.setattr(d, "urlopen", lambda *args, **kw: r)
    with pytest.raises(ValueError):
        d.read_range("https://example.invalid", 0, 16, etag="v1")
