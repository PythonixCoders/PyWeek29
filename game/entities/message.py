#!/usr/bin/python

import random

import pygame
from glm import ivec2, ivec4, vec3

from game.base.entity import Entity
from game.constants import *


class Message(Entity):
    """
    A single message in world space
    """

    def __init__(self, app, scene, text, color, **kwargs):
        super().__init__(app, scene, **kwargs)

        self.app = app
        self.scene = scene

        self.collision_size = self.size = vec3(24 * len(text), 24, 24)
        self.font_size = ivec2(24, 24)
        font_fn = "data/PressStart2P-Regular.ttf"

        self.font = self.app.load(
            font_fn + ":" + str(self.font_size.y),
            lambda: pygame.font.Font(font_fn, self.font_size.y, bold=True),
        )

        self.shadow_color = pygame.Color(120, 120, 120, 0)
        self.shadow2_color = pygame.Color(0, 0, 0, 0)

        self.set(text, color)

    def set(self, text, color):
        self.text = text
        self.size = vec3(24 * len(text), 24, 24)
        self.color = pygame.Color(color) if isinstance(color, str) else color

        self.surfaces = [
            self.font.render(text, True, self.shadow2_color),
            self.font.render(text, True, self.shadow_color),
            self.font.render(text, True, self.color),
        ]

        self.offsets = [vec3(2, -2, 0), vec3(-2, 3, 0), vec3(0, 0, 0)]

    def render(self, camera):
        for i, img in enumerate(self.surfaces):
            super().render(camera, self.surfaces[i], self.position + self.offsets[i])
