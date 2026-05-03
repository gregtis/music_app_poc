import json
import os


def load(library_dir):
    """Load library.json from library_dir.

    Returns (series_list, error_message).
    On success: error_message is None, series_list has resolved absolute paths
    and pygame-compatible color tuples.
    On failure: series_list is None, error_message describes what went wrong.
    """
    json_path = os.path.join(library_dir, "library.json")

    try:
        with open(json_path) as f:
            data = json.load(f)
    except FileNotFoundError:
        msg = f"library.json not found at:\n{json_path}"
        print(f"[library] ERROR: {msg}", flush=True)
        return None, msg
    except json.JSONDecodeError as e:
        msg = f"JSON syntax error in library.json\nline {e.lineno}, col {e.colno}: {e.msg}"
        print(f"[library] ERROR: {msg}", flush=True)
        return None, msg

    errors = _validate(data)
    if errors:
        msg = "library.json errors:\n" + "\n".join(f"  {e}" for e in errors)
        print(f"[library] ERROR:\n{msg}", flush=True)
        return None, msg

    return _resolve(data["series"], library_dir), None


def _validate(data):
    errors = []

    if not isinstance(data.get("series"), list) or not data["series"]:
        errors.append('"series" must be a non-empty list')
        return errors

    seen_ids = set()
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
            errors.append(f'{p}: "color" must be [R, G, B] integers 0-255')

        songs = s.get("songs")
        if isinstance(songs, list) and songs:
            for j, song in enumerate(songs):
                sp = f'{p}.songs[{j}]'
                for field in ("title", "file"):
                    if field not in song:
                        errors.append(f'{sp}: missing required field "{field}"')
                difficulty = song.get("difficulty")
                if difficulty is not None and difficulty not in ("easy", "medium", "hard"):
                    errors.append(f'{sp}: "difficulty" must be easy/medium/hard, got "{difficulty}"')
        elif songs is not None:
            errors.append(f'{p}: "songs" must be a non-empty list')

    return errors


def _resolve(series, library_dir):
    result = []
    for s in series:
        entry = dict(s)
        entry["color"] = tuple(s["color"])

        raw_image = s.get("image")
        entry["image"] = os.path.join(library_dir, raw_image) if raw_image else None

        entry["songs"] = [
            {**song, "file": os.path.join(library_dir, song["file"])}
            for song in s["songs"]
        ]
        result.append(entry)
    return result
