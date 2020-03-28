#!/usr/bin/python

import random

import pygame
from glm import ivec2, ivec4, vec3

from game.base.entity import Entity
from game.util import *
from game.constants import *


class Message(Entity):
    """
    A single message in world space
    """

    def __init__(self, app, scene, text, color, **kwargs):
        super().__init__(app, scene, **kwargs)

        self.app = app
        self.scene = scene

        self.collision_size = self.size = vec3(24 * len(text), 24, 150)
        self.font_size = ivec2(24, 24)

        self.shadow_color = pygame.Color(120, 120, 120, 0)
        self.shadow2_color = pygame.Color(0, 0, 0, 0)

        self.set(text, color)

    @property
    def font_size(self):
        return self._font_size

    @font_size.setter
    def font_size(self, value):
        self._font_size = value

        font_fn = "data/PressStart2P-Regular.ttf"
        self.font = self.app.load(
            font_fn + ":" + str(self.font_size.y),
            lambda: pygame.font.Font(font_fn, self.font_size.y, bold=True),
        )

    def set(self, text, color):
        self.text = text
        self.size = vec3(24 * len(text), 24, 24)
        self.color = pg_color(color)

        self.surfaces = [
            self.font.render(text, True, self.shadow2_color),
            self.font.render(text, True, self.shadow_color),
            self.font.render(text, True, self.color),
        ]

        self.offsets = [vec3(2, -2, 0), vec3(-2, 3, 0), vec3(0, 0, 0)]

    def render(self, camera, surf=None, pos=None, scale=True, fade=True):
        if not pos:
            pos = self.position
        for i, img in enumerate(self.surfaces):
            super().render(camera, self.surfaces[i], pos + self.offsets[i], scale, fade)
