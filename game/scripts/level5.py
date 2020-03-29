from math import pi
from random import uniform

from game.constants import GREEN
from game.scripts.level import Level


class Level5(Level):
    number = 5
    name = "Attack of the Butterflies"
    ground = "blue"
    sky = "#ff6500"
    music = "butterfly.ogg"

    def __call__(self):
        self.scene.cloudy()
        self.scene.stars()
        self.scene.lightning(0.03)
        self.scene.rocks(20)

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
            yield self.big_pause()

            self.wall(4, 4, 0.3, 0.3)
            yield self.bigg_pause()

        self.spawn()
        for i in range(3):
            yield from self.circle(5, 10 * i)

        # TODO: Check for level clear ?
        yield self.huge_pause()
        yield from self.slow_type("Well Done!", 5, color="green", clear=True)
