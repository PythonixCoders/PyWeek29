#!/usr/bin/python

import random

import pygame
from glm import ivec2, ivec4

from game.base.entity import Entity
from game.constants import *


class Message(Entity):
    """
    A single message in world space
    """

    def __init__(self, app, scene, text):
        super().__init__(app, scene)

        self.app = app
        self.scene = scene
        self.text = text

        self.font_size = ivec2(24, 24)
        font_fn = "data/PressStart2P-Regular.ttf"

        self.font = self.app.load(
            font_fn + ":" + str(self.font_size.y),
            lambda: pygame.font.Font(font_fn, self.font_size.y, bold=True),
        )

        # dirty flags for lazy redrawing
        self.dirty = True

        # set entity surface
        self._surface = pygame.Surface(
            self.app.size, pygame.SRCALPHA, 32
        ).convert_alpha()

        self.bg_color = ivec4(255, 255, 255, 0)  # transparent by default
        self.shadow_color = ivec4(120, 120, 120, 0)
        self.shadow2_color = ivec4(0, 0, 0, 0)

    def update(self, t):
        self.position = self.app.state.player.position + Z * 100
        pass
