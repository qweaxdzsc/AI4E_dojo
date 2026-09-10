"""完整网格回贴：下标、原始网格、坐标放宽、检查模式与门禁验收。"""

from functools import partial
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import torch
from omegaconf import OmegaConf
from vtkmodules.vtkCommonDataModel import vtkPolyData, vtkUnstructuredGrid
from vtkmodules.vtkIOXML import vtkXMLPolyDataWriter, vtkXMLUnstructuredGridWriter

from ai4e_contrib.ability.model.abupt.batch import collate
from ai4e_contrib.ability.model.abupt.model import construct
from ai4e_contrib.ability.model.abupt.sampling import prepare_inputs
from ai4e_core.abilities.data.source.read import read_file
from ai4e_core.abilities.postproc.export.mesh import (
    verify_mesh_outputs,
    write_surface_mesh,
    write_volume_mesh,
)
from ai4e_core.abilities.training.batch import to_device
from ai4e_core.abilities.transform.coordinate_normalization import CoordinateNormalization
from ai4e_core.applications.aero_cfd.post.mesh import prepare_fixed_inputs
from ai4e_core.applications.aero_cfd.post.stage import restore_model
from ai4e_core.applications.aero_cfd.train.resolve import apply_resolved
from ai4e_core.applications.aero_cfd.trainprep.dataset import prepare_partition_sample
from tests.integration.test_post_inference import _fit_then_post_config, _run_script
from tests.integration.test_shapenet_pre_recipe import _surface_quad, _volume_hex, _write_vtk
from tests.integration.test_train_recipe import prepared_case
from tests.support import SHAPENET_SAMPLES


def _query_config(cfg):
    _fit_then_post_config(cfg)
    cfg.post.query = True
    cfg.post.evaluate = False
    cfg.post.save_predictions = False
    cfg.post.export_vtk = False
    cfg.post.query_chunk_size = 1
    cfg.post.sample_indices = [0]
    return cfg


def _train_then_query(tmp_path, *, extra=None, post_extra=(), mutate=None):
    folder, cfg = prepared_case(tmp_path)
    _query_config(cfg)
    if extra:
        extra(cfg)
    result, directory, _ = _run_script(folder, cfg)
    assert result.returncode == 0, result.stderr
    cfg.post.checkpoint = str(directory / "checkpoints/last.pt")
    if mutate:
        mutate(cfg)
    return _run_script(folder, cfg, entry="post.py", extra=post_extra), folder, cfg


def _read_mesh_counts(surface_path, volume_path):
    from vtkmodules.vtkIOXML import vtkXMLPolyDataReader, vtkXMLUnstructuredGridReader

    surface = vtkXMLPolyDataReader()
    surface.SetFileName(str(surface_path))
    surface.Update()
    volume = vtkXMLUnstructuredGridReader()
    volume.SetFileName(str(volume_path))
    volume.Update()
    return surface.GetOutput(), volume.GetOutput()


def test_coordinate_apply_can_skip_range_check():
    transform = CoordinateNormalization((0.0,), (1.0,))
    inbound = torch.tensor([[0.25, 0.5, 0.75]])
    outbound = torch.tensor([[2.0, 0.0, 0.0]])
    torch.testing.assert_close(transform.apply(inbound), transform.apply(inbound, check_range=True))
    with pytest.raises(ValueError, match="超出"):
        transform.apply(outbound)
    relaxed = transform.apply(outbound, check_range=False)
    same = CoordinateNormalization((0.0,), (1.0,), check_range=False).apply(outbound)
    torch.testing.assert_close(relaxed, same)
    torch.testing.assert_close(relaxed[0, 0], torch.tensor(2000.0))


def test_full_mesh_query_writes_aligned_fields(tmp_path):
    (result, _, summary), _, cfg = _train_then_query(tmp_path)
    assert result.returncode == 0, result.stderr
    report = summary["reports"]["post"]
    assert report["mode"] == "post"
    assert report["indices"] == [0]
    item = report["meshes"][0]
    surface = Path(item["surface"])
    volume = Path(item["volume"])
    assert surface.name == "sample_0000_surface.vtp"
    assert volume.name == "sample_0000_volume.vtu"
    raw_surface = read_file(Path(cfg.dataset.root) / item["sample_id"] / "quadpress_smpl.vtk")
    raw_volume = read_file(Path(cfg.dataset.root) / item["sample_id"] / "hexvelo_smpl.vtk")
    written_surface, written_volume = _read_mesh_counts(surface, volume)
    assert written_surface.GetNumberOfPoints() == raw_surface.GetNumberOfPoints() == 4
    assert written_volume.GetNumberOfPoints() == raw_volume.GetNumberOfPoints() == 8
    assert written_surface.GetNumberOfCells() > 0
    assert written_volume.GetNumberOfCells() > 0
    assert written_surface.GetPointData().GetArray("pred_pressure") is not None
    assert written_volume.GetPointData().GetArray("pred_velocity") is not None
    assert written_surface.GetPointData().GetArray("gt_pressure") is not None
    assert written_volume.GetPointData().GetArray("gt_velocity") is not None
    verify_mesh_outputs(surface, volume, n_surface=4, n_volume=8)


def test_sample_index_out_of_range_writes_nothing(tmp_path):
    (result, _, summary), _, cfg = _train_then_query(
        tmp_path, mutate=lambda inner: setattr(inner.post, "sample_indices", [9])
    )
    assert result.returncode == 1
    assert summary["failed"]
    dest = Path(cfg.paths.datasets.predictions) / "mesh_vtk"
    assert not (dest / "sample_0009_surface.vtp").exists()
    assert not (dest / "sample_0009_volume.vtu").exists()


def test_missing_raw_surface_rejects(tmp_path):
    def remove_surface(cfg):
        (Path(cfg.dataset.root) / "b" / "quadpress_smpl.vtk").unlink()

    (result, _, summary), _, cfg = _train_then_query(tmp_path, mutate=remove_surface)
    assert result.returncode == 1
    assert summary["failed"]
    dest = Path(cfg.paths.datasets.predictions) / "mesh_vtk"
    assert not (dest / "sample_0000_surface.vtp").exists()


def test_query_geometry_matches_eval_prepare(tmp_path):
    (result, _, _), _, cfg = _train_then_query(
        tmp_path, extra=lambda cfg: setattr(cfg.post, "random_stream", "independent")
    )
    assert result.returncode == 0, result.stderr
    config = apply_resolved(OmegaConf.to_container(cfg, resolve=True), validate=False)
    restored = restore_model(
        config,
        SimpleNamespace(run_dir=Path(cfg.post.checkpoint).resolve().parents[1]),
        construct=construct,
    )
    first = prepare_fixed_inputs(
        config,
        restored,
        prepare_inputs=prepare_inputs,
        collate=collate,
        split="test",
        item=0,
    )
    second = prepare_fixed_inputs(
        config,
        restored,
        prepare_inputs=prepare_inputs,
        collate=collate,
        split="test",
        item=0,
    )
    prepare = partial(
        prepare_inputs,
        data_specs=config["model"]["data_specs"],
        bindings=config["trainprep"],
    )
    sampled = prepare_partition_sample(
        restored["index"],
        "test",
        0,
        prepare=prepare,
        normalization=restored["normalization"],
        physical_prepare=restored["physical_prepare"],
        normalized_input=restored["normalized_input"],
        sampling=config["sampling"],
        config=config,
        evaluation=True,
    )
    expected = to_device(collate([sampled]), restored["device"])["inputs"]
    expected.pop("domain_query_positions", None)
    expected.pop("domain_query_features", None)
    for name in ("geometry_position", "geometry_supernode_idx", "geometry_batch_idx"):
        torch.testing.assert_close(first[name], expected[name])
        torch.testing.assert_close(second[name], expected[name])
    for domain, points in expected["domain_anchor_positions"].items():
        torch.testing.assert_close(first["domain_anchor_positions"][domain], points)
        torch.testing.assert_close(second["domain_anchor_positions"][domain], points)


def test_dry_run_writes_no_mesh(tmp_path):
    (result, _, summary), _, cfg = _train_then_query(tmp_path, post_extra=("--dry-run",))
    assert result.returncode == 0, result.stderr
    assert summary["reports"]["post"]["mode"] == "post_check"
    assert not (Path(cfg.paths.datasets.predictions) / "mesh_vtk").exists()


def test_verify_rejects_missing_pred_or_cells(tmp_path):
    empty_surface = tmp_path / "empty_surface.vtp"
    empty_volume = tmp_path / "empty_volume.vtu"
    writer = vtkXMLPolyDataWriter()
    writer.SetFileName(str(empty_surface))
    writer.SetInputData(vtkPolyData())
    writer.Write()
    writer = vtkXMLUnstructuredGridWriter()
    writer.SetFileName(str(empty_volume))
    writer.SetInputData(vtkUnstructuredGrid())
    writer.Write()
    with pytest.raises(RuntimeError, match="没有面单元"):
        verify_mesh_outputs(empty_surface, empty_volume, n_surface=0, n_volume=0)

    surface = tmp_path / "cells_surface.vtp"
    volume = tmp_path / "cells_volume.vtu"
    raw_surface = tmp_path / "raw_surface.vtk"
    raw_volume = tmp_path / "raw_volume.vtk"
    _write_vtk(raw_surface, _surface_quad())
    _write_vtk(raw_volume, _volume_hex())
    from vtkmodules.vtkFiltersGeometry import vtkDataSetSurfaceFilter

    filt = vtkDataSetSurfaceFilter()
    filt.SetInputData(read_file(raw_surface))
    filt.Update()
    writer = vtkXMLPolyDataWriter()
    writer.SetFileName(str(surface))
    writer.SetInputData(filt.GetOutput())
    writer.Write()
    write_volume_mesh(read_file(raw_volume), np.zeros((8, 3)), volume)
    with pytest.raises(RuntimeError, match="缺少 pred_pressure"):
        verify_mesh_outputs(surface, volume, n_surface=4, n_volume=8)


@pytest.mark.local_data
def test_official_sample_mesh_points_exceed_anchors(shapenet_raw, tmp_path):
    sample = shapenet_raw / SHAPENET_SAMPLES[0]
    surface_path = sample / "quadpress_smpl.vtk"
    volume_path = sample / "hexvelo_smpl.vtk"
    if not surface_path.is_file() or not volume_path.is_file():
        pytest.skip(f"本地官方样本不完整: {sample}")
    surface = read_file(surface_path)
    volume = read_file(volume_path)
    assert surface.GetNumberOfPoints() > 256
    assert volume.GetNumberOfPoints() > 256
    out_surface = tmp_path / "sample_0000_surface.vtp"
    out_volume = tmp_path / "sample_0000_volume.vtu"
    write_surface_mesh(surface, np.zeros(surface.GetNumberOfPoints()), out_surface)
    write_volume_mesh(volume, np.zeros((volume.GetNumberOfPoints(), 3)), out_volume)
    verify_mesh_outputs(out_surface, out_volume, min_points=256)


def test_mesh_query_accepts_unused_surface_vertices(tmp_path):
    """真实 ShapeNet 表面有未被面单元引用的顶点，提取后不能按原点数误报失败。"""

    def add_unused_vertex(cfg):
        path = Path(cfg.dataset.root) / "b" / "quadpress_smpl.vtk"
        mesh = read_file(path)
        mesh.GetPoints().InsertNextPoint(0.5, 0.5, 0.5)
        attrs = mesh.GetPointData()
        for i in range(attrs.GetNumberOfArrays()):
            attrs.GetArray(i).InsertNextTuple(attrs.GetArray(i).GetTuple(0))
        _write_vtk(path, mesh)

    (result, _, summary), _, _ = _train_then_query(tmp_path, mutate=add_unused_vertex)
    assert result.returncode == 0, result.stderr
    record = summary["reports"]["post"]["meshes"][0]
    surface, _ = _read_mesh_counts(record["surface"], record["volume"])
    assert record["points"]["surface"] == 5
    assert surface.GetNumberOfPoints() == 4


@pytest.mark.skipif(not torch.backends.mps.is_available(), reason="需要真实 Apple GPU")
def test_mps_train_then_complete_mesh_query(tmp_path):
    def mps_config(cfg):
        cfg.train.device = "mps"

    (result, _, summary), _, _ = _train_then_query(tmp_path, extra=mps_config)
    assert result.returncode == 0, result.stderr
    assert len(summary["reports"]["post"]["meshes"]) == 1
