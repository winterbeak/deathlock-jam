# BASIC VISUALS
SCRN_W = 1280
SCRN_H = 720

FPS = 60
DEBUG_FPS = 5

# COLORS
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 15, 15)
GREEN = (0, 254, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
PLAYER_BODY = (253, 209, 77)

BACKGROUND_GREY = (240, 240, 240)

DARK_GREEN = (0, 100, 0)
DARK_BLUE = (0, 0, 100)
DARK_MAGENTA = (100, 0, 100)

LIGHT_GREEN = (100, 255, 100)
LIGHT_BLUE = (100, 100, 255)
LIGHT_MAGENTA = (255, 100, 255)

TRANSPARENT = (0, 255, 0)

# DIRECTIONS
LEFT = 1
UP = 2
RIGHT = 3
DOWN = 4
TOP = UP
BOTTOM = DOWN


def direction_string(direction):
    if direction == LEFT:
        return "LEFT"
    if direction == RIGHT:
        return "RIGHT"
    if direction == UP:
        return "UP"
    if direction == DOWN:
        return "DOWN"
    return "NONE"


VERT = 1
HORIZ = 2

# MISC / UNSORTED
GRAVITY = 0.55
