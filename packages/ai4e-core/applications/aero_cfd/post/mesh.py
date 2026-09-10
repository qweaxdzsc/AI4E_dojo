"""外流完整网格查询：测试下标、原始路径、固定锚点、分块回贴。"""

from functools import partial
from pathlib import Path

import numpy as np
import torch

from ai4e_core.abilities.data.extract.vtk_fields import extract_coordinates
from ai4e_core.abilities.data.source.read import read_file
from ai4e_core.abilities.inference.query import query_model
from ai4e_core.abilities.postproc.export.mesh import (
    extract_point_field,
    surface_mesh_point_count,
    verify_mesh_outputs,
    write_surface_mesh,
    write_volume_mesh,
)
from ai4e_core.abilities.training.batch import to_device
from ai4e_core.abilities.transform.coordinate_normalization import CoordinateNormalization
from ai4e_core.applications.aero_cfd.model.protocol import record_inputs
from ai4e_core.applications.aero_cfd.trainprep.dataset import prepare_partition_sample
from ai4e_core.base.events import sample_context

SURFACE_FILE = "quadpress_smpl.vtk"
VOLUME_FILE = "hexvelo_smpl.vtk"
MESH_FOLDER = "mesh_vtk"


def query_meshes(
    config, run, restored, *, prepare_inputs, collate, context_factory, progress=None, protocol=None
):
    """按测试下标查询原始顶点并提交表面/体积网格。"""
    settings = config.get("post") or {}
    split = str(settings.get("split") or config.get("train", {}).get("evaluation_split") or "test")
    samples = restored["index"].partitions.get(split) or []
    if not samples:
        raise ValueError(f"后处理查询分片缺失: {split}")
    indices = _sample_indices(settings)
    dest = Path(config["paths"]["datasets"]["predictions"]) / MESH_FOLDER
    if run.dry_run:
        return {"output": str(dest), "split": split, "indices": indices}
    written = []
    if progress:
        progress.report["meshes"] = written
    for index in indices:
        if index < 0 or index >= len(samples):
            raise IndexError(f"sample_indices 超出测试名单: {index}")
        sample_id = samples[index]
        samples = [{"sample_id": sample_id, "index": index}]
        with progress.unit(samples) if progress else sample_context("mesh", samples):
            surface_path, volume_path = raw_mesh_paths(config, sample_id)
            if not surface_path.is_file():
                raise FileNotFoundError(f"缺少原始表面网格: {surface_path}")
            if not volume_path.is_file():
                raise FileNotFoundError(f"缺少原始体积网格: {volume_path}")
            surface_data = read_file(surface_path)
            volume_data = read_file(volume_path)
            n_surface = surface_data.GetNumberOfPoints()
            n_volume = volume_data.GetNumberOfPoints()
            inputs = prepare_fixed_inputs(
                config,
                restored,
                prepare_inputs=prepare_inputs,
                collate=collate,
                split=split,
                item=index,
            )
            positions = {
                "surface": _model_positions(
                    restored["normalization"], extract_coordinates(surface_data)
                )[None],
                "volume": _model_positions(
                    restored["normalization"], extract_coordinates(volume_data)
                )[None],
            }
            if protocol is not None:
                record_inputs(protocol, "mesh", samples, inputs, positions)
            predicted = query_model(
                restored["model"],
                inputs,
                to_device(positions, next(restored["model"].parameters()).device),
                context_factory=context_factory,
                preparation_id=f"{restored['normalization'].digest}:{sample_id}:mesh",
                chunk_size=int(settings.get("query_chunk_size", 1024)),
            )
            pred_pressure = _physical_field(
                restored["normalization"], predicted, settings, "query_surface_pressure"
            )
            pred_velocity = _physical_field(
                restored["normalization"], predicted, settings, "query_volume_velocity"
            )
            if len(pred_pressure) != n_surface or len(pred_velocity) != n_volume:
                raise ValueError("反变换后的预测长度必须等于原始顶点数")
            stem = f"sample_{index:04d}"
            surface_out = dest / f"{stem}_surface.vtp"
            volume_out = dest / f"{stem}_volume.vtu"
            overwrite = bool(settings.get("overwrite", False))
            with sample_context("mesh.surface.save", samples):
                write_surface_mesh(
                    surface_data,
                    pred_pressure,
                    surface_out,
                    gt=extract_point_field(surface_data, kind="scalar", names=("pressure",)),
                    overwrite=overwrite,
                )
            if progress:
                progress.committed(surface_out)
            with sample_context("mesh.volume.save", samples):
                write_volume_mesh(
                    volume_data,
                    pred_velocity,
                    volume_out,
                    gt=extract_point_field(volume_data, kind="vector", names=("velocity",)),
                    overwrite=overwrite,
                )
            if progress:
                progress.committed(volume_out)
            verify_mesh_outputs(
                surface_out,
                volume_out,
                n_surface=surface_mesh_point_count(surface_data),
                n_volume=n_volume,
                min_points=settings.get("mesh_min_points"),
            )
            written.append(
                {
                    "index": index,
                    "sample_id": sample_id,
                    "surface": str(surface_out),
                    "volume": str(volume_out),
                    "points": {"surface": n_surface, "volume": n_volume},
                }
            )
    return {"output": str(dest), "split": split, "indices": indices, "meshes": written}


def prepare_fixed_inputs(config, restored, *, prepare_inputs, collate, split: str, item: int):
    """用训练评估同一入口准备几何和锚点，去掉预填充不允许的查询坐标。"""
    prepare = partial(
        prepare_inputs,
        data_specs=config["model"]["data_specs"],
        bindings=config["trainprep"],
    )
    sampled = prepare_partition_sample(
        restored["index"],
        split,
        item,
        prepare=prepare,
        normalization=restored["normalization"],
        physical_prepare=restored["physical_prepare"],
        normalized_input=restored["normalized_input"],
        sampling=config["sampling"],
        config=config,
        evaluation=True,
    )
    batch = to_device(collate([sampled]), next(restored["model"].parameters()).device)
    inputs = batch["inputs"]
    inputs.pop("domain_query_positions", None)
    inputs.pop("domain_query_features", None)
    return inputs


def raw_mesh_paths(config, sample_id: str) -> tuple[Path, Path]:
    """按案例数据根和设计号拼原始表面、体积文件。"""
    root = Path(config["dataset"]["root"])
    return root / sample_id / SURFACE_FILE, root / sample_id / VOLUME_FILE


def _sample_indices(settings) -> list[int]:
    raw = settings.get("sample_indices")
    if raw in (None, []):
        return [0]
    return [int(index) for index in raw]


def _model_positions(normalization, points) -> torch.Tensor:
    coords = torch.as_tensor(np.array(points, copy=True), dtype=torch.float32)
    transform = normalization.transforms["surface_position"]
    if isinstance(transform, CoordinateNormalization):
        return transform.apply(coords, check_range=False)
    return transform.apply(coords)


def _physical_field(normalization, predicted: dict, settings: dict, query_name: str):
    mapping = settings.get("denormalization") or {
        "query_surface_pressure": "surface_pressure",
        "query_volume_velocity": "volume_velocity",
    }
    if query_name not in predicted:
        raise KeyError(f"查询缺少预测场: {query_name}")
    value = predicted[query_name].detach().cpu().squeeze(0)
    physical = normalization.inverse(mapping[query_name], value)
    array = np.asarray(physical.numpy())
    if array.ndim == 2 and array.shape[-1] == 1:
        array = array.reshape(-1)
    return array
