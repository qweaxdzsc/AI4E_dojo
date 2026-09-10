"""预测块、完整数值场、VTP 点序拓扑和指标的逐项比较。"""

import argparse
import csv
import json
from pathlib import Path

import h5py
import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy

from tools.verification.transolver3.compare import compare
from tools.verification.transolver3.compare_training import compare_state


def read_vtp(path):
    """通过 VTK 检查实际文件，不能用文件存在替代网格验收。"""
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(str(path))
    reader.Update()
    mesh = reader.GetOutput()
    result = {
        "points": vtk_to_numpy(mesh.GetPoints().GetData()),
        "connectivity": vtk_to_numpy(mesh.GetPolys().GetConnectivityArray()),
        "offsets": vtk_to_numpy(mesh.GetPolys().GetOffsetsArray()),
    }
    for label, data in (("point", mesh.GetPointData()), ("field", mesh.GetFieldData())):
        result[label] = {
            data.GetArrayName(i): vtk_to_numpy(data.GetArray(i))
            for i in range(data.GetNumberOfArrays())
        }
    return result


def main():
    """遍历固定44样本全部产物；缺文件、缺字段或局部超差均失败。"""
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in (
        "actual-predictions",
        "expected-predictions",
        "actual-post",
        "expected-post",
        "manifest",
        "output",
    ):
        parser.add_argument("--" + arg, type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    names = manifest["splits"]["test"]
    reports = []
    if len(names) != 44 or manifest["point_count"] != 454404:
        raise ValueError("正式后处理验收需要44样本与每样本454404点")
    for name in names:
        for i in range(manifest["chunk_count"]):
            filename = f"{name}/prediction_part{i}.npy"
            reports.append(
                compare(
                    np.load(args.actual_predictions / filename),
                    np.load(args.expected_predictions / filename),
                    identity=filename,
                )
            )
        for suffix in (".h5", ".vtp"):
            a, b = args.actual_post / (name + suffix), args.expected_post / (name + suffix)
            if suffix == ".h5":
                with h5py.File(a) as left, h5py.File(b) as right:
                    if set(left) != set(right):
                        raise ValueError(f"{name}: HDF5字段不一致")
                    for key in right:
                        reports.append(
                            compare(left[key][...], right[key][...], identity=f"{name}/h5/{key}")
                        )
                        compare_state(
                            dict(left[key].attrs),
                            dict(right[key].attrs),
                            f"{name}/h5/{key}/attributes",
                            reports,
                        )
                    compare_state(
                        dict(left.attrs), dict(right.attrs), f"{name}/h5/attributes", reports
                    )
            else:
                left, right = read_vtp(a), read_vtp(b)
                for key in ("points", "connectivity", "offsets"):
                    reports.append(compare(left[key], right[key], identity=f"{name}/vtp/{key}"))
                for section in ("point", "field"):
                    if set(left[section]) != set(right[section]):
                        raise ValueError(f"{name}/vtp/{section}: 字段不一致")
                    for key in right[section]:
                        reports.append(
                            compare(
                                left[section][key],
                                right[section][key],
                                identity=f"{name}/vtp/{section}/{key}",
                            )
                        )
    left = json.loads((args.actual_post / "metrics.json").read_text())
    right = json.loads((args.expected_post / "metrics.json").read_text())
    for key in (
        "sample_count",
        "selected_samples",
        "selection_mode",
        "vtk_exported",
        "topology",
        "samples",
        "aggregate",
    ):
        compare_state(left[key], right[key], f"metrics/{key}", reports)
    with (
        (args.actual_post / "metrics.csv").open() as a,
        (args.expected_post / "metrics.csv").open() as b,
    ):
        left = list(csv.DictReader(a))
        right = list(csv.DictReader(b))
        if len(left) != len(right):
            raise ValueError("CSV样本数量不一致")
        for a, b in zip(left, right, strict=True):
            if a.keys() != b.keys() or a["sample_id"] != b["sample_id"]:
                raise ValueError("CSV身份或字段不一致")
            for key in a:
                if key != "sample_id":
                    reports.append(
                        compare(
                            float(a[key]), float(b[key]), identity=f"csv/{a['sample_id']}/{key}"
                        )
                    )
    report = {
        "passed": all(r["passed"] for r in reports),
        "sample_count": len(names),
        "point_count": len(names) * manifest["point_count"],
        "mismatch_count": sum(r.get("mismatch_count", int(not r["passed"])) for r in reports),
        "max_absolute_error": max((r.get("max_absolute_error") or 0) for r in reports),
        "comparisons": reports,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2))
    print(json.dumps({k: v for k, v in report.items() if k != "comparisons"}))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
