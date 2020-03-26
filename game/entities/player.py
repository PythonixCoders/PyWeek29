#!/usr/bin/python
from typing import List

import pygame
from glm import vec3, sign, length
from pygame.surface import SurfaceType
from copy import copy
import random
import weakref

from game.base.entity import Entity
from game.base.being import Being
from game.base.inputs import Inputs, Axis
from game.constants import *
from game.entities.bullet import Bullet
from game.entities.butterfly import Butterfly
from game.base.enemy import Enemy
from game.entities.weapons import Weapon, Pistol, MachineGun, LaserGun


class Player(Being):
    def __init__(self, app, scene, speed=PLAYER_SPEED):
        super().__init__(app, scene, filename=SHIP_IMAGE_PATH)
        self.game_state = self.scene.state

        self.score = 0
        self.hp = 3
        self.crosshair_surf: SurfaceType = app.load_img(CROSSHAIR_IMAGE_PATH, 3)
        self.crosshair_surf_green = app.load_img(CROSSHAIR_GREEN_IMAGE_PATH, 3)

        self.slots += [
            self.app.inputs["hmove"].always_call(self.set_vel_x),
            self.app.inputs["vmove"].always_call(self.set_vel_y),
            self.app.inputs["fire"].always_call(self.fire),
            self.app.inputs["switch-gun"].on_press_repeated(self.next_gun, 0.5),
        ]

        self.position = vec3(0, 0, 0)
        self.speed = vec3(speed)
        self.velocity = vec3(self.speed)

        self.alive = True
        self.solid = True

        self.weapons: List[Weapon] = [
            self.scene.add(gun(app, scene, self))
            for gun in (Pistol, MachineGun, LaserGun)
        ]
        self.current_weapon = 0

    @property
    def weapon(self):
        return self.weapons[self.current_weapon % len(self.weapons)]

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
        # if self.hp < 3:
        # self.smoke_event = scene.when.every(1, self.smoke)
        return damage

    def collision(self, other, dt):
        if isinstance(other, Enemy):
            self.score += other.hp
            other.kill(other.hp, None, self)

    def find_enemy_in_crosshair(self):
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

    def write_weapon_stats(self):
        wpn = self.weapons[self.current_weapon]
        # extra space here to clear terminal
        if wpn.max_ammo < 0:
            ammo = " " * 5  # spacing
        else:
            ammo = f"{wpn.ammo}/{wpn.max_ammo}   "

        self.game_state.terminal.write(wpn.letter + " " + ammo, (0, 21), wpn.color)

        self.game_state.terminal.write("♥ " * self.hp + "  " * (3 - self.hp), 0, "red")

        # self.game_state.terminal.write("WPN " + wpn.letter, (0,20), wpn.color)
        # if wpn.max_ammo == -1:
        #     self.game_state.terminal.write("AMMO " + str(wpn.ammo) + "  ", (0,21), wpn.color)
        # else:
        #     self.game_state.terminal.write("AMMO n/a  ", (0,21), wpn.color)

    def next_gun(self, btn):  # FIXME
        # switch weapon
        self.current_weapon = (self.current_weapon + 1) % len(self.weapons)
        self.play_sound("powerup.wav")

    def set_vel_x(self, axis: Axis):
        self.velocity.x = axis.value * self.speed.x

    def set_vel_y(self, axis: Axis):
        self.velocity.y = axis.value * self.speed.y

    def find_aim(self):
        camera = self.app.state.camera
        butt = self.find_enemy_in_crosshair()
        if butt is None:
            aim = camera.rel_to_world(vec3(0, 0, -camera.screen_dist))
        else:
            aim = butt.position

        return aim

    def fire(self, button):
        if not button.pressed:
            return

        # no ammo? switch to default
        if not self.weapon.ammo:
            self.current_weapon = 0

        if self.weapon.fire(self.find_aim()):
            self.play_sound("shoot.wav")

    def update(self, dt):

        if self.position.y <= -299:
            # too low ?
            self.velocity.y = max(0, self.velocity.y)
            self.position.y = -299
        elif self.position.y >= 300:
            # too high ?
            self.velocity.y = min(0, self.velocity.y)
            self.position.y = 300

        super().update(dt)

    def heading(self):

        camera = self.app.state.camera
        butt = self.find_enemy_in_crosshair()
        if butt is None:
            aim = camera.rel_to_world(vec3(0, 0, -camera.screen_dist))
        else:
            aim = butt.position

        start = camera.rel_to_world(BULLET_OFFSET)
        direction = aim - start
        return start, aim, direction

    # def smoke(self):

    #     start, aim, direction = self.heading()

    #     self.scene.add(
    #         Entity(
    #             self.app,
    #             self.scene,
    #             "bullet.png",
    #             position=self.position - start,
    #             # velocity=(
    #             #     vec3(*(random.random() for r in range(3))) - vec3(0.5)
    #             # ) * 10,
    #             life=1,
    #             particle=True,
    #         )
    #     )

    def render(self, camera):
        self.write_weapon_stats()

        # Ship
        rect = self._surface.get_rect()
        rect.center = (self.app.size[0] / 2, self.app.size[1] * 0.8)
        direction = self.velocity.xy / self.speed.xy
        rect.center += direction * (10, -10)

        self.app.screen.blit(self._surface, rect)

        # Crosshair
        rect = self.crosshair_surf.get_rect()
        rect.center = self.app.size / 2

        if self.find_enemy_in_crosshair():
            self.app.screen.blit(self.crosshair_surf_green, rect)
        else:
            self.app.screen.blit(self.crosshair_surf, rect)
