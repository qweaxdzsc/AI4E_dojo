"""点云与网格化导出开关、训练集 VTK 还原能力。"""

import importlib.util
from pathlib import Path

import vtk

import ai4e_spec.artifacts.inference as _installed_spec
from ai4e_contrib.application.datasets import nasa_crm, shapenet_car

_ROOT = Path(__file__).resolve().parents[2]


def _load(name: str, relative: str):
    path = _ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


_mesh = _load("infer_vtk_mesh_src", "packages/ai4e-core/abilities/postproc/export/mesh.py")
_capability = _load(
    "infer_vtk_capability_src",
    "packages/ai4e-core/applications/aero_cfd/infer/vtk_capability.py",
)
_inference = _load("infer_vtk_spec_src", "packages/ai4e-spec/artifacts/inference.py")
_installed_spec.apply_export_aliases = _inference.apply_export_aliases
_configuration = _load(
    "infer_vtk_configuration_src",
    "packages/ai4e-core/applications/aero_cfd/infer/configuration.py",
)
_vtk_export = _load(
    "infer_vtk_export_src",
    "packages/ai4e-core/applications/aero_cfd/infer/vtk_export.py",
)

mesh_topology_kind = _mesh.mesh_topology_kind
describe_vtk_exports = _capability.describe_vtk_exports
resolve_infer = _configuration.resolve_infer
InferenceRequest = _inference.InferenceRequest
apply_export_aliases = _inference.apply_export_aliases
skip_vtk = _vtk_export.skip_vtk
record_vtk_status = _vtk_export.record_vtk_status
vtk_status = _vtk_export.vtk_status
VTK_DISABLED = _vtk_export.VTK_DISABLED


def test_mesh_topology_kind_distinguishes_pointcloud_and_surface():
    points = vtk.vtkPoints()
    points.InsertNextPoint(0, 0, 0)
    cloud = vtk.vtkPolyData()
    cloud.SetPoints(points)
    verts = vtk.vtkCellArray()
    verts.InsertNextCell(1)
    verts.InsertCellPoint(0)
    cloud.SetVerts(verts)
    assert mesh_topology_kind(cloud) == "pointcloud"

    surface = vtk.vtkPolyData()
    surface.SetPoints(points)
    polys = vtk.vtkCellArray()
    polys.InsertNextCell(3)
    polys.InsertCellPoint(0)
    polys.InsertCellPoint(0)
    polys.InsertCellPoint(0)
    surface.SetPolys(polys)
    assert mesh_topology_kind(surface) == "surface"


def test_shapenet_declaration_enables_mesh_export():
    value = describe_vtk_exports({"dataset": {"root": "/tmp"}}, dataset_component=shapenet_car)
    assert value["pointcloud"]["available"] is True
    assert value["pointcloud"]["include_truth"] is True
    assert value["mesh"]["available"] is True
    assert value["mesh"]["include_truth"] is True
    assert "source_vtk" in value["mesh"]["sources"]


def test_nasa_connectivity_enables_mesh_export():
    value = describe_vtk_exports(
        {"dataset": {"connectivity_h5": "/tmp/conn.h5"}}, dataset_component=nasa_crm
    )
    assert value["mesh"]["available"] is True
    assert "connectivity" in value["mesh"]["sources"]
    assert value["mesh"]["structured"] is False


def test_nasa_unbound_disables_mesh_export():
    value = describe_vtk_exports({}, dataset_component=nasa_crm)
    assert value["mesh"]["available"] is False
    assert value["mesh"]["reason"] == "训练集没有可还原的 VTK 网格"


def test_vtkhdf_output_flag_does_not_enable_mesh_export():
    value = describe_vtk_exports({"rawprep": {"vtkhdf": True}}, dataset_component=None)
    assert value["mesh"]["available"] is False


def test_tensor_only_dataset_disables_mesh_export():
    value = describe_vtk_exports({"dataset": {}}, dataset_component=None)
    assert value["pointcloud"]["available"] is True
    assert value["mesh"]["available"] is False
    assert value["mesh"]["reason"] == "训练集没有可还原的 VTK 网格"


def test_old_export_vtk_false_disables_both_outputs():
    cfg = resolve_infer({"infer": {"samples": ["a"], "export_vtk": False}})
    assert cfg["infer"]["export_pointcloud"] is False
    assert cfg["infer"]["export_mesh"] is False
    assert cfg["infer"]["export_vtk"] is False


def test_split_keys_keep_pointcloud_when_mesh_off():
    cfg = resolve_infer(
        {"infer": {"samples": ["a"], "export_pointcloud": True, "export_mesh": False}}
    )
    assert cfg["infer"]["export_pointcloud"] is True
    assert cfg["infer"]["export_mesh"] is False
    assert cfg["infer"]["export_vtk"] is False


def test_inference_request_accepts_split_export_options():
    value = InferenceRequest.from_dict(
        {
            "expected_revision": "config",
            "checkpoints": [{"id": "r", "revision": "sha"}],
            "samples": ["a"],
            "options": {
                "evaluate": True,
                "save_predictions": True,
                "export_pointcloud": True,
                "export_mesh": False,
            },
        }
    )
    assert value.options["export_pointcloud"] is True
    assert value.options["export_mesh"] is False
    assert value.options["export_vtk"] is False


def test_old_export_vtk_false_evaluate_only_accepted():
    value = InferenceRequest.from_dict(
        {
            "expected_revision": "config",
            "checkpoints": [{"id": "r", "revision": "sha"}],
            "samples": ["a"],
            "options": {
                "evaluate": True,
                "save_predictions": False,
                "export_vtk": False,
                "export_pointcloud": None,
                "export_mesh": None,
            },
        }
    )
    assert value.options["export_pointcloud"] is False
    assert value.options["export_mesh"] is False
    assert value.options["evaluate"] is True


def test_absent_new_keys_follow_old_export_vtk():
    options = apply_export_aliases({"export_vtk": False, "evaluate": True})
    assert options["export_pointcloud"] is False
    assert options["export_mesh"] is False


def test_skip_mesh_keeps_pointcloud_status(tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text('{"identity": {"sample": "s"}}')
    record_vtk_status(
        path,
        vtk_status(exported=True, kind="anchor_pointcloud", sample_id="s"),
        channel="pointcloud",
    )
    status = skip_vtk(path, VTK_DISABLED, channel="mesh")
    assert status["exported"] is True
    assert status["pointcloud"]["exported"] is True
    assert status["mesh"]["exported"] is False
    assert status["mesh"]["reason"] == VTK_DISABLED
