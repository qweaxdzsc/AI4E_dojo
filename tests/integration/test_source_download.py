"""数据下载：HuggingFace、普通网址与多包解压。"""

from __future__ import annotations

import tarfile
import zipfile
from pathlib import Path

import pytest

from ai4e_core.abilities.data.source.download import (
    download_huggingface_file,
    download_huggingface_snapshot,
    download_url,
    extract_archives,
)


def test_extract_multiple_archives(tmp_path: Path) -> None:
    zip_path = tmp_path / "one.zip"
    with zipfile.ZipFile(zip_path, "w") as handle:
        handle.writestr("from_zip.txt", "zip")

    tar_path = tmp_path / "two.tar.gz"
    inner = tmp_path / "from_tar.txt"
    inner.write_text("tar", encoding="utf-8")
    with tarfile.open(tar_path, "w:gz") as handle:
        handle.add(inner, arcname="from_tar.txt")
    inner.unlink()

    extracted = extract_archives(tmp_path)

    assert zip_path in extracted
    assert tar_path in extracted
    assert (tmp_path / "from_zip.txt").read_text(encoding="utf-8") == "zip"
    assert (tmp_path / "from_tar.txt").read_text(encoding="utf-8") == "tar"


def test_huggingface_snapshot_uses_injected_fn(tmp_path: Path) -> None:
    calls: list[dict[str, object]] = []

    def fake_snapshot(**kwargs: object) -> str:
        calls.append(kwargs)
        Path(str(kwargs["local_dir"]), "marker.txt").write_text("ok", encoding="utf-8")
        return str(kwargs["local_dir"])

    dest = download_huggingface_snapshot(
        "org/demo",
        tmp_path / "hf",
        snapshot_download_fn=fake_snapshot,
    )

    assert dest == tmp_path / "hf"
    assert (dest / "marker.txt").is_file()
    assert calls[0]["repo_id"] == "org/demo"
    assert calls[0]["repo_type"] == "dataset"


def test_huggingface_file_uses_injected_fn(tmp_path: Path) -> None:
    def fake_file(**kwargs: object) -> str:
        saved = Path(str(kwargs["local_dir"])) / str(kwargs["filename"])
        saved.parent.mkdir(parents=True, exist_ok=True)
        saved.write_text("file", encoding="utf-8")
        return str(saved)

    saved = download_huggingface_file(
        "org/demo",
        "nested/item.bin",
        tmp_path / "hf-file",
        hf_hub_download_fn=fake_file,
    )

    assert saved.read_text(encoding="utf-8") == "file"


def test_url_download_uses_injected_fetch(tmp_path: Path) -> None:
    dest = tmp_path / "payload.bin"

    def fake_fetch(url: str, path: Path) -> None:
        path.write_text(url, encoding="utf-8")

    saved = download_url("https://example.test/data.zip", dest, fetch=fake_fetch)

    assert saved == dest
    assert dest.read_text(encoding="utf-8") == "https://example.test/data.zip"


@pytest.mark.network
def test_huggingface_downloads_tiny_public_file(hf_isolated_home: Path) -> None:
    saved = download_huggingface_file(
        "hf-internal-testing/tiny-random-bert",
        "config.json",
        hf_isolated_home / "dest",
        repo_type="model",
    )

    text = saved.read_text(encoding="utf-8")
    assert saved.is_file()
    assert saved.stat().st_size > 0
    assert "model_type" in text
