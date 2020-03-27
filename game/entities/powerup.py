#!/usr/bin/python

import random

import pygame
from glm import vec3
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

        if letter == None:  # random powerup
            # no default weapon and  add hearts
            powerups = list(w.letter for w in WEAPONS[1:]) + ["♥"]
            self.letter = random.choice(powerups)

        self.heart = self.letter == "♥"

        # get color of item
        if self.heart:
            color = pygame.Color("red")
        else:
            for wpn in WEAPONS:
                if self.letter == wpn.letter:
                    color = pygame.Color(wpn.color)
                    break
        assert color

        super().__init__(app, scene, self.letter, color, **kwargs)

        self.solid = True

        self.collision_size = self.size = vec3(500)
        self.time = 0
        self.offset = vec3(0)

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
        super().render(camera)
