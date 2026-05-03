#!/usr/bin/env python3
"""Validate a music library folder before restarting the app.

Usage:
    python validate_library.py <library_dir>

Exit code 0 = valid, 1 = errors found.
"""

import json
import os
import sys

VALID_DIFFICULTIES = {"easy", "medium", "hard"}


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <library_dir>")
        sys.exit(1)

    library_dir = sys.argv[1]
    errors = []

    # --- 1. library.json exists and parses ---
    json_path = os.path.join(library_dir, "library.json")
    print(f"Checking {json_path}...")

    try:
        with open(json_path) as f:
            raw = f.read()
    except FileNotFoundError:
        _fail([f"library.json not found at {json_path}"])

    try:
        data = json.loads(raw)
        print("  + Valid JSON")
    except json.JSONDecodeError as e:
        _fail([f"JSON syntax error at line {e.lineno}, col {e.colno}: {e.msg}"])

    # --- 2. Schema ---
    print("\nChecking schema...")

    if not isinstance(data.get("series"), list) or not data["series"]:
        _fail(['"series" must be a non-empty list'])

    seen_ids = set()
    file_checks = []

    for i, s in enumerate(data["series"]):
        sid = s.get("id", "?")
        p = f'series[{i}] "{sid}"'

        for field in ("id", "name", "color", "songs"):
            if field not in s:
                errors.append(f'{p}: missing required field "{field}"')

        if sid != "?":
            if sid in seen_ids:
                errors.append(f'{p}: duplicate id')
            seen_ids.add(sid)

        color = s.get("color")
        if color is not None and (
            not isinstance(color, list) or len(color) != 3
            or not all(isinstance(c, int) and 0 <= c <= 255 for c in color)
        ):
            errors.append(f'{p}: "color" must be [R, G, B] integers 0-255, got {color!r}')

        raw_image = s.get("image")
        if raw_image:
            file_checks.append((f'{p} image "{raw_image}"',
                                 os.path.join(library_dir, raw_image)))

        songs = s.get("songs")
        if isinstance(songs, list) and songs:
            for j, song in enumerate(songs):
                sp = f'{p}.songs[{j}]'
                for field in ("title", "file"):
                    if field not in song:
                        errors.append(f'{sp}: missing required field "{field}"')
                raw_file = song.get("file")
                if raw_file:
                    file_checks.append((f'{sp} "{raw_file}"',
                                        os.path.join(library_dir, raw_file)))
                difficulty = song.get("difficulty")
                if difficulty is not None and difficulty not in VALID_DIFFICULTIES:
                    errors.append(
                        f'{sp}: "difficulty" must be easy/medium/hard, got "{difficulty}"')
        elif songs is not None:
            errors.append(f'{p}: "songs" must be a non-empty list')

    if errors:
        for e in errors:
            print(f"  x {e}")
    else:
        print(f"  + {len(data['series'])} series, all IDs unique")

    # --- 3. Files on disk ---
    print("\nChecking files on disk...")
    for label, path in file_checks:
        if os.path.isfile(path):
            print(f"  + {label}")
        else:
            print(f"  x {label}  --  FILE NOT FOUND")
            errors.append(f"{label}: file not found")

    # --- Summary ---
    print()
    if not errors:
        print("Library is valid.")
        sys.exit(0)
    else:
        n = len(errors)
        print(f"{n} error{'s' if n != 1 else ''} found. Fix before restarting the app.")
        sys.exit(1)


def _fail(errors):
    for e in errors:
        print(f"  x {e}")
    n = len(errors)
    print(f"\n{n} error{'s' if n != 1 else ''} found.")
    sys.exit(1)


if __name__ == "__main__":
    main()
