#!/usr/bin/python
import pygame
from glm import vec3

from game.base.entity import Entity
from game.constants import *
from game.entities.bullet import Bullet
from game.entities.butterfly import Butterfly

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
        self.fire_offset = -15*Y - Z * 200

        self.solid = True

    def collision(self, other, dt):
        if isinstance(other, Butterfly):
            self.score += 1
            other.explode()

    def action(self, btn):

        # Assuming state is Game
        camera = self.app.state.camera
        aim = camera.rel_to_world(vec3(0, 0, -camera.screen_dist))
        start = self.position + self.fire_offset
        direction = aim - start
        self.scene.add(
            Bullet(self.app, self.scene, self, start, direction)
        )

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
