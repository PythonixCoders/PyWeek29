#!/usr/bin/env python

from game.base.entity import Entity


class Being(Entity):
    """
    An entity with HP
    """

    def __init__(self, app, scene, filename=None, **kwargs):
        super().__init__(app, scene, filename, **kwargs)
        self.solid = True
        self.hp = 1.0
        self.score = 0
        self.alive = True  # prevent mutliple kill()

    def hurt(self, dmg, bullet, damager):
        """
        Apply damage from bullet shot by damager
        Returns amount of damage taken (won't be more than self.hp)
        """
        if not self.hp:
            return 0
        dmg_taken = min(self.hp, dmg)
        if dmg_taken > 0:
            self.hp -= dmg_taken
            assert self.hp >= 0
            if self.hp == 0:
                self.kill(dmg_taken, bullet, damager)
            damager.score += max(int(dmg_taken), 1)
        return dmg_taken
