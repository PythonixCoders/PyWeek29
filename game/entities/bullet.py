#!/usr/bin/env python
# from .abstract.entity import Entity
from game.constants import *
from game.base.entity import Entity
from glm import vec3, normalize
from game.entities.butterfly import Butterfly


class Bullet(Entity):
    def __init__(self, app, scene, parent, position, direction):

        velocity = normalize(direction) * BULLET_SPEED
        super().__init__(
            app, scene, BULLET_IMAGE_PATH, position=position, velocity=velocity, life=1,
        )
        self.solid = True
        self.size.z = 1000  # to prevent tunneling
        self.parent = parent

    def collision(self, other, dt):
        if isinstance(other, Butterfly):
            self.parent.score += 1
            other.explode()
