#!/usr/bin/python
import pygame
from glm import vec3, sign, length
from pygame.surface import SurfaceType

from game.base.entity import Entity
from game.base.inputs import Inputs, Axis
from game.constants import *
from game.entities.bullet import Bullet
from game.entities.butterfly import Butterfly


class Player(Entity):
    def __init__(self, app, scene, speed=PLAYER_SPEED):
        super().__init__(app, scene, filename=SHIP_IMAGE_PATH)

        self.score = 0
        self.crosshair_surf: SurfaceType = app.load_img(CROSSHAIR_IMAGE_PATH, 3)
        self.crosshair_surf_green = app.load_img(CROSSHAIR_GREEN_IMAGE_PATH, 3)

        self.app.inputs["fire"].on_press_repeated(self.fire, 0.15)
        self.app.inputs["hmove"] += self.set_vel_x
        self.app.inputs["vmove"] += self.set_vel_y

        self.position = vec3(0, 0, 0)
        self.speed = vec3(speed)
        self.velocity = vec3(self.speed)

        self.solid = True

    def collision(self, other, dt):
        if isinstance(other, Butterfly):
            self.score += 1
            other.explode()

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

    def set_vel_x(self, axis: Axis):
        self.velocity.x = axis.value * self.speed.x

    def set_vel_y(self, axis: Axis):
        self.velocity.y = axis.value * self.speed.y

    def fire(self, *args):
        # Assuming state is Game
        camera = self.app.state.camera
        butt = self.find_butterfly_in_crosshair()
        if butt is None:
            aim = camera.rel_to_world(vec3(0, 0, -camera.screen_dist))
        else:
            aim = butt.position

        start = camera.rel_to_world(BULLET_OFFSET)
        direction = aim - start

        self.scene.add(Bullet(self.app, self.scene, self, start, direction))

    @property
    def horiz_direction(self):
        """Return which direction the player is moving along the X axis"""
        return -self.dir[0] + self.dir[1]

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
