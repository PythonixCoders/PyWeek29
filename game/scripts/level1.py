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
    sky = Level.night_sky
    music = "butterfly.ogg"

    def __call__(self):
        self.scene.cloudy()
        self.scene.rocks()
        self.scene.stars()
        self.scene.rain()
        self.scene.lightning()

        yield from super().__call__()

        self.spawn(0, 0)
        yield self.small_pause()
        self.spawn(0, 0)
        yield self.medium_pause()

        self.square(0.1)
        yield self.medium_pause()

        self.square(0.25)
        yield self.huge_pause()

        yield from self.slow_type("The butterflies are organising!", 5, delay=0.08)
        yield self.medium_pause()
        yield from self.slow_type(
            "Destroy them while we still can!", 5, "red", 0.08, True
        )

        yield from self.v_shape(5)
        yield self.big_pause()

        self.spawn(0, 0)
        yield self.small_pause()
        for i in range(1, 4):
            self.spawn(i / 14, 0)
            self.spawn(-i / 14, 0)
            self.spawn(0, i / 14)
            self.spawn(0, -i / 14)
            yield self.small_pause()

        # TODO: Check for level clear ?
        yield self.huge_pause()
        yield from self.slow_type("Well done !", 5, "green", clear=True)
