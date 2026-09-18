"""独立场检查点组成固定耦合模型组，禁止暗中选最新权重。"""

from pathlib import Path

import torch

from ai4e_core.abilities.data.save.arrays import save_json

from .contracts import digest, file_digest, read_record


def bind_checkpoint_group(checkpoints, path, *, required_fields):
    """冻结权重字节与各场训练契约；各场更新次数可以不同。"""
    if set(checkpoints) != set(required_fields):
        raise ValueError("耦合权重缺场或多场")
    members = {}
    for field, checkpoint in checkpoints.items():
        state = torch.load(checkpoint, map_location="cpu", weights_only=False)
        contract = state["contract"]
        if contract["field"] != field:
            raise ValueError("权重所属物理场不匹配")
        members[field] = {
            "path": str(Path(checkpoint).resolve()),
            "sha256": file_digest(checkpoint),
            "contract": contract,
            "updates": state["updates"],
        }
    if len({v["contract"]["system_id"] for v in members.values()}) != 1:
        raise ValueError("耦合权重的数据与归一化系统不兼容")
    record = {"kind": "coupled_weights_v1", "fields": members}
    record["content_id"] = digest(record)
    path = Path(path)
    if path.exists() and read_record(path, "coupled_weights_v1") != record:
        raise FileExistsError("权重组已存在；替换场权重须新建组合")
    save_json(path, record)
    return str(path.resolve())


def load_checkpoint_group(path, *, system_id, construct, device):
    """按固定字节重建网络；不允许以不同准备或最新权重替代。"""
    record = read_record(path, "coupled_weights_v1")
    models = {}
    for field, member in record["fields"].items():
        if (
            member["contract"]["system_id"] != system_id
            or file_digest(member["path"]) != member["sha256"]
        ):
            raise ValueError("权重组准备或权重内容发生变化")
        model = construct(member["contract"]["model"]).to(device)
        state = torch.load(member["path"], map_location=device, weights_only=False)
        model.load_state_dict(state["model"], strict=True)
        models[field] = model
    return models, record
