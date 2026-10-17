#!/usr/bin/env python3
"""Country editions of the supplied logo; all pixels outside two edit areas stay intact.

The original is a raster image, not an editable vector master. Country lettering
is re-created in a matching condensed gold serif. Flag geometry is adapted to a
round badge while national emblems retain their original aspect ratios.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from io import BytesIO
import json
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

import resvg_py
import cv2
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, PngImagePlugin

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
OUTPUT = ROOT / "deliverables"
COUNTRIES = json.loads((ROOT / "countries.json").read_text())
SCALE = 4
LANCZOS = Image.Resampling.LANCZOS
TEXT_BOX = (264, 624, 715, 676)
BADGE_BOX = (695, 731, 825, 861)
FONT = ASSETS / "fonts/Tinos-Bold.ttf"

# Number of painted SVG background children, ignoring definitions. The remaining
# children are rendered separately so circles, stars, coats of arms, and text are
# never stretched to fit the round badge.
BACKGROUND_COUNT = {
    "cl": 3, "py": 3, "ar": 2, "br": 1, "uy": 2, "bo": 3,
    "ve": 3, "ec": 3, "pe": 2, "rw": 3, "lr": 3, "gh": 3,
    "bf": 2, "dz": 2, "ao": 2, "ma": 1, "eg": 3, "cn": 1,
    "my": 1, "in": 3, "jp": 1, "kr": 1, "vn": 1, "pk": 2,
    "ph": 3,
}
# (sizing axis, fraction of badge diameter, center x, center y)
PLACEMENT = {
    "cl": ("h", .235, .29, .28), "py": ("h", .295, .5, .5),
    "ar": ("h", .285, .5, .5), "br": ("w", .965, .5, .5),
    "uy": ("h", .30, .285, .28), "bo": ("h", .40, .5, .5),
    "ve": ("w", .56, .5, .50), "ec": ("h", .50, .5, .51),
    "pe": ("h", .44, .5, .5), "rw": ("w", .24, .745, .27),
    "lr": ("h", .235, .28, .27), "gh": ("h", 1 / 3, .5, .5),
    "bf": ("h", .30, .5, .5), "dz": ("h", .50, .525, .5),
    "ao": ("h", .53, .5, .5), "ma": ("h", .40, .5, .5),
    "eg": ("h", .31, .5, .5), "cn": ("w", .37, .34, .315),
    "my": ("w", .37, .285, .295), "in": ("h", .30, .5, .5),
    "jp": ("h", .50, .5, .5), "kr": ("w", .83, .5, .5),
    "vn": ("h", .53, .5, .5), "pk": ("h", .54, .615, .5),
    "ph": ("h", .275, .265, .5),
}
DEFINITION_TAGS = {"defs", "clipPath", "mask", "style", "title", "desc"}


def tag(element: ET.Element) -> str:
    return element.tag.rsplit("}", 1)[-1]


def svg_image(root: ET.Element, width: int = 1200, square: bool = False) -> Image.Image:
    root = deepcopy(root)
    viewbox = [float(v) for v in root.get("viewBox").split()]
    height = width if square else round(width * viewbox[3] / viewbox[2])
    root.set("width", str(width))
    root.set("height", str(height))
    if square:
        root.set("preserveAspectRatio", "none")
    rendered = resvg_py.svg_to_bytes(
        svg_string=ET.tostring(root, encoding="unicode"), skip_system_fonts=True,
    )
    return Image.open(BytesIO(rendered)).convert("RGBA")


def split_flag(code: str) -> tuple[ET.Element, ET.Element]:
    root = ET.parse(ASSETS / "flags" / f"{code}.svg").getroot()
    background, foreground = deepcopy(root), deepcopy(root)
    background[:] = []
    foreground[:] = []
    seen = 0
    for child in root:
        if tag(child) in DEFINITION_TAGS:
            background.append(deepcopy(child))
            foreground.append(deepcopy(child))
        elif seen < BACKGROUND_COUNT[code]:
            background.append(deepcopy(child))
            seen += 1
        else:
            foreground.append(deepcopy(child))
    if code == "ph":
        # Keep the original eight-rayed sun. The three stars are positioned
        # separately to remain fully visible at the rounded canton corners.
        for child in foreground:
            if tag(child) == "g":
                child.remove(child[-1])
    return background, foreground


def star(draw: ImageDraw.ImageDraw, x: float, y: float, radius: float, color: str) -> None:
    points = []
    for i in range(10):
        angle = -np.pi / 2 + i * np.pi / 5
        r = radius if i % 2 == 0 else radius * .38196601125
        points.append((x + r * np.cos(angle), y + r * np.sin(angle)))
    draw.polygon(points, fill=color)


def adapted_background(code: str, image: Image.Image) -> Image.Image:
    """Maintain stripe counts and square cantons in a circular composition."""
    n = image.width
    draw = ImageDraw.Draw(image)

    def rect(box, color):
        draw.rectangle(tuple(round(v * n) for v in box), fill=color)

    if code == "cl":
        rect((0, 0, 1, .5), "#ffffff")
        rect((0, .5, 1, 1), "#d52b1e")
        rect((0, 0, .5, .5), "#0039a6")
    elif code in {"uy", "lr", "gr"}:
        count = 11 if code == "lr" else 9
        colors = {
            "uy": ("#ffffff", "#0038a8"),
            "lr": ("#bf0a30", "#ffffff"),
            "gr": ("#0D5EAF", "#ffffff"),
        }[code]
        for i in range(count):
            rect((0, i / count, 1, (i + 1) / count), colors[i % 2])
        if code == "uy":
            rect((0, 0, 5 / 9, 5 / 9), "#ffffff")
        elif code == "lr":
            rect((0, 0, .48, 5 / 11), "#002868")
        else:
            rect((0, 0, 5 / 9, 5 / 9), "#0D5EAF")
            rect((2 / 9, 0, 3 / 9, 5 / 9), "#ffffff")
            rect((0, 2 / 9, 5 / 9, 3 / 9), "#ffffff")
    elif code in {"fi", "dk"}:
        background, cross, thickness = (
            ("#ffffff", "#003580", 1 / 6) if code == "fi"
            else ("#c60c30", "#ffffff", .125)
        )
        rect((0, 0, 1, 1), background)
        rect((.37 - thickness / 2, 0, .37 + thickness / 2, 1), cross)
        rect((0, .5 - thickness / 2, 1, .5 + thickness / 2), cross)
    elif code == "ph":
        rect((0, 0, 1, .5), "#0038a8")
        rect((0, .5, 1, 1), "#ce1126")
        draw.polygon([(0, 0), (.62 * n, .5 * n), (0, n)], fill="#ffffff")
        for x, y, angle in [(.155, .28, 0), (.155, .72, 0), (.515, .5, 0)]:
            star(draw, x * n, y * n, .048 * n, "#fcd116")
    return image


def flag_square(code: str, n: int = 512) -> Image.Image:
    if code == "np":
        # Nepal is not rectangular. Keep both pennants, their blue border,
        # and the moon/sun intact on a warm-white enamel background.
        source = svg_image(ET.parse(ASSETS / "flags/np.svg").getroot())
        source = source.crop(source.getbbox())
        h = round(n * .76)
        source = source.resize((round(source.width * h / source.height), h), LANCZOS)
        result = Image.new("RGBA", (n, n), "#f8f5ec")
        result.alpha_composite(source, (round(n * .49 - source.width / 2), round(n * .51 - h / 2)))
        return result
    if code not in BACKGROUND_COUNT:
        root = ET.parse(ASSETS / "flags" / f"{code}.svg").getroot()
        return adapted_background(code, svg_image(root, n, square=True))
    background, foreground = split_flag(code)
    result = adapted_background(code, svg_image(background, n, square=True))
    detail = svg_image(foreground)
    bbox = detail.getbbox()
    if bbox is None:
        raise ValueError(f"No emblem found for {code}")
    detail = detail.crop(bbox)
    axis, fraction, cx, cy = PLACEMENT[code]
    ratio = n * fraction / (detail.width if axis == "w" else detail.height)
    detail = detail.resize((round(detail.width * ratio), round(detail.height * ratio)), LANCZOS)
    result.alpha_composite(detail, (round(n * cx - detail.width / 2), round(n * cy - detail.height / 2)))
    return result


def clean_country(original: Image.Image) -> Image.Image:
    array = np.array(original)
    mask = np.zeros(array.shape[:2], np.uint8)
    # Includes the old lettering and its dark embossed shadow, but not the
    # title above or the partnership text below.
    mask[626:675, 398:585] = 255
    cleaned = cv2.inpaint(array, mask, 4, cv2.INPAINT_TELEA)
    return Image.fromarray(cleaned)


def shift(image: Image.Image, x: int, y: int) -> Image.Image:
    shifted = Image.new("L", image.size)
    shifted.paste(image, (x, y))
    return shifted


def country_text(base: Image.Image, name: str) -> Image.Image:
    x0, y0, x1, y1 = TEXT_BOX
    patch = base.crop(TEXT_BOX).convert("RGBA").resize(((x1 - x0) * SCALE, (y1 - y0) * SCALE), LANCZOS)
    font = ImageFont.truetype(str(FONT), 54 * SCALE)
    bbox = font.getbbox(name.upper())
    glyph = Image.new("L", (bbox[2] - bbox[0] + 8 * SCALE, bbox[3] - bbox[1] + 4 * SCALE))
    ImageDraw.Draw(glyph).text((4 * SCALE - bbox[0], 2 * SCALE - bbox[1]), name.upper(), font=font, fill=255)
    glyph = glyph.crop(glyph.getbbox())
    # Match the narrow uppercase serif proportions of the supplied BRAZIL.
    target_width = min(round(glyph.width * .835), 416 * SCALE)
    glyph = glyph.resize((target_width, glyph.height), LANCZOS)
    mask = Image.new("L", patch.size)
    left = round((490 - x0) * SCALE - glyph.width / 2)
    top = round((630.3 - y0) * SCALE)
    mask.paste(glyph, (left, top))

    shadow = shift(mask, round(.7 * SCALE), round(2.0 * SCALE)).filter(ImageFilter.GaussianBlur(1.1 * SCALE))
    shadow = shadow.point(lambda a: round(a * .78))
    patch.alpha_composite(Image.composite(Image.new("RGBA", patch.size, (0, 0, 0, 255)), Image.new("RGBA", patch.size), shadow))
    outline = mask.filter(ImageFilter.MaxFilter(5))
    outline = ImageChops.subtract(outline, mask).point(lambda a: round(a * .7))
    patch.alpha_composite(Image.composite(Image.new("RGBA", patch.size, (86, 65, 33, 255)), Image.new("RGBA", patch.size), outline))

    yy, xx = np.indices((patch.height, patch.width), dtype=np.float32)
    t = np.clip((yy - top) / max(1, glyph.height - 1), 0, 1)
    stops = np.array([0, .18, .43, .55, .76, 1])
    colors = np.array([[211, 190, 145], [225, 204, 158], [244, 227, 185],
                       [236, 216, 172], [208, 183, 136], [184, 158, 115]])
    gold = np.stack([np.interp(t, stops, colors[:, c]) for c in range(3)], axis=-1)
    noise = np.random.default_rng(20261017).normal(0, 1.4, t.shape)
    gold += noise[..., None]
    light = np.asarray(ImageChops.subtract(mask, shift(mask, SCALE // 2, SCALE // 2)), dtype=np.float32) / 255
    dark = np.asarray(ImageChops.subtract(mask, shift(mask, -SCALE // 2, -SCALE // 2)), dtype=np.float32) / 255
    gold += light[..., None] * 14 - dark[..., None] * 15
    fill = Image.fromarray(np.uint8(np.clip(gold, 0, 255))).convert("RGBA")
    fill.putalpha(mask)
    patch.alpha_composite(fill)
    patch = patch.resize((x1 - x0, y1 - y0), LANCZOS)
    result = base.copy()
    # Only composite painted text pixels; do not resample the untouched navy.
    coverage = mask.filter(ImageFilter.MaxFilter(9))
    coverage = ImageChops.lighter(coverage, shadow)
    coverage = coverage.filter(ImageFilter.GaussianBlur(.4 * SCALE)).resize(patch.size, LANCZOS)
    coverage = coverage.point(lambda a: 255 if a > 0 else 0)
    result.paste(patch.convert("RGB"), (x0, y0), coverage)
    return result


def badge(code: str) -> Image.Image:
    n = (BADGE_BOX[2] - BADGE_BOX[0]) * SCALE
    yy, xx = np.indices((n, n), dtype=np.float32)
    cx, cy = 64.8 * SCALE, 65.0 * SCALE
    outer, inner = 61.7 * SCALE, 58.5 * SCALE
    dx, dy = (xx + .5 - cx) / SCALE, (yy + .5 - cy) / SCALE
    distance = np.sqrt(dx * dx + dy * dy)
    angle_light = -.32 * dx / 61.7 - .70 * dy / 61.7
    rim_radii = np.array([0, 58.1, 58.5, 59.1, 59.7, 60.2, 60.7, 61.25, 61.7, 100])
    rim_colors = np.array([
        [79, 60, 31], [79, 60, 31], [128, 101, 54], [234, 211, 153],
        [185, 151, 87], [236, 214, 157], [218, 190, 124], [114, 85, 42],
        [51, 40, 26], [51, 40, 26],
    ])
    rim = np.stack([np.interp(distance, rim_radii, rim_colors[:, k]) for k in range(3)], -1)
    rim += angle_light[..., None] * 25
    result = Image.fromarray(np.uint8(np.clip(rim, 0, 255))).convert("RGBA")
    outer_mask = np.uint8(np.clip((61.7 - distance) * SCALE + .5, 0, 1) * 255)
    result.putalpha(Image.fromarray(outer_mask))

    face_size = round(inner * 2)
    flag = flag_square(code, face_size)
    face = Image.new("RGB", (n, n), "#101a29")
    face.paste(flag.convert("RGB"), (round(cx - face_size / 2), round(cy - face_size / 2)))
    face_array = np.array(face, dtype=np.float32)
    x, y = dx / 58.5, dy / 58.5
    r2 = x * x + y * y
    dome = np.sqrt(np.clip(1 - r2, 0, 1))
    shade = .78 + .21 * dome - .038 * x - .055 * y
    face_array *= shade[..., None]
    sheen = .28 * np.exp(-((x + .40) / .42) ** 2 - ((y + .58) / .32) ** 2)
    sheen += .045 * np.exp(-((y + .69 - .13 * x) / .14) ** 2) * np.clip(1 - r2, 0, 1)
    face_array = face_array * (1 - sheen[..., None]) + 255 * sheen[..., None]
    face_array += np.random.default_rng(41).normal(0, .40, r2.shape)[..., None]
    face = Image.fromarray(np.uint8(np.clip(face_array, 0, 255))).convert("RGBA")
    face.putalpha(Image.fromarray(np.uint8(np.clip((58.5 - distance) * SCALE + .5, 0, 1) * 255)))
    result.alpha_composite(face)
    return result.resize((n // SCALE, n // SCALE), LANCZOS)


def filename(index: int, country: dict) -> str:
    return f"{index:02d}_Free_Recruiters_{country['name'].replace(' ', '_')}.png"


def create_preview(files: list[tuple[dict, Path]]) -> None:
    columns, width, image_size, row_height = 6, 340, 314, 364
    rows = (len(files) + columns - 1) // columns
    preview = Image.new("RGB", (columns * width + 48, 142 + rows * row_height + 40), "#0c1625")
    draw = ImageDraw.Draw(preview)
    heading = ImageFont.truetype(str(FONT), 45)
    caption = ImageFont.load_default(size=21)
    small = ImageFont.load_default(size=17)
    draw.text((38, 28), "FREE RECRUITERS", font=heading, fill="#e7c989")
    draw.text((39, 85), "41 COUNTRY EDITIONS  /  ORIGINAL NAVY & GOLD DESIGN", font=small, fill="#b9c1cd")
    draw.line((39, 124, preview.width - 39, 124), fill="#79623d", width=1)
    for i, (country, path) in enumerate(files):
        x = 24 + (i % columns) * width
        y = 144 + (i // columns) * row_height
        image = Image.open(path).convert("RGB")
        image.thumbnail((image_size, image_size), LANCZOS)
        preview.paste(image, (x + (width - image.width) // 2, y))
        label = f"{i + 1:02d}  {country['name']}"
        box = draw.textbbox((0, 0), label, font=caption)
        draw.text((x + (width - (box[2] - box[0])) / 2, y + image_size + 12), label, font=caption, fill="#e9dfca")
    preview.save(OUTPUT / "All_Countries_Preview.jpg", quality=93, subsampling=0, optimize=True)


def package(files: list[tuple[dict, Path]]) -> None:
    archive = OUTPUT / "Free_Recruiters_41_Countries.zip"
    with ZipFile(archive, "w", compression=ZIP_DEFLATED, compresslevel=6) as z:
        for _, path in files:
            z.write(path, f"Free_Recruiters_41_Countries/{path.name}")
        index = (
            "FREE RECRUITERS — 41 COUNTRY EDITIONS\n\n"
            "41 separate PNG images, each 1024 x 1029 pixels.\n"
            "Only the country name and round flag badge have been edited.\n"
            "The source image has a solid background; these are not transparent/vector logos.\n"
            "Names and flags follow the order requested.\n\n"
            "۴۱ لوگوی مجزا با فرمت PNG، در ابعاد تصویر اصلی: ۱۰۲۴ × ۱۰۲۹ پیکسل.\n"
            "فقط نام کشور و نشان پرچم تغییر کرده است.\n\n"
        )
        index += "\n".join(f"{i:02d}. {c['name']} — {c['fa']}" for i, (c, _) in enumerate(files, 1))
        z.writestr("Free_Recruiters_41_Countries/README.txt", index.encode("utf-8"))
    print(f"Archive: {archive.name} ({archive.stat().st_size / 1024**2:.1f} MiB)", flush=True)


def build(codes: list[str] | None = None) -> None:
    original = Image.open(ASSETS / "original.jpg").convert("RGB")
    if original.size != (1024, 1029):
        raise ValueError("This template is calibrated for the supplied 1024 × 1029 source")
    base = clean_country(original)
    OUTPUT.mkdir(exist_ok=True)
    (OUTPUT / "logos").mkdir(exist_ok=True)
    files = []
    for index, country in enumerate(COUNTRIES, 1):
        if codes and country["code"] not in codes:
            continue
        image = country_text(base, country["name"])
        badge_image = badge(country["code"])
        image.paste(badge_image, BADGE_BOX[:2], badge_image.getchannel("A"))
        path = OUTPUT / "logos" / filename(index, country)
        metadata = PngImagePlugin.PngInfo()
        metadata.add_text("Title", f"Free Recruiters {country['name']}")
        metadata.add_text("Country", country["name"])
        metadata.add_text("CountryCode", country["code"].upper())
        image.save(path, pnginfo=metadata, compress_level=9)
        print(f"{index:02d}/41 {country['name']}: {path.stat().st_size:,} bytes", flush=True)
        files.append((country, path))
    if not codes:
        create_preview(files)
        package(files)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="+", help="Render just these ISO country codes for review")
    args = parser.parse_args()
    build(args.only)
