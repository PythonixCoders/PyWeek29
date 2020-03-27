#!/usr/bin/env python
# from .abstract.entity import Entity
from glm import normalize

from game.base.being import Being
from game.base.entity import Entity
from game.constants import *


class Bullet(Entity):
    def __init__(
        self,
        app,
        scene,
        parent,
        position,
        direction,
        damage,
        img=BULLET_IMAGE_PATH,
        life=1,
        speed=BULLET_SPEED,
        **kwargs
    ):

        velocity = normalize(direction) * speed
        super().__init__(
            app,
            scene,
            BULLET_IMAGE_PATH,
            position=position,
            velocity=velocity,
            life=life,
            **kwargs
        )
        self.damage = damage
        self.solid = True
        self.size.z = BULLET_SIZE  # to prevent tunneling
        self.parent = parent  # whoever shot the bullet

    def collision(self, other, dt):
        # enemy vs player or player vs enemy?
        if isinstance(other, Being):
            if self.parent.friendly != other.friendly:
                other.hurt(self.damage, self, self.parent)  # apply dmg
                self.remove()  # remove the bullet
