from game.constants import GREEN
from game.scripts.level import Level

from game.entities.butterfly import Butterfly
from game.entities.buttabomber import ButtaBomber
from game.entities.flyer import Flyer


class Level5(Level):
    number = 5
    name = "Uh Oh"
    ground = "darkblue"
    sky = "darkred"
    music = "butterfly2.ogg"

    def __call__(self):
        self.scene.cloudy()
        self.scene.rocks()
        self.scene.stars()
        self.scene.rain()
        self.scene.lightning(50)

        yield from super().__call__()

        self.square(0.25, 0, ButtaBomber)

        # for i in range(1, 4):
        #     self.spawn(i / 14, 0)
        #     self.spawn(-i / 14, 0)
        #     self.spawn(0, i / 14)
        #     self.spawn(0, -i / 14)
        #     yield self.small_pause()

        # TODO: Check for level clear ?
        yield self.huge_pause()
        yield from self.slow_type("Well done !", 5, "green", clear=True)
