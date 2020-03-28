#!/usr/bin/env python

# Level Script

# Use scene.when to schedule events.
# Yield when you want to wait until the next event.
# This is a generator.  Using a busy loop will halt the game.
from math import tau, pi

from game.constants import GREEN
from game.scripts.level import Level


class Level2(Level):
    number = 2
    name = "The Rise of Butterflies"
    ground = GREEN
    music = "butterfly.ogg"

    def __call__(self):
        self.scene.cloudy()
        self.scene.rocks()

        yield from super().__call__()

        self.spawn(0, 0)
        yield from self.rotating_circle(2, 30, 0.5)
        yield self.medium_pause()

        self.spawn(0, 0)
        yield from self.rotating_circle(3, 30)
        yield self.big_pause()

        yield from self.v_shape(5)
        yield self.big_pause()

        yield from self.rotating_v_shape(4)
        yield self.big_pause()

        for i in range(3):
            self.spawn(0, 0)
            yield from self.rotating_circle(5, -40)
            yield self.big_pause()

        yield from self.slow_type("They plan to swarm us.")
        self.spawn_powerup("M", 0, 0)
        yield from self.slow_type("Take this Machine Gun!", color="green")
        self.terminal.write_center("Press shift to change guns.", 15)
        t = "X / Y on controller"
        self.terminal.write_center(t, 17)
        self.terminal.write_center("X", 17, color="blue", length=len(t))
        self.terminal.write_center(
            "Y", 17, color="yellow", length=len(t), char_offset=(4, 0)
        )

        yield self.bigg_pause()
        self.terminal.clear(5)
        self.terminal.clear(15)
        self.terminal.clear(17)

        self.wall(8, 4, 0.2, 0.1)
        yield self.bigg_pause()

        self.spawn_powerup("M")
        self.medium_pause()

        self.wall(8, 4, 0.2, 0.1)
        yield self.big_pause()

        yield from self.combine(
            self.rotating_v_shape(5, angular_mult=0.5),
            self.rotating_v_shape(5, pi / 3, angular_mult=0.5),
            self.rotating_v_shape(5, tau / 3, angular_mult=0.5),
        )
        self.spawn_powerup("M")
        yield self.bigg_pause()

        yield from self.rotating_circle(5, 10)
        yield from self.rotating_circle(7, 20)
        yield self.small_pause()
        yield from self.rotating_circle(11, 30)
        yield self.small_pause()
        yield from self.rotating_circle(11, 40)
        yield self.big_pause()

        # TODO: Check for level clear ?
        yield self.huge_pause()
        yield from self.slow_type("Well done!", 5, "green", clear=True)
