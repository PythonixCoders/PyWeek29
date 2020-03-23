#!/usr/bin/env python
import pygame
from glm import vec3

from game.abstract.entity import Entity


class Camera(Entity):
    """
    A camera whose position is the center of the screen
    """

    def __init__(self, app, scene, speed=vec3(200, 200, 1)):
        super().__init__(app, scene)
        self.keys = [
            pygame.K_LEFT,
            pygame.K_RIGHT,
            pygame.K_SPACE,
            pygame.K_LSHIFT,
            pygame.K_UP,
            pygame.K_DOWN,
        ]
        self.dir = [False] * len(self.keys)
        self.speed = speed

    def event(self, event):
        if event.type == pygame.KEYUP or event.type == pygame.KEYDOWN:
            for i, key in enumerate(self.keys):
                if key == event.key:
                    self.dir[i] = (event.type == pygame.KEYDOWN)

        self.velocity = (
            vec3(
                -self.dir[0] + self.dir[1],
                -self.dir[2] + self.dir[3],
                -self.dir[4] + self.dir[5],
            )
            * self.speed
        )

    def update(self, dt):
        super().update(dt)
