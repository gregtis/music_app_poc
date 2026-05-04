import os
import time
import pygame
import config

WHITE      = (255, 255, 255)
DIM        = (155, 155, 160)
BACK_COLOR = (55, 55, 60)
RADIUS     = 38   # pill shape for playback buttons


class CharacterScreen:
    def __init__(self, screen, character):
        self.screen    = screen
        self.character = character
        self.songs     = character["songs"]
        self.index     = 0
        self.playing   = False
        self._pulses   = {}

        self.font_char  = pygame.font.Font(config.FONT_PATH, 40)
        self.font_song  = pygame.font.Font(config.FONT_PATH, 26)
        self.font_label = pygame.font.Font(config.FONT_PATH, 18)
        self.font_btn   = pygame.font.Font(config.FONT_PATH, 28)
        self.font_char.bold = True
        self.font_song.bold = True
        self.font_btn.bold  = True

        self._build_layout()
        self._load_and_play()

    def _build_layout(self):
        w, h = config.SCREEN_WIDTH, config.SCREEN_HEIGHT
        self.back_rect = pygame.Rect(20, 15, 100, 42)

        btn_w, btn_h = 170, 76
        gap   = 24
        total = 3 * btn_w + 2 * gap
        x0    = (w - total) // 2
        y     = h - btn_h - 28

        self.prev_rect = pygame.Rect(x0,                    y, btn_w, btn_h)
        self.play_rect = pygame.Rect(x0 + btn_w + gap,      y, btn_w, btn_h)
        self.next_rect = pygame.Rect(x0 + 2 * (btn_w + gap), y, btn_w, btn_h)

    def _load_and_play(self):
        path = self.songs[self.index]["file"]
        if os.path.exists(path):
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(-1)
            self.playing = True
        else:
            print(f"Music file not found: {path}", flush=True)
            self.playing = False

    def stop(self):
        pygame.mixer.music.stop()
        self.playing = False

    def handle_tap(self, pos):
        if self.back_rect.collidepoint(pos):
            self._pulses["back"] = time.time()
            return "back"
        if self.play_rect.collidepoint(pos):
            self._pulses["play"] = time.time()
            if self.playing:
                pygame.mixer.music.pause()
                self.playing = False
            else:
                pygame.mixer.music.unpause()
                self.playing = True
        elif self.prev_rect.collidepoint(pos):
            self._pulses["prev"] = time.time()
            self.index = (self.index - 1) % len(self.songs)
            self._load_and_play()
        elif self.next_rect.collidepoint(pos):
            self._pulses["next"] = time.time()
            self.index = (self.index + 1) % len(self.songs)
            self._load_and_play()
        return None

    def _pulsed_rect(self, rect, btn_id):
        t = self._pulses.get(btn_id)
        if t is None:
            return rect
        elapsed = time.time() - t
        if elapsed >= 0.18:
            return rect
        scale = 1.0 + 0.15 * (1.0 - elapsed / 0.18)
        nw = int(rect.width * scale)
        nh = int(rect.height * scale)
        return pygame.Rect(rect.centerx - nw // 2, rect.centery - nh // 2, nw, nh)

    def draw(self):
        self.screen.fill(config.BG_COLOR)
        color = self.character["color"]
        song  = self.songs[self.index]
        w     = config.SCREEN_WIDTH

        # Back button
        br = self._pulsed_rect(self.back_rect, "back")
        pygame.draw.rect(self.screen, BACK_COLOR, br, border_radius=8)
        back = self.font_label.render("< Back", True, WHITE)
        self.screen.blit(back, (br.centerx - back.get_width() // 2,
                                br.centery - back.get_height() // 2))

        # Series name
        lines      = self.character["name"].split("\n")
        line_surfs = [self.font_char.render(l, True, color) for l in lines]
        line_h     = line_surfs[0].get_height()
        y = 75
        for surf in line_surfs:
            self.screen.blit(surf, (w // 2 - surf.get_width() // 2, y))
            y += line_h

        # Song title
        title = self.font_song.render(song["title"], True, WHITE)
        self.screen.blit(title, (w // 2 - title.get_width() // 2, 155))

        # Label (era / remix)
        if song.get("label"):
            label = self.font_label.render(song["label"], True, DIM)
            self.screen.blit(label, (w // 2 - label.get_width() // 2, 196))

        # Song counter
        counter = self.font_label.render(
            f"{self.index + 1} / {len(self.songs)}", True, DIM
        )
        self.screen.blit(counter, (w // 2 - counter.get_width() // 2, 228))

        # No-file warning
        if not self.playing and not pygame.mixer.music.get_busy():
            warn = self.font_label.render("(no music file)", True, (200, 80, 80))
            self.screen.blit(warn, (w // 2 - warn.get_width() // 2, 260))

        # Playback buttons (pill shape)
        for rect_base, btn_id, label in (
            (self.prev_rect, "prev", "<<"),
            (self.play_rect, "play", "||" if self.playing else " >"),
            (self.next_rect, "next", ">>"),
        ):
            r = self._pulsed_rect(rect_base, btn_id)
            pygame.draw.rect(self.screen, color, r, border_radius=RADIUS)
            surf = self.font_btn.render(label, True, WHITE)
            self.screen.blit(surf, (r.centerx - surf.get_width() // 2,
                                    r.centery - surf.get_height() // 2))
