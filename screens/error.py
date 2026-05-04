import pygame
import config

WHITE = (255, 255, 255)
RED   = (220, 60, 60)
DIM   = (140, 140, 145)


class ErrorScreen:
    def __init__(self, screen, message):
        self.screen     = screen
        self.font_title = pygame.font.Font(config.FONT_PATH, 34)
        self.font_body  = pygame.font.Font(config.FONT_PATH, 19)
        self.font_hint  = pygame.font.Font(config.FONT_PATH, 16)
        self.font_title.bold = True
        self._lines = self._wrap(message)

    def _wrap(self, text):
        max_w = config.SCREEN_WIDTH - 60
        lines = []
        for raw_line in text.split("\n"):
            words   = raw_line.split(" ")
            current = ""
            for word in words:
                test = (current + " " + word).strip()
                if self.font_body.size(test)[0] > max_w and current:
                    lines.append(current)
                    current = word
                else:
                    current = test
            lines.append(current)
        return lines

    def draw(self):
        self.screen.fill(config.BG_COLOR)
        w, h = config.SCREEN_WIDTH, config.SCREEN_HEIGHT

        title = self.font_title.render("Library Error", True, RED)
        self.screen.blit(title, (w // 2 - title.get_width() // 2, 40))

        y = 108
        for line in self._lines:
            surf = self.font_body.render(line, True, WHITE)
            self.screen.blit(surf, (30, y))
            y += surf.get_height() + 6

        hint = self.font_hint.render("Run: python validate_library.py <library_dir>", True, DIM)
        self.screen.blit(hint, (w // 2 - hint.get_width() // 2, h - 68))

        hint2 = self.font_hint.render("Check: sudo docker compose logs -f", True, DIM)
        self.screen.blit(hint2, (w // 2 - hint2.get_width() // 2, h - 44))
