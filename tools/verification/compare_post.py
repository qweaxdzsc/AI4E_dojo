"""按官方测试身份比较真实后处理张量、锚点点云和完整网格，不以文件存在替代数值验收。"""

import argparse
import json
from pathlib import Path

import numpy as np
import torch
import yaml
from comparison_protocol import MODES, assess, read_protocol
from vtkmodules.util.numpy_support import vtk_to_numpy
from vtkmodules.vtkIOXML import vtkXMLPolyDataReader, vtkXMLUnstructuredGridReader


def compare(
    manifest: Path,
    dojo_root: Path,
    reference_run: Path,
    output: Path,
    summary: Path | None = None,
    *,
    mode="inference",
    actual_protocol=None,
    reference_protocol=None,
):
    """字段按样本身份对应；坐标与拓扑精确比较，浮点预测采用预声明 FP32 容差。"""
    report = {"samples": 0, "max_abs": {}, "failures": [], "rtol": 1e-5, "atol": 1e-6}
    eligibility = assess(read_protocol(actual_protocol), read_protocol(reference_protocol), mode)
    report["eligibility"] = eligibility
    numeric = eligibility["status"] == "comparable"

    def check(name, actual, expected, *, exact=False):
        a, b = np.asarray(actual), np.asarray(expected)
        same_shape = a.shape == b.shape
        if a.dtype != b.dtype:
            report["failures"].append(
                {
                    "kind": "contract",
                    "field": name,
                    "actual_dtype": str(a.dtype),
                    "reference_dtype": str(b.dtype),
                }
            )
        error = (
            float(np.max(np.abs(a.astype(float) - b.astype(float))))
            if same_shape and a.size
            else 0.0
        )
        report["max_abs"][name] = max(report["max_abs"].get(name, 0), error)
        is_prediction = any(
            token in name
            for token in ("pred_pressure", "pred_velocity", "error_pressure", "error_velocity")
        ) or name.split("/")[-1] in {"surface_pressure", "volume_velocity"}
        if is_prediction and not numeric:
            report["max_abs"].pop(name, None)
        passed = same_shape and (
            True
            if is_prediction and not numeric
            else np.array_equal(a, b)
            if exact
            else np.allclose(a, b, rtol=1e-5, atol=1e-6)
        )
        if not passed:
            report["failures"].append(
                {
                    "kind": "numerical" if is_prediction and same_shape else "contract",
                    "field": name,
                    "actual_shape": list(a.shape),
                    "reference_shape": list(b.shape),
                    "max_abs": error,
                }
            )

    def read(path):
        reader = vtkXMLPolyDataReader() if path.suffix == ".vtp" else vtkXMLUnstructuredGridReader()
        reader.SetFileName(str(path))
        reader.Update()
        return reader.GetOutput()

    def mesh(a_path, b_path, label):
        if not a_path.is_file() or not b_path.is_file():
            report["failures"].append({"field": label, "missing": True})
            return
        a, b = read(a_path), read(b_path)
        check(
            label + "/points",
            vtk_to_numpy(a.GetPoints().GetData()),
            vtk_to_numpy(b.GetPoints().GetData()),
            exact=True,
        )
        check(label + "/cells", [a.GetNumberOfCells()], [b.GetNumberOfCells()], exact=True)
        for getter in (
            ("GetVerts", "GetLines", "GetPolys", "GetStrips")
            if a_path.suffix == ".vtp"
            else ("GetCells",)
        ):
            for array in ("GetOffsetsArray", "GetConnectivityArray"):
                check(
                    label + "/" + getter + "/" + array,
                    vtk_to_numpy(getattr(getattr(a, getter)(), array)()),
                    vtk_to_numpy(getattr(getattr(b, getter)(), array)()),
                    exact=True,
                )
        for i in range(b.GetPointData().GetNumberOfArrays()):
            expected = b.GetPointData().GetArray(i)
            name = expected.GetName()
            actual = a.GetPointData().GetArray(name)
            if actual is None:
                report["failures"].append({"field": label + "/" + name, "missing": True})
            else:
                check(label + "/" + name, vtk_to_numpy(actual), vtk_to_numpy(expected))
        for i in range(b.GetCellData().GetNumberOfArrays()):
            expected = b.GetCellData().GetArray(i)
            actual = a.GetCellData().GetArray(expected.GetName())
            if actual is None:
                report["failures"].append(
                    {"field": label + "/cells/" + expected.GetName(), "missing": True}
                )
            else:
                check(
                    label + "/cells/" + expected.GetName(),
                    vtk_to_numpy(actual),
                    vtk_to_numpy(expected),
                    exact=True,
                )

    names = json.loads(manifest.read_text())["partitions"]["test"]
    for i, sample in enumerate(names):
        reference_path = reference_run / f"eval/predictions/sample_{i:04d}.pt"
        if not reference_path.is_file() or not (dojo_root / f"sample_{i:04d}.pt").is_file():
            report["failures"].append({"sample": sample, "missing": True})
            continue
        expected = torch.load(reference_path, weights_only=True)
        packed = torch.load(dojo_root / f"sample_{i:04d}.pt", weights_only=True)
        if packed.keys() != expected.keys():
            report["failures"].append({"field": f"packed/{i}", "keys_differ": True})
        for name, value in expected.items():
            named_path = dojo_root / sample / f"{name}.pt"
            if not named_path.is_file() or name not in packed:
                report["failures"].append({"sample": sample, "field": name, "missing": True})
                continue
            actual = torch.load(named_path, weights_only=True)
            check(name, actual.numpy(), value.numpy(), exact=name.endswith("position"))
            check(
                "packed/" + name,
                packed[name].numpy(),
                value.numpy(),
                exact=name.endswith("position"),
            )
        for domain in ("surface", "volume"):
            mesh(
                dojo_root / sample / f"{domain}.vtp",
                reference_run / f"eval/predictions/vtk/sample_{i:04d}_{domain}.vtp",
                "anchors/" + domain,
            )
        report["samples"] += 1
    for path in sorted((reference_run / "eval/mesh_vtk").glob("sample_*")):
        mesh(dojo_root / "mesh_vtk" / path.name, path, "mesh/" + path.stem)
    if summary and numeric:
        metrics = json.loads(summary.read_text())["reports"]["post"]["evaluation"]["metrics"]
        reference_metrics = yaml.safe_load(
            (reference_run / "eval/tracker/summary.yaml").read_text()
        )
        report["metrics"] = []
        for name, actual in metrics.items():
            field, method = name.split("/")
            key = f"loss/test/{field}_{'l2err' if method == 'relative_l2' else method}/min"
            expected = float(reference_metrics[key])
            value = actual["value"]
            passed = abs(value - expected) <= 1e-6 + 1e-5 * abs(expected)
            report["metrics"].append(
                {"metric": name, "actual": value, "reference": expected, "passed": passed}
            )
            if not passed:
                report["failures"].append({"kind": "numerical", "field": "metric/" + name})
    report["contract_passed"] = not any(
        item.get("kind", "contract") == "contract" for item in report["failures"]
    )
    report["passed"] = not report["failures"] and (mode == "contract" or numeric)
    output.write_text(json.dumps(report, indent=2))
    print(json.dumps({k: v for k, v in report.items() if k != "failures"}))
    print(f"差异项数: {len(report['failures'])}")
    if not report["passed"]:
        raise AssertionError(f"后处理未对齐: {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--dojo-root", type=Path, required=True)
    parser.add_argument("--reference-run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--mode", choices=MODES, default="inference")
    parser.add_argument("--actual-protocol", type=Path)
    parser.add_argument("--reference-protocol", type=Path)
    args = parser.parse_args()
    compare(
        args.manifest,
        args.dojo_root,
        args.reference_run,
        args.output,
        args.summary,
        mode=args.mode,
        actual_protocol=args.actual_protocol,
        reference_protocol=args.reference_protocol,
    )
