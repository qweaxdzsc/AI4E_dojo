"""visConvertor模块真实几何到GLB转换接入测试。"""

from pathlib import Path

import pytest

from modules.visConvertor import convert_to_glb


BACKEND_ROOT = Path(__file__).resolve().parents[2]


def test_convert_ply_to_glb(tmp_path) -> None:
    """验证现有PLY几何可通过模块公开门面转换为非空GLB。"""

    output = tmp_path / "wing.glb"
    result = convert_to_glb(str(BACKEND_ROOT.parent / "resources" / "examples" / "wing_surface_geometry.ply"), str(output))
    assert Path(result) == output
    assert output.read_bytes()[:4] == b"glTF"


def test_reject_unsupported_conversion(tmp_path) -> None:
    """验证不支持的输入格式返回明确错误而不是生成伪结果。"""

    source = tmp_path / "unsupported.csv"
    source.write_text("x,y\n1,2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="unsupported GEO source format"):
        convert_to_glb(str(source), str(tmp_path / "bad.glb"))
