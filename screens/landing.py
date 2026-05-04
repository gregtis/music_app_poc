import time
import pygame
import config

WHITE  = (255, 255, 255)
BLUE   = (50, 120, 220)
ORANGE = (210, 100, 20)
RADIUS = 44


class LandingScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(config.FONT_PATH, 40)
        self.font_btn   = pygame.font.Font(config.FONT_PATH, 26)
        self.font_title.bold = True
        self.font_btn.bold   = True
        self._pulses = {}
        self._build_layout()

    def _build_layout(self):
        w, h = config.SCREEN_WIDTH, config.SCREEN_HEIGHT
        btn_w, btn_h = 360, 88
        gap = 28
        total_h = 2 * btn_h + gap
        y0 = h // 2 - total_h // 2 + 24
        cx = (w - btn_w) // 2
        self.browse_rect = pygame.Rect(cx, y0, btn_w, btn_h)
        self.quiz_rect   = pygame.Rect(cx, y0 + btn_h + gap, btn_w, btn_h)

    def handle_tap(self, pos):
        if self.browse_rect.collidepoint(pos):
            self._pulses["browse"] = time.time()
            return "browse"
        if self.quiz_rect.collidepoint(pos):
            self._pulses["quiz"] = time.time()
            return "quiz"
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
        w = config.SCREEN_WIDTH

        title = self.font_title.render("Nintendo Music Kiosk", True, WHITE)
        self.screen.blit(title, (w // 2 - title.get_width() // 2, 52))

        br = self._pulsed_rect(self.browse_rect, "browse")
        pygame.draw.rect(self.screen, BLUE, br, border_radius=RADIUS)
        browse = self.font_btn.render("Browse the Library", True, WHITE)
        self.screen.blit(browse, (br.centerx - browse.get_width() // 2,
                                  br.centery - browse.get_height() // 2))

        qr = self._pulsed_rect(self.quiz_rect, "quiz")
        pygame.draw.rect(self.screen, ORANGE, qr, border_radius=RADIUS)
        quiz = self.font_btn.render("Quiz", True, WHITE)
        self.screen.blit(quiz, (qr.centerx - quiz.get_width() // 2,
                                qr.centery - quiz.get_height() // 2))
