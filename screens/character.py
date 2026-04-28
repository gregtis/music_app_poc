import os
import pygame
import config

BG = (15, 15, 25)
WHITE = (255, 255, 255)
DIM = (150, 150, 150)
RADIUS = 10


class CharacterScreen:
    def __init__(self, screen, character):
        self.screen = screen
        self.character = character
        self.songs = character["songs"]
        self.index = 0
        self.playing = False

        self.font_char = pygame.font.SysFont("monospace", 42, bold=True)
        self.font_song = pygame.font.SysFont("monospace", 28, bold=True)
        self.font_label = pygame.font.SysFont("monospace", 20)
        self.font_btn = pygame.font.SysFont("monospace", 34, bold=True)

        self._build_layout()
        self._load_and_play()

    def _build_layout(self):
        w, h = config.SCREEN_WIDTH, config.SCREEN_HEIGHT
        self.back_rect = pygame.Rect(20, 15, 110, 46)

        btn_w, btn_h = 160, 80
        gap = 30
        total = 3 * btn_w + 2 * gap
        x0 = (w - total) // 2
        y = h - btn_h - 30

        self.prev_rect = pygame.Rect(x0, y, btn_w, btn_h)
        self.play_rect = pygame.Rect(x0 + btn_w + gap, y, btn_w, btn_h)
        self.next_rect = pygame.Rect(x0 + 2 * (btn_w + gap), y, btn_w, btn_h)

    def _load_and_play(self):
        path = self.songs[self.index]["file"]
        if os.path.exists(path):
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(-1)
            self.playing = True
        else:
            print(f"Music file not found: {path}")
            self.playing = False

    def stop(self):
        pygame.mixer.music.stop()
        self.playing = False

    def handle_tap(self, pos):
        if self.back_rect.collidepoint(pos):
            return "back"
        if self.play_rect.collidepoint(pos):
            if self.playing:
                pygame.mixer.music.pause()
                self.playing = False
            else:
                pygame.mixer.music.unpause()
                self.playing = True
        elif self.prev_rect.collidepoint(pos):
            self.index = (self.index - 1) % len(self.songs)
            self._load_and_play()
        elif self.next_rect.collidepoint(pos):
            self.index = (self.index + 1) % len(self.songs)
            self._load_and_play()
        return None

    def draw(self):
        self.screen.fill(BG)
        color = self.character["color"]
        song = self.songs[self.index]
        w = config.SCREEN_WIDTH

        # Back button
        pygame.draw.rect(self.screen, (55, 55, 75), self.back_rect, border_radius=RADIUS)
        back = self.font_label.render("< Back", True, WHITE)
        self.screen.blit(back, (self.back_rect.centerx - back.get_width() // 2,
                                self.back_rect.centery - back.get_height() // 2))

        # Series name (supports \n in config)
        lines = self.character["name"].split("\n")
        line_surfs = [self.font_char.render(l, True, color) for l in lines]
        line_h = line_surfs[0].get_height()
        y = 78
        for surf in line_surfs:
            self.screen.blit(surf, (w // 2 - surf.get_width() // 2, y))
            y += line_h

        # Song title
        title = self.font_song.render(song["title"], True, WHITE)
        self.screen.blit(title, (w // 2 - title.get_width() // 2, 158))

        # Label (era / remix) — only shown if non-empty
        if song["label"]:
            label = self.font_label.render(song["label"], True, DIM)
            self.screen.blit(label, (w // 2 - label.get_width() // 2, 200))

        # Song counter
        counter = self.font_label.render(
            f"{self.index + 1} / {len(self.songs)}", True, DIM
        )
        self.screen.blit(counter, (w // 2 - counter.get_width() // 2, 235))

        # No-file warning
        if not self.playing and not pygame.mixer.music.get_busy():
            warn = self.font_label.render("(no music file)", True, (180, 80, 80))
            self.screen.blit(warn, (w // 2 - warn.get_width() // 2, 270))

        # Control buttons
        for rect, label in (
            (self.prev_rect, "<<"),
            (self.play_rect, "||" if self.playing else " >"),
            (self.next_rect, ">>"),
        ):
            pygame.draw.rect(self.screen, color, rect, border_radius=RADIUS)
            pygame.draw.rect(self.screen, WHITE, rect, width=2, border_radius=RADIUS)
            surf = self.font_btn.render(label, True, WHITE)
            self.screen.blit(surf, (rect.centerx - surf.get_width() // 2,
                                    rect.centery - surf.get_height() // 2))
