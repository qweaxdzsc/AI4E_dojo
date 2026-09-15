from __future__ import annotations

import io
import tarfile

import pytest

from scripts.install_quarto import safe_extract_archive


def _write_tar(path, member_name: str, content: bytes = b"quarto"):
    with tarfile.open(path, "w:gz") as archive:
        member = tarfile.TarInfo(member_name)
        member.size = len(content)
        archive.addfile(member, io.BytesIO(content))


def _emulate_python_311(monkeypatch):
    original = tarfile.TarFile.extractall

    def legacy_extractall(self, path=".", members=None, *, numeric_owner=False):
        return original(
            self,
            path,
            members=members,
            numeric_owner=numeric_owner,
            filter="fully_trusted",
        )

    monkeypatch.setattr(tarfile.TarFile, "extractall", legacy_extractall)


def test_safe_extract_archive_supports_python_311_api(tmp_path, monkeypatch):
    archive_path = tmp_path / "quarto.tar.gz"
    output = tmp_path / "output"
    output.mkdir()
    _write_tar(archive_path, "quarto/bin/quarto")
    _emulate_python_311(monkeypatch)

    with tarfile.open(archive_path, "r:gz") as archive:
        safe_extract_archive(archive, output)

    assert (output / "quarto/bin/quarto").read_bytes() == b"quarto"


def test_safe_extract_archive_rejects_parent_traversal_on_python_311(tmp_path, monkeypatch):
    archive_path = tmp_path / "unsafe.tar.gz"
    output = tmp_path / "output"
    output.mkdir()
    _write_tar(archive_path, "../outside.txt")
    _emulate_python_311(monkeypatch)

    with tarfile.open(archive_path, "r:gz") as archive, pytest.raises(SystemExit, match="Unsafe archive path"):
        safe_extract_archive(archive, output)

    assert not (tmp_path / "outside.txt").exists()
