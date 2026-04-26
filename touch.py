import threading
import queue

import evdev
from evdev import ecodes

_tap_queue = queue.Queue()
_touch_x_raw = 0
_touch_y_raw = 0
_x_min = 0
_x_max = 4095
_y_min = 0
_y_max = 4095
_screen_w = 800
_screen_h = 480


def _map(value, in_min, in_max, out_min, out_max):
    if in_max == in_min:
        return out_min
    v = int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)
    return max(out_min, min(out_max, v))


def find_touchscreen():
    for path in evdev.list_devices():
        try:
            device = evdev.InputDevice(path)
            caps = device.capabilities()
            if ecodes.EV_ABS in caps:
                axes = {code for code, _ in caps[ecodes.EV_ABS]}
                if ecodes.ABS_MT_POSITION_X in axes or ecodes.ABS_X in axes:
                    return device
        except Exception:
            continue
    return None


def _reader(device):
    global _touch_x_raw, _touch_y_raw

    for event in device.read_loop():
        if event.type == ecodes.EV_ABS:
            if event.code in (ecodes.ABS_MT_POSITION_X, ecodes.ABS_X):
                _touch_x_raw = event.value
            elif event.code in (ecodes.ABS_MT_POSITION_Y, ecodes.ABS_Y):
                _touch_y_raw = event.value
            elif event.code == ecodes.ABS_MT_TRACKING_ID and event.value == -1:
                x = _map(_touch_x_raw, _x_min, _x_max, 0, _screen_w - 1)
                y = _map(_touch_y_raw, _y_min, _y_max, 0, _screen_h - 1)
                _tap_queue.put((x, y))
        elif event.type == ecodes.EV_KEY:
            if event.code == ecodes.BTN_TOUCH and event.value == 0:
                x = _map(_touch_x_raw, _x_min, _x_max, 0, _screen_w - 1)
                y = _map(_touch_y_raw, _y_min, _y_max, 0, _screen_h - 1)
                _tap_queue.put((x, y))


def init(screen_w, screen_h):
    global _x_min, _x_max, _y_min, _y_max, _screen_w, _screen_h

    _screen_w = screen_w
    _screen_h = screen_h

    device = find_touchscreen()
    if device is None:
        print("WARNING: No touchscreen found — touch input disabled.")
        return False

    caps = device.capabilities()
    if ecodes.EV_ABS in caps:
        for code, info in caps[ecodes.EV_ABS]:
            if code in (ecodes.ABS_MT_POSITION_X, ecodes.ABS_X):
                _x_min, _x_max = info.min, info.max
            elif code in (ecodes.ABS_MT_POSITION_Y, ecodes.ABS_Y):
                _y_min, _y_max = info.min, info.max

    t = threading.Thread(target=_reader, args=(device,), daemon=True)
    t.start()
    print(f"Touch: {device.name} ({device.path})  x={_x_min}–{_x_max}  y={_y_min}–{_y_max}")
    return True


def get_tap():
    """Return (x, y) of the next completed tap, or None."""
    try:
        return _tap_queue.get_nowait()
    except queue.Empty:
        return None
