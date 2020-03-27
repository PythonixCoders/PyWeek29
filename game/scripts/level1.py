#!/usr/bin/env python

# Level Script

# Use scene.when to schedule events.
# Yield when you want to wait until the next event.
# This is a generator.  Using a busy loop will halt the game.
from random import uniform

from game.scripts.level import Level
from game.constants import GREEN


class Level1(Level):
    name = "The butterfly awakens"
    ground = GREEN
    music = "butterfly.mp3"

    def __call__(self):

        yield from super().__call__()

        self.spawn(0, 0)
        yield self.pause(2)
        self.spawn(0, 0)
        yield self.pause(3)

        self.square(0.1)
        yield self.pause(2)

        self.square(0.25)
        yield self.pause(2)

        self.square(0.4)
        yield self.pause(5)

        self.spawn(0, 0)
        yield self.pause(1)
        for i in range(1, 5):
            self.spawn(i / 14, 0)
            self.spawn(-i / 14, 0)
            yield self.pause(1)
