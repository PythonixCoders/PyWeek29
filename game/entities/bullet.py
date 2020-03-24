#!/usr/bin/env python
# from .abstract.entity import Entity
from game.constants import *
from game.base.entity import Entity
from glm import vec3

# CURRENTLY UNUSED


class Bullet(Entity):
    def __init__(self, app, scene, parent, position=vec3(0)):
        super().__init__(
            app,
            scene,
            "bullet.png",
            position = position,
            velocity = parent.velocity + (-Z * 4000),
            life=1
        )

