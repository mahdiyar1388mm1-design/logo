#!/usr/bin/env python3
"""Validate all 41 exports, exact preservation of the original, and ZIP integrity."""
from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile
import json
import unittest

import numpy as np
from PIL import Image

from build_logos import TEXT_BOX, BADGE_BOX, filename

ROOT = Path(__file__).resolve().parents[1]
COUNTRIES = json.loads((ROOT / "countries.json").read_text())
OUTPUT = ROOT / "deliverables"


class DeliverableTests(unittest.TestCase):
    def test_country_list(self):
        self.assertEqual(len(COUNTRIES), 41)
        self.assertEqual(len({c["code"] for c in COUNTRIES}), 41)
        self.assertEqual(len({c["name"] for c in COUNTRIES}), 41)
        for c in COUNTRIES:
            self.assertTrue((ROOT / "assets/flags" / f"{c['code']}.svg").is_file())

    def test_images_and_original_preservation(self):
        original = np.array(Image.open(ROOT / "assets/original.jpg").convert("RGB"))
        allowed = np.zeros(original.shape[:2], dtype=bool)
        for x0, y0, x1, y1 in (TEXT_BOX, BADGE_BOX):
            allowed[y0:y1, x0:x1] = True
        country_regions, badges = set(), set()
        self.assertEqual(len(list((OUTPUT / "logos").glob("*.png"))), 41)
        for index, c in enumerate(COUNTRIES, 1):
            with self.subTest(country=c["name"]):
                path = OUTPUT / "logos" / filename(index, c)
                with Image.open(path) as image:
                    self.assertEqual(image.format, "PNG")
                    self.assertEqual(image.size, (1024, 1029))
                    self.assertEqual(image.mode, "RGB")
                    self.assertEqual(image.info["Country"], c["name"])
                    self.assertEqual(image.info["CountryCode"], c["code"].upper())
                    pixels = np.array(image)
                    self.assertTrue(np.array_equal(pixels[~allowed], original[~allowed]),
                                    "Pixels outside the country name and flag changed")
                    country_regions.add(sha256(image.crop(TEXT_BOX).tobytes()).hexdigest())
                    badges.add(sha256(image.crop(BADGE_BOX).tobytes()).hexdigest())
        self.assertEqual(len(country_regions), 41, "A country title was duplicated")
        self.assertEqual(len(badges), 41, "A flag badge was duplicated")

    def test_archive(self):
        with ZipFile(OUTPUT / "Free_Recruiters_41_Countries.zip") as archive:
            self.assertIsNone(archive.testzip())
            pngs = [n for n in archive.namelist() if n.endswith(".png")]
            self.assertEqual(len(pngs), 41)
            for index, c in enumerate(COUNTRIES, 1):
                name = filename(index, c)
                self.assertEqual(
                    archive.read(f"Free_Recruiters_41_Countries/{name}"),
                    (OUTPUT / "logos" / name).read_bytes(),
                )

    def test_preview_and_thumbnails(self):
        with Image.open(OUTPUT / "All_Countries_Preview.jpg") as image:
            self.assertGreater(image.width, 2000)
            self.assertGreater(image.height, 2000)
            image.verify()
        for c in COUNTRIES:
            path = OUTPUT / "thumbnails" / f"{c['code']}.webp"
            with Image.open(path) as image:
                self.assertEqual(image.size, (440, 442))
                image.verify()
        html = (OUTPUT / "index.html").read_text()
        self.assertEqual(html.count('class="country-card"'), 41)
        for c in COUNTRIES:
            self.assertIn(f'data-code="{c["code"]}"', html)


if __name__ == "__main__":
    unittest.main(verbosity=2)
