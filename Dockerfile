FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libsdl2-2.0-0 \
    libsdl2-mixer-2.0-0 \
    libsdl2-image-2.0-0 \
    libsdl2-ttf-2.0-0 \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV SDL_VIDEODRIVER=fbcon
ENV SDL_FBDEV=/dev/fb0
ENV SDL_AUDIODRIVER=alsa

CMD ["python", "main.py"]
