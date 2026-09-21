"""真实外流配置的测速、独立参考训练与完整预测对照，产物只写研究目录。"""

import argparse
import json
import resource
import time
from pathlib import Path

import numpy as np
import torch

from ai4e_contrib.application.aero_cfd.configuration import (
    application_parameters,
    load_components,
    load_configuration,
)
from ai4e_core.abilities.sampling.points import point_indices
from ai4e_core.applications.aero_cfd.trainprep import physical
from ai4e_core.applications.aero_cfd.trainprep.point_inputs import prepare_point_sample

from .aero_reference import audit_statistics, compare_batch, target_slices, train_reference
from .reference import REVISION


def open_case(case, preparation):
    """消费与公开研究脚本相同的配置和准备。"""
    cfg = load_configuration(Path(case) / "config.yaml")
    config = application_parameters(cfg)
    components = load_components(cfg)
    data = physical.consume(config, components.dataset, components.model, str(preparation))
    parameters = components.model.training_parameters(config)
    parameters.pop("domains")
    return config, components, data, parameters


def benchmark(case, preparation, output):
    """完整基础网络、真实训练查询及完整几何预算的前反向与查询块测速。"""
    config, components, data, options = open_case(case, preparation)
    batch = prepare_point_sample(data.view.read("train", 0), config, data.normalization)
    audit = audit_statistics(data)
    parity = compare_batch(options, batch["inputs"], target_slices(config, batch))
    torch.manual_seed(42)
    model = components.model.construct(**components.model.training_parameters(config))
    optimizer = components.model.optimizer_factory(model, config["train"])
    timings = []
    for _ in range(2):
        start = time.monotonic()
        optimizer.zero_grad()
        components.model.loss(model, batch, config)["loss"].backward()
        optimizer.step()
        timings.append(time.monotonic() - start)
    with torch.no_grad():
        start = time.monotonic()
        model(**batch["inputs"])
        forward = time.monotonic() - start
    record = {
        "source_revision": REVISION,
        "device": "cpu",
        "threads": torch.get_num_threads(),
        "update_seconds": timings,
        "forward_seconds": forward,
        "query_points": [v.shape[1] for v in batch["inputs"]["local_embedding"]],
        "geometry_points": batch["inputs"]["geometry"].shape[1],
        "parameters": sum(p.numel() for p in model.parameters()),
        "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "statistics_audit": audit,
        "parity": parity,
    }
    Path(output).write_text(json.dumps(record, indent=2))
    return record


def reference(case, preparation, output, epochs):
    """保存最终参考权重及每个测试样本的完整物理预测。"""
    config, _, data, options = open_case(case, preparation)
    model, training = train_reference(data, config, options, epochs=epochs)
    model.eval()
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    predictions = {}
    started = time.monotonic()
    with torch.no_grad():
        for row, name in enumerate(data.view.partitions["test"]):
            batch = prepare_point_sample(
                data.view.read("test", row), config, data.normalization, evaluation=True
            )
            inputs = batch["inputs"]
            streams = inputs["local_embedding"]
            context = {k: v for k, v in inputs.items() if k != "local_embedding"}
            result = {}
            for index, (domain, spec) in enumerate(
                config["model"]["data_specs"]["domains"].items()
            ):
                count = streams[index].shape[1]
                order = point_indices(
                    count,
                    count,
                    seed=config["infer"]["seed"],
                    sample="test/" + name,
                    operation=domain + ":infer",
                )
                prediction = torch.empty(count, sum(spec["output_dims"].values()))
                for ids in order.split(config["infer"]["query_chunk_size"]):
                    # 原网络要求全部流；无局部编码时其他流不影响目标流切片。
                    selected = tuple(
                        s[:, ids] if j == index else s[:, :1] for j, s in enumerate(streams)
                    )
                    prediction[ids] = model(local_embedding=selected, **context)[index][0]
                offset = 0
                for field, width in spec["output_dims"].items():
                    source = config["trainprep"]["domains"][domain]["targets"][field]
                    result[domain + "." + field] = data.normalization.inverse(
                        source, prediction[:, offset : offset + width]
                    )
                    offset += width
            predictions[name] = result
    torch.save(
        {"model": model.state_dict(), "history": training["history"], "predictions": predictions},
        output / "reference.pt",
    )
    report = {
        "source_revision": REVISION,
        "epochs": epochs,
        "history": training["history"],
        "training_seconds": training["seconds"],
        "inference_seconds": time.monotonic() - started,
        "points": {k: {f: len(x) for f, x in v.items()} for k, v in predictions.items()},
        "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    (output / "reference.json").write_text(json.dumps(report, indent=2))
    return report


def compare(run, reference_dir, output):
    """复算最终权重、逐更新损失及完整物理预测差异；容差不放宽。"""
    run = Path(run)
    ref = torch.load(Path(reference_dir) / "reference.pt", map_location="cpu", weights_only=False)
    dojo = torch.load(run / "checkpoints/last.pt", map_location="cpu", weights_only=False)
    differences = {}
    for name, value in dojo["model"].items():
        torch.testing.assert_close(value, ref["model"][name], atol=1e-6, rtol=1e-5)
        differences[name] = float((value - ref["model"][name]).abs().max())
    history = json.loads((run / "artifacts/training.json").read_text())
    actual = torch.tensor([v["value"] for v in history["curves"]["loss"]], dtype=torch.float64)
    expected = torch.tensor(ref["history"], dtype=torch.float64)
    torch.testing.assert_close(actual, expected, atol=1e-6, rtol=1e-5)
    history_delta = float((actual - expected).abs().max())
    results = json.loads((run / "artifacts/physical-predictions.json").read_text())
    fields = {}
    for row in results["results"]:
        path = Path(row["manifest"])
        metadata = json.loads(path.read_text())
        for name, expected in ref["predictions"][row["sample"]].items():
            value = torch.load(
                path.parent / metadata["filemap"][name + ".prediction"], weights_only=True
            )
            torch.testing.assert_close(value, expected, atol=1e-6, rtol=1e-5)
            fields[row["sample"] + "/" + name] = {
                "points": len(value),
                "max_abs": float((value - expected).abs().max()),
            }
    report = {
        "weights_max_abs": max(differences.values()),
        "history_max_abs": history_delta,
        "predictions": fields,
        "epochs": dojo["epoch"],
        "updates": dojo["updates"],
        "atol": 1e-6,
        "rtol": 1e-5,
    }
    Path(output).write_text(json.dumps(report, indent=2))
    return report


def audit_metrics(run):
    """以 NumPy CPU float64 独立复算固定结果指标，并核验网格原身份和字段。"""
    import vtk
    from vtk.util.numpy_support import vtk_to_numpy

    results = json.loads((Path(run) / "artifacts/physical-predictions.json").read_text())
    report = {}
    for row in results["results"]:
        path = Path(row["manifest"])
        meta = json.loads(path.read_text())

        def read(name, *, path=path, meta=meta):
            return torch.load(path.parent / meta["filemap"][name], weights_only=True).numpy()

        for metric in meta["metric_records"]:
            key = metric["domain"] + "." + metric["field"]
            a, b = (read(key + suffix).astype(np.float64) for suffix in (".prediction", ".truth"))
            component = metric["component"]
            if component == "magnitude":
                a, b = np.linalg.norm(a, axis=-1), np.linalg.norm(b, axis=-1)
            elif component != "scalar":
                a, b = a[:, int(component)], b[:, int(component)]
            error = a - b
            denominator = float(np.square(b).sum())
            variance = float(np.square(b - b.mean()).sum())
            values = {
                "mae": float(np.abs(error).mean()),
                "rmse": float(np.sqrt(np.square(error).mean())),
                "max_abs_error": float(np.abs(error).max()),
                "relative_l2": float(np.sqrt(np.square(error).sum() / denominator))
                if denominator
                else None,
                "r2": float(1 - np.square(error).sum() / variance) if variance else None,
            }
            for name, value in values.items():
                if value is not None:
                    np.testing.assert_allclose(
                        value, metric["values"][name], rtol=1e-10, atol=1e-12
                    )
            report[row["sample"] + "/" + metric["id"]] = values
        for domain, mesh in meta["meshes"].items():
            reader = (
                vtk.vtkXMLPolyDataReader()
                if domain == "surface"
                else vtk.vtkXMLUnstructuredGridReader()
            )
            reader.SetFileName(str(path.parent / mesh["path"]))
            reader.Update()
            data = reader.GetOutput()
            assert data.GetNumberOfCells() == mesh["cell_count"]
            ids = vtk_to_numpy(data.GetPointData().GetArray("original_point_id"))
            source_ids = read(meta["domains"][domain]["ids"])
            lookup = {int(value): i for i, value in enumerate(source_ids)}
            assert set(ids) == set(source_ids)
            order = [lookup[int(value)] for value in ids]
            for name in mesh["fields"]:
                actual = vtk_to_numpy(data.GetPointData().GetArray(name))
                expected = read(name)[order]
                np.testing.assert_array_equal(actual.reshape(expected.shape), expected)
    return report


def main():
    """各子任务串行调用；失败与成功均写入同一累计计算账本。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["benchmark", "reference", "compare"])
    parser.add_argument("--case")
    parser.add_argument("--preparation")
    parser.add_argument("--run")
    parser.add_argument("--reference")
    parser.add_argument("--output", required=True)
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--ledger", required=True)
    args = parser.parse_args()
    ledger = Path(args.ledger)
    state = json.loads(ledger.read_text()) if ledger.exists() else {"seconds": 0, "runs": []}
    if state["seconds"] >= (9600 if args.mode in {"reference", "benchmark"} else 10800):
        raise TimeoutError("累计预算禁止启动新计算")
    torch.set_num_threads(2)
    started = time.monotonic()
    status = "failed"
    try:
        if args.mode == "benchmark":
            result = benchmark(args.case, args.preparation, args.output)
        elif args.mode == "reference":
            result = reference(args.case, args.preparation, args.output, args.epochs)
        else:
            result = compare(args.run, args.reference, args.output)
        status = "passed"
        print(
            json.dumps(
                {k: v for k, v in result.items() if k not in {"parity", "statistics_audit"}},
                indent=2,
            )
        )
    finally:
        elapsed = time.monotonic() - started
        state["seconds"] += elapsed
        state["runs"].append(
            {
                "label": args.mode + ":" + str(args.case or args.run),
                "seconds": elapsed,
                "status": status,
            }
        )
        ledger.write_text(json.dumps(state, indent=2))


if __name__ == "__main__":
    main()
