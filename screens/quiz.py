import os
import random
import pygame
import config

BG = (15, 15, 25)
WHITE = (255, 255, 255)
GREEN = (50, 200, 80)
RED = (220, 60, 60)
DIM = (130, 130, 130)
RADIUS = 12
NUM_QUESTIONS = 3


class QuizScreen:
    def __init__(self, screen):
        self.screen = screen
        self.score = 0
        self.question_index = 0
        self.state = "asking"

        all_songs = [
            (series, song)
            for series in config.CHARACTERS
            for song in series["songs"]
        ]
        random.shuffle(all_songs)
        self.questions = all_songs[:NUM_QUESTIONS]

        self.font_prompt = pygame.font.SysFont("monospace", 26, bold=True)
        self.font_btn = pygame.font.SysFont("monospace", 24, bold=True)
        self.font_result = pygame.font.SysFont("monospace", 36, bold=True)
        self.font_action = pygame.font.SysFont("monospace", 28, bold=True)
        self.font_score = pygame.font.SysFont("monospace", 22, bold=True)

        self._build_layout()
        self._load_question()

    def _build_layout(self):
        w, h = config.SCREEN_WIDTH, config.SCREEN_HEIGHT

        self.back_rect = pygame.Rect(20, 15, 110, 46)

        btn_w, btn_h = 220, 90
        gap = 20
        total_w = 3 * btn_w + 2 * gap
        x0 = (w - total_w) // 2
        self.option_rects = [
            pygame.Rect(x0 + i * (btn_w + gap), h - btn_h - 40, btn_w, btn_h)
            for i in range(3)
        ]

        action_w, action_h = 260, 70
        self.action_rect = pygame.Rect((w - action_w) // 2, h - action_h - 40, action_w, action_h)

    def _load_question(self):
        self.answer_series, self.song = self.questions[self.question_index]
        self.options = config.CHARACTERS[:]
        random.shuffle(self.options)
        self._play()

    def _play(self):
        path = self.song["file"]
        if os.path.exists(path):
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(-1)

    def stop(self):
        pygame.mixer.music.stop()

    def _on_correct(self):
        self.score += 1
        self.question_index += 1
        if self.question_index >= NUM_QUESTIONS:
            self.state = "done"
        else:
            self._load_question()

    def handle_tap(self, pos):
        if self.state == "asking":
            if self.back_rect.collidepoint(pos):
                return "home"
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(pos):
                    if self.options[i]["id"] == self.answer_series["id"]:
                        self._on_correct()
                    else:
                        self.state = "wrong"
                    return None
        elif self.state == "wrong":
            if self.action_rect.collidepoint(pos):
                self.state = "asking"
        elif self.state == "done":
            if self.action_rect.collidepoint(pos):
                return "home"
        return None

    def draw(self):
        self.screen.fill(BG)
        w, h = config.SCREEN_WIDTH, config.SCREEN_HEIGHT

        if self.state == "asking":
            pygame.draw.rect(self.screen, (55, 55, 75), self.back_rect, border_radius=8)
            back = self.font_btn.render("< Back", True, WHITE)
            self.screen.blit(back, (self.back_rect.centerx - back.get_width() // 2,
                                    self.back_rect.centery - back.get_height() // 2))

            score_surf = self.font_score.render(f"{self.score} / {NUM_QUESTIONS} correct", True, DIM)
            self.screen.blit(score_surf, (w - score_surf.get_width() - 20, 25))

            prompt = self.font_prompt.render("Which game series is this song from?", True, WHITE)
            self.screen.blit(prompt, (w // 2 - prompt.get_width() // 2, 75))

            hint = self.font_btn.render("Listen to the song and make your pick...", True, DIM)
            self.screen.blit(hint, (w // 2 - hint.get_width() // 2, 120))

            for rect, series in zip(self.option_rects, self.options):
                pygame.draw.rect(self.screen, series["color"], rect, border_radius=RADIUS)
                pygame.draw.rect(self.screen, WHITE, rect, width=3, border_radius=RADIUS)

                lines = series["name"].split("\n")
                line_surfs = [self.font_btn.render(l, True, WHITE) for l in lines]
                line_h = line_surfs[0].get_height()
                total_h = line_h * len(line_surfs)
                y_start = rect.centery - total_h // 2
                for surf in line_surfs:
                    self.screen.blit(surf, (rect.centerx - surf.get_width() // 2, y_start))
                    y_start += line_h

        elif self.state == "wrong":
            result = self.font_result.render("Nope! Try again.", True, RED)
            self.screen.blit(result, (w // 2 - result.get_width() // 2, h // 2 - 60))

            pygame.draw.rect(self.screen, (160, 50, 50), self.action_rect, border_radius=RADIUS)
            pygame.draw.rect(self.screen, WHITE, self.action_rect, width=2, border_radius=RADIUS)
            btn = self.font_action.render("Try Again", True, WHITE)
            self.screen.blit(btn, (self.action_rect.centerx - btn.get_width() // 2,
                                   self.action_rect.centery - btn.get_height() // 2))

        elif self.state == "done":
            result = self.font_result.render("Good job, you answered all 3!", True, GREEN)
            self.screen.blit(result, (w // 2 - result.get_width() // 2, h // 2 - 60))

            pygame.draw.rect(self.screen, (40, 130, 60), self.action_rect, border_radius=RADIUS)
            pygame.draw.rect(self.screen, WHITE, self.action_rect, width=2, border_radius=RADIUS)
            btn = self.font_action.render("Home", True, WHITE)
            self.screen.blit(btn, (self.action_rect.centerx - btn.get_width() // 2,
                                   self.action_rect.centery - btn.get_height() // 2))
