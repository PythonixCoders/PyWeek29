#!/usr/bin/python
import pygame
from glm import vec3

from game.abstract.entity import Entity


class Player(Entity):

    def __init__(self, app, scene, speed=vec3(1000, 1000, 1)):
        super().__init__(app, scene)
        self.score = 0

        self.keys = [
            pygame.K_LEFT,
            pygame.K_RIGHT,
            pygame.K_UP,
            pygame.K_DOWN,
            pygame.K_SPACE,
            pygame.K_LSHIFT,
        ]
        self.dir = [False] * len(self.keys)
        self.speed = speed

    def event(self, event):
        if event.type == pygame.KEYUP or event.type == pygame.KEYDOWN:
            for i, key in enumerate(self.keys):
                if key == event.key:
                    self.dir[i] = (event.type == pygame.KEYDOWN)

    def update(self, dt):
        self.velocity = (
            vec3(
                -self.dir[0] + self.dir[1],
                -self.dir[2] + self.dir[3],
                -self.dir[4] + self.dir[5],
            )
            * self.speed
        )

        super().update(dt)
