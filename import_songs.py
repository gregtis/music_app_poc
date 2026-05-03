#!/usr/bin/env python3
"""Scan a library folder for new MP3s and add them to library.json.

For each series subfolder, finds MP3 files not already in library.json,
reads their ID3 tags, and appends new song entries. Existing entries are
never modified. Run validate_library.py afterwards to confirm.

Usage:
    python3 import_songs.py <library_dir>
"""

import json
import os
import re
import sys

# Noise patterns to strip from album tags when deriving the game name.
_ALBUM_NOISE = re.compile(
    r'\s*[:\-–]\s*(original\s+)?((complete\s+)?soundtrack|ost|gamerip|'
    r'expanded\s+soundtrack.*|music\s+collection.*).*$',
    re.IGNORECASE,
)

# If the artist tag matches any of these, it's a series/band name, not a composer.
_NOT_A_COMPOSER = re.compile(
    r'^(the\s+legend\s+of\s+zelda|zelda|mario|splatoon|nintendo|'
    r'various\s+artists?|unknown)$',
    re.IGNORECASE,
)

# Internal-ID title patterns (e.g. "BGM_Course_Athletic_Normal").
_INTERNAL_TITLE = re.compile(r'^(bgm|sfx|se|jingle)[_\-]', re.IGNORECASE)


def _read_id3(path):
    """Return a dict of cleaned tag values from an MP3. All values may be None."""
    try:
        from mutagen.id3 import ID3, ID3NoHeaderError
    except ImportError:
        print("  ! mutagen not installed — install with: sudo apt install python3-mutagen")
        return {}

    try:
        tags = ID3(path)
    except Exception:
        return {}

    def _str(key):
        val = tags.get(key)
        return str(val).strip() if val else None

    raw_title    = _str('TIT2')
    raw_album    = _str('TALB')
    raw_artist   = _str('TPE1')
    raw_year     = _str('TDRC') or _str('TYER')

    # Title: discard internal IDs, fall back to None (caller uses filename stem)
    title = None
    if raw_title and not _INTERNAL_TITLE.match(raw_title):
        title = raw_title.strip('‎‏​')  # strip invisible unicode

    # Game: strip noisy suffixes from album tag
    game = None
    if raw_album:
        game = _ALBUM_NOISE.sub('', raw_album).strip().strip(':').strip()
        if not game:
            game = None

    # Composer: discard if it looks like a series name
    composer = None
    if raw_artist and not _NOT_A_COMPOSER.match(raw_artist.strip()):
        composer = raw_artist.strip()

    # Year: extract the first 4-digit year from whatever format is present
    year = None
    if raw_year:
        m = re.search(r'\b(1[89]\d{2}|20[012]\d)\b', raw_year)
        if m:
            year = int(m.group(1))

    return {'title': title, 'game': game, 'composer': composer, 'year': year}


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <library_dir>")
        sys.exit(1)

    library_dir = sys.argv[1]
    json_path = os.path.join(library_dir, 'library.json')

    try:
        with open(json_path) as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"library.json not found at {json_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"JSON error: {e}")
        sys.exit(1)

    total_added = 0

    for series in data['series']:
        sid = series['id']
        folder = os.path.join(library_dir, sid)
        if not os.path.isdir(folder):
            continue

        # Build set of filenames already tracked
        existing = {os.path.basename(s['file']) for s in series['songs']}

        new_files = sorted(
            f for f in os.listdir(folder)
            if f.endswith('.mp3') and f not in existing
        )

        if not new_files:
            print(f"{sid}: no new files")
            continue

        print(f"\n{sid}: {len(new_files)} new file(s)")

        for fname in new_files:
            path = os.path.join(folder, fname)
            tags = _read_id3(path)

            stem = os.path.splitext(fname)[0]
            title    = tags.get('title') or stem
            game     = tags.get('game')
            composer = tags.get('composer')
            year     = tags.get('year')

            entry = {
                'title':    title,
                'file':     f'{sid}/{fname}',
                'game':     game,
                'year':     year,
                'system':   None,
                'composer': composer,
                'difficulty': None,
                'tags':     [],
            }
            series['songs'].append(entry)
            total_added += 1

            tag_summary = ', '.join(
                f'{k}={v!r}' for k, v in
                [('game', game), ('year', year), ('composer', composer)]
                if v is not None
            )
            print(f"  + {fname}")
            print(f"    title: {title!r}")
            if tag_summary:
                print(f"    tags:  {tag_summary}")
            else:
                print(f"    tags:  (none found — fill in manually)")

    if total_added == 0:
        print("\nNo new songs found.")
        return

    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\nAdded {total_added} song(s) to {json_path}")
    print("Review and clean up library.json, then run: python3 validate_library.py <library_dir>")


if __name__ == '__main__':
    main()
