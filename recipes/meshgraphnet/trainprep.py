"""为训练固定原始图样本引用；不改变物理字段。"""

from __future__ import annotations

import json
from pathlib import Path

from configuration import load_configuration, validate

from ai4e_contrib.application.spatiotemporal_pde.meshgraphnet.provenance import identity
from ai4e_core import run
from ai4e_core.abilities.data.save.bundle import file_digest, save_json


def trainprep(cfg, physical=None):
    """校验并登记供训练与推理消费的固定数据分片。"""
    cfg = validate(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    if physical is None:
        physical = cfg["inputs"]["trainprep"].get("dataset")
    if isinstance(physical, (str, Path)):
        raw = json.loads(Path(physical).read_text())
        physical = {
            split: value["path"] if isinstance(value, dict) else value
            for split, value in raw.get("splits", {}).items()
        }
    if not isinstance(physical, dict):
        raise TypeError("trainprep 需要 rawprep 返回的分片字典")
    output = session.output_dir("trainprep")
    prepared = {split: str(Path(path).resolve()) for split, path in physical.items()}
    if "valid" in prepared and "eval" not in prepared:
        prepared["eval"] = prepared["valid"]
    declarations = {
        split: {"path": path, "sha256": file_digest(path)} for split, path in prepared.items()
    }
    manifest = save_json(
        output / "manifest.json",
        {
            "kind": "meshgraphnet-cylinder-flow-prepared-v1",
            "splits": declarations,
            "provenance": identity(),
        },
    )
    session.record_asset(
        "prepared-manifest",
        manifest,
        kind="preparation",
        stage="trainprep",
        dependencies=sorted(set(prepared.values())),
        semantics={"kind": "meshgraphnet-cylinder-flow-prepared-v1"},
    )
    result = {**prepared, "manifest": manifest}
    session.report(result, stage="trainprep")
    return result


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"trainprep": trainprep},
            script=__file__,
            only=["trainprep"],
            config_loader=load_configuration,
        )
    )
