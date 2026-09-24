"""原始发布轨迹：逐样本读取、保存、身份交接由正文明确连接。"""

from configuration import component
from local_data import read_record

from ai4e_core.abilities.data.save.arrays import save_json
from ai4e_core.run import TrainingRun


def rawprep(cfg):
    """只筛选训练与验证发布成员，不消费预整理张量或隐藏集。"""
    session = TrainingRun()
    output = session.output_dir("rawprep")
    manifest = read_record(cfg["inputs"]["rawprep"]["manifest"])
    samples = [
        {"split": split, "entry": entry}
        for split in ["train", "validation"]
        for entry in manifest[split]
    ]
    reader = component(cfg["components"]["reader"])(
        cfg["inputs"]["rawprep"]["source"], cfg["science"]["fields"], output
    )
    records = session.execute_samples(samples, reader, stage="rawprep")
    physical = {
        split: [r for r in records if r["split"] == split] for split in ["train", "validation"]
    }
    path = output / "physical.json"
    save_json(path, physical)
    session.record_asset(
        "physical",
        path,
        kind="dataset",
        stage="rawprep",
        dependencies=[r["manifest"] for r in records],
    )
    session.report({"physical": str(path), "trajectories": len(records)}, stage="rawprep")
    return str(path)
