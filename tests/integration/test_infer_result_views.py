"""固定结果两种视图：全样本等权聚合、分片身份及导出字段一致。"""

import csv

import pytest
from openpyxl import load_workbook

from ai4e_core.applications.aero_cfd.infer.evaluation import summarize_records
from ai4e_core.applications.aero_cfd.infer.exports import comparison_table, export_results


def results():
    records = [
        {
            "checkpoint_id": "cp",
            "checkpoint": "weights",
            "split": split,
            "sample": sample,
            "field_id": "surface:p:scalar",
            "label": "Pressure",
            "status": "succeeded",
            "unit": "Pa",
            "expected": 1 if split == "train" else 3,
            "values": {"mae": value, "rmse": value + 1},
            "algorithm": "physical-metrics-v2",
        }
        for split, sample, value in [
            ("train", "same", 1),
            ("test", "same", 3),
            ("test", "b", 5),
            ("test", "c", 7),
        ]
    ]
    return {"records": records, "statistics": summarize_records(records, include_all=True)}


def test_checkpoint_pool_uses_samples_not_partition_means():
    value = results()
    row = next(r for r in value["statistics"] if r["split"] == "__all__" and r["metric"] == "mae")
    assert row["mean"] == 4 and row["median"] == 4
    assert row["p90"] == pytest.approx(6.4) and row["expected"] == 4
    unannotated = [{k: v for k, v in r.items() if k != "expected"} for r in value["records"]]
    assert all(
        r["expected"] == 4
        for r in summarize_records(unannotated, include_all=True)
        if r["split"] == "__all__"
    )
    records = value["records"][:1]
    records[0]["expected_all"] = 4
    partial = summarize_records(records, include_all=True)[-1]
    assert partial["expected"] == 4 and not partial["complete"]


@pytest.mark.parametrize("mode", ["checkpoint", "sample"])
def test_table_columns_export_same_fixed_values(tmp_path, mode):
    value = results()
    config = {
        "mode": mode,
        "checkpoint_id": "cp",
        "pairs": [
            {"field_id": "surface:p:scalar", "metric": "mae"},
            {"field_id": "surface:p:scalar", "metric": "rmse"},
        ],
        "aggregations": ["mean", "p90"],
    }
    rows = comparison_table(value, config)
    assert len(rows) == (1 if mode == "checkpoint" else 4)
    assert len(rows[0]) == (6 if mode == "checkpoint" else 4)
    if mode == "sample":
        assert rows[0]["样本"] == rows[1]["样本"] == "same"
        assert rows[0]["分片"] != rows[1]["分片"]
        assert rows[0]["Pressure · mae (Pa)"] == 1
    for format in ["csv", "xlsx"]:
        path = tmp_path / (mode + "." + format)
        export_results(value, str(path), format=format, selection={"view": config})
        if format == "xlsx":
            sheet = list(load_workbook(path)["当前表格"].values)
            assert list(sheet[0]) == list(rows[0]) and list(sheet[1]) == list(rows[0].values())
        else:
            with path.open(encoding="utf-8-sig") as stream:
                output = list(csv.DictReader(stream))
            assert list(output[0]) == list(rows[0]) and len(output) == len(rows)


def test_performance_values_use_recorded_prediction_time():
    from ai4e_core.applications.aero_cfd.infer.evaluation import result_views

    records = results()["records"][:1]
    records[0].update(
        selected_metrics=["prediction_seconds", "throughput"], timings={"prediction": 0.25}
    )
    value = result_views(records)
    assert value["records"][0]["values"]["throughput"] == 4
    config = {
        "mode": "sample",
        "checkpoint_id": "cp",
        "pairs": [{"field_id": "surface:p:scalar", "metric": "throughput"}],
    }
    assert list(comparison_table(value, config)[0].values())[-1] == 4
    records[0]["timings"] = {}
    missing = result_views(records)["records"][0]
    assert missing["values"]["throughput"] is None and missing["undefined"]["throughput"]


def test_identical_field_labels_keep_distinct_export_columns():
    value = results()
    value["records"] += [{**r, "field_id": "volume:p:scalar"} for r in value["records"]]
    value["statistics"] = summarize_records(value["records"], include_all=True)
    config = {
        "mode": "checkpoint",
        "pairs": [
            {"field_id": field, "metric": "mae"}
            for field in ["surface:p:scalar", "volume:p:scalar"]
        ],
        "aggregations": ["mean"],
    }
    row = comparison_table(value, config)[0]
    assert len(row) == 4
    assert row["Pressure [surface:p:scalar] · mae · Mean (Pa)"] == 4
    assert row["Pressure [volume:p:scalar] · mae · Mean (Pa)"] == 4
