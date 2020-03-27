#!/usr/bin/env python

from game.base.entity import Entity
import random
from glm import vec3


class Being(Entity):
    """
    An entity with HP
    """

    def __init__(self, app, scene, filename=None, **kwargs):
        super().__init__(app, scene, filename, **kwargs)
        self.solid = True
        self.hp = 1
        self.stats = None
        self.alive = True  # prevent mutliple kill()
        self.friendly = False

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
            killed = False
            if self.hp == 0:
                killed = self.kill(dmg_taken, bullet, damager)
            if damager.stats:
                damager.stats.kills = int(killed)
                damager.stats.damage_done += dmg_taken
                damager.score += max(int(dmg_taken), 1)
        return dmg_taken

    def explode(self):
        # TODO: This is supposed to be an explosion
        for x in range(10):
            self.scene.add(
                Entity(
                    self.app,
                    self.scene,
                    "bullet.png",
                    position=self.position,
                    velocity=self.velocity
                    + (
                        vec3(random.random(), random.random(), random.random())
                        - vec3(0.5)
                    )
                    * 100,
                    life=1,
                    particle=True,
                ),
            )
