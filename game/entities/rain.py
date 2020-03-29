from random import randint, choice

import glm
from glm import vec2, vec3, ivec2
import pygame
import random

from game.base.entity import Entity
from game.constants import CLOUD_IMAGE_PATHS
from game.util import ncolor, random_rgb, pg_color
from game.constants import *


class Rain(Entity):
    def __init__(self, app, scene, pos: vec3, z_vel: float, **kwargs):

        super().__init__(app, scene, None, position=pos, **kwargs)

        filled = "RAIN" in self.app.cache

        self._surface = self.app.load(
            "RAIN", lambda: pygame.Surface(ivec2(2, 24)).convert()
        )
        if not filled:
            self._surface.fill(
                pg_color(glm.mix(ncolor("lightgray"), self.scene.sky_color, 0.5))
            )

        self.velocity = vec3(0, -1000, 1000 + z_vel)

    def update(self, t):
        if self.position.y < -300:
            self.remove()
            return
        super().update(t)

    def render(self, camera):
        return super().render(camera, scale=False, fade=False)
