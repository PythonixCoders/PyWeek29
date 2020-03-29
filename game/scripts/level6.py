from game.entities.ai import ChasingAi, AvoidAi, RandomFireAi
from game.entities.buttabomber import ButtaBomber
from game.entities.flyer import Flyer
from game.scripts.level import Level


class Level6(Level):
    number = 6
    name = "The Return of the Butterfly"
    ground = "#F0E149"
    sky = "#562A85"
    music = "butterfly.ogg"
    default_ai = ChasingAi

    def __call__(self):
        self.scene.cloudy()
        self.scene.rocks(30)
        self.scene.stars()
        self.scene.rain()
        # self.scene.lightning_strike()

        yield from super().__call__()

        # with self.skip():
        #     self.engine_boost(1.5 ** 2)

        #     yield from self.slow_type("This level is still in construction")
        #     yield from self.slow_type("Sorry", 7, "red")

        # yield from self.slow_type("Here is some missing content", 9)

        # yield self.medium_pause()

        # self.spawn_powerup("star", 0, 0)
        # yield self.pause(10)

        for x in range(3):
            for i in range(1, 5):
                self.square(i * 0.1, None, ButtaBomber)
                self.square(0.25, None, Flyer)
                yield self.pause(5)

        # TODO: Check for level clear ?
        yield self.huge_pause()
        yield from self.slow_type("Well done !", 5, "green", clear=True)
