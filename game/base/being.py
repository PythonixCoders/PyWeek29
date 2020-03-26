#!/usr/bin/env python

from game.base.entity import Entity


class Being(Entity):
    """
    An entity with HP
    """

    def __init__(self, app, scene, filename=None):
        super().__init__(app, scene, filename)
        self.solid = True
        self.hp = 1.0

    def hurt(self, dmg, bullet, player):
        if not self.hp:
            return 0
        self.hp -= dmg
        if self.hp <= 0:
            player.score += max(int(dmg), 1)
            self.kill(dmg, bullet, player)
            return dmg
        return dmg
