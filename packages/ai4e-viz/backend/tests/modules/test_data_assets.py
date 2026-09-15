"""dataAssets模块Repository接入测试，使用独立临时SQLite。"""

from modules.dataAssets import application, repository


def _artifact(artifact_id: str = "U-TEST-DATASET") -> dict:
    return {
        "artifact_id": artifact_id, "name": "测试数据集", "file_name": "sample.csv",
        "file_path": "objects/datasets/aa/sample.csv", "format": "CSV", "sha256": "a" * 64,
        "size_bytes": 12, "declared_kind": "table", "source": "uploaded",
    }


def test_data_asset_repository_lifecycle(tmp_path, monkeypatch) -> None:
    """验证登记、去重、画像、分类修正和查询均由模块Repository完成。"""

    monkeypatch.setenv("QODER_ASSET_DB", str(tmp_path / "datasets.sqlite3"))
    created = repository.upsert_artifact(_artifact())
    assert created["artifact_id"] == "U-TEST-DATASET"
    assert repository.find_uploaded_by_sha256("a" * 64)["artifact_id"] == created["artifact_id"]

    analyzed = repository.save_analysis(
        created["artifact_id"], {"inferred_kind": "table", "rows": 2}, {"candidates": []},
        validation_status="pass", family="PLT",
    )
    assert analyzed["parse_status"] == "ready"
    assert analyzed["profile"]["rows"] == 2

    classified = repository.update_classification(created["artifact_id"], "series", "人工复核")
    assert classified["declared_kind"] == "series"
    assert classified["version"] == 2
    assert [item["artifact_id"] for item in repository.list_artifacts()] == [created["artifact_id"]]


def test_data_asset_analysis_error_keeps_record(tmp_path, monkeypatch) -> None:
    """验证解析失败只更新诊断状态，不删除数据集记录。"""

    monkeypatch.setenv("QODER_ASSET_DB", str(tmp_path / "datasets-error.sqlite3"))
    repository.upsert_artifact(_artifact("U-ERROR"))
    failed = repository.save_analysis_error("U-ERROR", {"code": "PARSE_FAILED"})
    assert failed["parse_status"] == "error"
    assert failed["profile"]["error"]["code"] == "PARSE_FAILED"


def test_invalid_uploaded_asset_keeps_id_and_diagnostic(tmp_path, monkeypatch) -> None:
    """验证上传内容解析失败时仍保留资产ID、原始文件和诊断。"""

    monkeypatch.setenv("QODER_ASSET_DB", str(tmp_path / "upload-error.sqlite3"))
    monkeypatch.setattr(application, "UPLOAD_DIR", tmp_path / "objects")
    result = application.register_uploaded_asset("broken.csv", b"\xff\xfe\x00", "auto")
    assert result["artifact_id"].startswith("U-")
    assert result["artifact"]["parse_status"] == "error"
    assert result["error"]["code"] == "PARSE_FAILED"
    assert list((tmp_path / "objects").rglob("broken.csv"))
