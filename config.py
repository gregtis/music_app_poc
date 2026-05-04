import os

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480

LIBRARY_DIR = os.environ.get("LIBRARY_DIR", "./library")

BG_COLOR  = (38, 38, 40)
FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "fonts", "Nunito-Bold.ttf")
