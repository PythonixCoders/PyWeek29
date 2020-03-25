#!/usr/bin/env python
# from .abstract.entity import Entity
from game.constants import *
from game.base.entity import Entity
from glm import vec3

# CURRENTLY UNUSED


class Bullet(Entity):
    def __init__(self, app, scene, position=vec3(0), velocity=None):
        super().__init__(
            app,
            scene,
            "bullet.png",
            position=position,
            velocity=(velocity or (-Z * 4000)),
            life=1,
        )
