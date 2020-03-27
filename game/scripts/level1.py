#!/usr/bin/env python

# Level Script

# Use scene.when to schedule events.
# Yield when you want to wait until the next event.
# This is a generator.  Using a busy loop will halt the game.
from game.scripts.level import Level
from game.constants import GREEN


class Level1(Level):
    name = "Level 1"
    sky = "#59ABE3"
    ground = GREEN
    music = "butterfly.mp3"

    def __call__(self):

        yield from super().__call__()

        for _ in range(10):
            self.spawn(0, 0)
            self.spawn_powerup(0, 0)
            yield self.pause(1)

        self.spawn(0.5, 0.5)
        self.spawn(0.5, -0.5)
        self.spawn(-0.5, -0.5)
        self.spawn(-0.5, 0.5)

        yield self.pause(3)

        self.spawn(0, 0)
        yield self.pause(1)
        for i in range(1, 5):
            self.spawn(i / 10, 0)
            self.spawn(-i / 10, 0)
            yield self.pause(1)
