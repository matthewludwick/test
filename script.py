#!/usr/bin/env python3
"""
Download real trail photos to replace the placeholder SVGs.

USAGE:
  1. Make sure you're in the site/ folder (the one with index.html in it).
  2. Run:  python3 download_photos.py
  3. The script will:
       - Download a curated Unsplash photo for each trail and the hero image
       - Save them as .jpg files in images/trails/ and images/
       - Update js/trails.js, index.html, and safety.html to point to the
         new .jpg files

REQUIREMENTS:
  - Python 3.7+
  - Internet connection (only uses Python's standard library, no pip installs)

HOW IT WORKS:
  - Uses direct images.unsplash.com CDN URLs. These work permanently without
    an API key. Unsplash's old source.unsplash.com redirector was shut down
    in 2024, so we use direct CDN URLs instead.
  - To swap a photo: visit unsplash.com, find a photo you like, right-click
    it and choose "Copy Image Address." Paste that URL into PHOTO_MAP below
    (replace the relevant entry's URL).

REVERTING:
  - Delete the .jpg files in images/trails/ and images/
  - Find/replace ".jpg" with ".svg" in js/trails.js  (only on image paths)
  - Find/replace "images/hero.jpg" with "images/hero.svg" in index.html
    and safety.html
"""

import os
import sys
import urllib.request
import urllib.error

# ----------------------------------------------------------------------------
# Curated Pacific Northwest hiking photos from Unsplash.
# Each entry: (base_filename, full_unsplash_cdn_url, short_description)
# The base_filename MUST match what's currently in js/trails.js (without ext).
# ----------------------------------------------------------------------------
PHOTO_MAP = [
    ("photo-1600929622034",
     "https://images.unsplash.com/photo-1600929622034-03132aad9692?w=1080&fm=jpg&q=80",
     "old-growth forest"),
    ("photo-1630626883157",
     "https://images.unsplash.com/photo-1630626883157-ee79a00218ae?w=1080&fm=jpg&q=80",
     "river gorge"),
    ("photo-1621863200562",
     "https://images.unsplash.com/photo-1621863200562-b32931090e19?w=1080&fm=jpg&q=80",
     "rocky summit"),
    ("photo-1630123738777",
     "https://images.unsplash.com/photo-1630123738777-fdd4f8b7d16b?w=1080&fm=jpg&q=80",
     "forest canopy"),
    ("photo-1696219364293",
     "https://images.unsplash.com/photo-1696219364293-e38483602e49?w=1080&fm=jpg&q=80",
     "alpine peaks"),
    ("photo-1599606843763",
     "https://images.unsplash.com/photo-1599606843763-84d2622d5a05?w=1080&fm=jpg&q=80",
     "mountain lake"),
    ("photo-1534991199945",
     "https://images.unsplash.com/photo-1534991199945-78b32ba73274?w=1080&fm=jpg&q=80",
     "alpine lake"),
    ("photo-1696219364361",
     "https://images.unsplash.com/photo-1696219364361-ba4eac9f2361?w=1080&fm=jpg&q=80",
     "valley overlook"),
    ("photo-1593916845953",
     "https://images.unsplash.com/photo-1593916845953-88c95e58a586?w=1080&fm=jpg&q=80",
     "waterfall canyon"),
]

# Hero image (wider crop of the waterfall canyon used in the original React app)
HERO_URL = "https://images.unsplash.com/photo-1593916845953-88c95e58a586?w=1920&fm=jpg&q=80"


def download(url, out_path):
    """Download a single URL to out_path. Returns True on success."""
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (school project / download-photos.py)"
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        if len(data) < 5000:
            print(f"    ! response was only {len(data)} bytes, skipping")
            return False
        with open(out_path, "wb") as f:
            f.write(data)
        return True
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
        print(f"    ! failed: {e}")
        return False


def main():
    if not os.path.isfile("index.html") or not os.path.isfile("js/trails.js"):
        print("ERROR: run this from inside the site/ folder (the one containing index.html).")
        print(f"       Current directory: {os.getcwd()}")
        sys.exit(1)

    os.makedirs("images/trails", exist_ok=True)

    print("Downloading trail photos from Unsplash...")
    print()

    success_bases = []
    failed = []

    for base, url, caption in PHOTO_MAP:
        out_path = f"images/trails/{base}.jpg"
        print(f"  {base}.jpg  ({caption})")
        if download(url, out_path):
            size_kb = os.path.getsize(out_path) // 1024
            print(f"    ✓ saved → {out_path}  ({size_kb} KB)")
            success_bases.append(base)
        else:
            failed.append(base)

    # Hero
    print()
    print("Downloading hero image...")
    hero_ok = download(HERO_URL, "images/hero.jpg")
    if hero_ok:
        size_kb = os.path.getsize("images/hero.jpg") // 1024
        print(f"    ✓ saved → images/hero.jpg  ({size_kb} KB)")
    else:
        print(f"    ! hero failed, keeping images/hero.svg")

    # --- Update js/trails.js ---
    print()
    print("Updating js/trails.js...")
    with open("js/trails.js", "r", encoding="utf-8") as f:
        trails_js = f.read()
    js_edits = 0
    for base in success_bases:
        old = f"images/trails/{base}.svg"
        new = f"images/trails/{base}.jpg"
        count = trails_js.count(old)
        if count > 0:
            trails_js = trails_js.replace(old, new)
            js_edits += count
    with open("js/trails.js", "w", encoding="utf-8") as f:
        f.write(trails_js)
    print(f"    ✓ updated {js_edits} reference(s)")

    # --- Update HTML files (hero image) ---
    if hero_ok:
        for html_file in ("index.html", "safety.html"):
            if not os.path.isfile(html_file):
                continue
            with open(html_file, "r", encoding="utf-8") as f:
                content = f.read()
            new_content = content.replace("images/hero.svg", "images/hero.jpg")
            if new_content != content:
                with open(html_file, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"    ✓ updated hero reference in {html_file}")

    # --- Summary ---
    print()
    print("=" * 60)
    print(f"Downloaded: {len(success_bases)}/{len(PHOTO_MAP)} trail photo(s)" +
          f" + {'1 hero' if hero_ok else '0 hero'}")
    if failed:
        print(f"Failed:     {len(failed)} ({', '.join(failed)})")
        print("            Those trails still use the SVG placeholder.")
    print("=" * 60)
    print()
    print("Done! Open index.html (or push to GitHub) to see the new photos.")
    print()
    print("Tip: to swap any photo for a different one, edit PHOTO_MAP at the")
    print("top of this script, delete the corresponding .jpg, and re-run.")


if __name__ == "__main__":
    main()
