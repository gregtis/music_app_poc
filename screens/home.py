import os
import pygame
import config

BG = (15, 15, 25)
WHITE = (255, 255, 255)
MARGIN = 30
RADIUS = 12


class HomeScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont("monospace", 34, bold=True)
        self.font_name = pygame.font.SysFont("monospace", 26, bold=True)
        self.font_initial = pygame.font.SysFont("monospace", 80, bold=True)
        self.font_label = pygame.font.SysFont("monospace", 20)
        self.back_rect = pygame.Rect(20, 15, 110, 46)
        self.cards = self._build_cards()

    def _build_cards(self):
        w, h = config.SCREEN_WIDTH, config.SCREEN_HEIGHT
        n = len(config.CHARACTERS)
        card_w = (w - MARGIN * (n + 1)) // n
        card_h = int(h * 0.68)
        card_y = h - card_h - MARGIN

        cards = []
        for i, char in enumerate(config.CHARACTERS):
            x = MARGIN + i * (card_w + MARGIN)
            rect = pygame.Rect(x, card_y, card_w, card_h)
            image = self._load_image(char["image"], card_w - 20, card_h - 60)
            cards.append({"char": char, "rect": rect, "image": image})
        return cards

    def _load_image(self, path, w, h):
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, (w, h))
            except Exception:
                pass
        return None

    def handle_tap(self, pos):
        if self.back_rect.collidepoint(pos):
            return "back"
        for card in self.cards:
            if card["rect"].collidepoint(pos):
                return card["char"]
        return None

    def draw(self):
        self.screen.fill(BG)

        pygame.draw.rect(self.screen, (55, 55, 75), self.back_rect, border_radius=8)
        back = self.font_label.render("< Back", True, WHITE)
        self.screen.blit(back, (self.back_rect.centerx - back.get_width() // 2,
                                self.back_rect.centery - back.get_height() // 2))

        title = self.font_title.render("Select a Game Series", True, WHITE)
        self.screen.blit(title, ((config.SCREEN_WIDTH - title.get_width()) // 2, 18))

        for card in self.cards:
            char = card["char"]
            rect = card["rect"]
            color = char["color"]

            pygame.draw.rect(self.screen, color, rect, border_radius=RADIUS)
            pygame.draw.rect(self.screen, WHITE, rect, width=3, border_radius=RADIUS)

            if card["image"]:
                self.screen.blit(card["image"], (rect.x + 10, rect.y + 10))
            else:
                initial = self.font_initial.render(char["name"][0], True, WHITE)
                self.screen.blit(
                    initial,
                    (rect.centerx - initial.get_width() // 2,
                     rect.centery - initial.get_height() // 2 - 15),
                )

            lines = char["name"].split("\n")
            line_surfs = [self.font_name.render(l, True, WHITE) for l in lines]
            line_h = line_surfs[0].get_height()
            total_h = line_h * len(line_surfs)
            y_start = rect.bottom - total_h - 10
            for surf in line_surfs:
                self.screen.blit(surf, (rect.centerx - surf.get_width() // 2, y_start))
                y_start += line_h
