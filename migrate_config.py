#!/usr/bin/env python3
"""One-time migration: reads config.py and generates library/library.json.

Also copies MP3s and images into the library/ folder structure.

Usage:
    python migrate_config.py
"""

import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(__file__))
import config  # noqa: E402

MUSIC_PREFIX = "assets/music/"
IMAGE_PREFIX = "assets/images/characters/"
OUT_DIR = os.path.join(os.path.dirname(__file__), "library")


def strip_prefix(path, prefix):
    if path and path.startswith(prefix):
        return path[len(prefix):]
    return path


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    series = []
    files_to_copy = []

    for char in config.CHARACTERS:
        raw_image = char.get("image", "")
        image_rel = strip_prefix(raw_image, IMAGE_PREFIX)

        image_exists = raw_image and os.path.exists(raw_image)
        if image_exists:
            files_to_copy.append((raw_image, os.path.join(OUT_DIR, image_rel)))

        songs = []
        for song in char["songs"]:
            raw_file = song["file"]
            file_rel = strip_prefix(raw_file, MUSIC_PREFIX)
            if raw_file and os.path.exists(raw_file):
                files_to_copy.append((raw_file, os.path.join(OUT_DIR, file_rel)))
            songs.append({
                "title": song["title"],
                "file": file_rel,
                "game": None,
                "year": None,
                "system": None,
                "composer": None,
                "difficulty": None,
                "tags": [],
            })

        series.append({
            "id": char["id"],
            "name": char["name"].replace("\n", " "),
            "color": list(char["color"]),
            "image": image_rel if image_exists else None,
            "songs": songs,
        })

    # Copy files
    copied = 0
    skipped = 0
    for src, dst in files_to_copy:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.exists(dst):
            skipped += 1
        else:
            shutil.copy2(src, dst)
            copied += 1

    # Write library.json
    library = {"schema_version": "1.0", "series": series}
    out_path = os.path.join(OUT_DIR, "library.json")
    with open(out_path, "w") as f:
        json.dump(library, f, indent=2)

    print(f"Written:  {out_path}")
    print(f"Copied:   {copied} file(s) into library/")
    if skipped:
        print(f"Skipped:  {skipped} file(s) already present")
    print()
    print("Quiz fields (game, year, system, composer, difficulty) are null.")
    print("Edit library/library.json to fill them in before using quiz mode.")
    print()
    print("Validate with:  python validate_library.py library/")


if __name__ == "__main__":
    main()
