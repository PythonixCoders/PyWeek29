#!/usr/bin/env python

# Level Script

# Use scene.when to schedule events.
# Yield when you want to wait until the next event.
# This is a generator.  Using a busy loop will halt the game.
from game.levels.level import Level


class Level1(Level):
    name = "Level 1"
    sky = "#59ABE3"

    def script(self):
        yield from super().script()

        for _ in range(10):
            self.spawn(0, 0)
            yield self.pause(0.5)
