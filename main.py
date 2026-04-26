import os
import sys

import pygame

import config
import touch
from screens.home import HomeScreen
from screens.character import CharacterScreen


def main():
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    on_pi = os.environ.get("SDL_VIDEODRIVER") in ("fbcon", "kmsdrm")
    if on_pi:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        config.SCREEN_WIDTH, config.SCREEN_HEIGHT = screen.get_size()
    else:
        screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    print(f"Display init OK: {config.SCREEN_WIDTH}x{config.SCREEN_HEIGHT}", flush=True)
    pygame.display.set_caption("Music App")
    pygame.mouse.set_visible(not on_pi)

    touch.init(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)

    clock = pygame.time.Clock()
    home = HomeScreen(screen)
    current = "home"
    char_screen = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                _quit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                _quit()
            elif event.type == pygame.MOUSEBUTTONUP:
                _handle_tap(event.pos, current, home, char_screen)
                current, char_screen = _route(event.pos, current, home, char_screen, screen)

        tap = touch.get_tap()
        if tap:
            current, char_screen = _route(tap, current, home, char_screen, screen)

        if current == "home":
            home.draw()
        else:
            char_screen.draw()

        pygame.display.flip()
        clock.tick(30)


def _handle_tap(pos, current, home, char_screen):
    pass


def _route(pos, current, home, char_screen, screen):
    if current == "home":
        char = home.handle_tap(pos)
        if char:
            return "character", CharacterScreen(screen, char)
    else:
        result = char_screen.handle_tap(pos)
        if result == "back":
            char_screen.stop()
            return "home", None
    return current, char_screen


def _quit():
    pygame.mixer.music.stop()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
