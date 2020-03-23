#!/usr/bin/env python

import pygame
import functools
from game.abstract.signal import Signal
from game.abstract.when import When

# key function to do depth sort
z_compare = functools.cmp_to_key(lambda a, b: a.get().z - b.get().z)


class Scene(Signal):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.when = When()

    def add(self, entity):
        slot = self.connect(entity, weak=False)
        entity.slots.append(slot)
        return entity

    def remove(self, entity):
        return self.disconnect(entity)

    def update(self, t):

        # do time-based events
        self.when.update(t)

        # self.sort(lambda a, b: a.z < b.z)
        self.slots = sorted(self.slots, key=z_compare)

        # call update(t) on each entitiy
        self.each(lambda x, t: x.update(t), t)

    def render(self, camera):
        # call render(camera) on all scene entities
        self.app.screen.fill(pygame.Color("lightblue"))

        # call render on each entity
        self.each(lambda x: x.render(camera))
