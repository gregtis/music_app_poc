# tasks.md — Music App POC

Track progress here. Mark tasks `[x]` when done.

---

## Phase 1 — MVP

### Setup
- [ ] Scaffold full folder/file structure
- [ ] `git init` + initial commit
- [ ] Create GitHub repo and push

### Docker
- [ ] Write `Dockerfile` (Python 3 + pygame + evdev)
- [ ] Write `docker-compose.yml` with `/dev/fb0`, `/dev/input/event*`, `/dev/snd` device passthrough
- [ ] Verify container builds locally on WSL

### Config
- [ ] Write `config.py` — 3 characters (Mario, Link, Samus), 3 songs each, file paths, display names
- [ ] Create `src/assets/music/` folder structure (mario/, link/, samus/)
- [ ] Add placeholder MP3s or silence files for testing before real music is added

### Touch Input (do this first — highest risk)
- [ ] Spike: confirm evdev reads touch events from correct `/dev/input/event*` inside container
- [ ] Write touch device auto-detection (scan by capabilities, not hardcoded path)
- [ ] Map raw evdev coordinates to screen pixel coordinates

### Screens
- [ ] `src/main.py` — pygame init, `SDL_VIDEODRIVER=fbcon`, screen router loop
- [ ] `src/screens/home.py` — character select, 3 tap targets (colored rects + name labels)
- [ ] `src/screens/character.py` — song title display, play/pause button, next/prev buttons, back button
- [ ] Wire audio: `pygame.mixer` plays MP3 on character screen, stops on back

### Deploy
- [ ] Write `QUICKSTART.md`
- [ ] Write `scripts/deploy.sh` (SSH into Pi, git pull, docker compose up --build)

### Validation
- [ ] Deploy to Pi 5 and run `sudo docker compose up -d`
- [ ] All 3 characters reachable by touch
- [ ] Play/pause works
- [ ] Next/prev song works
- [ ] Back returns to home screen
- [ ] Audio comes out of speakers

---

## Phase 2 — Polish

- [ ] Replace colored-rect placeholders with real character PNG artwork
- [ ] Add Nintendo-style pixel/retro TTF font
- [ ] Add tap sound effect (short blip on any button press)
- [ ] Add screen transition (fade or slide between home and character screen)
- [ ] Show era/remix label alongside song title on player screen
- [ ] Add visual press feedback (button highlight/flash on tap)

---

## Phase 3 — Stretch

- [ ] Add 4th+ character (config.py only change)
- [ ] Add more songs per character
- [ ] Per-character color theme on player screen
- [ ] On-screen volume control (+/-)
- [ ] "Now playing" animation (bouncing sprite or waveform)
- [ ] Idle attract mode / screensaver after 60s of no input
