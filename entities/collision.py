import pygame
import constants as const

import sound
import grid
import punchers


class KinematicsPoint:
    def __init__(self, x=0, y=0):
        self._x = x
        self._y = y

        self.x_vel = 0.0
        self.y_vel = 0.0
        self.x_acc = 0.0
        self.y_acc = 0.0

        self._x_dir = 0
        self._y_dir = 0

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        x = int(value)
        self._x = x

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        y = int(value)
        self._y = y

    def update(self):
        self._update_kinematics()
        self._update_direction()

    def _update_kinematics(self):
        self.x_vel += self.x_acc
        self.y_vel += self.y_acc

        self.x += self.x_vel
        self.y += self.y_vel

    def _update_direction(self):
        if self.x_vel < 0:
            self._x_dir = const.LEFT
        elif self.x_vel > 0:
            self._x_dir = const.RIGHT
        else:
            self._x_dir = 0

        if self.y_vel < 0:
            self._y_dir = const.UP
        elif self.y_vel > 0:
            self._y_dir = const.DOWN
        else:
            self._y_dir = 0

    def _next_x(self):
        """returns the x position of the body on the next frame"""
        return self._x + self.x_vel + self.x_acc

    def _next_y(self):
        """returns the y position of the body on the next frame"""
        return self._y + self.y_vel + self.y_acc

    def _stop_x(self):
        self._x_dir = 0
        self.x_vel = 0
        self.x_acc = 0

    def _stop_y(self):
        self._y_dir = 0
        self.y_vel = 0
        self.y_acc = 0


class Collision(KinematicsPoint):
    CHECK_STEPS = 4

    def __init__(self, level, width, height, x=0, y=0, extend_x=0, extend_y=0):
        super().__init__(x, y)
        self._width = width
        self._height = height

        self._extend_x = extend_x
        self._extend_y = extend_y
        self._gridbox = pygame.Rect(x, y, width, height)
        self._hitbox = pygame.Rect(x - extend_x, y - extend_y,
                                   width + extend_x * 2, height + extend_y * 2)

        self.collide_void = True
        self.collide_deathlock = True

        self.level = level  # reference to the level layout

        self.ignore_collision = False

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        x = int(value)
        self._x = x
        self._gridbox.x = x
        self._hitbox.x = x - self._extend_x

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        y = int(value)
        self._y = y
        self._gridbox.y = y
        self._hitbox.y = y - self._extend_y

    @property
    def center_x(self):
        return self._x + self._width // 2

    @center_x.setter
    def center_x(self, value):
        x = int(value) - self._width // 2
        self.x = x

    @property
    def center_y(self):
        return self._y + self._height // 2

    @center_y.setter
    def center_y(self, value):
        y = int(value) - self._height // 2
        self.y = y

    @property
    def center_pos(self):
        return self.center_x, self.center_y

    def update(self):
        if not self.ignore_collision:
            self._collide_stage()
        super().update()

    def _snap_x(self, col, side=const.LEFT):
        """snaps you to either the left side or right side of a tile"""
        if side == const.LEFT:
            self.x = grid.x_of(col, const.LEFT) - self._width
            self._stop_x()

        elif side == const.RIGHT:
            self.x = grid.x_of(col, const.RIGHT)
            self._stop_x()

    def _snap_y(self, row, side=const.TOP):
        """snaps you to either the top or bottom of a tile"""
        if side == const.TOP:
            self.y = grid.y_of(row, const.TOP) - self._height
            self._stop_y()

        elif side == const.BOTTOM:
            self.y = grid.y_of(row, const.BOTTOM)
            self._stop_y()

    def _collide_stage(self):
        """checks collision with stage and updates movement accordingly

        if screen_edge is True, then the edge of the screen acts as a wall."""

        for step in range(1, self.CHECK_STEPS + 1):
            diff_x = self._next_x() - self._x
            diff_y = self._next_y() - self._y

            if diff_x < 0:
                dir_x = const.LEFT
            elif diff_x > 0:
                dir_x = const.RIGHT
            else:
                dir_x = 0

            if diff_y < 0:
                dir_y = const.UP
            elif diff_y > 0:
                dir_y = const.DOWN
            else:
                dir_y = 0

            left_x = self._x
            right_x = left_x + self._width - 1
            top_y = int(self._y + (diff_y * (step / self.CHECK_STEPS)))
            bottom_y = top_y + self._height - 1

            if dir_y == const.UP:
                if self.level.collide_horiz(left_x, right_x, top_y, self.collide_deathlock):
                    self._snap_y(grid.row_at(top_y), const.BOTTOM)
            elif dir_y == const.DOWN:
                if self.level.collide_horiz(left_x, right_x, bottom_y, self.collide_deathlock):
                    self._snap_y(grid.row_at(bottom_y), const.TOP)

            left_x = int(self._x + (diff_x * (step / 4)))
            right_x = left_x + self._width - 1
            top_y = self._y
            bottom_y = top_y + self._height - 1

            if dir_x == const.LEFT:
                if self.level.collide_vert(left_x, top_y, bottom_y, self.collide_deathlock):
                    self._snap_x(grid.col_at(left_x), const.RIGHT)

            elif dir_x == const.RIGHT:
                if self.level.collide_vert(right_x, top_y, bottom_y, self.collide_deathlock):
                    self._snap_x(grid.col_at(right_x), const.LEFT)

    def _against_wall(self):
        top_y = self._y
        bottom_y = top_y + self._height - 1

        if self._x_dir == const.LEFT:
            x = self._x - 1
            return self.level.collide_vert(x, top_y, bottom_y, self.collide_deathlock)

        elif self._x_dir == const.RIGHT:
            x = self._x + self._width
            return self.level.collide_vert(x, top_y, bottom_y, self.collide_deathlock)

    def _against_floor(self):
        x1 = self._x + 1
        x2 = x1 + self._width - 2
        y = self._y + self._height
        return self.level.collide_horiz(x1, x2, y, self.collide_deathlock)

    def draw_gridbox(self, surface, cam, color=const.RED):
        pygame.draw.rect(surface, color, cam.move_rect(self._gridbox))

    def draw_hitbox(self, surface, cam, color=const.BLUE):
        pygame.draw.rect(surface, color, cam.move_rect(self._hitbox))

    def draw(self, surface, cam):
        self.draw_gridbox(surface, cam)


class GravityCollision(Collision):
    def __init__(self, level, width, height, terminal_velocity,
                 x=0, y=0, extend_x=0, extend_y=0):
        super().__init__(level, width, height, x, y, extend_x, extend_y)
        self._terminal_velocity = terminal_velocity
        self.ignore_gravity = False

    @property
    def grounded(self):
        if self.y_vel < 0:
            return False
        return self._against_floor()

    def update(self):
        if not self.ignore_gravity and not self.grounded:
            self.y_acc = const.GRAVITY
        super().update()
        self.y_vel = min(self.y_vel, self._terminal_velocity)


class PunchableGravityCollision(GravityCollision):
    HIT_SOUNDS = sound.load_numbers("hit%i", 3)
    INVULN_LENGTH = 5

    PUNCHER_X_VEL = 5
    PUNCHER_UP_VEL = 12
    PUNCHER_DOWN_VEL = 7

    def __init__(self, level, width, height, terminal_velocity,
                 x=0, y=0, extend_x=0, extend_y=0):
        super().__init__(level, width, height, terminal_velocity,
                         x, y, extend_x, extend_y)

        self.invuln_frames = 0
        self.puncher_x_vel = 0
        self.puncher_deceleration = 0.5

    def update(self):
        super().update()
        if not self.ignore_collision:
            self.collide_punchers()

    def _stop_x(self):
        super()._stop_x()
        self.puncher_x_vel = 0

    def _next_x(self):
        return super()._next_x() + self.puncher_x_vel

    def _update_kinematics(self):
        super()._update_kinematics()
        self._update_puncher_vel()
        self.x += self.puncher_x_vel

    def _update_puncher_vel(self):
        if self.grounded:
            if self.puncher_x_vel < 0:
                self.puncher_x_vel += self.puncher_deceleration
                if self.puncher_x_vel > 0:
                    self.puncher_x_vel = 0

            elif self.puncher_x_vel > 0:
                self.puncher_x_vel -= self.puncher_deceleration
                if self.puncher_x_vel < 0:
                    self.puncher_x_vel = 0

    def _get_hit(self):
        self.invuln_frames = self.INVULN_LENGTH
        self.HIT_SOUNDS.play_random()

    def collide_punchers(self):
        if not self.invuln_frames:
            center_col = grid.col_at(self.center_x)
            center_row = grid.row_at(self.center_y)

            if self.level.has_tile(grid.PunchZone, center_col, center_row):
                self._activate_punch_zone(center_col, center_row)
                return

            # Only do special upwards puncher checks if player isn't moving up
            if self.y_vel >= 0:

                # Upwards punchers can also punch based on left and right of the
                # entity rather than just the player's center.  Otherwise, you'll
                # sometimes see the player stand for a moment on the very edge of an
                # upwards puncher
                left_col = grid.col_at(self.x + 2)
                if self.level.has_tile(grid.PunchZone, left_col, center_row):
                    tile = self.level.get_tile(grid.PunchZone, left_col, center_row)
                    if tile.direction == const.UP:
                        self._activate_punch_zone(left_col, center_row)
                        return

                right_col = grid.col_at(self.x + self._width - 3)
                if self.level.has_tile(grid.PunchZone, right_col, center_row):
                    tile = self.level.get_tile(grid.PunchZone, right_col, center_row)
                    if tile.direction == const.UP:
                        self._activate_punch_zone(right_col, center_row)

        elif self.invuln_frames:
            self.invuln_frames -= 1

    def _activate_punch_zone(self, col, row):
        tile = self.level.get_tile(grid.PunchZone, col, row)
        if tile.direction == const.LEFT:
            self._get_hit()
            punchers.add(col, row, const.LEFT)
            self.puncher_x_vel = -self.PUNCHER_X_VEL

            if self.x_vel > 0:
                self.x_vel = 0

        elif tile.direction == const.UP:
            self._get_hit()
            punchers.add(col, row, const.UP)
            self.y_vel = -self.PUNCHER_UP_VEL

        elif tile.direction == const.RIGHT:
            self._get_hit()
            punchers.add(col, row, const.RIGHT)
            self.puncher_x_vel = self.PUNCHER_X_VEL

            if self.x_vel < 0:
                self.x_vel = 0

        elif tile.direction == const.DOWN:
            self._get_hit()
            punchers.add(col, row, const.DOWN)
            self.y_vel = self.PUNCHER_DOWN_VEL
