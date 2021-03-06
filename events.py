import pygame

pygame.init()


number_keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
               pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0]


class Keybind:
    def __init__(self, key_list):
        self.list = key_list

    @property
    def is_held(self):
        for key in self.list:
            if keys.is_held(key):
                return True
        return False

    @property
    def is_pressed(self):
        for key in self.list:
            if key in keys.pressed_keys:
                return True
        return False

    @property
    def is_released(self):
        for key in self.list:
            if key in keys.released_keys:
                return True
        return False


class MouseHandler:
    def __init__(self):
        self.clicked = False
        self.released = False
        self.held = False
        self.position = (0, 0)
        self.relative = (0, 0)
        self.button = -1
        self.release_lock = False


class KeyHandler:
    def __init__(self):
        self.held = False
        self.held_keys = []
        self.pressed = False
        self.pressed_keys = []
        self.released = False
        self.released_keys = []

    def is_held(self, key):
        return key in self.held_keys


quit_program = False


def update():
    global quit_program

    mouse.clicked = False
    mouse.released = False
    mouse.position = pygame.mouse.get_pos()
    mouse.relative = pygame.mouse.get_rel()

    keys.released = False
    keys.released_keys = []
    keys.pressed = False
    keys.pressed_keys = []

    for event in pygame.event.get():
        if mouse.release_lock:
            mouse.release_lock = False
            mouse.button = -1

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse.held = True
            mouse.clicked = True
            mouse.button = event.button
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse.held = False
            mouse.released = True
            mouse.release_lock = True

        elif event.type == pygame.KEYDOWN:
            keys.held_keys.append(event.key)
            keys.pressed = True
            keys.pressed_keys.append(event.key)

        elif event.type == pygame.KEYUP:
            keys.held_keys.remove(event.key)

            keys.released = True
            keys.released_keys.append(event.key)

        elif event.type == pygame.QUIT:
            quit_program = True

    keys.held = len(keys.held_keys) > 0


mouse = MouseHandler()
keys = KeyHandler()
