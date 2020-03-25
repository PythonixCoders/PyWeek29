#!/usr/bin/env python
# from .abstract.entity import Entity
from game.constants import *
from game.base.entity import Entity
from glm import vec3


class Bullet(Entity):
    def __init__(self, app, parent, scene, position=vec3(0), velocity=None):
        super().__init__(
            app,
            scene,
            "bullet.png",
            position=position,
            velocity=(velocity or (-Z * 4000)),
            life=1,
        )
        self.solid = True
        self.size.z = 1000  # to prevent tunneling
        self.parent = None

    def collision(self, other, dt):
        # print('bullet collision ->', other)
        # if self.removed:
        #     assert False
        if self.parent and self.parent is not other:
            self.parent.score += 1
            other.remove()
