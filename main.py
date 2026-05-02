import fcntl
import os
import sys

import pygame

import config
import touch
from screens.home import HomeScreen
from screens.character import CharacterScreen
from screens.landing import LandingScreen
from screens.quiz import QuizScreen

KDSETMODE = 0x4B3A
KD_GRAPHICS = 0x01
KD_TEXT = 0x00
FB0_PATH = '/dev/fb0'
TTY_PATH = '/dev/tty1'


def _tty_graphics(tty_path):
    """Switch VT to graphics mode so the kernel stops drawing cursor/text over fb0."""
    try:
        tty = open(tty_path, 'r+b', buffering=0)
        fcntl.ioctl(tty, KDSETMODE, KD_GRAPHICS)
        return tty
    except Exception as e:
        print(f"tty graphics mode unavailable: {e}", flush=True)
        return None


def _tty_restore(tty):
    if tty:
        try:
            fcntl.ioctl(tty, KDSETMODE, KD_TEXT)
            tty.close()
        except Exception:
            pass


def _fb_geometry():
    with open('/sys/class/graphics/fb0/virtual_size') as f:
        w, h = map(int, f.read().strip().split(','))
    with open('/sys/class/graphics/fb0/bits_per_pixel') as f:
        bpp = int(f.read().strip())
    return w, h, bpp


def main():
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    on_pi = os.environ.get('SDL_VIDEODRIVER') == 'offscreen'

    tty = None
    fb = None

    try:
        if on_pi:
            tty = _tty_graphics(TTY_PATH)
            fb_w, fb_h, fb_bpp = _fb_geometry()
            print(f"Framebuffer: {fb_w}x{fb_h} @ {fb_bpp}bpp", flush=True)
            display = pygame.display.set_mode((fb_w, fb_h))
            screen = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            surf_fb = pygame.Surface((fb_w, fb_h), 0, fb_bpp)
            fb = open(FB0_PATH, 'rb+')
        else:
            display = screen = pygame.display.set_mode(
                (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
            )
            surf_fb = None
            fb_w = fb_h = None

        print(f"Display init OK: {config.SCREEN_WIDTH}x{config.SCREEN_HEIGHT}", flush=True)
        pygame.display.set_caption("Music App")
        pygame.mouse.set_visible(not on_pi)

        touch.init(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)

        clock = pygame.time.Clock()
        landing = LandingScreen(screen)
        home = HomeScreen(screen)
        current = "landing"
        char_screen = None
        quiz_screen = None

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return
                elif event.type == pygame.MOUSEBUTTONUP:
                    current, char_screen, quiz_screen = _route(
                        event.pos, current, landing, home, char_screen, quiz_screen, screen)

            tap = touch.get_tap()
            if tap:
                current, char_screen, quiz_screen = _route(
                    tap, current, landing, home, char_screen, quiz_screen, screen)

            if current == "landing":
                landing.draw()
            elif current == "home":
                home.draw()
            elif current == "character":
                char_screen.draw()
            elif current == "quiz":
                quiz_screen.draw()

            if on_pi:
                scaled = pygame.transform.scale(screen, (fb_w, fb_h))
                surf_fb.blit(scaled, (0, 0))
                fb.seek(0)
                fb.write(surf_fb.get_buffer().raw)
            else:
                pygame.display.flip()

            clock.tick(30)

    finally:
        if fb:
            fb.close()
        _tty_restore(tty)
        pygame.mixer.music.stop()
        pygame.quit()


def _route(pos, current, landing, home, char_screen, quiz_screen, screen):
    if current == "landing":
        result = landing.handle_tap(pos)
        if result == "browse":
            return "home", None, None
        if result == "quiz":
            return "quiz", None, QuizScreen(screen)
    elif current == "home":
        char = home.handle_tap(pos)
        if char:
            return "character", CharacterScreen(screen, char), None
    elif current == "character":
        result = char_screen.handle_tap(pos)
        if result == "back":
            char_screen.stop()
            return "home", None, None
    elif current == "quiz":
        result = quiz_screen.handle_tap(pos)
        if result == "home":
            quiz_screen.stop()
            return "landing", None, None
    return current, char_screen, quiz_screen


if __name__ == "__main__":
    main()
    sys.exit()
