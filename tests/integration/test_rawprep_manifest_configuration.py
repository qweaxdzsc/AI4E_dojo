"""A3：能力依赖与可编辑范围由组件声明统一校验。"""

from copy import deepcopy

import pytest

from ai4e_contrib.application.datasets import nasa_crm, shapenet_car
from ai4e_core.applications.aero_cfd.rawprep.descriptor import validate_rawprep


@pytest.mark.parametrize(
    "edit",
    [
        {"geometry": []},
        {"geometry": ["nearest_vertex", "mesh_signed_distance"]},
        {"save_fields": ["surface_pressure"]},
        {"format": "bad"},
        {"fields": []},
        {"sources": [{}]},
        {"geometry": {"nearest_vertex": {"epsilon": -1}}},
        {"statistics": {"fields": "invalid"}},
    ],
)
def test_invalid_car_configuration(edit):
    profile = shapenet_car.describe_rawprep()
    raw = {**deepcopy(profile["defaults"]), **edit}
    with pytest.raises(ValueError):
        validate_rawprep(raw, profile)


def test_nasa_enables_vtkhdf_by_default():
    p = nasa_crm.describe_rawprep()
    assert p["vtkhdf"] is True
    assert p["defaults"]["vtkhdf"] is True
    validate_rawprep(p["defaults"], p)
