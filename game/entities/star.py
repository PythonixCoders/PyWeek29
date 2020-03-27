from random import randint, choice

from glm import vec2, vec3, ivec2
import pygame
import random

from game.base.entity import Entity
from game.constants import CLOUD_IMAGE_PATHS


class Star(Entity):
    def __init__(self, app, scene, pos: vec3, z_vel: float):
        vel = vec3(0, 0, z_vel)

        super().__init__(
            app, scene, choice(CLOUD_IMAGE_PATHS), position=pos, velocity=vel, scale=4
        )

        self._surface = self.app.load(
            "STAR", lambda: pygame.Surface(ivec2(4)).convert()
        )
        self._surface.fill((255, 255, 255))

    def render(self, camera):
        return super().render(camera, None, None, False)

    def __call__(self, script):
        yield
        while True:
            r = random.random()
            self.visible = True
            yield script.sleep(random.random())
            self.visible = False
            yield script.sleep(r / 10)
