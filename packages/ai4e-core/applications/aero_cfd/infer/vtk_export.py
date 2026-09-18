"""推理 VTK 交付：默认写出预测与真值，跳过必须留下原因。"""

from __future__ import annotations

import json
from pathlib import Path

from ai4e_core.abilities.data.save.arrays import save_json
from ai4e_core.abilities.data.save.store import load_named_tensor
from ai4e_core.abilities.postproc.export.pointcloud import write_pointcloud
from ai4e_core.base.events import event

VTK_DISABLED = "用户关闭了导出 VTK 网格化数据"
VTK_POINTCLOUD_DISABLED = "用户关闭了导出点云数据"
VTK_MESH_DISABLED = VTK_DISABLED
VTK_NO_PREDICTION = "未保存预测，无法写出 VTK"
VTK_NO_SOURCE_ROOT = "缺少原始数据根（dataset.root 或 inputs.rawprep.source），不能回贴完整网格"
VTK_NO_SOURCE_MESH = "找不到原始表面/体积网格，不能回贴完整网格"
VTK_ANCHOR_KIND = "anchor_pointcloud"
VTK_FULL_KIND = "full_source_mesh"


def original_dataset_root(config: dict) -> Path | None:
    """原始网格根目录；平台配置常把路径放在 inputs.rawprep.source，不回写用户树。"""
    dataset = config.get("dataset") if isinstance(config.get("dataset"), dict) else {}
    raw = (
        (config.get("inputs") or {}).get("rawprep")
        if isinstance(config.get("inputs"), dict)
        else {}
    )
    raw = raw if isinstance(raw, dict) else {}
    value = dataset.get("root") or raw.get("source")
    if isinstance(value, str) and value.strip():
        return Path(value)
    return None


def sample_identity(metadata: dict, *, fallback: str | None = None) -> dict:
    """稳定样本身份；外流沿用 param1/<设计号>，与处理后目录同一编号。"""
    identity = metadata.get("identity") if isinstance(metadata.get("identity"), dict) else {}
    sample = identity.get("sample") or metadata.get("sample") or fallback
    split = identity.get("split") or metadata.get("split")
    if not sample:
        raise ValueError("推理 VTK 需要 sample_id")
    return {
        "sample_id": str(sample),
        "source_sample_id": str(identity.get("source_sample") or sample),
        "split": None if split in (None, "") else str(split),
    }


def vtk_status(
    *, exported: bool, reason: str | None = None, kind: str | None = None, **extra
) -> dict:
    """给清单和页面的跳过/成功记录，不能只用缺文件表示关闭。"""
    return {"exported": bool(exported), "reason": reason, "kind": kind, **extra}


def _channel_record(status: dict) -> dict:
    return {
        key: status[key]
        for key in ("exported", "reason", "kind")
        if key in status and (key != "kind" or status[key] is not None)
    }


def record_vtk_status(
    manifest_path: str | Path, status: dict, *, channel: str | None = None
) -> dict:
    """把 VTK 状态写进样本清单；点云与网格化分频道，跳过一种不盖掉另一种。"""
    path = Path(manifest_path)
    metadata = json.loads(path.read_text())
    current = dict(metadata.get("vtk") or {})
    channel = channel or status.get("channel")
    payload = {key: value for key, value in status.items() if key != "channel"}
    if channel in {"pointcloud", "mesh"}:
        record = dict(current.get(channel) or {})
        record.update(_channel_record(payload))
        current[channel] = record
        for key in ("sample_id", "source_sample_id", "split", "domains"):
            if key in payload:
                current[key] = payload[key]
    else:
        current.update(payload)
        if payload.get("exported") is False:
            mesh = dict(current.get("mesh") or {})
            if mesh.get("exported") is not True:
                mesh["exported"] = False
                mesh.setdefault("reason", payload.get("reason"))
                current["mesh"] = mesh
    pointcloud = current.get("pointcloud") if isinstance(current.get("pointcloud"), dict) else {}
    mesh = current.get("mesh") if isinstance(current.get("mesh"), dict) else {}
    current["exported"] = bool(pointcloud.get("exported") or mesh.get("exported"))
    if pointcloud.get("exported") and mesh.get("exported") is False:
        current["exported"] = True
        current["kind"] = pointcloud.get("kind") or current.get("kind")
        current["reason"] = mesh.get("reason")
    elif current["exported"]:
        current["kind"] = (
            (mesh.get("kind") if mesh.get("exported") else None)
            or pointcloud.get("kind")
            or current.get("kind")
        )
        current.pop("reason", None)
    else:
        current["reason"] = mesh.get("reason") or pointcloud.get("reason") or payload.get("reason")
    metadata["vtk"] = current
    save_json(path, metadata)
    return current


def skip_vtk(
    manifest_path: str | Path, reason: str, *, channel: str | None = None, **extra
) -> dict:
    """明确记录未写出 VTK 的原因，并打阶段日志。"""
    identity = sample_identity(
        json.loads(Path(manifest_path).read_text()), fallback=Path(manifest_path).parent.name
    )
    event("网格", "跳过", 原因=reason, sample_id=identity["sample_id"], **extra)
    return record_vtk_status(
        manifest_path,
        vtk_status(exported=False, reason=reason, sample_id=identity["sample_id"], **extra),
        channel=channel,
    )


def write_anchor_prediction_vtk(
    manifest_path: str | Path, *, overwrite: bool = False, committed=None
) -> dict:
    """把已保存的预测和真值写成同目录点云 VTK，场名沿用 ``.prediction`` / ``.truth``。

    锚点没有完整单元，不能冒充原始网格；完整网格由查询步骤另行交付。
    """
    manifest_path = Path(manifest_path)
    metadata = json.loads(manifest_path.read_text())
    identity = sample_identity(metadata, fallback=manifest_path.parent.name)
    root = manifest_path.parent
    meshes = metadata.setdefault("meshes", {})

    def read(name: str):
        filename = Path(metadata["filemap"][name])
        if filename.name != str(filename):
            raise ValueError("预测成员路径越界")
        return load_named_tensor(root / filename).numpy()

    written = {}
    for domain, declaration in (metadata.get("domains") or {}).items():
        points = read(declaration["position"])
        fields = {}
        for key in declaration.get("targets", {}).values():
            for suffix in (".prediction", ".truth"):
                name = key + suffix
                if name in metadata.get("filemap", {}):
                    fields[name] = read(name)
        if not fields:
            continue
        destination = root / (domain + ".vtp")
        if destination.exists() and not overwrite:
            raise FileExistsError(str(destination))
        write_pointcloud(
            destination,
            points,
            fields,
            field_data={
                "sample_id": identity["sample_id"],
                "source_sample_id": identity["source_sample_id"],
                **({} if identity["split"] is None else {"split": identity["split"]}),
            },
        )
        if committed:
            committed(destination)
        record = {
            "path": destination.name,
            "entity_set": "sampled_anchors",
            "association": "point",
            "kind": VTK_ANCHOR_KIND,
            "fields": list(fields),
            "point_count": len(points),
            "sample_id": identity["sample_id"],
            "source_sample_id": identity["source_sample_id"],
            "split": identity["split"],
        }
        if domain in meshes and meshes[domain].get("entity_set") == "full_source_mesh":
            meshes[domain + "_anchors"] = record
        else:
            meshes[domain] = record
        written[domain] = record
    if not written:
        return skip_vtk(manifest_path, "已保存预测没有可写到 VTK 的物理场", channel="pointcloud")
    save_json(manifest_path, metadata)
    record_vtk_status(
        manifest_path,
        vtk_status(
            exported=True,
            kind=VTK_ANCHOR_KIND,
            sample_id=identity["sample_id"],
            source_sample_id=identity["source_sample_id"],
            split=identity["split"],
            domains=sorted(written),
        ),
        channel="pointcloud",
    )
    event(
        "网格",
        "写出",
        sample_id=identity["sample_id"],
        文件=",".join(item["path"] for item in written.values()),
    )
    return written


def merge_full_mesh_record(metadata: dict, domain: str, record: dict) -> None:
    """完整网格占用域键；已有锚点点云改挂 ``{domain}_anchors``。"""
    meshes = metadata.setdefault("meshes", {})
    current = meshes.get(domain)
    if current and current.get("entity_set") != "full_source_mesh":
        meshes[domain + "_anchors"] = current
    meshes[domain] = record


def stamp_mesh_identity(path: str | Path, identity: dict) -> None:
    """给已写出的 VTP/VTU 补样本身份，不改点场。"""
    import vtk

    target = Path(path)
    if target.suffix.lower() == ".vtp":
        reader, writer = vtk.vtkXMLPolyDataReader(), vtk.vtkXMLPolyDataWriter()
    else:
        reader, writer = vtk.vtkXMLUnstructuredGridReader(), vtk.vtkXMLUnstructuredGridWriter()
    reader.SetFileName(str(target))
    reader.Update()
    mesh = reader.GetOutput()
    for name in ("sample_id", "source_sample_id", "split"):
        value = identity.get(name)
        if not value:
            continue
        array = vtk.vtkStringArray()
        array.SetName(name)
        array.InsertNextValue(str(value))
        mesh.GetFieldData().AddArray(array)
    writer.SetFileName(str(target))
    writer.SetInputData(mesh)
    writer.SetDataModeToAppended()
    if writer.Write() != 1:
        raise OSError(f"写入 VTK 样本身份失败: {target}")
