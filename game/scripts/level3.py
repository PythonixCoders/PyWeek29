from math import pi
from random import uniform

from game.constants import GREEN
<<<<<<< HEAD:game/scripts/level3.py
=======
from game.entities.ai import RandomFireAi
from game.entities.flyer import Flyer
>>>>>>> add level 5:game/scripts/level5.py
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

<<<<<<< HEAD:game/scripts/level3.py
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
=======
        with self.skip():
            yield from super().__call__()

            yield from self.slow_type("Since their last beating")
            yield self.small_pause()
            yield from self.slow_type("They put their hands on guns", 7)
            yield self.small_pause()
            yield from self.slow_type("And are now", 9)
            yield self.small_pause()
            yield from self.slow_type("ATTACKING US!", 12, "red", 0.03)

            for i in range(5):
                self.terminal.write_center("ATTACKING US!", 12, "red")
                yield self.pause(0.1)
                self.terminal.clear(12)
                yield self.pause(0.1)
            self.terminal.clear()

            self.spawn()
            yield self.small_pause()
            self.spawn()
            yield self.small_pause()
            self.spawn()
            yield self.small_pause()

            yield from self.slow_type("Keep moving!")
            yield self.small_pause()
            yield from self.slow_type("Engine boost :)", 13, "green")
            self.engine_boost(1.5)

            self.square(0.1)
            yield self.medium_pause()
            self.terminal.clear()

            for i in range(51):
                self.spawn(uniform(-0.3, 0.2), uniform(-0.2, 0.2))
                self.spawn(uniform(-0.3, 0.2), uniform(-0.2, 0.2))
                yield self.small_pause()

                if i % 20 == 10:
                    self.spawn_powerup("heart", uniform(-0.3, 0.2), uniform(-0.2, 0.2))
                if i % 20 == 19:
                    self.spawn_powerup("A", uniform(-0.3, 0.2), uniform(-0.2, 0.2))

            yield from self.rotating_circle(10, 20)
            self.big_pause()
            yield from self.rotating_v_shape(5)
            self.spawn_powerup("M", 0.2)
            self.spawn_powerup("A", -0.2)
            self.spawn_powerup("L", -0)
            yield self.bigg_pause()

            self.wall(4, 4, 0.3, 0.3)
            yield self.medium_pause()

            self.spawn_powerup("heart", -0.2)
            self.spawn_powerup("A", 0.2)
>>>>>>> add level 5:game/scripts/level5.py
            yield self.big_pause()

            self.wall(4, 4, 0.3, 0.3)
            yield self.bigg_pause()

        self.spawn()
        for i in range(3):
            yield from self.circle(5, 10 * i)

        # TODO: Check for level clear ?
        yield self.huge_pause()
        yield from self.slow_type("Well Done!", 5, color="green", clear=True)
