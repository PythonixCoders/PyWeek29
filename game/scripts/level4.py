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
    default_ai = AvoidAi(50, 40)

    def __call__(self):
        self.scene.stars()

        # reset in case we are doing the level again
        # As it is changed throughout the level
        self.default_ai = AvoidAi(50, 40)

        yield from super().__call__()
        self.engine_boost(1.5)

        text = """
        The butterflies have been hiding
        in the great Desert.
        
        Put it an end
        While they're still weak!
        """
        yield from self.slow_type_lines(text, 5, "yellow", 0.05)

        for i in range(10):
            self.spawn(uniform(-0.5, 0.5), 0)
            yield self.medium_pause()
        yield self.medium_pause()

        yield from self.v_shape(4)
        yield self.medium_pause()

        yield from self.combine(
            self.rotating_v_shape(4), self.rotating_v_shape(4, start_angle=pi / 2)
        )
        yield self.bigg_pause()

        yield from self.combine(
            self.rotating_v_shape(4),
            self.rotating_v_shape(4, start_angle=pi * 2 / 3),
            self.rotating_v_shape(4, start_angle=pi * 4 / 3),
        )
        yield self.bigg_pause()

        text = """
They sure are avoiding well.
Take those aiming bullets.
And teach them a lesson!        
        """.splitlines()
        yield from self.slow_type(text[1], color="yellow")
        self.spawn_powerup("A", 0, 0)
        yield from self.slow_type(text[2].center(len(text[1])), color="green")
        yield from self.slow_type(text[3].center(len(text[1])), color="yellow")

        yield self.big_pause()

        self.default_ai.radius *= 1.3

        for i in range(20):
            self.spawn(uniform(-0.3, 0.3), 0)
            yield self.small_pause()
        yield self.big_pause()

        yield from self.combine(
            self.rotating_v_shape(5), self.rotating_v_shape(5, start_angle=pi),
        )
        yield self.big_pause()

        self.spawn_powerup("A", 0, 0)
        yield from self.rotating_circle(5, 30, 1.3)
        yield self.big_pause()

        self.spawn(0, 0)
        yield from self.rotating_circle(5, 60, 1.5)
        self.spawn_powerup("A", 0, 0)
        yield self.huge_pause()

        yield from self.rotating_circle(
            8, 100,
        )
        self.huge_pause()

        yield from self.rotating_v_shape(4)
        self.medium_pause()
        yield from self.rotating_v_shape(4)

        # TODO: Check for level clear ?
        yield self.huge_pause()
        yield from self.slow_type("Well done !", 5, "green", clear=True)
