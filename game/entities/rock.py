from random import randint, choice

import glm
from glm import vec2, vec3, ivec2
import pygame
import random

from game.base.entity import Entity
from game.constants import CLOUD_IMAGE_PATHS
from game.util import ncolor, random_rgb, pg_color
from game.constants import *


class Rock(Entity):
    def __init__(self, app, scene, pos: vec3, z_vel: float, **kwargs):

        super().__init__(app, scene, None, position=pos, velocity=Z * 1000, **kwargs)

        self._surface = None
        gcolor = self.scene.ground_color
        if gcolor:

            if "ROCK" not in self.app.cache:
                # self.color = ncolor("white")
                self._surface = pygame.Surface(ivec2(4))
                # self.color = ncolor("white")
                self._surface.fill(pg_color(glm.mix(ncolor("black"), gcolor, 0.4)))
                # self._surface.fill((0,0,0))

                self.app.cache["ROCK"] = self._surface

                # self.velocity = Z * 10000 + z_vel
            else:
                self._surface = self.app.cache["ROCK"]

    def update(self, t):
        if not self._surface or self.position.z > self.scene.player.position.z:
            self.remove()
            return
        super().update(t)

    def render(self, camera):
        return super().render(camera, fade=False)
