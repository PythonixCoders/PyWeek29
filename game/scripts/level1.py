#!/usr/bin/env python

# Level Script

# Use scene.when to schedule events.
# Yield when you want to wait until the next event.
# This is a generator.  Using a busy loop will halt the game.

from game.constants import GREEN
from game.scripts.level import Level


class Level1(Level):
    number = 1
    name = "The Butterflies Awaken"
    ground = GREEN
    music = "butterfly.ogg"

    def __call__(self):
        self.cloudy()

        yield from super().__call__()

        self.spawn(0, 0)
        yield self.pause(2)
        self.spawn(0, 0)
        yield self.pause(3)

        self.square(0.1)
        yield self.pause(2)

        self.square(0.25)
        yield self.pause(10)

        yield from self.slow_type("The butterflies are organising !", 5, delay=0.08)
        yield self.pause(2)
        yield from self.slow_type(
            "Destroy them while we still can !", 5, "red", 0.08, True
        )

        self.spawn(0, 0)
        yield self.pause(1)
        for i in range(1, 5):
            self.spawn(i / 14, 0)
            self.spawn(-i / 14, 0)
            yield self.pause(1)

        yield self.pause(3)

        self.spawn(0, 0)
        yield self.pause(1)
        for i in range(1, 4):
            self.spawn(i / 14, 0)
            self.spawn(-i / 14, 0)
            self.spawn(0, i / 14)
            self.spawn(0, -i / 14)
            yield self.pause(1)

        # TODO: Check for level clear ?
        yield self.pause(15)
        yield from self.slow_type("Well done !", 5, "green", clear=True)
