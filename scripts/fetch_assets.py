#!/usr/bin/env python3
"""Fetch the public SVG flags and licensed font via the authenticated GitHub CLI."""
from __future__ import annotations

import base64
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
FLAG_COMMIT = "c09927e63705529bbf59ca6684cd9b23225dddad"
COUNTRIES = json.loads((ROOT / "countries.json").read_text())


def fetch(item: tuple[str, str]) -> str:
    destination, api_path = item
    path = ROOT / destination
    if path.is_file():
        return f"Already present: {destination}"
    response = subprocess.run(
        ["gh", "api", api_path], check=True, capture_output=True, text=True
    )
    data = json.loads(response.stdout)
    if data.get("encoding") != "base64":
        raise RuntimeError(f"Unexpected content encoding: {api_path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(base64.b64decode(data["content"]))
    return f"Saved {destination} ({path.stat().st_size:,} bytes)"


def main() -> None:
    items = [
        (
            f"assets/flags/{c['code']}.svg",
            f"repos/hampusborgos/country-flags/contents/svg/{c['code']}.svg?ref={FLAG_COMMIT}",
        )
        for c in COUNTRIES
    ]
    items += [
        (
            "assets/fonts/Tinos-Bold.ttf",
            "repos/google/fonts/contents/ofl/tinos/Tinos-Bold.ttf",
        ),
        (
            "assets/fonts/Tinos-OFL.txt",
            "repos/googlefonts/tinos/contents/OFL.txt?ref=3b4482a99b80ea5fc75f187b1be3120a3f5905b3",
        ),
    ]
    with ThreadPoolExecutor(max_workers=6) as pool:
        for result in pool.map(fetch, items):
            print(result, flush=True)


if __name__ == "__main__":
    main()
