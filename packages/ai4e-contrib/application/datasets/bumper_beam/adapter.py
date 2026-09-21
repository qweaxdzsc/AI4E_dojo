"""公开保险杠样本名单、原字段与工况身份绑定。"""

import json
from pathlib import Path

GLOBAL_FIELDS = ("velocity_x", "thickness_scale", "rwall_origin_y")


class BumperSource:
    """保留官方124/7分片，原网格及全部时间字段不删改。"""

    def __init__(self, root):
        root = Path(root)
        self.root = root / "CURATED_DATA_VTP" if (root / "CURATED_DATA_VTP").is_dir() else root
        self.global_features = json.loads((self.root / "GLOBAL_FEATURES.json").read_text())
        self.paths = {}
        for split, folder in [("train", "TRAINING_DATA"), ("validation", "VALIDATION_DATA")]:
            self.paths[split] = sorted(
                (self.root / folder).glob("*.vtp"), key=lambda p: int(p.stem.removeprefix("Run"))
            )
            if not self.paths[split]:
                raise ValueError(f"缺少 {split} VTP")

    def samples(self):
        """返回官方文件身份与分片，不随机重划。"""
        return [
            {"id": path.stem, "split": split, "index": i}
            for split, paths in self.paths.items()
            for i, path in enumerate(paths)
        ]

    def read(self, sample):
        """返回原网格及有序工况声明；时间转换留给 core。"""
        import pyvista as pv

        path = self.paths[sample["split"]][sample["index"]]
        values = self.global_features[path.stem]
        return pv.read(path), {
            "source": path.name,
            "global_fields": list(GLOBAL_FIELDS),
            "global_values": [values[key] for key in GLOBAL_FIELDS],
            "units": {
                "position": "mm",
                "time": "ms",
                "mass": "kg",
                "stress": "kg/(mm ms^2)",
                "strain": "1",
            },
        }
