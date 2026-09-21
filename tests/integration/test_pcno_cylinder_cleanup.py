"""精确清单清理：保留原始数据和最终模型，防止越界和竞态。"""

import pytest

from tools.verification.pcno.cylinder.cleanup import apply, plan


def test_cleanup_protects_sources_and_detects_change(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "data").write_bytes(b"original")
    final = tmp_path / "final.pt"
    final.write_bytes(b"checkpoint")
    cache = tmp_path / "cache"
    cache.mkdir()
    (cache / "tensor").write_bytes(b"x" * 100)
    with pytest.raises(ValueError, match="保护"):
        plan(str(tmp_path), [str(raw)], [str(raw), str(final)])
    ledger = plan(str(tmp_path), [str(cache)], [str(raw), str(final)])
    (cache / "tensor").write_bytes(b"changed")
    with pytest.raises(ValueError, match="改变"):
        apply(ledger)
    report = apply(plan(str(tmp_path), [str(cache)], [str(raw), str(final)]))
    assert report["reclaimed_bytes"] == 7 and not cache.exists()
    assert (raw / "data").read_bytes() == b"original" and final.read_bytes() == b"checkpoint"
