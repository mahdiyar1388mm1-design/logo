# Free Recruiters — 41 country editions

۴۱ نسخهٔ مجزا از لوگوی ارسالی، با نام انگلیسی کشور و پرچم همان کشور.
قاب، نشان مرکزی و نوشته‌های ثابت تصویر اصلی دست‌نخورده باقی مانده‌اند.

## Deliverables

- **[Download all 41 logos](deliverables/Free_Recruiters_41_Countries.zip)** — ZIP containing 41 individually named, full-resolution PNGs and a bilingual index.
- **[Overview of all 41](deliverables/All_Countries_Preview.jpg)** — numbered preview in the order requested.
- **[Individual PNGs](deliverables/logos/)** — 1024 × 1029 pixels, matching the supplied image.
- **[Browse the gallery](deliverables/index.html)** — Persian/English country search, region filters, full-size previews, and individual downloads. Works locally without a build or external services.

These are raster edits of the supplied JPEG, not new vector artwork, transparent logos, or enlarged print masters. The original solid background is retained. Only the country-name area and the round flag badge are edited. Flag insignia retain their aspect ratios; stripe/canton layouts are adapted for circular badges. Nepal's double pennant is preserved on a light badge background. Bolivia and Peru use the coat-of-arms versions supplied by the flag source.

## Rebuild

Python 3.11 or later:

```sh
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/build_logos.py
.venv/bin/python scripts/build_gallery.py
.venv/bin/python scripts/verify_deliverables.py
```

All required source assets are included, so rebuilding does not need a network connection.
For a quick single-country render:

```sh
.venv/bin/python scripts/build_logos.py --only co np kr
```

To view the gallery over HTTP:

```sh
python -m http.server 8080 --bind 0.0.0.0 --directory deliverables
```

The server exposes **only the deliverables directory**, not the repository or its Git metadata.

## Sources

- `assets/original.jpg`: the image supplied by the user, copied without recompression.
- `assets/flags/*.svg`: [hampusborgos/country-flags](https://github.com/hampusborgos/country-flags), pinned to `c09927e63705529bbf59ca6684cd9b23225dddad`. The upstream attribution/public-domain notice is retained in `assets/flags/README.source.md`. Local circular adaptations are used only for the badges; the supplied SVG source files are unchanged.
- `assets/fonts/Tinos-Bold.ttf`: Tinos Bold, from [Google Fonts](https://github.com/google/fonts/tree/main/ofl/tinos), under the SIL Open Font License. License retained in `assets/fonts/Tinos-OFL.txt`.
- `countries.json`: all 41 countries, ISO codes, Persian labels, and requested ordering.

`scripts/fetch_assets.py` can restore missing public source assets via the GitHub CLI. It never reads or stores credentials.

## Validation

`verify_deliverables.py` checks the exact country count, unique names/flags, image dimensions and metadata, archive CRCs and file contents, thumbnails, and gallery entries. It also checks **pixel-for-pixel identity with the original outside the two edit regions** for every PNG.

The finished image files and download archive are included because they are the requested deliverables. Virtual environments, intermediate crops, and scratch renders are ignored.
