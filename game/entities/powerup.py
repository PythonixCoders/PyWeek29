#!/usr/bin/python

import pygame
from glm import vec3, ivec2
import random
import math

from game.entities.message import Message
from game.entities.weapons import WEAPONS
from game.base.entity import Entity
from game.constants import *


class Powerup(Message):
    def __init__(self, app, scene, letter, **kwargs):
        self.letter = letter
        color = None

        if self.letter == "heart":
            self.letter = "♥"
        if self.letter == "star":
            self.letter = "*"
        if letter is None:  # random powerup
            # no default weapon and  add hearts
            powerups = list(w.letter for w in WEAPONS[1:]) + ["♥"]
            self.letter = random.choice(powerups)

        self.heart = self.letter == "♥"
        self.star = self.letter == "*"

        # get color of item
        if self.heart:
            color = pygame.Color("red")
        elif self.star:
            color = pygame.Color("white")

        else:
            for wpn in WEAPONS:
                if self.letter == wpn.letter:
                    color = pygame.Color(wpn.color)
                    break
        assert color

        super().__init__(app, scene, self.letter, color, **kwargs)

        self.solid = True

        self.size = (10, 10)  # About the same as the butterlies
        self.collision_size = vec3(100, 100, 300)
        self.time = 0
        self.offset = vec3(0)

        self.velocity.z = 100

    def __call__(self, script):
        color = self.color
        while True:
            self.set(self.letter, "gray")
            yield script.sleep(0.2)
            self.set(self.letter, color)
            yield script.sleep(0.2)

    def update(self, dt):
        super().update(dt)
        self.time += dt
        self.offset.y = math.sin(self.time * math.tau)

    def render(self, camera):
        half_diag = vec3(-self.size[0], self.size[1], 0) / 2
        world_half_diag = camera.rel_to_world(half_diag) - camera.position

        pos_tl = camera.world_to_screen(self.position + world_half_diag)
        pos_bl = camera.world_to_screen(self.position - world_half_diag)

        if None in (pos_tl, pos_bl):
            # behind the camera
            self.scene.remove(self)
            return

        self.font_size = ivec2(pos_bl.xy - pos_tl.xy) / 2

        # fade = 2 == twice bright
        super().render(camera, None, self.position + self.offset, fade=2)
