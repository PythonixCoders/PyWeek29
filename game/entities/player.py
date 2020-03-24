#!/usr/bin/python
import pygame
from glm import vec3

from game.base.entity import Entity
from game.constants import *
from game.entities.bullet import Bullet

# from game.entities.bullet import Bullet


class Player(Entity):
    def __init__(self, app, scene, speed):
        super().__init__(app, scene)
        self.score = 0

        self.dirkeys = [
            # directions
            pygame.K_LEFT,
            pygame.K_RIGHT,
            pygame.K_UP,
            pygame.K_DOWN,
        ]
        self.actionkeys = [pygame.K_RETURN, pygame.K_SPACE]
        self.dir = [False] * len(self.dirkeys)
        self.speed = speed
        self.fire_offset = - Y * 10 - Z * 200

    def action(self, btn):
        self.scene.add(Bullet(
            self.app,
            self.scene,
            self,
            self.position + self.fire_offset
        ))

    def event(self, event):
        if event.type == pygame.KEYUP or event.type == pygame.KEYDOWN:
            for i, key in enumerate(self.dirkeys):
                if key == event.key:
                    self.dir[i] = event.type == pygame.KEYDOWN
            for i, key in enumerate(self.actionkeys):
                if key == event.key:
                    if event.type == pygame.KEYDOWN:
                        self.action(0)

    def update(self, dt):

        self.velocity = (
            vec3(
                -self.dir[0] + self.dir[1],
                -self.dir[3] + self.dir[2],
                -1,  # always going forwards
            )
            * self.speed
        )

        super().update(dt)
