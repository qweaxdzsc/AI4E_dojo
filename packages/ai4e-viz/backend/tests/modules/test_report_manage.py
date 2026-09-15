"""reportManage模块的实体、版本、导出和灾难恢复接入测试。"""

from modules.reportManage import create_export, create_report, duplicate_report, freeze_report, get_export, get_report_version, list_reports, restore_reports_from_snapshot


def test_report_manage_lifecycle(tmp_path, monkeypatch) -> None:
    """验证创建、列表、冻结、复制和导出任务完整链路。"""

    monkeypatch.setenv("QODER_REPORT_DB", str(tmp_path / "reports.sqlite3"))
    report = create_report({"title": "模块报告", "author": "测试", "template": "blank"})
    assert report["status"] == "draft"
    assert list_reports()[0]["report_id"] == report["report_id"]

    version = freeze_report(report["report_id"], "测试")
    assert version["version"] == 1
    assert get_report_version(report["report_id"])["content_hash"] == version["content_hash"]

    copied = duplicate_report(report["report_id"], "复制人")
    assert copied["report_id"] != report["report_id"]
    assert copied["title"].endswith("副本")

    export = create_export(report["report_id"], 1, "html", "portable")
    assert get_export(export["export_id"])["status"] == "queued"


def test_restore_reports_from_snapshot_preserves_both_databases(tmp_path, monkeypatch) -> None:
    """验证恢复只补入缺失报告、可重复执行且不覆盖当前报告。"""

    source = tmp_path / "legacy.sqlite3"
    target = tmp_path / "current.sqlite3"
    monkeypatch.setenv("QODER_REPORT_DB", str(source))
    legacy = create_report({"title": "旧进程新增报告", "author": "测试", "template": "blank"})

    monkeypatch.setenv("QODER_REPORT_DB", str(target))
    current = create_report({"title": "当前运行库报告", "author": "测试", "template": "blank"})
    first = restore_reports_from_snapshot(source)
    assert first == {
        "reports_inserted": 1, "versions_inserted": 0,
        "exports_inserted": 0, "records_unchanged": 0,
    }
    assert {item["report_id"] for item in list_reports()} == {
        legacy["report_id"], current["report_id"],
    }

    second = restore_reports_from_snapshot(source)
    assert second["reports_inserted"] == 0
    assert second["records_unchanged"] == 1
