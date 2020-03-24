#!/usr/bin/env python
# from .abstract.entity import Entity
from game.constants import *
from game.base.entity import Entity

# CURRENTLY UNUSED


class Bullet(Entity):
    def __init__(self, app, scene, position):
        super().__init__(app, scene, "bullet.png")
        self.position = position
        self.velocity = -Z * 2000
        self.life = 1

    def update(self, t):
        super().update(t)
        print(self.position)
