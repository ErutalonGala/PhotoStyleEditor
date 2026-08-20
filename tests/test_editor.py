from pathlib import Path

import pytest

pytest.importorskip("PIL")
from PIL import Image

from photostyle.editor import FILTER_MAP, PhotoDocument, apply_filter, centered_crop


def test_filter_intensity_zero_keeps_original():
    image = Image.new("RGB", (20, 20), (80, 120, 160))
    assert apply_filter(image, "film", 0).tobytes() == image.tobytes()


def test_all_presets_preserve_dimensions():
    image = Image.new("RGB", (31, 19), (110, 140, 90))
    for key in FILTER_MAP:
        assert apply_filter(image, key, 72).size == image.size


@pytest.mark.parametrize(("ratio", "expected"), [((1, 1), (100, 100)), ((16, 9), (178, 100)), ((9, 16), (56, 100))])
def test_centered_crop_matches_ratio(ratio, expected):
    assert centered_crop(Image.new("RGB", (200, 100)), ratio).size == expected


def test_document_exports_png(tmp_path: Path):
    source = tmp_path / "source.jpg"
    Image.new("RGB", (80, 60), "#cba276").save(source)
    document = PhotoDocument.open(source)
    document.filter_key = "portrait"
    document.crop_ratio = (1, 1)
    output = document.export_png(tmp_path / "result.jpeg")
    assert output.suffix == ".png"
    assert Image.open(output).size == (60, 60)


def test_unknown_filter_is_rejected():
    with pytest.raises(ValueError, match="Unknown filter"):
        apply_filter(Image.new("RGB", (10, 10)), "missing", 100)
