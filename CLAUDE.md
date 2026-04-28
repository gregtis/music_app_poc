# CLAUDE.md — Music App POC

## What This Project Is

A Nintendo museum-style touchscreen kiosk app running on a Raspberry Pi 5 with no desktop environment. Users tap a character on screen, which takes them to that character's music player. Simple, fun, kid-friendly. No network required, no frills.

Inspired by the kind of interactive displays you'd find in a Nintendo museum exhibit.

---

## Hardware Target

| Component   | Detail                                        |
|-------------|-----------------------------------------------|
| Device      | Raspberry Pi 5                                |
| Display     | `/dev/fb0` — DRM FBDEV compat layer, 1024×600 RGB565 (16bpp) |
| Touchscreen | `/dev/input/event*` — auto-detected via evdev (ILITEK-TOUCH on event5) |
| Audio       | `/dev/snd`                                    |
| No desktop environment — X11/Wayland are NOT available |

---

## Stack

| Layer          | Choice           | Why                                                        |
|----------------|------------------|------------------------------------------------------------|
| Language       | Python 3         | Simple, fast to iterate, good Pi ecosystem                 |
| UI / Render    | pygame           | Software surface rendering; handles touch + audio well     |
| Display output | Direct `/dev/fb0` write | Bypasses SDL display drivers entirely (see below) |
| Audio          | pygame.mixer     | Built-in MP3 playback, no extra deps                       |
| Container      | Docker + Compose | Reproducible, easy to redeploy                             |
| Music format   | MP3              | Small, universally available, easy to source               |
| Version control | Git             | Push to GitHub, pull on Pi                                 |

---

## File Structure

```
music_app_poc/
├── CLAUDE.md               # This file
├── QUICKSTART.md           # How to build and run
├── tasks.md                # Phase-by-phase task checklist
├── docker-compose.yml      # Device mappings, container config
├── Dockerfile              # Python + pygame image
├── requirements.txt        # Python dependencies
├── config.py               # Characters, songs, metadata (single source of truth)
├── main.py                 # Entry point, pygame init, screen router, fb0 writer
├── touch.py                # Evdev touch input — auto-detects touchscreen device
├── screens/
│   ├── home.py             # Character select screen
│   └── character.py        # Music player screen
├── assets/
│   ├── images/characters/  # Character PNGs (drop in to replace placeholders)
│   └── music/
│       ├── mario/          # MP3s — filenames must match config.py
│       ├── link/
│       └── inkling_girl/
└── scripts/
    └── deploy.sh           # SSH + git pull + docker compose up on Pi
```

> Music files are bundled inside the Docker image (not mounted as a volume). This keeps the container fully self-contained but means rebuilding when music changes. Keep MP3s small; use 128kbps.

---

## How to Build and Run

```bash
# On the Pi (or via deploy.sh from dev machine)
cd ~/projects/music_app_poc
git pull
sudo docker compose up -d --build   # rebuild image + start
sudo docker compose up -d           # start without rebuild
sudo docker compose down            # stop
sudo docker compose logs -f         # tail logs
```

The `scripts/deploy.sh` script automates SSH + pull + rebuild from the WSL dev machine:
```bash
PI_HOST=raspberrypi.local PI_USER=pi bash scripts/deploy.sh
```

---

## Display Architecture — Read This Before Touching Anything Display-Related

### What works and why

`SDL_VIDEODRIVER=offscreen` renders pygame to a CPU-side surface with no display driver involvement. Each frame, `main.py` reads the raw 16-bit pixels from that surface and writes them directly to `/dev/fb0`. The DRM FBDEV compatibility layer (which backs `/dev/fb0`) maps those writes onto the KMS CRTC driving HDMI-A-1.

The rendering pipeline in `main.py`:
1. Screens draw to a logical `pygame.Surface` at 800×480
2. That surface is scaled to 1024×600 (native display size) via `pygame.transform.scale`
3. Blitted into a pre-allocated 16-bit `pygame.Surface` (RGB565, matching `/dev/fb0`)
4. Raw bytes written to `/dev/fb0` via an open file handle each frame
5. `pygame.display.flip()` is NOT called on Pi — it's a no-op with offscreen driver

### Why kmsdrm does not work — do not try to revert to it

Pi 5 uses KMS/DRM for display. SDL2's kmsdrm video driver was the first approach tried, and it fails for a fundamental reason baked into SDL2's source code:

> "Maybe you didn't ask for it, but if you can get it, you will."

SDL2 kmsdrm unconditionally adds `SDL_WINDOW_OPENGL` to any window it creates if EGL is available. This makes `SDL_GetWindowSurface()` return `NULL` (you cannot mix OpenGL and surface rendering on the same SDL window). pygame's `display.fill()` and all drawing calls write to a dead CPU buffer. `pygame.display.flip()` calls `SDL_UpdateWindowSurface()` which silently fails. The DRM scanout buffer stays at its EGL-initialized all-black state. The result: app runs correctly (touch, audio, routing all work) but the screen is black.

Removing EGL from the container (`libegl1`) to force a software path breaks kmsdrm init entirely — SDL2 2.32.4's kmsdrm driver requires EGL unconditionally.

### SDL2 video drivers available in the container

The container's `libsdl2-2.0-0` (Debian Bookworm arm64) has these drivers compiled in:

```
x11, wayland, KMSDRM, offscreen, dummy, evdev
```

**No `fbcon`.** Do not attempt `SDL_VIDEODRIVER=fbcon`.

### TTY graphics mode — why it's needed

When the container starts, `/dev/tty1` is the active Linux VT showing the Pi's console (boot info, IP address, etc.). The kernel's `fbcon` subsystem draws text and a blinking cursor onto `/dev/fb0` continuously. Without suppressing this, the cursor appears as a small black rectangle with a blinking yellow line overlaid on top of the app.

`main.py` fixes this by switching `/dev/tty1` to `KD_GRAPHICS` mode at startup using the `KDSETMODE` ioctl (`0x4B3A`). In graphics mode, the kernel stops all text/cursor rendering to the framebuffer. `KD_TEXT` mode is restored on exit so the console comes back cleanly.

This is the same mechanism X11 and Wayland compositors use when they take over the display.

`privileged: true` in `docker-compose.yml` is required for the `ioctl` to succeed.

### Framebuffer format

`/dev/fb0` on Pi 5: **1024×600, 16 bits per pixel, RGB565, stride = 2048 bytes.**

- Total frame size: 1024 × 600 × 2 = 1,228,800 bytes
- Pixel format: 5 bits red (high), 6 bits green, 5 bits blue (low) — little-endian
- pygame's 16-bit `Surface` matches this format natively; `get_buffer().raw` gives the correct bytes

---

## Touch Input Architecture

Touch is handled entirely via evdev, bypassing SDL input. `touch.py` auto-detects the touchscreen by scanning `/dev/input/event*` for devices with `ABS_MT_POSITION_X` or `ABS_X` capability. A daemon thread reads events and enqueues completed taps.

**Important:** Multitouch devices (including the ILITEK-TOUCH) fire both `ABS_MT_TRACKING_ID == -1` (MT finger-lift) and `BTN_TOUCH == 0` (single-touch compat) on a single physical lift. Using both handlers queues every tap twice, causing double-firing. `touch.py` detects at init whether the device supports MT tracking IDs and uses only one path — MT for multitouch devices, `BTN_TOUCH` only as a fallback for single-touch devices.

---

## Key Decisions

**config.py as single source of truth**
Adding a character or song = editing one file. No hardcoded names or paths scattered through UI code.

**Music bundled in the image, not volume-mounted**
No path management on the Pi, no missing files, no setup steps. Trade-off: rebuild required when music changes.

**Idle state: character select, no music**
Clean, kid-friendly. No ambient music or screensaver complexity.

**Songs are just songs**
Each character has 3 MP3s. No need to label them as "era" vs "remix" in the UI — the player just lets you cycle through them.

---

## MVP v1 — Complete

- [x] App launches on Pi 5 via `sudo docker compose up -d` with no other setup
- [x] Character select screen renders 3 characters (Mario, Link, Inkling Girl) on the framebuffer
- [x] Tapping a character navigates to that character's music player screen
- [x] Music player shows song title, plays MP3 on tap
- [x] Play/pause button works
- [x] Next/previous song cycling works (one tap = one song)
- [x] Back button returns to character select
- [x] Touch input works correctly (ILITEK-TOUCH, auto-detected)
- [x] Audio plays through `/dev/snd`
- [x] Container runs headlessly with no desktop environment
- [x] Terminal cursor suppressed via KD_GRAPHICS mode

---

## MVP v2 — Next

Visual and UX polish to make it feel like a real Nintendo kiosk:

- [ ] Real character artwork — replace colored-rectangle placeholders with PNG images in `assets/images/characters/`
- [ ] Nintendo-style font — replace `monospace` with a bold pixel or display font (e.g. a free Nintendo-style TTF bundled in `assets/fonts/`)
- [ ] Tap sound effect — short click or chime on button press to give tactile feedback
- [ ] Screen transition — brief fade or slide when navigating between screens
- [ ] Song labels — optionally surface the `"label"` field in `config.py` (currently hidden if empty) to distinguish game titles or remixes

Adding a character or song only requires editing `config.py`. Code changes are only needed for new UI features.

---

## Rules for Future AI Sessions

1. **Do not add features beyond what the user explicitly asks for.** No favorites, no volume slider, no settings screen, no network features.
2. **Do not switch the stack.** pygame on Python is the chosen renderer. Do not suggest Electron, Qt, Tkinter, or web-based alternatives.
3. **Extensibility lives in `config.py`.** Adding characters or songs = editing config, not restructuring code.
4. **Display path is offscreen + /dev/fb0. Do not change it.** Do not attempt kmsdrm, fbcon, or any other SDL video driver. See "Display Architecture" above for the full reasoning.
5. **Touch input is evdev, not mouse.** Do not assume a mouse cursor exists. Touch is auto-detected; do not hardcode `/dev/input/event5`.
6. **Keep it kid-friendly and Nintendo-flavored.** Big tap targets, bold colors, simple navigation. No text-heavy UI.
7. **Deployment is always `sudo docker compose up -d` on the Pi.** Do not introduce steps that break this workflow.
8. **Music files are the user's responsibility.** Do not write code to download, stream, or auto-source music.

---

## Development Workflow

```bash
# Local (WSL Ubuntu)
git add . && git commit -m "..." && git push

# On Pi (via SSH), or use scripts/deploy.sh
cd ~/projects/music_app_poc
git pull
sudo docker compose up -d --build
```

---

## Environment Notes

- Dev machine: Windows with WSL Ubuntu, using Claude Code
- Pi accessed via SSH from WSL (passwordless key auth configured)
- Pi IP: 192.168.7.39, user: gregtis
- Pi project path: `~/projects/music_app_poc`
- Git remote: https://github.com/gregtis/music_app_poc
