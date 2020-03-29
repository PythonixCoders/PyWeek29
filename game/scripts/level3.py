from math import pi
from random import uniform

from game.constants import GREEN
from game.scripts.level import Level


class Level3(Level):
    number = 3
    name = "Attack of the Butterflies"
    ground = GREEN
    sky = "#040a15"
    music = "butterfly.ogg"

    def __call__(self):
        self.scene.cloudy()
        self.scene.stars()
        self.scene.lightning(0.03)
        self.scene.rocks(20)

        yield from super().__call__()

        yield from self.slow_type("They try to take us by surprise")
        yield from self.slow_type("         But we've got...      ")
        yield from self.slow_type(
            "           BIG GUNS!           ", color="red", clear=5
        )

        with self.set_faster(2):
            yield from self.v_shape(20)
            yield from self.v_shape(10, dir=(0, 1))
        self.spawn_powerup("M")
        yield self.medium_pause()

        with self.set_faster(2):
            yield from self.combine(self.v_shape(20), self.v_shape(10, dir=(0, 1)))
        self.spawn_powerup("M")

        yield self.big_pause()

        # FIXME: Maybe in an other level
        yield from self.slow_type("Quick!", self.terminal.size.y / 2, delay=0.05)

        yield from self.rotating_circle(5, 10)
        yield from self.rotating_circle(10, 20)

        yield from self.slow_type(
            "KILL THEM ALL!",
            self.terminal.size.y / 2,
            color="red",
            delay=0.1,
            clear=True,
        )

        with self.set_faster(3):
            yield from self.rotating_v_shape(6, angular_mult=0.2)
            yield from self.rotating_v_shape(5, pi, angular_mult=0.4)
            self.spawn_powerup(letter="heart")
            yield from self.rotating_v_shape(3, pi, angular_mult=0.6)
        yield self.big_pause()

        for i in range(1, 5):
            center = uniform(-0.3, 0.3), uniform(-0.2, 0.2)
            self.spawn(*center)
            yield from self.rotating_circle(
                11 - 2 * i, 20, speed_mult=1 + i, center=center
            )
            yield self.big_pause()

            self.wall(4, 4, 0.3, 0.3)
            yield self.bigg_pause()

        self.spawn()
        for i in range(3):
            yield from self.circle(5, 10 * i)

        # TODO: Check for level clear ?
        yield self.huge_pause()
        yield from self.slow_type("Well Done!", 5, color="green", clear=True)
