"""B2/B3/C2：逐场编译保留实体路由，旧容器保持独立语义。"""

import pytest

from ai4e_core.applications.aero_cfd.rawprep.extraction import compile_extraction


def extraction(layout="fields"):
    return {
        "layout": layout,
        "entries": [
            {
                "id": "fields",
                "outputs": [
                    {
                        "name": "pressure",
                        "members": [
                            {
                                "source_field": "surface/point/point_scalars",
                                "output_member": "p",
                                "components": 1,
                            }
                        ],
                    }
                ],
            }
        ],
    }


def test_field_tensor_route_and_legacy_bundle():
    result = compile_extraction(extraction())
    assert result["fields"] == {"pressure": {"domain": "surface", "field": "fields.point_scalars"}}
    assert result["members"] == {}
    assert (
        compile_extraction(extraction("containers"))["members"]["pressure"]["p"]
        == result["fields"]["pressure"]
    )


def test_single_field_cannot_be_a_bundle():
    value = extraction()
    value["entries"][0]["outputs"][0]["members"].append(
        {"source_field": "surface/geometry/points", "output_member": "xyz", "components": 3}
    )
    with pytest.raises(ValueError, match="恰好"):
        compile_extraction(value)


@pytest.mark.parametrize("name", ["../escape", "a/b", ""])
def test_field_name_cannot_escape(name):
    value = extraction()
    value["entries"][0]["outputs"][0]["name"] = name
    with pytest.raises(ValueError):
        compile_extraction(value)
