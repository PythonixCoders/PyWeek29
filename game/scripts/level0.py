#!/usr/bin/env python

# Level Script

# Use scene.when to schedule events.
# Yield when you want to wait until the next event.
# This is a generator.  Using a busy loop will halt the game.
from random import uniform

from game.entities.ai import CircleAi, ChasingAi
from game.scripts.level import Level
from game.constants import GREEN


class Level0(Level):
    number = 0
    name = "Tutorial"
    ground = GREEN
    music = "butterfly.ogg"

    def __call__(self):
        self.cloudy()

        yield from super().__call__()

        self.slow_type("You better right code if you want a tutorial", 5)

        # TODO: Check for level clear ?
        yield self.pause(15)
        # yield from self.slow_type("Well done !", 5, "green", clear=True)
