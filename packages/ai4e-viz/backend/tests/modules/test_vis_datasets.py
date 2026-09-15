"""visDatasets模块画像与数据质量检测测试。"""

from modules.visDatasets import inspect_profile, supported_kind_names, supported_upload_formats


def test_dataset_capability_registry_remains_available() -> None:
    """验证资产模块拆分后解析格式和语义类型能力没有丢失。"""

    assert {"csv", "npz", "vtu", "glb"} <= supported_upload_formats().keys()
    assert {"table", "tensor", "field", "mesh"} <= set(supported_kind_names())


def test_dataset_inspection_reports_parse_and_nan_issues() -> None:
    """验证数据体检仍由visDatasets生成可解释的问题列表。"""

    issues = inspect_profile({"failed": True, "error": {"code": "BROKEN"}, "nan_count": 3})
    assert [issue.code for issue in issues] == ["parse_failed", "contains_nan"]
