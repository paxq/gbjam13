import sys, os
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)
img_dir = resource_path("img")
sound_dir = resource_path("sfx")
font_dir = resource_path("font")

SCREEN_WIDTH = 160
SCREEN_HEIGHT = 144
SCALE_MODIFIER = 4
TILE_SIZE = 16
FPS = 60
ANIMATION_COOLDOWN = 12