#!/usr/bin/python
import pygame
from glm import vec3

from game.base.entity import Entity
from game.constants import *

# from game.entities.bullet import Bullet


class Player(Entity):
    def __init__(self, app, scene, speed=vec3(1000, 1000, 1)):
        super().__init__(app, scene)
        self.score = 0

        self.dirkeys = [
            # directions
            pygame.K_LEFT,
            pygame.K_RIGHT,
            pygame.K_UP,
            pygame.K_DOWN,
        ]
        self.actionkeys = [pygame.K_RETURN]
        self.dir = [False] * len(self.dirkeys)
        self.speed = speed

    def action(self, btn):
        # print('shoot')
        if btn == 0:
            self.scene.add(
                Entity(
                    self.app,
                    self.scene,
                    "butterfly-orange.png",
                    position=self.position,
                    velocity=-Z*10,
                    life=0.5,
                )
            )

    def event(self, event):
        if event.type == pygame.KEYUP or event.type == pygame.KEYDOWN:
            for i, key in enumerate(self.dirkeys):
                if key == event.key:
                    self.dir[i] = event.type == pygame.KEYDOWN
            for i, key in enumerate(self.actionkeys):
                if key == event.key:
                    if event.type == pygame.KEYDOWN:
                        self.action(i)

    def update(self, dt):
        self.velocity = (
            vec3(
                -self.dir[0] + self.dir[1],
                -self.dir[2] + self.dir[3],
                -1,  # always going forwards
            )
            * self.speed
        )

        super().update(dt)
