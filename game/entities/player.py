#!/usr/bin/python
import pygame
from glm import vec3, sign, length
from pygame.surface import SurfaceType
from copy import copy
import weakref

from game.base.entity import Entity
from game.base.being import Being
from game.base.inputs import Inputs, Axis
from game.constants import *
from game.entities.bullet import Bullet
from game.entities.butterfly import Butterfly
from game.base.enemy import Enemy


class Weapon:
    def __init__(self, letter, filename, color, ammo, speed, damage):
        self.letter = letter
        self.filename = filename
        self.color = color
        self.max_ammo = ammo  # max ammo
        self.ammo = 0  # current ammo
        self.speed = float(speed)
        self.damage = damage
        self.img = None


class Player(Being):

    Weapons = [
        Weapon("P", "bullet.png", "yellow", -1, 10, 1),
        Weapon("M", "machinegun.png", "orange", 25, 5, 1),
        Weapon("L", "laser.png", "red", 20, 2, 2),
    ]

    def __init__(self, app, scene, speed=PLAYER_SPEED):
        super().__init__(app, scene, filename=SHIP_IMAGE_PATH)
        self.game_state = self.scene.state

        self.score = 0
        self.hp = 3
        self.crosshair_surf: SurfaceType = app.load_img(CROSSHAIR_IMAGE_PATH, 3)
        self.crosshair_surf_green = app.load_img(CROSSHAIR_GREEN_IMAGE_PATH, 3)

        self.dirkeys = [
            # directions
            pygame.K_LEFT,
            pygame.K_RIGHT,
            pygame.K_UP,
            pygame.K_DOWN,
        ]

        self.actionkeys = [pygame.K_RETURN, pygame.K_SPACE, pygame.K_LSHIFT]
        self.dir = [False] * len(self.dirkeys)
        self.actions = [False] * len(self.actionkeys)
        self.slots += [
            self.app.inputs["hmove"].always_call(self.set_vel_x),
            self.app.inputs["vmove"].always_call(self.set_vel_y),
            self.app.inputs["fire"].on_press_repeated(self.fire, 0.15),
        ]

        self.position = vec3(0, 0, 0)
        self.speed = vec3(speed)
        self.velocity = vec3(self.speed)

        self.alive = True
        self.solid = True
        self.fire_cooldown = False  # True if firing is blocked
        self.firing = False
        self.fire_offset = Z * 400

        self.weapons = list(map(lambda w: copy(w), self.Weapons))
        self.current_weapon = 0
        self.update_stats()

        # load images
        for weapon in self.weapons:
            # weapon.img = app.load_img(weapon.filename) #FIXME more gfx
            weapon.img = app.load_img("bullet.png")

            # temp: give player all ammo
            weapon.ammo = weapon.max_ammo

        wpn = self.weapons[self.current_weapon]
        # self.fire_slot = self.app.inputs["fire"].on_press_repeated(self.fire, 1 / wpn.speed)

    def kill(self, damage, bullet, enemy):
        # TODO: player death
        return False

    def hurt(self, damage, bullet, enemy):
        """
        Take damage from an object `bullet` shot by enemy
        """
        if self.hp <= 0:
            return 0

        damage = min(self.hp, damage)  # calc effective damage (not more than hp)
        self.hp -= damage
        if self.hp <= 0:
            self.kill(damage, bullet, enemy)
        return damage

    def collision(self, other, dt):
        if isinstance(other, Enemy):
            self.score += other.hp
            other.kill(other.hp, None, self)

    def find_butterfly_in_crosshair(self):
        # Assuming state is Game
        camera = self.app.state.camera
        screen_center = camera.screen_size / 2
        crosshair_radius = self.crosshair_surf.get_width() / 2
        for entity in self.scene.slots:
            entity = entity.get()
            if isinstance(entity, Butterfly):
                center = camera.world_to_screen(entity.position)
                if (
                    center
                    and length(center - screen_center)
                    < crosshair_radius + entity.render_size.x / 2
                ):
                    return entity

    def reset_fire_cooldown(self):
        self.fire_cooldown = False

    def update_stats(self):
        wpn = self.weapons[self.current_weapon]
        # extra space here to clear terminal
        if wpn.max_ammo == -1:
            ammo = " " * 5  # spacing
        else:
            ammo = str(wpn.ammo) + "/" + str(wpn.max_ammo) + " " * 3  # spacing

        self.game_state.terminal.write(wpn.letter + " " + ammo, (0, 21), wpn.color)

        self.game_state.terminal.write("♥ " * self.hp + "  " * (3 - self.hp), 0, "red")

        # self.game_state.terminal.write("WPN " + wpn.letter, (0,20), wpn.color)
        # if wpn.max_ammo == -1:
        #     self.game_state.terminal.write("AMMO " + str(wpn.ammo) + "  ", (0,21), wpn.color)
        # else:
        #     self.game_state.terminal.write("AMMO n/a  ", (0,21), wpn.color)

    def action(self, btn):
        if btn == 2:
            # switch weapon
            self.current_weapon = (self.current_weapon + 1) % len(self.weapons)
            wpn = self.weapons[self.current_weapon]
            self.update_stats()
            self.play_sound("powerup.wav")

    def set_vel_x(self, axis: Axis):
        self.velocity.x = axis.value * self.speed.x

    def set_vel_y(self, axis: Axis):
        self.velocity.y = axis.value * self.speed.y

    def fire(self, *args):

        # if self.fire_cooldown:
        #     return False

        wpn = self.weapons[self.current_weapon]

        # no ammo? switch to default
        if not wpn.ammo:
            self.current_weapon = 0
            wpn = self.weapons[0]
            self.update_stats()

        camera = self.app.state.camera
        butt = self.find_butterfly_in_crosshair()
        if butt is None:
            aim = camera.rel_to_world(vec3(0, 0, -camera.screen_dist))
        else:
            aim = butt.position

        start = camera.rel_to_world(BULLET_OFFSET) - Z * self.fire_offset
        direction = aim - start

        # weapon logic
        if wpn.letter == "P":
            self.scene.add(
                Bullet(
                    self.app, self.scene, self, start, direction, wpn.damage, wpn.img
                )
            )
        elif wpn.letter == "M":
            self.scene.add(
                Bullet(
                    self.app,
                    self.scene,
                    self,
                    start - X * 8,
                    direction,
                    wpn.damage,
                    wpn.img,
                )
            )
            self.scene.add(
                Bullet(
                    self.app,
                    self.scene,
                    self,
                    start + X * 8,
                    direction,
                    wpn.damage,
                    wpn.img,
                )
            )
        if wpn.letter == "L":
            for x in range(5):
                self.scene.add(
                    Bullet(
                        self.app,
                        self.scene,
                        self,
                        start - Z * 100 * x,
                        direction,
                        wpn.damage / 5,
                        wpn.img,
                    )
                )

        self.play_sound("shoot.wav")

        # self.fire_cooldown = True

        # Weapon fire delay
        # One-time event slots are removed automatically by Entity.update()
        self.slots += self.scene.when.once(1 / wpn.speed, self.reset_fire_cooldown)
        # self.fire_slot = self.app.inputs["fire"].on_press_repeated(self.fire, 1 / wpn.speed)

        wpn.ammo -= 1
        if not wpn.ammo:
            self.current_weapon = 0

        self.update_stats()

        return True

    def event(self, event):
        if event.type == pygame.KEYUP or event.type == pygame.KEYDOWN:
            for i, key in enumerate(self.dirkeys):
                if key == event.key:
                    self.dir[i] = event.type == pygame.KEYDOWN
            for i, key in enumerate(self.actionkeys):
                if key == event.key:
                    b = event.type == pygame.KEYDOWN
                    self.actions[i] = b
                    if b:
                        self.action(i)

    @property
    def horiz_direction(self):
        """Return which direction the player is moving along the X axis"""
        return -self.dir[0] + self.dir[1]

    def update(self, dt):

        # self.velocity = (
        #     vec3(
        #         self.horiz_direction,
        #         -self.dir[3] + self.dir[2],
        #         -1,  # always going forwards
        #     )
        #     * self.speed
        # )

        if self.position.y <= -299:
            # too low ?
            self.velocity.y = max(0, self.velocity.y)
            self.position.y = -299
        elif self.position.y >= 300:
            # too high ?
            self.velocity.y = min(0, self.velocity.y)
            self.position.y = 300

        # if self.actions[0] or self.actions[1]:
        #     self.fire()

        super().update(dt)

    def render(self, camera):

        # Ship
        rect = self._surface.get_rect()
        rect.center = (self.app.size[0] / 2, self.app.size[1] * 0.8)
        direction = sign(self.velocity.xy)
        rect.center += direction * (10, -10)

        self.app.screen.blit(self._surface, rect)

        # Crosshair
        rect = self.crosshair_surf.get_rect()
        rect.center = self.app.size / 2

        if self.find_butterfly_in_crosshair():
            self.app.screen.blit(self.crosshair_surf_green, rect)
        else:
            self.app.screen.blit(self.crosshair_surf, rect)
