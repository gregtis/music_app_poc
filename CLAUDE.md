# CLAUDE.md — Music App POC

## What This Project Is

A Nintendo museum-style touchscreen kiosk app running on a Raspberry Pi 5 with no desktop environment. Users tap a character on screen, which takes them to that character's music player. Simple, fun, kid-friendly. No network required, no frills.

Inspired by the kind of interactive displays you'd find in a Nintendo museum exhibit.

---

## Hardware Target

| Component   | Detail                        |
|-------------|-------------------------------|
| Device      | Raspberry Pi 5                |
| Display     | `/dev/fb0` (raw framebuffer)  |
| Touchscreen | `/dev/input/event5`           |
| Audio       | `/dev/snd`                    |
| No desktop environment — X11/Wayland are NOT available |

---

## Stack

| Layer       | Choice         | Why                                                       |
|-------------|----------------|-----------------------------------------------------------|
| Language    | Python 3       | Simple, fast to iterate, good Pi ecosystem                |
| UI / Render | pygame         | Draws directly to framebuffer; handles touch + audio well |
| Audio       | pygame.mixer   | Built-in MP3 playback, no extra deps                      |
| Container   | Docker + Compose | Reproducible, easy to redeploy                          |
| Music format | MP3           | Small, universally available, easy to source              |
| Version control | Git        | Push to GitHub, pull on Pi                                |

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
├── main.py                 # Entry point, pygame init, screen router
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

> Note: Music files are bundled inside the Docker image (not mounted as a volume). This keeps the container fully self-contained but means rebuilding the image when music changes. Keep MP3s small; use 128kbps.

---

## Key Decisions

**Python + pygame over Node/Electron or C++/SDL2**
Pygame runs directly on the Linux framebuffer via `SDL_VIDEODRIVER=fbcon`. It handles touch input, audio mixing, and 2D rendering in one library with minimal setup. Right choice for a Pi with no desktop.

**Music bundled in the image, not volume-mounted**
Simplicity wins. No path management on the Pi, no missing files, no setup steps beyond `docker compose up -d`. Trade-off: larger image size.

**No privileged Docker mode**
Devices are passed through explicitly via `devices:` in `docker-compose.yml`. Avoids granting the container full hardware access unnecessarily.

**Songs cover both eras and remixes**
Each character has 3 MP3s that may span different game soundtracks (OoT vs BotW) and/or remix vs original. The player UI lets you cycle through them. No need to distinguish "era" vs "remix" in the UI — they're just songs.

**config.py as single source of truth**
Adding a new character or song means editing one file (`config.py`). No hardcoded character names or file paths scattered through the UI code. This is the extensibility hook.

**Idle state: character select screen, no music**
Clean, simple, kid-friendly. No ambient music or screensaver to add complexity.

---

## MVP Definition ("Done")

- [ ] App launches on Pi 5 via `sudo docker compose up -d` with no other setup
- [ ] Character select screen renders 3 characters (Mario, Link, Inkling Girl) on the framebuffer
- [ ] Tapping a character navigates to that character's music player screen
- [ ] Music player shows song title, plays MP3 on tap
- [ ] Play/pause button works
- [ ] Next/previous song cycling works
- [ ] Back button returns to character select
- [ ] Touch input works correctly on `/dev/input/event5`
- [ ] Audio plays through `/dev/snd`
- [ ] Container runs headlessly with no desktop environment

---

## Rules for Future AI Sessions

1. **Do not add features beyond the MVP list above.** No favorites, no volume slider, no settings screen, no network features unless the user explicitly asks.
2. **Do not switch the stack.** pygame on Python is the chosen renderer. Do not suggest Electron, Qt, Tkinter, or web-based alternatives.
3. **Extensibility lives in `config.py`.** Adding characters or songs = editing config, not restructuring code.
4. **No desktop environment.** Do not write code that depends on X11, Wayland, or a display server. `SDL_VIDEODRIVER=fbcon` must be set.
5. **Touch input is evdev, not mouse.** Handle touch via `/dev/input/event5` using pygame's evdev support or direct evdev reading — do not assume a mouse cursor exists.
6. **Keep it kid-friendly and Nintendo-flavored.** Big tap targets, bold colors, simple navigation. No text-heavy UI.
7. **Deployment is always `sudo docker compose up -d` on the Pi.** Do not introduce steps that break this workflow.
8. **Music files are the user's responsibility.** Do not write code to download, stream, or auto-source music. Assume files exist at the paths defined in `config.py`.

---

## Development Workflow

```
# Local (WSL Ubuntu, Windows machine)
git commit && git push

# On Raspberry Pi (via SSH)
cd ~/projects/music_app_poc
git pull
sudo docker compose up -d --build
```

The `scripts/deploy.sh` script automates the SSH + pull + rebuild step from the dev machine.

---

## Environment Notes

- Dev machine: Windows with WSL Ubuntu, using Claude Code
- Pi is accessed via SSH from WSL
- Git remote: GitHub (repo TBD)
- Pi project path: `~/projects/music_app_poc`
