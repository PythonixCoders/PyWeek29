from random import randint, choice

from glm import vec2, vec3, ivec2
import pygame
import random

from game.base.entity import Entity
from game.constants import CLOUD_IMAGE_PATHS


class Star(Entity):
    def __init__(self, app, scene, pos: vec3, z_vel: float):
        vel = vec3(0, 0, z_vel)

        super().__init__(app, scene, None, position=pos, velocity=vel)

        self._surface = self.app.load(
            "STAR", lambda: pygame.Surface(ivec2(4)).convert()
        ).copy()
        self._surface.fill((255, 255, 255))
        self._surface.set_alpha(50)

    def render(self, camera):
        return super().render(camera, scale=False, fade=False)

    def __call__(self, script):
        yield
        while True:
            self._surface.set_alpha(50)
            yield script.sleep(random.uniform(1, 10))

            if random.random() < 0.5:
                self._surface.set_alpha(0)
            else:
                self._surface.set_alpha(120)
            yield script.sleep(0.1)
