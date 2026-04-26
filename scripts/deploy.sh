#!/bin/bash
set -e

PI_HOST="${PI_HOST:-raspberrypi.local}"
PI_USER="${PI_USER:-pi}"
PI_PATH="${PI_PATH:-~/projects/music_app_poc}"

echo "Deploying to $PI_USER@$PI_HOST:$PI_PATH ..."
ssh "$PI_USER@$PI_HOST" "cd $PI_PATH && git pull && sudo docker compose up -d --build"
echo "Done."
