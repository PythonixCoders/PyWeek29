#!/usr/bin/env python

from game.base.entity import Entity
from game.constants import Y, SOUNDS_DIR, SPRITES_DIR, ORANGE, FULL_FOG_DISTANCE


class Enemy(Entity):
    DEFAULT_SCALE = 5

    def __init__(self, app, scene, pos, color=ORANGE, scale=DEFAULT_SCALE, num=0, hp=1):
        super().__init__(app, scene)
        self.num = num
        self.solid = True
        self.hp = hp

    def hurt(self, dmg, bullet, player):
        if not self.hp:
            return 0
        self.hp -= dmg
        if self.hp <= 0:
            player.score += dmg
            self.kill(dmg, bullet, player)
            return dmg
        return dmg
