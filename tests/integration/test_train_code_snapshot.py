"""第 35 项：当次源码快照含未跟踪修改。"""

import tarfile
from pathlib import Path

from ai4e_core.run.session import run_recipe
from tests.integration.test_train_recipe import prepared_case


def test_snapshot_includes_untracked_source_change(tmp_path):
    folder, cfg = prepared_case(tmp_path)
    cfg.train.mode = "probe"
    cfg.train.snapshot = True
    marker = folder / "snapshot_marker.txt"
    marker.write_text("uncommitted-snapshot-marker", encoding="utf-8")
    before = set(Path(cfg.run_root).iterdir()) if Path(cfg.run_root).exists() else set()
    assert (
        run_recipe(
            cfg,
            stages={"train": lambda _: None},
            script=folder / "train.py",
            only=["train"],
            flags={"dry_run": False, "overwrite": False, "continue_on_error": False},
        )
        == 0
    )
    run_dir = (set(Path(cfg.run_root).iterdir()) - before).pop()
    archive = run_dir / "code.tar.gz"
    assert archive.is_file()
    with tarfile.open(archive, "r:gz") as bundle:
        names = bundle.getnames()
        matched = [name for name in names if name.endswith("snapshot_marker.txt")]
        assert matched
        extracted = bundle.extractfile(matched[0]).read().decode()
    assert "uncommitted-snapshot-marker" in extracted
