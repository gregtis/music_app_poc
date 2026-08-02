import os
import random
import time
import pygame
import config

WHITE      = (255, 255, 255)
GREEN      = (50, 210, 90)
RED        = (220, 60, 60)
DIM        = (150, 150, 155)
BACK_COLOR = (55, 55, 60)
RADIUS     = 14
NUM_QUESTIONS = 3


class QuizScreen:
    def __init__(self, screen, series):
        self.screen         = screen
        self.series         = series
        self.score          = 0
        self.question_index = 0
        self.state          = "asking"
        self.correct_time   = None
        self._pulses        = {}

        all_songs = [(s, song) for s in series for song in s["songs"]]
        random.shuffle(all_songs)
        self.questions = all_songs[:NUM_QUESTIONS]

        self.font_prompt = pygame.font.Font(config.FONT_PATH, 24)
        self.font_btn    = pygame.font.Font(config.FONT_PATH, 22)
        self.font_result = pygame.font.Font(config.FONT_PATH, 48)
        self.font_action = pygame.font.Font(config.FONT_PATH, 26)
        self.font_score  = pygame.font.Font(config.FONT_PATH, 20)
        self.font_prompt.bold = True
        self.font_btn.bold    = True
        self.font_result.bold = True
        self.font_action.bold = True

        self._build_layout()
        self._load_question()

    def _build_layout(self):
        w, h = config.SCREEN_WIDTH, config.SCREEN_HEIGHT
        self.back_rect = pygame.Rect(20, 15, 100, 42)

        btn_w, btn_h = 220, 88
        gap     = 18
        total_w = 3 * btn_w + 2 * gap
        x0      = (w - total_w) // 2
        self.option_rects = [
            pygame.Rect(x0 + i * (btn_w + gap), h - btn_h - 36, btn_w, btn_h)
            for i in range(3)
        ]

        action_w, action_h = 260, 68
        self.action_rect = pygame.Rect((w - action_w) // 2, h - action_h - 36, action_w, action_h)

    def _load_question(self):
        self.answer_series, self.song = self.questions[self.question_index]
        wrong = [s for s in self.series if s["id"] != self.answer_series["id"]]
        self.options = random.sample(wrong, min(2, len(wrong))) + [self.answer_series]
        random.shuffle(self.options)
        self._play()

    def _play(self):
        path = self.song["file"]
        if os.path.exists(path):
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(-1)

    def stop(self):
        pygame.mixer.music.stop()

    def update(self):
        if self.state == "correct" and self.correct_time is not None:
            if time.time() - self.correct_time >= 1.0:
                self.correct_time = None
                self.question_index += 1
                if self.question_index >= NUM_QUESTIONS:
                    self.state = "done"
                else:
                    self._load_question()
                    self.state = "asking"

    def _on_correct(self):
        self.score += 1
        self.correct_time = time.time()
        self.state = "correct"

    def handle_tap(self, pos):
        if self.state == "asking":
            if self.back_rect.collidepoint(pos):
                return "home"
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(pos):
                    self._pulses[f"opt_{i}"] = time.time()
                    if self.options[i]["id"] == self.answer_series["id"]:
                        self._on_correct()
                    else:
                        self.state = "wrong"
                    return None
        elif self.state == "wrong":
            if self.action_rect.collidepoint(pos):
                self._pulses["action"] = time.time()
                self.state = "asking"
        elif self.state == "done":
            if self.action_rect.collidepoint(pos):
                self._pulses["action"] = time.time()
                return "home"
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
        w, h = config.SCREEN_WIDTH, config.SCREEN_HEIGHT

        if self.state == "asking":
            pygame.draw.rect(self.screen, BACK_COLOR, self.back_rect, border_radius=8)
            back = self.font_btn.render("< Back", True, WHITE)
            self.screen.blit(back, (self.back_rect.centerx - back.get_width() // 2,
                                    self.back_rect.centery - back.get_height() // 2))

            score_surf = self.font_score.render(f"{self.score} / {NUM_QUESTIONS} correct", True, DIM)
            self.screen.blit(score_surf, (w - score_surf.get_width() - 20, 22))

            prompt = self.font_prompt.render("Which game series is this song from?", True, WHITE)
            self.screen.blit(prompt, (w // 2 - prompt.get_width() // 2, 72))

            hint = self.font_score.render("Listen and make your pick...", True, DIM)
            self.screen.blit(hint, (w // 2 - hint.get_width() // 2, 112))

            for i, (rect, opt) in enumerate(zip(self.option_rects, self.options)):
                r = self._pulsed_rect(rect, f"opt_{i}")
                pygame.draw.rect(self.screen, opt["color"], r, border_radius=RADIUS)
                lines      = opt["name"].split("\n")
                line_surfs = [self.font_btn.render(l, True, WHITE) for l in lines]
                line_h     = line_surfs[0].get_height()
                total_h    = line_h * len(line_surfs)
                y_start    = r.centery - total_h // 2
                for surf in line_surfs:
                    self.screen.blit(surf, (r.centerx - surf.get_width() // 2, y_start))
                    y_start += line_h

        elif self.state == "correct":
            correct_surf = self.font_result.render("Correct!", True, GREEN)
            self.screen.blit(correct_surf,
                             (w // 2 - correct_surf.get_width() // 2, h // 2 - 55))
            score_surf = self.font_action.render(
                f"{self.score} / {NUM_QUESTIONS} correct", True, WHITE)
            self.screen.blit(score_surf,
                             (w // 2 - score_surf.get_width() // 2, h // 2 + 20))

        elif self.state == "wrong":
            result = self.font_result.render("Nope! Try again.", True, RED)
            self.screen.blit(result, (w // 2 - result.get_width() // 2, h // 2 - 55))

            r = self._pulsed_rect(self.action_rect, "action")
            pygame.draw.rect(self.screen, (160, 50, 50), r, border_radius=RADIUS)
            btn = self.font_action.render("Try Again", True, WHITE)
            self.screen.blit(btn, (r.centerx - btn.get_width() // 2,
                                   r.centery - btn.get_height() // 2))

        elif self.state == "done":
            result = self.font_result.render("Nice work!", True, GREEN)
            self.screen.blit(result, (w // 2 - result.get_width() // 2, h // 2 - 55))
            score_surf = self.font_action.render(
                f"You got {self.score} / {NUM_QUESTIONS} correct", True, WHITE)
            self.screen.blit(score_surf,
                             (w // 2 - score_surf.get_width() // 2, h // 2 + 10))

            r = self._pulsed_rect(self.action_rect, "action")
            pygame.draw.rect(self.screen, (40, 140, 70), r, border_radius=RADIUS)
            btn = self.font_action.render("Home", True, WHITE)
            self.screen.blit(btn, (r.centerx - btn.get_width() // 2,
                                   r.centery - btn.get_height() // 2))
