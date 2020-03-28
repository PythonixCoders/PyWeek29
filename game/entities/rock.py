from random import randint, choice

from glm import vec2, vec3, ivec2
import pygame
import random

from game.base.entity import Entity
from game.constants import CLOUD_IMAGE_PATHS
from game.util import ncolor, random_rgb
from game.constants import *


class Rock(Entity):
    def __init__(self, app, scene, pos: vec3, z_vel: float, **kwargs):

        super().__init__(app, scene, None, position=pos, **kwargs)

        self.color = ncolor("white")
        # self.color = glm.mix(
        #     ncolor(self.scene.ground_color or 'white'),
        #     random_rgb(),
        #     random.random() * 0.8
        # )
        self._surface = pygame.Surface(ivec2(8))
        self._surface.fill(self.color)

        self.velocity = Z * 500

    def render(self, camera):
        return super().render(camera, scale=False)
