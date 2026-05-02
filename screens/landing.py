import pygame
import config

BG = (15, 15, 25)
WHITE = (255, 255, 255)
RADIUS = 14


class LandingScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont("monospace", 38, bold=True)
        self.font_btn = pygame.font.SysFont("monospace", 26, bold=True)
        self._build_layout()

    def _build_layout(self):
        w, h = config.SCREEN_WIDTH, config.SCREEN_HEIGHT
        btn_w, btn_h = 340, 100
        gap = 40
        total_h = 2 * btn_h + gap
        y0 = (h - total_h) // 2 + 30

        cx = (w - btn_w) // 2
        self.browse_rect = pygame.Rect(cx, y0, btn_w, btn_h)
        self.quiz_rect = pygame.Rect(cx, y0 + btn_h + gap, btn_w, btn_h)

    def handle_tap(self, pos):
        if self.browse_rect.collidepoint(pos):
            return "browse"
        if self.quiz_rect.collidepoint(pos):
            return "quiz"
        return None

    def draw(self):
        self.screen.fill(BG)
        w = config.SCREEN_WIDTH

        title = self.font_title.render("Nintendo Music Kiosk", True, WHITE)
        self.screen.blit(title, (w // 2 - title.get_width() // 2, 50))

        pygame.draw.rect(self.screen, (50, 100, 200), self.browse_rect, border_radius=RADIUS)
        pygame.draw.rect(self.screen, WHITE, self.browse_rect, width=3, border_radius=RADIUS)
        browse = self.font_btn.render("Browse the Library", True, WHITE)
        self.screen.blit(browse, (self.browse_rect.centerx - browse.get_width() // 2,
                                  self.browse_rect.centery - browse.get_height() // 2))

        pygame.draw.rect(self.screen, (200, 100, 20), self.quiz_rect, border_radius=RADIUS)
        pygame.draw.rect(self.screen, WHITE, self.quiz_rect, width=3, border_radius=RADIUS)
        quiz = self.font_btn.render("Quiz", True, WHITE)
        self.screen.blit(quiz, (self.quiz_rect.centerx - quiz.get_width() // 2,
                                self.quiz_rect.centery - quiz.get_height() // 2))
