"""Image loading and non-destructive editing primitives."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

STANDARD_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp"}
RAW_EXTENSIONS = {".dng", ".cr2", ".cr3", ".nef", ".arw", ".raf", ".orf", ".rw2", ".pef"}
SUPPORTED_EXTENSIONS = STANDARD_EXTENSIONS | RAW_EXTENSIONS


def _channel_curve(image: Image.Image, red: float, green: float, blue: float) -> Image.Image:
    channels = image.convert("RGB").split()
    factors = (red, green, blue)
    adjusted = [c.point(lambda value, factor=f: max(0, min(255, int(value * factor)))) for c, f in zip(channels, factors)]
    return Image.merge("RGB", adjusted)


def _original(image: Image.Image) -> Image.Image:
    return image.copy()


def _film(image: Image.Image) -> Image.Image:
    result = ImageEnhance.Contrast(image).enhance(0.91)
    result = ImageEnhance.Color(result).enhance(0.83)
    result = _channel_curve(result, 1.06, 1.01, 0.90)
    return ImageEnhance.Brightness(result).enhance(1.03)


def _ins(image: Image.Image) -> Image.Image:
    result = ImageEnhance.Brightness(image).enhance(1.08)
    result = ImageEnhance.Contrast(result).enhance(0.90)
    return ImageEnhance.Color(_channel_curve(result, 1.02, 1.04, 1.08)).enhance(0.90)


def _landscape(image: Image.Image) -> Image.Image:
    result = ImageEnhance.Color(image).enhance(1.28)
    result = ImageEnhance.Contrast(result).enhance(1.16)
    return result.filter(ImageFilter.UnsharpMask(radius=1.5, percent=115, threshold=3))


def _portrait(image: Image.Image) -> Image.Image:
    result = _channel_curve(image, 1.07, 1.01, 0.96)
    result = ImageEnhance.Contrast(result).enhance(0.94)
    return ImageEnhance.Brightness(result).enhance(1.04)


def _mono(image: Image.Image) -> Image.Image:
    gray = ImageOps.grayscale(image)
    return ImageEnhance.Contrast(gray).enhance(1.24).convert("RGB")


def _vintage(image: Image.Image) -> Image.Image:
    result = ImageEnhance.Color(image).enhance(0.62)
    result = _channel_curve(result, 1.13, 1.02, 0.78)
    return ImageEnhance.Contrast(result).enhance(0.88)


@dataclass(frozen=True)
class FilterPreset:
    key: str
    name: str
    description: str
    accent: str
    transform: Callable[[Image.Image], Image.Image]


FILTERS = (
    FilterPreset("original", "原图", "干净自然", "#a8a49b", _original),
    FilterPreset("film", "胶片", "柔和暖调", "#d09a64", _film),
    FilterPreset("ins", "INS 清新", "低饱和明亮", "#9eb8b3", _ins),
    FilterPreset("landscape", "风景", "鲜活通透", "#739486", _landscape),
    FilterPreset("portrait", "人像", "温润肤色", "#cf9c8f", _portrait),
    FilterPreset("mono", "黑白纪实", "深邃影调", "#777b80", _mono),
    FilterPreset("vintage", "复古褪色", "旧时光感", "#a58263", _vintage),
)
FILTER_MAP = {preset.key: preset for preset in FILTERS}


def load_image(path: str | Path) -> Image.Image:
    """Load a standard or RAW image, normalized to oriented RGB."""
    path = Path(path)
    if path.suffix.lower() in RAW_EXTENSIONS:
        try:
            import rawpy
        except ImportError as exc:
            raise RuntimeError("读取 RAW 文件需要安装 rawpy") from exc
        with rawpy.imread(str(path)) as raw:
            pixels = raw.postprocess(use_camera_wb=True, no_auto_bright=False, output_bps=8)
        return Image.fromarray(pixels).convert("RGB")
    with Image.open(path) as source:
        return ImageOps.exif_transpose(source).convert("RGB")


def ratio_crop(
    image: Image.Image,
    ratio: tuple[int, int] | None,
    anchor: tuple[float, float] = (0.5, 0.5),
) -> Image.Image:
    """Crop to *ratio*, positioning the crop within the spare space by *anchor*.

    Each anchor component is normalized from 0 (top/left) to 1 (bottom/right).
    Values outside that range are clamped so a crop can never leave the image.
    """
    if ratio is None:
        return image.copy()
    target = ratio[0] / ratio[1]
    width, height = image.size
    anchor_x = max(0.0, min(1.0, anchor[0]))
    anchor_y = max(0.0, min(1.0, anchor[1]))
    if width / height > target:
        crop_width = round(height * target)
        left = round((width - crop_width) * anchor_x)
        box = (left, 0, left + crop_width, height)
    else:
        crop_height = round(width / target)
        top = round((height - crop_height) * anchor_y)
        box = (0, top, width, top + crop_height)
    return image.crop(box)


def centered_crop(image: Image.Image, ratio: tuple[int, int] | None) -> Image.Image:
    """Crop the largest centered rectangle matching *ratio*."""
    return ratio_crop(image, ratio)


def apply_filter(image: Image.Image, key: str, intensity: int) -> Image.Image:
    """Apply a preset and blend it with the source at 0–100 intensity."""
    if key not in FILTER_MAP:
        raise ValueError(f"Unknown filter: {key}")
    amount = max(0, min(100, intensity)) / 100
    source = image.convert("RGB")
    styled = FILTER_MAP[key].transform(source)
    return Image.blend(source, styled, amount)


@dataclass
class PhotoDocument:
    path: Path
    original: Image.Image
    filter_key: str = "original"
    intensity: int = 70
    crop_ratio: tuple[int, int] | None = None
    crop_anchor: tuple[float, float] = (0.5, 0.5)
    _preview_cache: dict[tuple, Image.Image] = field(default_factory=dict, repr=False)

    @classmethod
    def open(cls, path: str | Path) -> "PhotoDocument":
        return cls(Path(path), load_image(path))

    def render(self, max_size: tuple[int, int] | None = None) -> Image.Image:
        key = (self.filter_key, self.intensity, self.crop_ratio, self.crop_anchor, max_size)
        if key not in self._preview_cache:
            result = ratio_crop(self.original, self.crop_ratio, self.crop_anchor)
            result = apply_filter(result, self.filter_key, self.intensity)
            if max_size:
                result.thumbnail(max_size, Image.Resampling.LANCZOS)
            self._preview_cache[key] = result
        return self._preview_cache[key].copy()

    def render_uncropped(self, max_size: tuple[int, int] | None = None) -> Image.Image:
        """Render filters without the committed crop for an interactive crop preview."""
        result = apply_filter(self.original, self.filter_key, self.intensity)
        if max_size:
            result.thumbnail(max_size, Image.Resampling.LANCZOS)
        return result

    def export_png(self, destination: str | Path) -> Path:
        destination = Path(destination).with_suffix(".png")
        destination.parent.mkdir(parents=True, exist_ok=True)
        self.render().save(destination, "PNG", optimize=True)
        return destination
