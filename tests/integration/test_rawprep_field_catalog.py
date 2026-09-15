"""B1：检查真实字段的存在、类型和分量，拒绝混用点和单元。"""

import pytest

from ai4e_core.applications.aero_cfd.rawprep.catalog import check_requested_fields


def test_requested_field_missing_or_wrong_components():
    cfg = {
        "fields": {"surface": {"p": {"array": "pressure", "association": "point", "components": 1}}}
    }
    with pytest.raises(ValueError, match="缺少字段"):
        check_requested_fields([], cfg)
    field = {"field_id": "surface/point/pressure", "components": 3}
    with pytest.raises(ValueError, match="分量"):
        check_requested_fields([field], cfg)
    field["components"] = 1
    check_requested_fields([field], cfg)
