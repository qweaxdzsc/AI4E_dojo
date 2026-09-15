"""visIO模块Repository接入测试，验证其与数据集外键协作。"""

from modules.dataAssets import repository as dataset_repository
from modules.visIO import repository


def test_visualization_repository_lifecycle(tmp_path, monkeypatch) -> None:
    """验证创建、查询、过滤、表现更新和最近记录。"""

    database = tmp_path / "visualizations.sqlite3"
    monkeypatch.setenv("QODER_ASSET_DB", str(database))
    dataset_repository.upsert_artifact({
        "artifact_id": "A-IO", "name": "IO测试", "file_name": "field.npz",
        "file_path": "objects/datasets/aa/field.npz", "format": "NPZ", "sha256": "b" * 64,
        "size_bytes": 20, "declared_kind": "field", "source": "uploaded", "dataset_id": "D-1",
    })
    created = repository.create_visualization({
        "visualization_id": "V-IO", "artifact_id": "A-IO", "recommendation_id": "R-1",
        "spec_id": "S-1", "spec_version": 1, "function_id": "field.scalar",
        "renderer": "trame", "parameters": {"field": "pressure"},
        "payload": {"artifact": {"kind": "field"}}, "representations": {},
    })
    assert created["parameters"]["field"] == "pressure"
    assert len(created["content_hash"]) == 64
    assert repository.list_visualizations(dataset_id="D-1", kind="field")[0]["visualization_id"] == "V-IO"

    updated = repository.update_visualization_representations("V-IO", {"static": {"path": "derived/previews/v.png"}})
    assert updated["representations"]["static"]["path"].endswith("v.png")
    assert repository.latest_visualization("A-IO")["visualization_id"] == "V-IO"
