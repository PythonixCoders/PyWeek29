from game.scripts.level import Level
from game.constants import GREEN
from game.entities.ai import *


class Level3(Level):
    number = 3
    name = "The Butterflies Strike Back"
    ground = GREEN
    music = "butterfly.ogg"

    def __call__(self):
        self.cloudy()

        yield from super().__call__()
        yield from self.spawn_powerup(0, 0, letter="heart")

        yield from self.v_shape(5)
        yield from self.v_shape(5, dir=(0, 1))
        yield self.pause(4)

        yield from self.slow_type(
            "The Butterflies are Swarming You",
            self.terminal.size.y / 2,
            delay=0.05,
            clear=True,
        )
        yield self.pause(1)
        yield from self.slow_type("Quick!", self.terminal.size.y / 2, delay=0.05)
        yield from self.slow_type(
            "KILL THEM ALL!",
            self.terminal.size.y / 2,
            color="red",
            delay=0.1,
            clear=True,
        )
        yield self.pause(1)

        self.spawn(0, 0)
        # yield from self.square(0.2)
        yield from self.rotating_v_shape(3, angular_speed=0.3)
        yield self.pause(10)
        yield from self.circle(10, 0.4, delay=0.2)
        yield self.pause(5)

        yield from self.slow_type(
            "You defeated many of them...",
            5,
            delay=0.05,
            clear=True,
        )
        yield from self.slow_type("...But some remain", 5, delay=0.05, clear=True)
        yield self.pause(1)
        yield from self.slow_type("Take this, you'll need it!", 5, color="green", clear=False)

        yield from self.spawn_powerup(0, 0, letter="heart")
        yield self.pause(7)

        for i in range(5):
            yield from self.circle((i + 1) * 2, i / 5 * 0.7, ai=AvoidAi())
            yield self.pause(5)

        # TODO: Check for level clear ?
        yield self.pause(10)
        yield from self.slow_type("Well Done!", 5, color="green", clear=True)
