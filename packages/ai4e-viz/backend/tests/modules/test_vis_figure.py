"""图片预览模块的格式边界和文件元数据测试。"""

import pytest

from modules.visFigure import describe_figure


def test_figure_describes_png_without_decoding_business_state(tmp_path) -> None:
    """图片模块应返回稳定文件元数据并接受大小写扩展名。"""

    image = tmp_path / "preview.PNG"
    image.write_bytes(b"\x89PNG\r\n\x1a\n")
    metadata = describe_figure(str(image))
    assert metadata.name == "preview.PNG"
    assert metadata.extension == ".png"
    assert metadata.byte_size == 8


def test_figure_rejects_non_image_format(tmp_path) -> None:
    """图片预览不得把任意文件伪装成受支持图片。"""

    source = tmp_path / "notes.txt"
    source.write_text("not an image", encoding="utf-8")
    with pytest.raises(ValueError):
        describe_figure(str(source))
