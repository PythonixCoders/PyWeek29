#!/usr/bin/env python
from glm import ivec2
from .entity import Entity
import enum
import pygame
from glm import vec2, vec3


class Camera(Entity):
    """
    A camera whose position is the center of the screen
    """
    def __init__(self, app, scene):
        super().__init__(app, scene)
        self.depth = 2
        self.keys = [
            pygame.K_LEFT,
            pygame.K_RIGHT,
            pygame.K_SPACE,
            pygame.K_LSHIFT,
            pygame.K_UP,
            pygame.K_DOWN,
        ]
        self.dir = [False] * len(self.keys)

        self.speed = 1000

    def event(self, ev):
        if ev.type == pygame.KEYUP or ev.type == pygame.KEYDOWN:
            for i in range(len(self.keys)):
                if self.keys[i] == ev.key:
                    self.dir[i] = True if ev.type == pygame.KEYDOWN else False

        self.velocity = (
            vec3(
                (-1 if self.dir[0] else 0) + (1 if self.dir[1] else 0),
                (-1 if self.dir[2] else 0) + (1 if self.dir[3] else 0),
                (-1 if self.dir[4] else 0) + (1 if self.dir[5] else 0),
            )
            * self.speed
        )
        self._velocity_z = self._velocity_z / 1000.0

    def update(self, t):
        super().update(t)
        # print(self.position)
