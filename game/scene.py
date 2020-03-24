#!/usr/bin/env python

import pygame
import functools
from game.util.signal import Signal, Slot
from game.util.when import When
from os import path
from pygame import Color

# key function to do depth sort
z_compare = functools.cmp_to_key(lambda a, b: a.get().position.z - b.get().position.z)


class Scene(Signal):
    def __init__(self, app, script="level1"):
        super().__init__()
        self.app = app
        self.when = When()
        self.paused = False
        self.script_slots = []
        self._sky_color = pygame.Color("lightblue")
        self.dt = 0
        self.script_fn = script

        self.script = script  # (this calls script() property)

    @property
    def script(self):
        return self.script_fn

    @script.setter
    def script(self, script):
        local = {}
        exec(open(path.join("game/scripts/", script + ".py")).read(), globals(), local)
        self._script = local["script"](self.app, self)

    def sleep(self, t):
        return self.when.once(t, self.resume)

    def add(self, entity):
        self.slots.append(self.connect(entity, weak=False))
        if hasattr(entity, "event"):
            entity.slots.append(self.app.add_event_listener(entity))
        return entity

    @property
    def sky_color(self):
        return self._sky_color

    @sky_color.setter
    def sky_color(self, c):
        # if isinstance(c, float):
        #     c = int(c * 255)
        #     self._sky_color = Color(c, c, c, 0)
        #     return

        if isinstance(c, str):
            self._sky_color = Color(c)
            return

        self._sky_color = Color(*c)

    def remove(self, entity):
        return self.disconnect(entity)

    def resume(self):
        self.paused = False

    def update(self, dt):

        # do time-based events
        self.when.update(dt)

        # scripts needs this
        self.dt = dt

        # run script
        if not self.paused:
            try:
                a = next(self._script)
                self.script_slots.append(a)
            except StopIteration:
                print("Level Finished")
            self.paused = True
            # self.app.state = None # 'menu'

        # self.sort(lambda a, b: a.z < b.z)
        self.slots = sorted(self.slots, key=z_compare)

        # call update(dt) on each entity
        self.each(lambda x, dt: x.update(dt), dt)

    def render(self, camera):
        # call render(camera) on all scene entities
        self.app.screen.fill(self._sky_color)

        # call render on each entity
        self.each(lambda x: x.render(camera))
