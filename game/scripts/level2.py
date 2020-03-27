#!/usr/bin/env python

# Level Script

# Use scene.when to schedule events.
# Yield when you want to wait until the next event.
# This is a generator.  Using a busy loop will halt the game.
from math import pi
from random import uniform

from game.entities.ai import CircleAi, ChasingAi
from game.scripts.level import Level
from game.constants import GREEN


class Level2(Level):
    number = 2
    name = "N"
    ground = GREEN
    music = "butterfly.ogg"

    def __call__(self):
        self.scene.cloudy()
        self.scene.stars()

        yield from super().__call__()

        self.spawn(0, 0)
        yield from self.rotating_circle(2, 30, 20)
        yield self.pause(4)

        self.spawn(0, 0)
        yield from self.rotating_circle(2, -30, 40)
        yield self.pause(4)

        self.spawn(0, 0)
        yield from self.rotating_circle(3, 30)
        yield self.pause(4)

        yield from self.v_shape(5)
        yield self.pause(5)

        yield from self.rotating_v_shape(4, delay=1.5)
        yield self.pause(5)

        for i in range(3):
            self.spawn(0, 0)
            yield from self.rotating_circle(5, -40)
            yield self.pause(3)

        # TODO: Check for level clear ?
        yield self.pause(10)
        yield from self.slow_type("Well done !", 5, "green", clear=True)
