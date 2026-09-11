"""严格实体身份差值，不插值、不配准，也不根据点数猜测可比性。"""

import json
from pathlib import Path

import torch

from ai4e_core.abilities.data.save.arrays import save_json
from ai4e_core.abilities.data.save.store import load_named_tensor, write_tensor_file
from ai4e_core.abilities.postproc.coordinate_space import coordinate_space


def difference(left: dict, right: dict) -> torch.Tensor:
    """校验来源、归属、单位、实体 ID、坐标和拓扑后执行 left-right。"""
    if coordinate_space(left.get("coordinate_space")) != coordinate_space(
        right.get("coordinate_space")
    ):
        raise ValueError("差值不可比: coordinate_space 缺失或不一致")
    for key in ("entity_set", "association", "unit", "topology"):
        if key not in left or key not in right or left[key] is None or left[key] != right[key]:
            raise ValueError(f"差值不可比: {key} 缺失或不一致")
    for key in ("ids", "coordinates"):
        if key not in left or key not in right or not torch.equal(left[key], right[key]):
            raise ValueError(f"差值不可比: {key} 不一致")
    ids = left["ids"]
    if ids.dtype != torch.int64 or ids.ndim != 1 or len(ids.unique()) != len(ids):
        raise ValueError("差值实体 ID 必须唯一 int64")
    a, b = left["values"], right["values"]
    if (
        a.shape != b.shape
        or a.shape[0] != len(ids)
        or not a.is_floating_point()
        or not b.is_floating_point()
    ):
        raise ValueError("差值形状或浮点类型不一致")
    if not torch.isfinite(a).all() or not torch.isfinite(b).all():
        raise ValueError("差值包含无效数值")
    return a - b


def compare_files(inputs: list[dict], output_dir: Path, options: dict) -> dict:
    """读取 task 已校验的两个张量资产和身份清单，原子发布差值。"""
    if len(inputs) != 2:
        raise ValueError("差值需要两个固定输入")
    records = []
    for item in inputs:
        tensors = load_named_tensor(item["path"])
        metadata = json.loads(Path(item["metadata_path"]).read_text())
        if "filemap" in metadata and "domains" in metadata:
            matches = [
                key
                for key, filename in metadata["filemap"].items()
                if Path(filename).name == Path(item["path"]).name
            ]
            if len(matches) != 1:
                raise ValueError("预测字段引用不唯一")
            logical = matches[0]
            expected = Path(item["metadata_path"]).parent / metadata["filemap"][logical]
            if Path(item["path"]).resolve() != expected.resolve():
                raise ValueError("预测字段与其清单引用路径不一致")
            domain, field, kind = logical.split(".")
            if kind not in {"prediction", "truth"}:
                raise ValueError("差值需选择预测或真值字段")
            declaration = metadata["domains"][domain]
            root = Path(item["metadata_path"]).parent

            def member(name, metadata=metadata, root=root):
                relative = Path(metadata["filemap"][name])
                if relative.name != str(relative):
                    raise ValueError("预测字段路径越界")
                return load_named_tensor(root / relative)

            records.append(
                {
                    "values": tensors,
                    "coordinate_space": declaration.get("coordinate_space"),
                    "ids": member(declaration["ids"]),
                    "coordinates": member(declaration["position"]),
                    "association": "point",
                    "unit": declaration.get("units", {}).get(field),
                    "topology": declaration.get("topology"),
                    "entity_set": declaration.get("entity_set"),
                }
            )
        else:
            records.append({**metadata, **tensors})
    values = difference(*records)
    path = write_tensor_file(
        output_dir / "difference.pt",
        {"values": values, "ids": records[0]["ids"], "coordinates": records[0]["coordinates"]},
    )
    save_json(
        output_dir / "difference.json",
        {
            **{k: records[0][k] for k in ("entity_set", "association", "unit", "topology")},
            "coordinate_space": coordinate_space(records[0].get("coordinate_space")),
        },
    )
    return {
        "path": str(path),
        "metadata_path": str(output_dir / "difference.json"),
        "shape": list(values.shape),
        "operation": "left-right",
    }
