#!/usr/bin/env python

# Level Script

# Use scene.when to schedule events.
# Yield when you want to wait until the next event.
# This is a generator.  Using a busy loop will halt the game.
from math import pi
from random import uniform

from game.entities.ai import CircleAi, ChasingAi
from game.scripts.level import Level


class Level4(Level):
    number = 4
    name = "The Butterfly Menace"
    ground = "#F7CA18"
    sky = "#303266"
    music = "butterfly.ogg"

    def __call__(self):
        self.scene.stars()

        yield from super().__call__()

        text = """
        The butterflies have been hiding
        in the great Desert.
        
        Put it and end
        While they're still weak!
        """
        yield from self.slow_type_lines(text, 5, "yellow", 0.05)

        # TODO: Check for level clear ?
        yield self.pause(100)
        yield from self.slow_type("Well done !", 5, "green", clear=True)
