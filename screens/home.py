import os
import time
import pygame
import config

WHITE      = (255, 255, 255)
BACK_COLOR = (55, 55, 60)
COLS       = 4
MARGIN     = 20
GAP        = 15
HEADER     = 72
RADIUS     = 14


class HomeScreen:
    def __init__(self, screen, series):
        self.screen  = screen
        self.series  = series
        self.font_title   = pygame.font.Font(config.FONT_PATH, 28)
        self.font_name    = pygame.font.Font(config.FONT_PATH, 16)
        self.font_initial = pygame.font.Font(config.FONT_PATH, 52)
        self.font_label   = pygame.font.Font(config.FONT_PATH, 18)
        self.font_title.bold = True
        self.font_name.bold  = True
        self.back_rect = pygame.Rect(20, 15, 100, 42)
        self._pulses   = {}
        self.cards     = self._build_cards()

    def _card_dims(self):
        n      = len(self.series)
        n_rows = (n + COLS - 1) // COLS
        card_w = (config.SCREEN_WIDTH - MARGIN * 2 - GAP * (COLS - 1)) // COLS
        avail  = config.SCREEN_HEIGHT - HEADER - MARGIN * 2 - GAP * (n_rows - 1)
        card_h = avail // n_rows
        return card_w, card_h

    def _build_cards(self):
        card_w, card_h = self._card_dims()
        n      = len(self.series)
        n_rows = (n + COLS - 1) // COLS
        cards  = []
        for i, char in enumerate(self.series):
            row = i // COLS
            col = i % COLS
            in_last_row       = (row == n_rows - 1)
            last_row_count    = n - (n_rows - 1) * COLS
            if in_last_row and last_row_count < COLS:
                row_w = last_row_count * card_w + (last_row_count - 1) * GAP
                x = (config.SCREEN_WIDTH - row_w) // 2 + col * (card_w + GAP)
            else:
                x = MARGIN + col * (card_w + GAP)
            y    = HEADER + MARGIN + row * (card_h + GAP)
            rect = pygame.Rect(x, y, card_w, card_h)
            image = self._load_image(char["image"], card_w - 20, card_h - 52)
            cards.append({"char": char, "rect": rect, "image": image})
        return cards

    def _load_image(self, path, w, h):
        if path and os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, (w, h))
            except Exception:
                pass
        return None

    def handle_tap(self, pos):
        if self.back_rect.collidepoint(pos):
            self._pulses["back"] = time.time()
            return "back"
        for i, card in enumerate(self.cards):
            if card["rect"].collidepoint(pos):
                self._pulses[f"card_{i}"] = time.time()
                return card["char"]
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

        br = self._pulsed_rect(self.back_rect, "back")
        pygame.draw.rect(self.screen, BACK_COLOR, br, border_radius=8)
        back = self.font_label.render("< Back", True, WHITE)
        self.screen.blit(back, (br.centerx - back.get_width() // 2,
                                br.centery - back.get_height() // 2))

        title = self.font_title.render("Select a Series", True, WHITE)
        self.screen.blit(title, ((config.SCREEN_WIDTH - title.get_width()) // 2, 18))

        for i, card in enumerate(self.cards):
            char  = card["char"]
            rect  = self._pulsed_rect(card["rect"], f"card_{i}")
            color = char["color"]

            pygame.draw.rect(self.screen, color, rect, border_radius=RADIUS)

            if card["image"]:
                img = card["image"]
                ix  = rect.x + (rect.width - img.get_width()) // 2
                self.screen.blit(img, (ix, rect.y + 10))
            else:
                initial = self.font_initial.render(char["name"][0], True, WHITE)
                self.screen.blit(
                    initial,
                    (rect.centerx - initial.get_width() // 2,
                     rect.centery - initial.get_height() // 2 - 12),
                )

            lines     = char["name"].split("\n")
            line_surfs = [self.font_name.render(l, True, WHITE) for l in lines]
            line_h    = line_surfs[0].get_height()
            total_h   = line_h * len(line_surfs)
            y_start   = rect.bottom - total_h - 10
            for surf in line_surfs:
                self.screen.blit(surf, (rect.centerx - surf.get_width() // 2, y_start))
                y_start += line_h
