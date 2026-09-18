"""D1—D4：逐层物理状态、网格字段及部分交付门禁。"""

import json
from types import SimpleNamespace

import numpy as np
import pytest
import torch

from ai4e_contrib.ability.model.transolver3.inference import SurfaceInference
from ai4e_contrib.ability.model.transolver3.model import construct
from ai4e_core.abilities.postproc.export.field_surface import write_vtp
from ai4e_core.abilities.postproc.surface_geometry import SurfaceTopology
from ai4e_core.abilities.sampling.stride import reconstruct
from ai4e_core.applications.aero_cfd.infer.pointfields import complete
from ai4e_core.applications.aero_cfd.post.progress import PostProgress
from tests.integration.test_transolver_training import reference_module
from tools.verification.transolver3.compare import require


def test_every_layer_and_decoded_block():
    """D1：独立原缓存网络逐层汇总，全部缓存及解码块通过固定容差。"""
    ref = reference_module("Transolver_chunk_opt_matrix_mul_amortize.py")
    parameters = {
        "n_hidden": 16,
        "n_layers": 2,
        "n_head": 4,
        "mlp_ratio": 2,
        "slice_num": 4,
        "space_dim": 12,
        "fun_dim": 0,
        "out_dim": 4,
        "unified_pos": False,
    }
    torch.manual_seed(2)
    model = construct(**parameters)
    caching = ref.PhysicalStateCachingModel(**parameters).eval()
    decoding = ref.FullMeshDecodingModel(**parameters).eval()
    caching.load_state_dict(model.state_dict())
    decoding.load_state_dict(model.state_dict())
    chunks = [torch.randn(1, n, 12) for n in (9, 8, 8, 8)]
    states = []
    with torch.no_grad():
        for layer in range(2):
            num = den = None
            for x in chunks:
                _, a, b = caching([x], states, layer, use_checkpoint=False)
                num = a if num is None else num + a
                den = b if den is None else den + b
            states.append(num / (den[..., None] + 1e-5))
        outputs = [decoding([x], states, use_checkpoint=False)[0] for x in chunks]
    observed = []
    component = SurfaceInference(model)
    results = list(
        component.predict(
            lambda: ((i, {"features": x}) for i, x in enumerate(chunks)),
            observer=lambda _, i, x: observed.append(x.detach().clone()),
        )
    )
    for i, (actual, expected) in enumerate(zip(observed, states, strict=True)):
        require(actual.numpy(), expected.numpy(), identity=f"cache/{i}")
    for (i, actual), expected in zip(results, outputs, strict=True):
        require(actual["fields"].numpy(), expected.numpy(), identity=f"prediction/{i}")


def test_vtp_topology_and_fields(tmp_path):
    """D3：写出的网格保留原点序、真实单元及四场和向量模长。"""
    import vtk
    from vtk.util.numpy_support import vtk_to_numpy

    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32)
    normals = np.tile([0, 0, 1], (3, 1)).astype(np.float32)
    topology = SurfaceTopology(np.array([[0, 1, 2]]), np.empty((0, 4), dtype=np.int64), 3, 3)
    path = tmp_path / "mesh.vtp"
    truth = np.arange(12, dtype=np.float32).reshape(3, 4)
    write_vtp(
        path,
        topology=topology,
        points=points,
        normals=normals,
        area=np.full(3, 1 / 6, dtype=np.float32),
        conditions=np.arange(6, dtype=np.float32),
        truth=truth,
        prediction=truth + 1,
        labels=["cp", "cfx", "cfy", "cfz"],
        condition_names=list("abcdef"),
    )
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(str(path))
    reader.Update()
    mesh = reader.GetOutput()
    assert mesh.GetNumberOfCells() == 1
    np.testing.assert_array_equal(vtk_to_numpy(mesh.GetPoints().GetData()), points)
    np.testing.assert_array_equal(vtk_to_numpy(mesh.GetPolys().GetConnectivityArray()), [0, 1, 2])
    np.testing.assert_array_equal(
        vtk_to_numpy(mesh.GetPointData().GetArray("cp_prediction")), truth[:, 0] + 1
    )
    assert mesh.GetPointData().GetArray("cf_magnitude_error") is not None


def test_partial_delivery_and_missing_prediction(tmp_path):
    """D4：首个样本成功而后续失败，保留交付但不宣称分支完成。"""
    records = {}
    run = SimpleNamespace(
        report=lambda *a, **k: None,
        artifact=lambda k, v: records.update({k: json.loads(json.dumps(v))}),
    )
    progress = PostProgress(run, {"results": True})
    progress.report["operations"]["results"]["expected"] = 2
    with (
        progress.operation("results"),
        progress.unit([{"sample_id": "Sample001", "partition": "test"}]),
    ):
        progress.committed(tmp_path / "Sample001.h5")
    progress.finish(ValueError("second sample failed"))
    assert records["post-progress.json"]["status"] == "failed"
    result = records["post-progress.json"]["operations"]["results"]
    assert result["status"] == "partial" and result["completed"] == 1 and result["artifacts"]
    assert not complete(tmp_path, "wrong", 20, 4)
    with pytest.raises(ValueError):
        reconstruct([np.ones((2, 4), dtype=np.float32)], 3)


def test_preflight_and_selection_collision(tmp_path):
    """D4：干跑/提交共享覆盖门禁，选择顺序参与文件名，恢复显式放行重算。"""
    from ai4e_core.applications.aero_cfd.infer.pointfields import metrics_stem, preflight, select

    output = tmp_path / "out"
    output.mkdir()
    selected = ["Sample002", "Sample001"]
    assert metrics_stem(selected, False) != metrics_stem(selected[::-1], False)
    (output / (metrics_stem(selected, False) + ".json")).write_text("{}")
    with pytest.raises(FileExistsError):
        preflight(
            tmp_path / "pred",
            output,
            selected,
            selected,
            {"infer": False, "export_vtk": False, "export_hdf5": False},
        )
    preflight(tmp_path / "pred", output, selected, selected, {"resume": True})
    with pytest.raises(ValueError):
        select(selected, ["Sample999"])
    with pytest.raises(ValueError):
        select(selected, selected, all_samples=True)


def test_real_post_write_failure_and_retry(tmp_path, monkeypatch):
    """D4：真实HDF5写入失败保留首个交付，旧目录存在不能计入本次成功。"""
    import copy
    import os
    import subprocess
    import sys
    from pathlib import Path

    from omegaconf import OmegaConf

    from ai4e_contrib.ability.model.transolver3 import component
    from ai4e_contrib.application.datasets import nasa_crm
    from ai4e_core.applications.aero_cfd.infer import pointfields
    from tests.transolver_assets import configuration

    cfg, path = configuration(tmp_path)
    root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            str(root / "tools/verification/transolver3/dojo.py"),
            "--config",
            str(path),
        ],
        env={**os.environ, "OMP_NUM_THREADS": "1"},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    run_dir = next(Path(cfg.run_root).iterdir())
    config = OmegaConf.to_container(cfg, resolve=True)
    config["post"].update(
        checkpoint=str(run_dir / "checkpoints/best.pt"), infer=False, resume=True, overwrite=True
    )
    records = {}
    run = SimpleNamespace(
        run_dir=run_dir,
        dry_run=False,
        report=lambda *a, **k: None,
        artifact=lambda name, value: records.update({name: copy.deepcopy(value)}),
    )
    original = pointfields.write_h5

    def fail_second(path, **values):
        if path.stem == "Sample002":
            raise OSError("injected second sample failure")
        return original(path, **values)

    monkeypatch.setattr(pointfields, "write_h5", fail_second)
    with pytest.raises(OSError, match="second sample"):
        pointfields.execute(config, nasa_crm, component, run)
    progress = records["post-progress.json"]
    assert progress["status"] == "failed"
    results = progress["operations"]["results"]
    assert results["completed"] == 1 and results["status"] == "failed"
    assert results["samples"][-1]["samples"][0]["sample_id"] == "Sample002"
    assert results["samples"][-1]["samples"][0]["partition"] == "test"
    assert len(results["artifacts"]) == 1
    monkeypatch.setattr(pointfields, "write_h5", original)
    pointfields.execute(config, nasa_crm, component, run)
    assert records["post-progress.json"]["status"] == "succeeded"
    assert records["post-progress.json"]["operations"]["results"]["completed"] == 2
