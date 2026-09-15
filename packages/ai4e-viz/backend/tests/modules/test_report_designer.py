"""reportDesigner模块的文档校验与草稿乐观锁接入测试。"""

import pytest

from modules.reportDesigner import get_draft, replace_draft
from modules.reportDesigner.domain import scaffold_document, validate_document
from modules.reportManage import create_report


def test_report_designer_draft_revision(tmp_path, monkeypatch) -> None:
    """验证草稿校验、保存和过期修订冲突。"""

    monkeypatch.setenv("QODER_REPORT_DB", str(tmp_path / "designer.sqlite3"))
    report = create_report({"title": "编排测试", "template": "blank"})
    draft = get_draft(report["report_id"])
    document = draft["document"]
    document["metadata"]["title"] = "编排后标题"
    saved = replace_draft(report["report_id"], draft["draft_revision"], document)
    assert saved["draft_revision"] == draft["draft_revision"] + 1
    with pytest.raises(RuntimeError):
        replace_draft(report["report_id"], draft["draft_revision"], document)


def test_report_designer_domain_validation() -> None:
    """验证文档骨架有效且非法空章节会被拒绝。"""

    document = scaffold_document({"title": "校验", "template": "blank"})
    assert validate_document(document) == []
    assert validate_document({"sections": []})[0]["path"] == "/sections"


def test_task_visualization_reference_survives_draft_and_rejects_bad_revision(tmp_path, monkeypatch):
    """报告冻结任务资产与配置修订，不保存临时工作区URL。"""
    from modules.reportDesigner.domain import _block as make_block
    monkeypatch.setenv("QODER_REPORT_DB", str(tmp_path / "scoped-report.sqlite3"))
    report = create_report({"title": "物理场引用", "template": "blank"})
    draft = get_draft(report["report_id"])
    ref = {"project_id":"p", "task_id":"t", "visualization_id":"v", "revision":1, "content_hash":"a"*64, "view":0}
    block = make_block("visualization", source_ref=ref)
    document = draft["document"]
    document["sections"][0]["rows"].append({"id":"scoped-row", "gap":16, "align":"start", "blocks":[block]})
    saved = replace_draft(report["report_id"], draft["draft_revision"], document)
    assert saved["document"]["sections"][0]["rows"][-1]["blocks"][0]["source_ref"] == ref
    block["source_ref"]["revision"] = 0
    assert any(error["path"].endswith("/revision") for error in validate_document(document))
