#!/usr/bin/env python

import pygame
import functools
from game.util.signal import Signal
from game.util.when import When

# key function to do depth sort
z_compare = functools.cmp_to_key(lambda a, b: a.get().position.z - b.get().position.z)


class Scene(Signal):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.when = When()

    def add(self, entity):
        slot = self.connect(entity, weak=False)
        entity.slots.append(slot)
        if hasattr(entity, "event"):
            entity.slots.append(self.app.add_event_listener(entity))
        return entity

    def remove(self, entity):
        return self.disconnect(entity)

    def update(self, dt):

        # do time-based events
        self.when.update(dt)

        # self.sort(lambda a, b: a.z < b.z)
        self.slots = sorted(self.slots, key=z_compare)

        # call update(dt) on each entitiy
        self.each(lambda x, dt: x.update(dt), dt)

    def render(self, camera):
        # call render(camera) on all scene entities
        self.app.screen.fill(pygame.Color("lightblue"))

        # call render on each entity
        self.each(lambda x: x.render(camera))
