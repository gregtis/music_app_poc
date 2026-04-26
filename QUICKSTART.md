# QUICKSTART — Music App POC

## What you need

**Dev machine (WSL Ubuntu):** Docker, Git
**Raspberry Pi 5:** Docker + Compose, Git, SSH access from dev machine

---

## 1. Add your music files

Drop MP3s into the matching folders and name them exactly as listed in `config.py`:

```
assets/music/mario/       mario_1.mp3  mario_2.mp3  mario_3.mp3
assets/music/link/        link_1.mp3   link_2.mp3   link_3.mp3
assets/music/inkling_girl/  inkling_girl_1.mp3  ...  inkling_girl_3.mp3
```

To use different filenames, update the `"file"` field in `config.py` to match.

---

## 2. First-time Pi setup

SSH into the Pi and run:

```bash
mkdir -p ~/projects && cd ~/projects
git clone <your-github-repo-url> music_app_poc
```

---

## 3. Deploy

From your dev machine (WSL):

```bash
git add . && git commit -m "update" && git push
```

Then run the deploy script (set `PI_HOST` and `PI_USER` to match your Pi):

```bash
PI_HOST=raspberrypi.local PI_USER=pi bash scripts/deploy.sh
```

Or SSH in manually and run:

```bash
cd ~/projects/music_app_poc && git pull && sudo docker compose up -d --build
```

---

## 4. Stop / restart

```bash
sudo docker compose down        # stop
sudo docker compose up -d       # start (no rebuild)
sudo docker compose up -d --build  # start + rebuild image
```

## 5. View logs

```bash
sudo docker compose logs -f
```

---

## Troubleshooting

**Blank screen**
Confirm `/dev/fb0` exists: `ls -la /dev/fb0`

**No touch response**
Run `sudo evtest` on the Pi to identify your touchscreen's event device.
If it's not `event5`, the app auto-detects it — check the container logs for the confirmed device path.

**No audio**
Check `aplay -l` and `amixer` on the Pi to confirm the audio device is present and unmuted.

**"(no music file)" shown on player screen**
The MP3 for that song is missing. Check filenames match `config.py` exactly.
