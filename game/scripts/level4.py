#!/usr/bin/env python

# Level Script

# Use scene.when to schedule events.
# Yield when you want to wait until the next event.
# This is a generator.  Using a busy loop will halt the game.
from math import pi
from random import uniform

from game.entities.ai import CircleAi, ChasingAi, AvoidAi
from game.scripts.level import Level


class Level4(Level):
    number = 4
    name = "The Butterfly Menace"
    ground = "#F7CA18"
    sky = "#303266"
    music = "butterfly.ogg"
    default_ai = AvoidAi(10, 30)

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

        for i in range(10):
            self.spawn(uniform(-0.5, 0.5), 0)
            yield self.pause(2)
        yield self.pause(2)

        yield from self.v_shape(4)
        yield self.pause(4)

        yield from self.combine(
            self.rotating_v_shape(4), self.rotating_v_shape(4, start_angle=pi / 2)
        )

        # TODO: Check for level clear ?
        yield self.pause(100)
        yield from self.slow_type("Well done !", 5, "green", clear=True)
