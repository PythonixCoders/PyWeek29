#!/usr/bin/env python
# from .abstract.entity import Entity
from game.constants import *
from game.base.entity import Entity
from glm import vec3, normalize
from game.base.enemy import Enemy


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
        **kwargs
    ):

        velocity = normalize(direction) * BULLET_SPEED
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
        if isinstance(other, Enemy):
            other.hurt(self.damage, self, self.parent)  # apply dmg
            self.remove()  # remove the bullet
